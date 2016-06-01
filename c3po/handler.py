import tornado.web

from tornado import gen

from utils import dynamic_client_getter, search_method_option_in_service, pb2json


class HelloHandler(tornado.web.RequestHandler):

    def initialize(self, server, debug):
        self.server = server
        self.stubs = server.stubs
        self.debug = debug

    def get(self):
        html = '''Hello C3PO!<br>
        Here are the stubs!<br>
        <hr>
        '''
        for name, stub in self.stubs.items():
            html += '<h1>%s</h1>' % name
            for k, v in stub.__dict__.items():
                html += '%s=%s' % (k, v) + '<br>'
            html += 'server=%s' % (str(self.server))
            html += '<hr>'
        self.write(html)


class ServiceHandler(tornado.web.RequestHandler):

    def initialize(self, server, debug):
        self.server = server
        self.stubs = server.stubs
        self.debug = debug

    @gen.coroutine
    def get(self, service, call):
        try:
            self.before_request('GET', service, call, self.stubs)
        except Exception as e:
            self.set_status(403)
            ret = dict(error='method not allowed')
            if self.debug:
                ret['exception'] = str(e)
            self.write(ret)
            return

        return self.parse_service_call(service, call)

    @gen.coroutine
    def post(self, service, call):
        try:
            self.before_request('POST', service, call, self.stubs)
        except Exception as e:
            self.set_status(403)
            ret = dict(error='method not allowed')
            if self.debug:
                ret['exception'] = str(e)
            self.write(ret)
            return

        return self.parse_service_call(service, call)

    def before_request(self, http_method, service, call, stubs):
        opt = search_method_option_in_service(stubs, service, call)
        method = 'POST'
        if opt and opt.get('method'):
            method = opt.get('method')
        method = str(method).upper()
        http_method = str(http_method).upper()
        if method != http_method:
            raise Exception('method %s != http_method %s' % (
                method, http_method))

    def parse_service_call(self, service, call):
        client = dynamic_client_getter(self.stubs, service)
        args = dict()
        for k, v in self.request.arguments.items():
            if isinstance(v, list):
                v = v[0]
            args[k] = v
        with_call = args.get('with_call') == 1

        if self.server.request_handler:
            args['metadata'] = self.server.request_handler(self.request)

        ret = dict()
        response = None

        try:
            if with_call:
                args['with_call'] = True
                response, call = getattr(client, call)(**args)
            else:
                response = getattr(client, call)(**args)
        except Exception, e:
            self.set_status(400)
            ret = dict(error='no such a service')
            if self.debug:
                ret['msg'] = str(e)

        if response:
            try:
                ret = pb2json(response)
            except:
                self.set_status(400)
                ret = dict(error='cannot load from pb')

        self.write(ret)
