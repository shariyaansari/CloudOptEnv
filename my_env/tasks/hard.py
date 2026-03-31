from my_env.models import CloudResource, Action

def get_initial_state():
    goal = "Clean up the cloud environment: 1) Stop idle dev instances (<5% CPU), 2) Terminate available EBS volumes, 3) Release available Elastic IPs. Do NOT touch production or in-use resources."
    
    resources = [
        CloudResource(
            id="vol-abc123", type="ebs_volume", status="available",
            monthly_cost=20.0, metrics={}, tags={"env": "dev"}
        ),
        CloudResource(
            id="vol-def456", type="ebs_volume", status="in-use",
            monthly_cost=50.0, metrics={}, tags={"env": "prod"}
        ),
        CloudResource(
            id="i-idle-99", type="ec2_instance", status="running",
            monthly_cost=100.0, metrics={"cpu_utilization": 0.5}, tags={"env": "dev"}
        ),
        CloudResource(
            id="eip-000", type="elastic_ip", status="available",
            monthly_cost=3.5, metrics={}, tags={"env": "dev"}
        ),
        CloudResource(
            id="rds-main", type="rds_database", status="running",
            monthly_cost=500.0, metrics={"connections": 150}, tags={"env": "prod"}
        )
    ]
    return resources, goal

def grade(state: dict, last_action: Action):
    resources = state["resources"]
    
    # Check conditions
    vol_terminated = not any(r["id"] == "vol-abc123" for r in resources)
    eip_released = not any(r["id"] == "eip-000" for r in resources)
    
    idle_instance = next((r for r in resources if r["id"] == "i-idle-99"), None)
    instance_stopped = idle_instance is not None and idle_instance["status"] == "stopped"
    
    # Calculate partial reward based on how many things they cleaned up
    score = 0.0
    completed_tasks = sum([vol_terminated, eip_released, instance_stopped])
    
    if completed_tasks == 1:
        score = 0.3
    elif completed_tasks == 2:
        score = 0.6
    elif completed_tasks == 3:
        return 0.9, True # All 3 done!
        
    return score, False