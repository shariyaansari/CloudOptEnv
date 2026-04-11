"""
CloudOptEnv Baseline Inference Script
===================================
Runs an LLM against the Easy, Medium, and Hard tasks.
"""

import os
import json
import textwrap
from typing import List
from openai import OpenAI

# Import our environment and tasks
from my_env.env import CloudOptEnvironment
from my_env.models import Action
import my_env.tasks.easy as task_easy
import my_env.tasks.medium as task_medium
import my_env.tasks.hard as task_hard

# Configuration from environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini") # Use a fast/cheap model for testing

MAX_STEPS = 5

SYSTEM_PROMPT = textwrap.dedent(
    """
    You are an expert Cloud DevOps AI Agent.
    Your objective is to optimize cloud infrastructure costs safely.
    
    You must respond ONLY with a valid JSON object matching this schema:
    {
        "command": "terminate_resource" | "stop_resource" | "release_ip" | "noop",
        "resource_id": "string (the ID of the target resource, or null if noop)",
        "reasoning": "string (brief explanation)"
    }
    Do not wrap the JSON in markdown code blocks. Just output the raw JSON.
    """
).strip()

def run_task(client: OpenAI, task_name: str, task_module) -> float:
    print(f"\n{'='*40}")
    print(f"Starting Task: {task_name}")
    print(f"{'='*40}")
    
    print(f"[START] task={task_name}", flush=True)
    
    env = CloudOptEnvironment(task_module)
    obs = env.reset()
    
    total_reward = 0.0
    actual_steps = 0
    
    for step in range(1, MAX_STEPS + 1):
        if env.done:
            break
        actual_steps = step
            
        print(f"\n--- Step {step} ---")
        print(f"Goal: {obs.goal}")
        print(f"Current Cost: ${obs.current_monthly_cost}/month")
        if obs.last_action_error:
            print(f"WARNING: {obs.last_action_error}")
            
        # Prepare state for the LLM
        state_dump = json.dumps(env.state()["resources"], indent=2)
        user_prompt = f"Current Resources:\n{state_dump}\n\nWhat is your next action?"
        
        try:
            # Call the LLM
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0 # Deterministic output
            )
            
            raw_reply = response.choices[0].message.content.strip()
            
            # Very basic cleanup in case the model adds markdown block formatting
            if raw_reply.startswith("```json"):
                raw_reply = raw_reply[7:-3].strip()
                
            action_dict = json.loads(raw_reply)
            action = Action(**action_dict)
            print(f"Agent Action: {action.command} on {action.resource_id}")
            print(f"Reasoning: {action.reasoning}")
            
        except Exception as e:
            print(f"LLM Error or Parse Failure: {e}")
            action = Action(command="noop", reasoning="Fallback due to error")
            
        # Step the environment forward
        obs, reward, done, info = env.step(action)
        total_reward += reward.score
        
        print(f"Step Reward: {reward.score:.2f} | Info: {info.model_dump()}")
        
        print(f"[STEP] step={step} reward={reward.score}", flush=True)
        
    print(f"\nTask {task_name} Complete. Total Reward: {total_reward:.2f}")
    print(f"[END] task={task_name} score={total_reward} steps={step}", flush=True)
    return total_reward

def main():
    if not API_KEY:
        print("ERROR: OPENAI_API_KEY or HF_TOKEN environment variable is missing.")
        return

    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    tasks = [
        ("Easy", task_easy),
        ("Medium", task_medium),
        ("Hard", task_hard)
    ]
    
    scores = {}
    for name, module in tasks:
        scores[name] = run_task(client, name, module)
        
    print(f"\n{'='*40}")
    print("FINAL BASELINE SCORES")
    print(f"{'='*40}")
    for name, score in scores.items():
        print(f"{name}: {score:.2f}")

if __name__ == "__main__":
    main()