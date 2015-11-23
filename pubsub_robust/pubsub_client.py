""" pubub_client.py

Simple client that sends messages on pubsub_server.
"""

import struct
import socket
import sys

CONNECT_HEADER_FORMAT = '<I'
CONNECT_HEADER_SIZE = struct.calcsize(CONNECT_HEADER_FORMAT)

HEADER_FORMAT = '<II'  # topic, body_size
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
CLOSE_TOPIC = 0


def send_msg(conn, topic, body):
    header = struct.pack(HEADER_FORMAT, topic, len(body))
    msg = header + body.encode('UTF-8')
    conn.sendall(msg)


def connect_to_server(host, port, topic_list):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    # Send topic list
    num_topics = len(topic_list)
    header = struct.pack(CONNECT_HEADER_FORMAT, num_topics)
    body = struct.pack('<' + 'I' * num_topics, *topic_list)
    msg = header + body
    s.sendall(msg)

    return s


def close_connection(conn):
    body_size = 0
    msg = struct.pack('<II', CLOSE_TOPIC, body_size)
    conn.sendall(msg)
    conn.close()


def publish(host, port, topic):
    topic_list = []
    conn = connect_to_server(host, port, topic_list)
    for i in range(100000):
        send_msg(conn, 1, 'Casablanca is a great restaurant')
    close_connection(conn)


def subscribe(host, port, topic):
    topic_list = [topic]
    conn = connect_to_server(host, port, topic_list)
    while True:
        # For speed, we're just receiving and not decoding - to test the server
        data = conn.recv(1024)
        print('Received: {}'.format(data))
    close_connection(conn)

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8888

    def usage():
        print('Usage: {} <pub or sub> <topic number>')
        sys.exit(1)

    try:
        mode = sys.argv[1]
        topic = int(sys.argv[2])
    except IndexError:
        usage()
    if mode == 'pub':
        publish(host, port, topic)
    elif mode == 'sub':
        subscribe(host, port, topic)
    else:
        usage()
