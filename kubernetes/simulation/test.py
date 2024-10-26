# %%
from fleet_model import FleetModel
import mesa
import numpy as np
import json
import pandas as pd
from pymongo import MongoClient

# %%
# # Step 2: Connect to the MongoDB server
# username = 'guest'
# password = 'guest'
# client = MongoClient(f'mongodb://{username}:{password}@localhost:27017/')


# # Step 3: Access the "fleet-sim" database
# db = client['fleet-sim']

# # Step 4: Access the "configs" collection
# collection = db['configs']

# # Step 5: Perform the query
# result = collection.find_one(
#     { "name": "config1" },
#     { "config": 1, "_id": 0 }
# )

# params = result['config']
# print(params)
# with open('D:/GitHub/bachelorseminar/simulation/workspaces.json', 'r') as f:
#     params = json.load(f)

with open('D:/GitHub/bachelorseminar/simulation/config.json', 'r') as f:
    params = json.load(f)

print(params)
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
# results_df = results_df.loc[results_df["Status"] is not None,]
#results_df = results_df[results_df["Status"].notna()]
print(results_df)
# %%
