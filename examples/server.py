import os
import sys

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
C3PO_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, C3PO_DIR + '/')

from c3po.server import Server, Stub

app = Server()

stub = Stub()
stub.name = 'hello'
stub.client_import_type = 'path'
stub.client_module_path = (CURRENT_DIR + '/grpc/client.py')
stub.client_module_name = 'client'
stub.get_client_func = 'get_client'

stub.server_pb2_import_type = 'path'
stub.server_pb2_module_name = 'server_pb2'
stub.server_pb2_module_path = (CURRENT_DIR + '/grpc/server_pb2.py')

app.register(stub)

def handle_header(request):
    metadata = ()
    return metadata

def status_handler(response):
    return 200

app.request_handler = handle_header
app.status_handler= status_handler

try:
    print('running server on 0.0.0.0:8888')
    app.run(debug=True)
except KeyboardInterrupt:
    pass
