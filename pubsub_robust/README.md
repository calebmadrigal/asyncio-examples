# pub-sub server

Pub/sub tcp server with asyncio.

## Usage

Run server:

    python3 pubsub_server.py

Run subscriber client (to topic 1):

    python3 pubsub_client.py sub 1

Run publisher client (to topic 1):

    python3 pubsub_client.py pub 1

The publisher currently sends 100,000 32-byte messages.

## Description

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

## Performance

Initial performance testing:

1-byte messages
* 40k messages/second - 1 subscriber
* 25k messages/second - 2 subscribers
* 20k messages/second - 3 subscribers

32-byte messages
* 20k messages/second - 1 subscriber
* 16k messages/second - 2 subscribers
* 15k messages/second - 3 subscribers

