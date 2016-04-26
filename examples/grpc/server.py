import time
import server_pb2

ONE_DAY_IN_SECONDS = 60 * 60 * 24


class ServiceImpl(server_pb2.BetaSimpleServiceServicer):
    def hello(self, request, context):
        say = request.say
        return server_pb2.HelloResponse(reply='you said: %s' % say)

    Hello = hello


def run():
    server = server_pb2.beta_create_SimpleService_server(
        ServiceImpl()
    )
    server.add_insecure_port('%s:%s' % ('0.0.0.0', 50051))
    server.start()
    print('server started...')
    try:
        while True:
            time.sleep(ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    run()
