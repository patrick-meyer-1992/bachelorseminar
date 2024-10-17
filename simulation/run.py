# %%
import pika
from fleet_model import FleetModel
import mesa
import numpy as np
import pandas as pd
import json

# %%
# Queue parameters
queue_name = 'json_queue'

# Connect to RabbitMQ
credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=mq_port, credentials=credentials))
channel = connection.channel()

# Declare queue (in case it doesn't exist)
channel.queue_declare(queue=queue_name, durable=True)

# Callback function to process messages
def callback(ch, method, properties, body):
    params = json.loads(body)
    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)
    
    # Run mesa.batch_run with the received params
    results = mesa.batch_run(
        FleetModel,
        parameters=params,
        iterations=1,
        max_steps=np.inf,
        number_processes=1,
        data_collection_period=1,
        display_progress=True,
    )
    # Convert results to DataFrame and print
    results_df = pd.DataFrame(results)
    print(results_df)

# Set up consumer
channel.basic_consume(queue=queue_name, on_message_callback=callback)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()




