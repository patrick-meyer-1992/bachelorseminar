# %%
from money_model import MoneyModel
from fleet_model import FleetModel
import seaborn as sns
import numpy as np
import mesa
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json

# %%
# params = {"width": 10, "height": 10, "N": range(5, 100, 5)}

with open("D:/GitHub/bachelorseminar/simulation/workspaces.json") as f:
    params = json.load(f)

    
results = mesa.batch_run(
    FleetModel,
    parameters=params,
    iterations=1,
    max_steps=np.inf,
    number_processes=1,
    data_collection_period=1,
    display_progress=True,
)
# %%
results = pd.DataFrame(results)
# print(results)
# %%

def plot(data):
    """ Create a plotly figure with the number of operational vehicles per day. """
    data = data.loc[:,["iteration", "Step", "Status"]]
    data = data.groupby(["iteration", "Step"])["Status"].value_counts().reset_index(name="Count")
    return data
    # Create the bar plot
    # fig = px.bar(
    #     operational_counts, 
    #     x="Step", 
    #     y="Operational",
    #     title="Number of Operational Vehicles per Day")
    
    # return fig
# %%
p = plot(results)
print(p)
# p.show()
# %%

p

# %%
