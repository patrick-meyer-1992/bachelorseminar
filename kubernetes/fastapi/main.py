from typing import Union
from fastapi import FastAPI, status, HTTPException
from pymongo import MongoClient
import os
from fastapi.middleware.cors import CORSMiddleware
import pika
import json

mongodb_host = os.getenv('MONGODB_HOST')
mongodb_port = os.getenv('MONGODB_PORT')
mongodb_user = os.getenv('MONGO_INITDB_ROOT_USERNAME')
mongodb_password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
# Connection parameters
rabbitmq_host = os.getenv('RABBITMQ_HOST')
rabbitmq_port = os.getenv('RABBITMQ_PORT')
rabbitmq_user = os.getenv('RABBITMQ_DEFAULT_USER')
rabbitmq_password = os.getenv('RABBITMQ_DEFAULT_PASS')

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

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

client = MongoClient(f'mongodb://{mongodb_user}:{mongodb_password}@{mongodb_host}:{mongodb_port}/')
db = client["fleet-sim"]
collection = db["configs"]

@app.get("/get_config/{name}")
def get_config(name: str):
    result = collection.find_one({"name": name})
    if result and "config" in result:
        return {"config": result["config"]}
    else:
        raise HTTPException(status_code=404, detail="Item not found")

@app.get("/get_configs/")
def get_configs():
    results = collection.find({}, {"_id": 0, "name": 1})
    configs = [result["name"] for result in results if "name" in result]
    if configs:
        return {"configs": configs}
    else:
        raise HTTPException(status_code=404, detail="No configs found")
    
@app.post("/add_config/{name}", status_code=status.HTTP_200_OK)
def add_config(name: str, config: Union[str, dict]):
    if collection.find_one({"name": name}):
        raise HTTPException(status_code=400, detail="Item already exists")
    else:
        collection.insert_one({"name": name, "config": config})
        return {"status": "success"}
    
@app.post("/add_sim_job/", status_code=status.HTTP_200_OK)
def add_sim_job(config_name: str, num_vehicles: int, num_iterations: int):
    message = {
        "config": config_name,
        "num_vehicles": num_vehicles,
        "num_iterations": num_iterations
    }
    message = json.dumps(message).encode('utf-8')
    channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=message)
    return {"status": "success"}

    

