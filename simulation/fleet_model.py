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

class FleetModel(mesa.Model):
    def __init__(self, num_vehicles: int = 100, start_date: date = date(2024, 1, 1), end_date: date = date(2024, 12, 31)):
        super().__init__()
        self.num_vehicles = num_vehicles
        self.current_date = start_date
        self.end_date = end_date
        self.schedule = mesa.time.RandomActivation(self)
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

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
        self.current_date += timedelta(days=1)
        if self.current_date >= self.end_date:
            print(f"Simulation ended on {self.current_date}")
            self.running = False
