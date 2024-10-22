import pika
import json

# Connection parameters
rabbitmq_host = 'localhost'
rabbitmq_port = 5672
rabbitmq_user = ''
rabbitmq_password = ''

# Queue and exchange parameters
queue_name = 'json_queue'
exchange_name = 'json_exchange'
routing_key = 'json_key'

# Connect to RabbitMQ
credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials))
channel = connection.channel()

# Declare exchange
channel.exchange_declare(exchange=exchange_name, exchange_type='direct')

# Declare queue
channel.queue_declare(queue=queue_name, durable=True)

# Bind queue to exchange
channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)

# Example of sending a JSON message
with open("D:/GitHub/bachelorseminar/simulation/config.json") as f:
    message = f.read()

channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=message)

print(f"Sent message: {message}")

# Close connection
connection.close()