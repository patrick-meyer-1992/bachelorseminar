from datetime import date, timedelta
import mesa
import numpy as np

class VehicleAgent(mesa.Agent):
    def __init__(self, unique_id, model, failure_rate):
        super().__init__(unique_id, model)
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

        # Check for failure
        self.check_failure()
        # Repair if failed
        if self.status == "failed" or self.status == "repairing":
            self.perform_repair()


    # def perform_maintenance(self):
    #     self.last_maintenance = self.model.schedule.time
    #     self.status = "operational"

    def check_failure(self):
        # if np.random.exponential(1 / self.mtbf) < 1:
        if np.random.uniform() < self.failure_rate:
            self.health = 0
            self.status = "failed"

    def perform_repair(self):
        self.status = "repairing"
        self.health += np.random.normal(self.repair_rate, 3)
        if self.health >= 100:
            self.status = "operational"

class WorkerAgent(mesa.Agent):
    def __init__(self, unique_id, model, repair_rate: float):
        super().__init__(unique_id, model)
        self.repair_rate = repair_rate

class WorkspaceAgent(mesa.Agent):
    def __init__(self, unique_id, model, workers: list[WorkerAgent], repair_facility: 'RepairFacilityAgent'):
        super().__init__(unique_id, model)
        self.workers = dict()
        self.available = True
        self.vehicle = None
        self.repair_facility = repair_facility

        for worker in workers:
            self.workers["id"] = WorkerAgent(worker["id"], self.model, worker["repair_rate"])
    
    def check_in_vehicle(self, vehicle: VehicleAgent):
        self.vehicle = vehicle
        self.available = False

    def step(self):
        if self.vehicle is not None:
            self.repair_vehicle()
    
    def check_out_vehicle(self):
        self.vehicle = None
        self.available = True

    def repair_vehicle(self):
        repair_rate = sum([worker.repair_rate for worker in self.workers])
        self.vehicle.health = self.vehicle.health + repair_rate    

class RepairFacilityAgent(mesa.Agent):
    def __init__(self, unique_id, model, workspaces: list[dict]):
        super().__init__(unique_id, model)
        self.workspaces = dict()

        for workspace in workspaces:
            self.workspaces[workspace["id"]] = WorkspaceAgent(workspace["id"], self.model, workspace["workers"], repair_facility=self)

        self.vehicles = dict()

    def check_in_vehicle(self, vehicle: VehicleAgent):
        self.vehicles[vehicle.unique_id] = vehicle

    def check_out_vehicle(self, vehicle: VehicleAgent):
        self.vehicles.pop(vehicle.unique_id)

class FleetModel(mesa.Model):
    def __init__(self, 
                 num_vehicles: int = 100, 
                 start_date: date = date(2024, 1, 1), 
                 end_date: date = date(2024, 12, 31),
                 repair_facilities: list = list()
            ):
        super().__init__()
        self.schedule = mesa.time.RandomActivation(self)
        self.num_vehicles = num_vehicles
        self.current_date = start_date
        self.end_date = end_date
        self.set_repair_facilities(repair_facilities)
        self.datacollector = mesa.DataCollector(
            agent_reporters={"Status": "status"}
        )
        self.running = True

        # Create vehicles
        for i in range(self.num_vehicles):
            # usage_model = np.random.choice(["light", "medium", "heavy"])
            # maintenance_interval = np.random.randint(5, 15)
            failure_rate = np.random.uniform(0.01, 0.1)
            vehicle = VehicleAgent(i, self, failure_rate)
            self.schedule.add(vehicle)


    def set_repair_facilities(self, repair_facilities: list):
        for repair_facility in repair_facilities:
            self.schedule.add(RepairFacilityAgent(repair_facility["id"], self, repair_facility["workspaces"]))
    
    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
        self.current_date += timedelta(days=1)
        if self.current_date >= self.end_date:
            print(f"Simulation ended on {self.current_date}")
            self.running = False