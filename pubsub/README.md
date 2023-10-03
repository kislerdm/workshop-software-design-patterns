# PubSub

The application mimics pubsub and provides HTTP interface.

## Producer

POST /publish/{topic}
body: record

## Consumer

The consumption starts from the latest offset by default. It means that the consumer will wait for the next incoming
event to be consumed.

GET /consume/{topic}/{clientID}

Use the query parameter `from_start` to start consuming from zero offset:

GET /consume/{topic}/{clientID}?from_start=true
