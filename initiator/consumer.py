import pika, json
from initiator.fixInitiator import FIXInitiator
import os 


RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'orders'
CONFIG_FILE = 'client.cfg' 
fix_client = FIXInitiator(CONFIG_FILE)
fix_client.start()

def callback(ch, method, properties, body):
    order = json.loads(body)
    print("Received order from queue:", order)
    
    try:
        fix_client.send_order(order)  # send through FIX
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("Order executed successfully.")
    except Exception as e:
        print("Failed to execute order:", e)
        # optionally: don't ack, or send to a dead-letter queue

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME, durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

print("Waiting for orders from RabbitMQ...")
channel.start_consuming()
