import server_pb2

import atexit

from grpc.beta import implementations
from random import randint
from grpc._adapter._types import ConnectivityState

global _pool
_pool = dict()


class ChannelPool(object):

    def __init__(self, host, port, pool_size):
        self.host = host
        self.port = port
        self.pool_size = pool_size
        self.channels = []
        self.stubs = []
        # only index, no ref!
        # and this is a stub rank!
        self.working_channel_indexs = set()
        self.connect()

    def flush_channels(self):
        # call this method to check all the channels status
        # if channel connection is failed or idle
        # we could try to reconnect sometime
        channels = [self.channels[i] for i in self.working_channel_indexs]
        for channel in channels:
            try:
                state = channel._low_channel.check_connectivity_state(True)
                if state == ConnectivityState.CONNECTING:
                    self.on_channel_connection(channel, state)
                elif state == ConnectivityState.TRANSIENT_FAILURE:
                    self.on_transient_failure(channel, state)
                elif state == ConnectivityState.FATAL_FAILURE:
                    self.on_fatal_failure(channel, state)
                else:
                    self.on_success(channel, state)
            except Exception, e:
                self.on_exception(channel, state, e)

    def on_channel_connection(self, channel, state):
        pass

    def on_transient_failure(self, channel, state):
        pass

    def on_fatal_failure(self, channel, state):
        pass

    def on_success(self, channel, state):
        pass

    def on_exception(self, channel, state, e):
        pass

    def connect(self):
        for i in range(self.pool_size):
            channel = implementations.insecure_channel(self.host, self.port)
            stub = server_pb2.beta_create_SimpleService_stub(channel)
            # we need to make channels[i] == stubs[i]->channel
            self.channels.append(channel)
            self.stubs.append(stub)

    def shutdown(self):
        for channel in self.channels:
            del channel
        del self.channels
        for stub in self.stubs:
            del stub
        del self.stubs
        self.channels = []
        self.stubs = []

    def get_stub(self):
        index = randint(0, self.pool_size - 1)
        self.working_channel_indexs.add(index)
        return self.stubs[index]

    def __del__(self):
        self.shutdown()


class ClientImpl(object):
    def __init__(self, host='0.0.0.0', port=50051, size=1):
        self.pool = ChannelPool(host, port, size)
        self.pool.connect()
        self.register()

    def register(self):
        key = str(id(self))
        value = self
        if _pool.get(key):
            old_obj = _pool.get(key)
            del old_obj
        _pool[key] = value

    def shutdown(self):
        self.pool.shutdown()

    @property
    def stub(self):
        return self.pool.get_stub()

    def hello(self, words, with_call=False):
        request = server_pb2.HelloRequest(say=words)
        return self.stub.Hello(request, 3, with_call=with_call)

    Hello = hello


def get_client():
    if _pool:
        key = _pool.keys()[0]
        return _pool[key]
    client = ClientImpl()
    return client


def exit_handler():
    # this is a gRPC python bug
    # so we need to end everything
    # when app close
    for _, obj in _pool.items():
        obj.shutdown()

atexit.register(exit_handler)
