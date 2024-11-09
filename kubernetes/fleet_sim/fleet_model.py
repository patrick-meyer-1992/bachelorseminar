from datetime import date, timedelta
import mesa
import numpy as np
# from pymongo import MongoClient
import os
import requests

# mongodb_host = os.getenv('MONGODB_HOST')
# mongodb_port = os.getenv('MONGODB_PORT')
# mongodb_user = os.getenv('MONGO_INITDB_ROOT_USERNAME')
# mongodb_password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')

fastapi_host = os.getenv('FASTAPI_HOST')
fastapi_port = os.getenv('FASTAPI_PORT')

# client = MongoClient(f'mongodb://{mongodb_user}:{mongodb_password}@{mongodb_host}:{mongodb_port}/')
# db = client['fleet-sim']
# collection = db['configs']

class VehicleAgent(mesa.Agent):
    def __init__(self, unique_id, model, failure_rate):
        super().__init__(unique_id, model)
        self.type = "Vehicle"
        # self.usage_model = usage_model
        # self.maintenance_interval = maintenance_interval
        # self.mtbf = mtbf
        self.failure_rate = failure_rate
        # self.last_maintenance = 0
        self.status = "operational"
        self.repair_rate = 10
        self.health = 100

    def step(self):
        # Check if maintenance is due
        # if self.model.schedule.time - self.last_maintenance >= self.maintenance_interval:
        #     self.perform_maintenance()
        if self.status == "operational":
            # Check for failure
            self.check_failure()
        # Repair if failed
        if self.status == "failed":
            self.look_for_repair_facility()

    def look_for_repair_facility(self):
        self.model.distribute_vehicle_to_repair_facility(self)

    # def perform_maintenance(self):
    #     self.last_maintenance = self.model.schedule.time
    #     self.status = "operational"

    def check_failure(self):
        # if np.random.exponential(1 / self.mtbf) < 1:
        if np.random.uniform() < self.failure_rate:
            self.health = 0
            self.status = "failed"

class WorkerAgent(mesa.Agent):
    def __init__(self, unique_id, model, repair_rate_mean: float, repair_rate_sd: float):
        super().__init__(unique_id, model)
        self.repair_rate_mean = repair_rate_mean
        self.repair_rate_sd = repair_rate_sd
        self.type = "Worker"
        self.model.schedule.add(self)

    def get_repair_rate(self):
        return np.random.normal(self.repair_rate_mean, self.repair_rate_sd)

class WorkspaceAgent(mesa.Agent):
    def __init__(self, unique_id, model, workers: list[WorkerAgent], repair_facility: 'RepairFacilityAgent'):
        super().__init__(unique_id, model)
        self.type = "workspace"
        self.workers = dict()
        self.available = True
        self.vehicle = None
        self.repair_facility = repair_facility
        self.model.schedule.add(self)

        for worker in workers:
            self.add_worker(worker["id"], worker["repair_rate_mean"], worker["repair_rate_sd"])

    def add_worker(self, id: str, repair_rate_mean: float, repair_rate_sd: float):
        self.workers[id] = WorkerAgent(id, self.model, repair_rate_mean, repair_rate_sd)
    
    def check_in_vehicle(self, vehicle: VehicleAgent):
        self.vehicle = vehicle
        self.vehicle.status = "repairing"
        self.available = False
 
    def check_out_vehicle(self):
        self.repair_facility.check_out_vehicle(self.vehicle)
        self.vehicle = None
        self.available = True

    def repair_vehicle(self):
        repair_rate = sum([worker.get_repair_rate() for worker in self.workers.values()])
        self.vehicle.health = self.vehicle.health + repair_rate  
        if self.vehicle.health >= 100:
            self.vehicle.health = 100             
    
    # def step(self):
    #     if self.vehicle is not None:
    #         self.repair_vehicle()

    def step(self):
        if self.vehicle is not None:
            self.repair_vehicle()
            if self.vehicle.health >= 100:
                self.vehicle.status = "operational" 
                self.check_out_vehicle()

class RepairFacilityAgent(mesa.Agent):
    def __init__(self, unique_id, model, workspaces: list[dict]):
        super().__init__(unique_id, model)
        self.type = "repair_facility"
        self.workspaces = dict()
        self.vehicles = dict()
        for workspace in workspaces:
            self.add_workspace(workspace["id"], workspace["children"])

    def add_workspace(self, id: str, workers: list[dict]):
        self.workspaces[id] = WorkspaceAgent(id, self.model, workers, self)

    def check_in_vehicle(self, vehicle: VehicleAgent):
        self.vehicles[vehicle.unique_id] = vehicle

    def check_out_vehicle(self, vehicle: VehicleAgent):
        self.vehicles.pop(vehicle.unique_id)

    def get_queue_length(self):
        return len(self.vehicles) - len([workspace for workspace in self.workspaces.values() if not workspace.available])

    def step(self):
        # Distribute vehicles to workspaces
        for vehicle in self.vehicles.values():
            if vehicle.status == "repairing":
                continue
            for workspace in self.workspaces.values():
                if workspace.available:
                    workspace.check_in_vehicle(vehicle)
                    break

class FleetModel(mesa.Model):
    def __init__(self, 
                 repair_config_name: str,
                 num_vehicles: int = 100, 
                 start_date: date = date(2023, 12, 31), 
                 end_date: date = date(2024, 12, 31),
            ):
        super().__init__()
        self.schedule = mesa.time.RandomActivation(self)
        self.num_vehicles = num_vehicles
        self.current_date = start_date
        self.end_date = end_date
        self.set_repair_facilities(repair_config_name)
        self.datacollector = mesa.DataCollector(
            model_reporters={"date": "current_date"},
            agent_reporters={"status": "status", "id": "unique_id", "type": "type"},
        )
        self.running = True

        # Create vehicles
        for i in range(self.num_vehicles):
            # usage_model = np.random.choice(["light", "medium", "heavy"])
            # maintenance_interval = np.random.randint(5, 15)
            failure_rate = np.random.uniform(0.01, 0.1)
            vehicle = VehicleAgent(i, self, failure_rate)
            self.schedule.add(vehicle)

    def load_repair_config(self, repair_config_name: str) -> list:
        # result = collection.find_one(
        #     { "name": repair_config_name },
        #     { "config": 1, "_id": 0 }
        # )
        result = requests.get(f'http://{fastapi_host}:{fastapi_port}/config/{repair_config_name}').json()
        return result['config']

    def set_repair_facilities(self, repair_config_name: str):
        repair_facilities = self.load_repair_config(repair_config_name)
        for repair_facility in repair_facilities:
            self.schedule.add(RepairFacilityAgent(repair_facility["id"], self, repair_facility["children"]))

    def distribute_vehicle_to_repair_facility(self, vehicle: VehicleAgent):
        repair_facility = np.random.choice([agent for agent in self.schedule.agents if isinstance(agent, RepairFacilityAgent)])
        repair_facility.check_in_vehicle(vehicle)
    
    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
        self.current_date += timedelta(days=1)
        if self.current_date >= self.end_date:
            print(f"Simulation ended on {self.current_date}")
            self.running = False