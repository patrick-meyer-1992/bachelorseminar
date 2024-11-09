# %%
from fleet_model import FleetModel
import mesa
import numpy as np
import json
import pandas as pd
# from pymongo import MongoClient
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
from sqlalchemy.sql import text
from sqlalchemy import create_engine

postgres_host = os.getenv('POSTGRES_HOST')
postgres_db = os.getenv('POSTGRES_DB')
postgres_port = "5432"
postgres_user = os.getenv('POSTGRES_USER')
postgres_password = os.getenv('POSTGRES_PASSWORD')

engine = create_engine(f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}')


# %%
experiment_id = "test2"
query = text("SELECT * FROM vehicle_status WHERE experiment_id = :experiment_id")
params = {"experiment_id": experiment_id}
df = pd.read_sql(query, con=engine, params=params)

# %%
df_mean = df.groupby("date")[["operational", "failed", "repairing"]].mean().reset_index()
# %%
fig = go.Figure()
fig.add_trace(go.Scatter(x=df_mean["date"], y=df_mean["failed"], mode='lines', name='Failed'))
fig.add_trace(go.Scatter(x=df_mean["date"], y=df_mean["operational"], mode='lines', name='Operational'))
fig.add_trace(go.Scatter(x=df_mean["date"], y=df_mean["repairing"], mode='lines', name='Repairing'))
fig.show()
print(fig.to_json())

# with open('D:/GitHub/bachelorseminar/kubernetes/fleet_sim/workspaces.json', 'r') as f:
#     params = json.load(f)

params = {
    "num_vehicles": 100,
    "repair_config_name": "config4"
}
# %%
fastapi_host = os.getenv('FASTAPI_HOST')
fastapi_port = os.getenv('FASTAPI_PORT')
print(f'http://{fastapi_host}:{fastapi_port}/config/config4')
result = requests.get(f'http://{fastapi_host}:{fastapi_port}/config/config4')
result = result.json()
# %%
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
results_df = results_df[results_df["type"].notna()]
vehicle_df = results_df[results_df["type"] == "Vehicle"]
status_counts = vehicle_df.groupby(["date", "status"]).size().unstack(fill_value=0).reset_index()
status_counts["repair_config_name"] = results[0]["repair_config_name"]
status_counts["num_vehicles"] = results[0]["num_vehicles"]
status_counts["date"] = status_counts["date"].astype(str)
message = json.dumps(status_counts.to_dict())

# with open("D:/GitHub/bachelorseminar/kubernetes/fleet_sim/message.json", "w") as f:
#     f.write(message)

# %%
response = requests.post("http://localhost:8000/result", data=message)
if response.status_code == 200:
    print("Data successfully sent to the database.")
else:
    print(f"Failed to send data to the database. Status code: {response.status_code}")

# %%
fig = go.Figure()
fig.add_trace(go.Scatter(x=status_counts["Date"], y=status_counts["failed"], mode='lines', name='Failed'))
fig.add_trace(go.Scatter(x=status_counts["Date"], y=status_counts["operational"], mode='lines', name='Operational'))
fig.add_trace(go.Scatter(x=status_counts["Date"], y=status_counts["repairing"], mode='lines', name='Repairing'))
fig.show()
# %%
