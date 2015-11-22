import asyncio


class BusServer:
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
        subscriber_topics = self.subscriber_to_topics[subscriber_writer]
        print('Removing subscriber {} from topics: {}'.format(client_addr, subscriber_topics))
        for topic in subscriber_topics:
            self.topic_to_subscribers[topic].remove(subscriber_writer)
        del self.subscriber_to_topics[subscriber_writer]

    @asyncio.coroutine
    def handle_client(self, client_reader, client_writer):
        client_addr = client_writer.get_extra_info('peername')
        # Get topics
        topics_raw = (yield from client_reader.readline())
        topics = topics_raw.decode("utf-8").rstrip().split(',')
        print('New client {} subscribes to topics: {}'.format(client_addr, topics))
        for topic in topics:
            self.add_subscriber(topic, client_writer)

        while True:
            full_msg_bytes = (yield from client_reader.readline())
            full_msg = full_msg_bytes.decode("utf-8").rstrip()

            if not full_msg or full_msg == 'goodbye':  # an empty string means the client disconnected
                break
            topic, msg = full_msg.split(',')

            if topic in self.topic_to_subscribers:
                for subscriber_writer in self.topic_to_subscribers[topic]:
                    subscriber_writer.write(full_msg_bytes)

            yield from client_writer.drain()

        self.remove_subscriber(client_writer, client_addr)
        client_writer.close()

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
    server = BusServer()
    server.start(loop)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        server.stop(loop)
        loop.close()

if __name__ == '__main__':
    main()
