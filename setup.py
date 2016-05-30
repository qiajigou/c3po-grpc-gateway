from c3po import __version__
from setuptools import setup, find_packages

setup(
    name='c3po',
    version=__version__,
    description='A light weight Python gRPC transport layer gateway with tornado named c3po.',
    author='GuoJing',
    author_email='soundbbg@gmail.com',
    license='MIT',
    url='https://github.com/qiajigou/c3po-grpc-gateway',
    zip_safe=False,
    packages=find_packages(exclude=['examples', 'tests']),
)
