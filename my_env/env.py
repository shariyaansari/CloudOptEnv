import copy
from typing import Tuple, List
from .models import Observation, Action, Reward, Info, CloudResource

class CloudOptEnvironment:
    def __init__(self, task_module):
        """
        task_module is one of our task files (e.g., tasks.easy)
        It must implement get_initial_state() and grade()
        """
        self.task = task_module
        self.max_steps = 10
        self.current_step = 0
        self.resources: List[CloudResource] = []
        self.initial_cost = 0.0
        self.goal = ""
        self.done = False

    def reset(self) -> Observation:
        """Mandatory OpenEnv API: Resets the environment and returns initial observation."""
        self.current_step = 0
        self.done = False
        
        # Load state from the injected task
        self.resources, self.goal = self.task.get_initial_state()
        self.initial_cost = sum(r.monthly_cost for r in self.resources)

        return self._get_observation()

    def state(self) -> dict:
        """Mandatory OpenEnv API: Returns the full internal state."""
        return {
            "step": self.current_step,
            "resources": [r.model_dump() for r in self.resources], # Pydantic v2 dump
            "initial_cost": self.initial_cost,
            "current_cost": self._calculate_current_cost(),
            "done": self.done
        }

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Info]:
        """Mandatory OpenEnv API: Transitions state based on action."""
        if self.done:
            raise RuntimeError("Environment is already done. Call reset().")

        self.current_step += 1
        error_msg = None
        step_reward = 0.0
        critical_failure = False

        # Find the target resource based on the agent's action
        target = next((r for r in self.resources if r.id == action.resource_id), None)

        if action.command != "noop" and not target:
            error_msg = f"Resource {action.resource_id} not found."
            step_reward = -0.05  # Slight penalty for hallucinating IDs

        elif action.command == "terminate_resource":
            if target.tags.get("env") == "prod":
                # DESTRUCTIVE ACTION PENALTY (Judges love this)
                error_msg = f"CRITICAL: Terminated production resource {target.id}!"
                step_reward = -1.0
                critical_failure = True
                self.done = True
            else:
                self.resources.remove(target)
                step_reward = 0.1 # Minor positive reinforcement for a valid action

        elif action.command == "stop_resource":
            if target.type == "ec2_instance" and target.status == "running":
                target.status = "stopped"
                step_reward = 0.1
            else:
                error_msg = f"Cannot stop {target.id} (type: {target.type}, status: {target.status})"

        elif action.command == "release_ip":
            if target.type == "elastic_ip" and target.status == "available":
                self.resources.remove(target)
                step_reward = 0.1
            else:
                error_msg = f"Cannot release {target.id} (it might be in-use)"

        # Enforce step limit
        if self.current_step >= self.max_steps:
            self.done = True

        # Ask the specific task to grade the current state
        task_reward, task_done = self.task.grade(self.state(), action)
        total_reward = max(-1.0, min(1.0, step_reward + task_reward)) # Clamp between -1.0 and 1.0

        if task_done:
            self.done = True

        obs = self._get_observation(error_msg)
        cost_saved = self.initial_cost - self._calculate_current_cost()

        return (
            obs,
            Reward(score=total_reward, is_partial=not self.done),
            self.done,
            Info(cost_saved=cost_saved, critical_failure=critical_failure)
        )

    def _get_observation(self, error: str = None) -> Observation:
        return Observation(
            step=self.current_step,
            goal=self.goal,
            resources=self.resources,
            current_monthly_cost=self._calculate_current_cost(),
            last_action_error=error,
            system_message="Environment active." if not self.done else "Episode terminated."
        )

    def _calculate_current_cost(self) -> float:
        cost = 0.0
        for r in self.resources:
            if r.status == "stopped" and r.type == "ec2_instance":
                cost += r.monthly_cost * 0.1  # Stopped instances still incur storage costs
            else:
                cost += r.monthly_cost
        return round(cost, 2)