import json
import sys
import imp
import importlib

from google.protobuf import json_format
from google.protobuf import descriptor_pb2


class ProtoParseException(Exception):
    pass


class ParseException(Exception):
    pass


def dynamic_client_getter(stubs, service_name):
    stub = stubs.get(service_name)
    if stub:
        if stub.client_import_type == 'path':
            if stub.client_module_name in sys.modules.keys():
                md = importlib.import_module(stub.client_module_name)
            else:
                md = imp.load_source(
                    stub.client_module_name,
                    stub.client_module_path)
        else:
            md = importlib.import_module(stub.client_module)
        cl = getattr(md, stub.get_client_func)
        return cl()


def get_service_identify(stubs, service_name):
    stub = stubs.get(service_name)
    if stub:
        if stub.server_pb2_import_type == 'path':
            if stub.server_pb2_module_name in sys.modules.keys():
                md = importlib.import_module(stub.server_pb2_module_name)
            else:
                md = imp.load_source(
                    stub.server_pb2_module_name,
                    stub.server_pb2_module_path)
        else:
            md = importlib.import_module(stub.server_pb2_module)
        return get_service_identify_from_pb_file(stubs, md)


def get_service_identify_from_pb_file(stubs, pb2):
    method_mapping = dict()
    p = descriptor_pb2.FileDescriptorProto()
    pb2.DESCRIPTOR.CopyToProto(p)
    for s in p.service:
        for m in s.method:
            if not method_mapping.get(m.name):
                method_mapping[m.name] = dict()
            for k, v in m.options._fields.items():
                if hasattr(v, '_fields'):
                    for i, j in v._fields.items():
                        method_mapping[m.name][i.name] = j
    return method_mapping


def search_method_option_in_service(stubs, service, call):
    idt = get_service_identify(stubs, service)
    if not idt:
        raise ProtoParseException('not registed service')
    options = dict()

    for k, v in idt.items():
        if str(k).lower() == call:
            options = v
            break

    if options:
        return options
    raise ProtoParseException('no such a call')


def pb2json(pb):
    return json.loads(json_format.MessageToJson(pb))


def json2pb(pb, js):
    if isinstance(js, dict):
        js = json.dumps(js)
    return json_format.Parse(js, pb)
