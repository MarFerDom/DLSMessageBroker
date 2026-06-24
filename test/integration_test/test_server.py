import pytest
import socket
import json
import logging
from os import path, getenv, getcwd
from sys import argv, _getframe

HOST = getenv("HOST") or "127.0.0.1"
PORT = getenv("PORT") or 65000
# path.dirname(argv[0]) does not work because of env
REQ_RESP_FILEPATH = path.join(getcwd(), 'test', 'integration_test', 'test_send_recv.json')

logging.basicConfig(level=logging.INFO)

def send_recv_test_wrapper(payload, right_response):
    # Wrapper for request and response
    def wrapped():
        # Open socket connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
            client_sock.settimeout(5.0)
            client_sock.connect((HOST, PORT))

            # Send request
            client_sock.sendall(payload.encode())
            print(f"{_getframe().f_code.co_name}: Sending payload")

            # Get response
            response = client_sock.recv(1024)
            print(f"{_getframe().f_code.co_name}: Received reponse")

            # Assert correct reponse
            assert response.decode() == right_response, f"Response mismatch\n{response : }\n{right_response : }"
    return wrapped

with open(REQ_RESP_FILEPATH, 'r') as f:
    test_payloads = json.load(f)
    for test in test_payloads["test_io"]:
        globals()[test['name']] = send_recv_test_wrapper(payload=test['payload'], right_response=test['response'])

if __name__ == "__main__":
    items = dict(filter(
        lambda item: item[0].startswith("test_") and callable(item[1]),
        globals().items()
    ))
    for call in items.values():
        call()