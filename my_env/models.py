from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field

# --- OBSERVATION SPACE ---
class CloudResource(BaseModel):
    id: str
    type: Literal["ec2_instance", "ebs_volume", "rds_database", "elastic_ip"]
    status: Literal["running", "stopped", "available", "in-use"]
    monthly_cost: float
    metrics: Dict[str, float] = Field(description="e.g., {'cpu_utilization': 1.2, 'network_in': 500}")
    tags: Dict[str, str] = Field(description="e.g., {'env': 'prod'}")

class Observation(BaseModel):
    step: int
    goal: str
    resources: List[CloudResource]
    current_monthly_cost: float
    last_action_error: Optional[str] = None
    system_message: Optional[str] = None

# --- ACTION SPACE ---
class Action(BaseModel):
    command: Literal["terminate_resource", "stop_resource", "release_ip", "noop"]
    resource_id: Optional[str] = Field(default=None, description="The ID of the resource to act upon")
    reasoning: str = Field(description="Brief explanation of why the agent took this action")

# --- REWARD & INFO ---
class Reward(BaseModel):
    score: float = Field(ge=-1.0, le=1.0, description="Reward signal")
    is_partial: bool = Field(default=True, description="Whether this is a step reward or final reward")

class Info(BaseModel):
    cost_saved: float
    critical_failure: bool