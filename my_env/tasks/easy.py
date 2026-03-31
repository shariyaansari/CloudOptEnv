from my_env.models import CloudResource, Action

def get_initial_state():
    goal = "Release all unattached Elastic IPs to save costs. Do not touch production instances."
    
    # The starting state the agent will see
    resources = [
        CloudResource(
            id="eip-12345", type="elastic_ip", status="available",
            monthly_cost=3.65, metrics={}, tags={"env": "dev"}
        ),
        CloudResource(
            id="i-99999", type="ec2_instance", status="running",
            monthly_cost=150.0, metrics={"cpu_utilization": 85.0}, tags={"env": "prod"}
        )
    ]
    return resources, goal

def grade(state: dict, last_action: Action):
    """
    Returns (reward: float, done: bool)
    Checks if the specific goal for this task was met.
    """
    resources = state["resources"]
    
    # Check if the unattached IP is gone
    eip_exists = any(r["id"] == "eip-12345" for r in resources)

    if not eip_exists:
        # Task completed perfectly
        return 0.9, True # 0.9 + 0.1 from step reward = 1.0 total
        
    return 0.0, False