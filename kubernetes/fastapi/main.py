from typing import Union
from fastapi import FastAPI, status, HTTPException
from pymongo import MongoClient
import os
from fastapi.middleware.cors import CORSMiddleware
import pika
import json
from sqlalchemy import create_engine
import pandas as pd
from sqlalchemy.sql import text
import plotly.graph_objects as go

mongodb_host = os.getenv('MONGODB_HOST')
mongodb_port = os.getenv('MONGODB_PORT')
mongodb_user = os.getenv('MONGO_INITDB_ROOT_USERNAME')
mongodb_password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')

rabbitmq_host = os.getenv('RABBITMQ_HOST')
rabbitmq_port = os.getenv('RABBITMQ_PORT')
rabbitmq_user = os.getenv('RABBITMQ_DEFAULT_USER')
rabbitmq_password = os.getenv('RABBITMQ_DEFAULT_PASS')

postgres_host = os.getenv('POSTGRES_HOST')
postgres_db = os.getenv('POSTGRES_DB')
postgres_port = "5432"
postgres_user = os.getenv('POSTGRES_USER')
postgres_password = os.getenv('POSTGRES_PASSWORD')

engine = create_engine(f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}')

# Queue and exchange parameters
queue_name = 'json_queue'
exchange_name = 'json_exchange'
routing_key = 'json_key'
# Connect to RabbitMQ
credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)

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

@app.get("/config/{name}")
def config(name: str):
    result = collection.find_one({"name": name})
    if result and "config" in result:
        return {"config": result["config"]}
    else:
        raise HTTPException(status_code=404, detail="Item not found")

@app.get("/configs/")
def configs():
    results = collection.find({}, {"_id": 0, "name": 1})
    configs = [result["name"] for result in results if "name" in result]
    if configs:
        return {"configs": configs}
    else:
        raise HTTPException(status_code=404, detail="No configs found")
    
@app.get("/experiments/")
def experiments():
    query = text("SELECT DISTINCT experiment_id FROM vehicle_status")  
    df = pd.read_sql(query, con=engine)
    experiments = df["experiment_id"].tolist()
    return {"experiments": experiments}

@app.post("/add_config/{name}", status_code=status.HTTP_200_OK)
def add_config(name: str, config: Union[str, dict]):
    if collection.find_one({"name": name}):
        raise HTTPException(status_code=400, detail="Item already exists")
    else:
        collection.insert_one({"name": name, "config": config["config"]})
        return {"status": "success"}
    
@app.post("/sim_jobs/", status_code=status.HTTP_200_OK)
def sim_jobs(message: dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange_name, exchange_type='direct')
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
    num_iterations = int(message.pop("num_iterations"))
    # message = {
    #     "experiment_id": experiment_id,
    #     "config": config_name,
    #     "num_vehicles": num_vehicles,
    # }
    repair_config_names = message.pop("repair_config_name")
    repair_config_names = repair_config_names.replace(" ", "").split(",")

    num_vehicles = message.pop("num_vehicles")
    num_vehicles = num_vehicles.replace(" ", "").split(",")

    # message = json.dumps(message).encode('utf-8')

    for repair_config_name in repair_config_names:
        for num_vehicle in num_vehicles:
            for _ in range(num_iterations):
                job = dict()
                job["experiment_id"] = message["experiment_id"]
                job["repair_config_name"] = repair_config_name
                job["num_vehicles"] = int(num_vehicle)
                job = json.dumps(job).encode('utf-8')
                channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=job)
    # for _ in range(num_iterations):
    #     channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=message)
    connection.close()
    return {"status": "success"}

@app.post("/result/{experiment_id}", status_code=status.HTTP_200_OK)
def result(result: dict, experiment_id: str):
    # result = json.loads(result)
    df = pd.DataFrame(result)
    df["experiment_id"] = experiment_id
    df.to_sql("vehicle_status", con=engine, if_exists="append", index=False)
    return {"status": "success"}

@app.get("/experiment_params/{experiment_id}")
def experiment_params(experiment_id: str):
    query = text(f"SELECT DISTINCT num_vehicles, repair_config_name FROM vehicle_status WHERE experiment_id = '{experiment_id}'")
    df = pd.read_sql(query, con=engine)
    num_vehicles = df["num_vehicles"].unique().tolist()
    repair_config_name = df["repair_config_name"].unique().tolist()
    return {
        "num_vehicles": num_vehicles,
        "repair_config_name" : repair_config_name
    }

@app.get("/plot_result/")
def plot_result(experiment_id: str, num_vehicles: int, repair_config_name: str):
    query = text("SELECT * FROM vehicle_status WHERE experiment_id = :experiment_id AND num_vehicles = :num_vehicles AND repair_config_name = :repair_config_name")
    params = {"experiment_id": experiment_id, "num_vehicles": num_vehicles, "repair_config_name": repair_config_name}
    df = pd.read_sql(query, con=engine, params=params)
    df_mean = df.groupby("date")[["operational", "failed", "repairing"]].mean().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_mean["date"], y=df_mean["failed"], mode='lines', name='Failed'))
    fig.add_trace(go.Scatter(x=df_mean["date"], y=df_mean["operational"], mode='lines', name='Operational'))
    fig.add_trace(go.Scatter(x=df_mean["date"], y=df_mean["repairing"], mode='lines', name='Repairing'))
    # fig.update_layout(
    #     title=f"Anzahl Fahrzeuge pro Zustand",
    #     xaxis_title='',
    #     yaxis_title='Anzahl Fahrzeuge'
    # )
    fig_json = fig.to_json(engine="json")
    fig_json = json.loads(fig_json)
    return fig_json

# @app.get("/health", status_code=status.HTTP_200_OK)
# def health_check():
#     try:
#         # Check if the persistent connection is open
#         if connection.is_open:
#             return {"status": "ok"}
#         else:
#             raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="RabbitMQ connection is closed")
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))