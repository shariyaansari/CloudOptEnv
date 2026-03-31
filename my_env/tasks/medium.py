from my_env.models import CloudResource, Action

def get_initial_state():
    goal = "Stop any development EC2 instances that have a CPU utilization of less than 5%."
    
    resources = [
        CloudResource(
            id="i-dev-777", type="ec2_instance", status="running",
            monthly_cost=45.0, metrics={"cpu_utilization": 1.2}, tags={"env": "dev"}
        ),
        CloudResource(
            id="i-prod-888", type="ec2_instance", status="running",
            monthly_cost=300.0, metrics={"cpu_utilization": 89.5}, tags={"env": "prod"}
        )
    ]
    return resources, goal

def grade(state: dict, last_action: Action):
    resources = state["resources"]
    
    dev_instance = next((r for r in resources if r["id"] == "i-dev-777"), None)
    
    if dev_instance and dev_instance["status"] == "stopped":
        return 0.9, True # Success! Agent stopped the idle instance.
        
    return 0.0, False