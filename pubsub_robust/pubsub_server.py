""" pubsub_server.py

This is a simple pub-sub server that works over TCP.

When a client first connects, it sends the list of topics it wants to subscribe to
in this format:

* body size (little-endian unsigned int)
* list of little-endian unsigned ints, one for each topic. 0 is the only excluded value,
  as 0 indicates a close-connection command.

Messages are in this format:

* topic (little-endian unsigned int)
* body size (little-endian unsigned int)
* body (raw bytes in any format)

When a client wishes to close the connection, it sends:

* topic = 0
* body size = 0
* no body

"""

import asyncio
import struct

CONNECT_HEADER_FORMAT = '<I'
CONNECT_HEADER_SIZE = struct.calcsize(CONNECT_HEADER_FORMAT)

HEADER_FORMAT = '<II'  # topic, body_size
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
CLOSE_TOPIC = 0


class PubSubBus:
    def __init__(self):
        self.server = None
        self.topic_to_subscribers = {}  # topic -> [sub1_writer, sub2_writer, ...]
        self.subscriber_to_topics = {}  # subscriber_writer -> [topic1, topic2, ...]

    def add_subscriber(self, topic, subscriber_writer):
        if topic in self.topic_to_subscribers:
            self.topic_to_subscribers[topic].append(subscriber_writer)
        else:
            self.topic_to_subscribers[topic] = [subscriber_writer]

        if subscriber_writer in self.subscriber_to_topics:
            self.subscriber_to_topics[subscriber_writer].append(topic)
        else:
            self.subscriber_to_topics[subscriber_writer] = [topic]

    def remove_subscriber(self, subscriber_writer, client_addr):
        if subscriber_writer in self.subscriber_to_topics:
            subscriber_topics = self.subscriber_to_topics[subscriber_writer]
            print('Removing subscriber {} from topics: {}'.format(client_addr, subscriber_topics))
            for topic in subscriber_topics:
                self.topic_to_subscribers[topic].remove(subscriber_writer)
            del self.subscriber_to_topics[subscriber_writer]

    @asyncio.coroutine
    def read_exact(self, client_reader, bytes_to_read):
        bytes_read = 0
        buf = b''
        while bytes_read < bytes_to_read:
            just_read = yield from client_reader.read(bytes_to_read - bytes_read)
            if not just_read:
                raise IOError('Client closed before reading full message')
            buf += just_read
            bytes_read += len(just_read)
        return buf

    @asyncio.coroutine
    def read_message(self, client_reader):
        raw_header = yield from self.read_exact(client_reader, HEADER_SIZE)
        try:
            topic, body_size = struct.unpack(HEADER_FORMAT, raw_header)
        except struct.error:
            raise IOError('Invalid message header. Should be 2 little-endian ' +
                          'unsigned ints representing (1) topic (2) body size')

        body = yield from self.read_exact(client_reader, body_size)
        full_msg = raw_header + body

        return topic, full_msg

    @asyncio.coroutine
    def read_connect_message(self, client_reader):
        raw_header = yield from self.read_exact(client_reader, CONNECT_HEADER_SIZE)
        try:
            num_topics = struct.unpack(CONNECT_HEADER_FORMAT, raw_header)[0]
        except (struct.error, IndexError):
            raise IOError('Invalid connect message header. Should be a little-endian unsigned int')

        body_format = '<' + 'I' * num_topics
        body_size = struct.calcsize(body_format)
        body = yield from self.read_exact(client_reader, body_size)

        try:
            topic_list = struct.unpack(body_format, body)
        except struct.error:
            raise IOError('Invalid connect message body. Should be a sequence ' +
                          'of little-endian unsigned ints')

        return topic_list

    @asyncio.coroutine
    def handle_client(self, client_reader, client_writer):
        client_addr = client_writer.get_extra_info('peername')
        print('New connection from {}'.format(client_addr))

        # Get topics - the initial message the client should send
        try:
            topic_list = yield from self.read_connect_message(client_reader)
        except IOError as e:
            print('ERROR: {}'.format(e))
            client_writer.close()
            return

        for topic in topic_list:
            self.add_subscriber(topic, client_writer)

        print('Client {} subscribes to topics: {}'.format(client_addr, topic_list))

        def close_connection():
            self.remove_subscriber(client_writer, client_addr)
            client_writer.close()

        try:
            while True:
                topic, msg = yield from self.read_message(client_reader)

                if topic == CLOSE_TOPIC:
                    break

                if topic in self.topic_to_subscribers:
                    for subscriber_writer in self.topic_to_subscribers[topic]:
                        subscriber_writer.write(msg)

                yield from client_writer.drain()

        except IOError as e:
            print('ERROR: {}'.format(e))

        close_connection()

    def start(self, loop):
        coro = asyncio.start_server(self.handle_client, '127.0.0.1', 8888, loop=loop)
        self.server = loop.run_until_complete(coro)
        print('Serving on {}'.format(self.server.sockets[0].getsockname()))

    def stop(self, loop):
        if self.server is not None:
            self.server.close()
            loop.run_until_complete(self.server.wait_closed())
            self.server = None


def main():
    loop = asyncio.get_event_loop()

    # creates a server and starts listening to TCP connections
    server = PubSubBus()
    server.start(loop)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        server.stop(loop)
        loop.close()

if __name__ == '__main__':
    main()
