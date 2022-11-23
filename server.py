import socket
import re
from http import HTTPStatus


def get_raw_request(clientConn):
    end_headers = '\r\n\r\n'
    data_str = ''
    while True:
        data = clientConn.recv(1024)
        data_str += data.decode()
        if not data:
            break
        if end_headers in data_str:
            break
    return data_str.split(end_headers)[0]


def get_headers(request):
    headers = ''
    regexp = '(?P<headers>Host[\w\s.\/:\*-]*)'
    match = re.search(regexp, request)
    if match:
        headers = match.group('headers')
    return headers


def get_method(request):
    method = request.split()[0]
    return method


def get_status(request):
    status_with_desc = f'200 {HTTPStatus(200).name}'
    regexp = '(?P<status>\/\?status=)(?P<value>\d+)'
    match = re.search(regexp, request)
    if match:
        status = int(match.group('value'))
        status_with_desc = f'{status} {HTTPStatus(status).name}'
    return status_with_desc


def send_to_client(clientConn, payload):
    clientConn.send(payload)


with socket.socket() as serverSocket:
    serverSocket.bind(('localhost', 8888))
    serverSocket.listen()

    while True:
        clientConn, clientAddr = serverSocket.accept()
        data = get_raw_request(clientConn)
        headers = get_headers(data)
        method = get_method(data)
        status = get_status(data)

        result = f'Request Method: {method}\n' \
                 f'Response Status: {status}\n' \
                 f'{headers}'
        print(result)
        send_to_client(clientConn, result.encode())
