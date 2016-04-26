import os
import sys

C3PO_DIR = os.path.dirname(os.path.realpath(__file__))
C3PO_DIR = os.path.dirname(C3PO_DIR)
sys.path.insert(0, C3PO_DIR + '/')

from c3po.server import Server, Stub

app = Server()

stub = Stub()
stub.name = 'hello'
stub.client_import_type = 'path'
stub.client_module_path = ('/Users/guojing/vipkid/'
                           'c3po-grpc-gateway/examples/grpc/client.py')
stub.client_module_name = 'client'
stub.get_client_func = 'get_client'

stub.server_pb2_import_type = 'path'
stub.server_pb2_module_name = 'server_pb2'
stub.server_pb2_module_path = ('/Users/guojing/vipkid'
                               '/c3po-grpc-gateway/examples'
                               '/grpc/server_pb2.py')

app.register(stub)

try:
    print('running server on 0.0.0.0:8888')
    app.run(debug=True)
except KeyboardInterrupt:
    pass
