# %%
import pika
from fleet_model import FleetModel
import mesa
import numpy as np
import json
import os
import pandas as pd
import requests

# %%
# Connection parameters
rabbitmq_host = os.getenv('RABBITMQ_HOST')
rabbitmq_port = os.getenv('RABBITMQ_PORT')
rabbitmq_user = os.getenv('RABBITMQ_DEFAULT_USER')
rabbitmq_password = os.getenv('RABBITMQ_DEFAULT_PASS')

fastapi_host = os.getenv('FASTAPI_HOST')
fastapi_port = os.getenv('FASTAPI_PORT')

# Queue parameters
queue_name = 'json_queue'

# Connect to RabbitMQ
credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials))
channel = connection.channel()

# Declare queue (in case it doesn't exist)
channel.queue_declare(queue=queue_name, durable=True)

# Callback function to process messages
def callback(ch, method, properties, body):
    params = json.loads(body)
    print(params)
    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

    experiment_id = params.pop("experiment_id")
    repair_config_name = params["repair_config_name"]
    num_vehicles = params["num_vehicles"]
    
    # Run mesa.batch_run with the received params
    results = mesa.batch_run(
        FleetModel,
        parameters=params,
        iterations=1,
        max_steps=np.inf,
        number_processes=1,
        data_collection_period=1,
        display_progress=False,
    )
    results_df = pd.DataFrame(results)
    results_df = results_df[results_df["type"].notna()]
    vehicle_df = results_df[results_df["type"] == "Vehicle"]
    status_counts = vehicle_df.groupby(["date", "status"]).size().unstack(fill_value=0).reset_index()
    status_counts["repair_config_name"] = repair_config_name
    status_counts["num_vehicles"] = num_vehicles
    status_counts["date"] = status_counts["date"].astype(str)
    message = json.dumps(status_counts.to_dict())
    requests.post(f"http://{fastapi_host}:{fastapi_port}/result/{experiment_id}", data=message)
    print("Results posted to FastAPI")

# Set up consumer
print('Waiting for messages. To exit press CTRL+C')
channel.basic_consume(queue=queue_name, on_message_callback=callback)

channel.start_consuming()




