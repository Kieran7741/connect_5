import os

HOST = 'localhost:5000'
API_PREFIX = '{host}/api/v1/'.format(host=HOST)


def make_request_to_server(endpoint, method='GET'):

    url = os.path.join(API_PREFIX, endpoint)



