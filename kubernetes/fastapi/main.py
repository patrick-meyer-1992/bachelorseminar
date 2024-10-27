from typing import Union
from fastapi import FastAPI, status, HTTPException
from pymongo import MongoClient
import os
from fastapi.middleware.cors import CORSMiddleware

mongodb_host = os.getenv('MONGODB_HOST')
mongodb_port = os.getenv('MONGODB_PORT')
mongodb_user = os.getenv('MONGO_INITDB_ROOT_USERNAME')
mongodb_password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')


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
    

