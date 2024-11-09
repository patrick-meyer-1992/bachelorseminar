CREATE TABLE vehicle_status (
    experiment_id VARCHAR(255),
    Date DATE,
    operational INT,
    failed INT,
    repairing INT,
    repair_config_name VARCHAR(255),
    num_vehicles INT
);