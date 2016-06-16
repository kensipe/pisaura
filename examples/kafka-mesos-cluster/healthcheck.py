import sys
import argparse
from pykafka import KafkaClient

INIT, BEFORE_FAILURE, AFTER_FAILURE, AFTER_REVERT = range(4)
STEPS = [INIT, BEFORE_FAILURE, AFTER_FAILURE, AFTER_REVERT]

parser = argparse.ArgumentParser(description='healthcheck')
parser.add_argument('--broker', dest='broker', action='append', default=[])
parser.add_argument('--exclude-broker', dest='exclude_broker', action='append', default=[])
parser.add_argument('--step', dest='step', action='store', type=int, default=INIT)
args = parser.parse_args()

brokers = args.broker
exclude_brokers = args.exclude_broker
hosts = list(set(brokers) - set(exclude_brokers)) if args.step == AFTER_FAILURE else brokers

client = KafkaClient(hosts=",".join(hosts))
topic = client.topics['healthcheck.test']
print("Connected")

# write to the topic
print("Producing messages")
with topic.get_sync_producer() as producer:
    for i in range(4):
        producer.produce('test message %s' % i ** 2)

# read from the topic
print("Consuming")
consumer = topic.get_simple_consumer()
messages = []
for i in range(4):
    message = consumer.consume()
    if message is not None:
        messages.append(message.value)

# check if at least one message can be consumed
print("Consumed %s messages" % len(messages))
if not messages:
    sys.exit()
