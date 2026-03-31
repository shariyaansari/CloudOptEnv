---
title: CloudOptEnv
emoji: ☁️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# CloudOptEnv ☁️💰

**An OpenEnv submission for real-world Cloud Infrastructure Cost Optimization.**
... (keep the rest of your README exactly the same)

# CustomerSupportEnv

**An environment for training AI agents to handle customer support interactions.**

## Environment Description & Motivation
**Real-World Utility:** Customer support automation is critical for scaling support operations. Agents must classify issues accurately, suggest appropriate solutions, and know when to escalate.

**CustomerSupportEnv** simulates realistic customer support scenarios. An AI agent receives customer queries, must classify the issue type, suggest relevant solutions, and escalate when necessary—all while maximizing customer satisfaction.

## Observation Space
The agent receives a highly structured Pydantic model representing the current support interaction:
* `customer_query`: The customer's issue description (string).
* `conversation_history`: List of previous messages exchanged (list of strings).
* `status`: Current interaction status (`new`, `in_progress`, `done`).

## Action Space
The agent issues typed commands via the `Action` Pydantic model:
* `command`: `terminate_resource` | `stop_resource` | `release_ip` | `noop`
* `resource_id`: The target ID.
* `reasoning`: A brief text explanation for the action (useful for audit logs).

## Tasks & Graders
The environment includes 3 progressive difficulty levels with deterministic, programmatic graders. Rewards are continuous [-1.0, 1.0].

1. **Easy (`tasks/easy_task.py`)**: 
   * *Scenario:* "My payment was deducted but order not confirmed"
   * *Objective:* Classify as `payment` issue and suggest `refund` solution.
   * *Difficulty:* Low. Single-step reasoning. Tests issue classification.
2. **Medium (`tasks/medium_task.py`)**: 
   * *Scenario:* "I received a damaged product"
   * *Objective:* Classify as `product_issue` and suggest `replacement` solution.
   * *Difficulty:* Medium. Tests pattern recognition and solution mapping.
3. **Hard (`tasks/hard_task.py`)**: 
   * *Scenario:* "I was charged twice and no response from support"
   * *Objective:* Classify as `payment` issue, suggest `refund and escalate`, and handle escalation appropriately.
   * *Difficulty:* High. Multi-step reasoning and escalation handling
## Setup & Usage Instructions

**1. Install Dependencies**
```

**2. Run Inference Baseline**
```bash
python inference.py
```

This will run the rule-based baseline agent through all three difficulty levels and print scores for each.

## How It Works
- `env/env.py`: The `CustomerSupportEnv` class implementing the environment dynamics.
- `env/models.py`: Pydantic models for `Observation` and `Action`.
- `env/state.py`: Internal state tracking for each episode.
- `tasks/`: Task definitions for easy, medium, and hard difficulty levels.
- `graders/`: Deterministic graders that score agent performance.
- `inference.py`: Baseline agent implementation and test runner.on tool locally just to be 100% sure everything is wired up right:
```bash
openenv validate