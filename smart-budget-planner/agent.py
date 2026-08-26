"""
agent.py
-----------------------------------------------------------------------------
PURPOSE
Defines BudgetAgent: the class that actually runs the plan-act loop. It
owns one Memory object and, on each call to run(goal), repeatedly asks the
LLM what to do next, executes any tool it chooses via tools.py, feeds the
result back, and lets the LLM decide the next step — until it has enough
information to give a final answer. This file is the "brain + control
flow" of the whole project; everything else (config, tools, memory) exists
to support this loop.

WHAT WILL EVENTUALLY GO HERE
- __init__: creates a Memory instance, builds the LLM client using values
  from config.py, sets the system prompt.
- run(goal, max_steps=config.MAX_STEPS): the main entry point called from
  the notebook.
- The loop itself:
    1. send [system prompt + chat_history + goal] + TOOL_SCHEMAS to the LLM
    2. if the LLM returned a tool call -> look it up in TOOL_REGISTRY,
       execute it with the current Memory, log the call + result to the
       trace, append the result to chat_history, go back to step 1
    3. if the LLM returned a plain answer -> log it as the final answer,
       return it, stop
- A small safety check so the loop always stops within max_steps.

WHICH CSE476 REQUIREMENT THIS SATISFIES
- "A plan-act loop (it takes more than one step)" — directly, this file
  IS the loop.
- "Takes more than one step, deciding what to do next from tool results" —
  the step-2/step-1 cycle above is exactly this.
- Ties together the required agentic behavior example (check balance ->
  consider expense -> calculate -> decide -> explain) by being the place
  where the LLM's reasoning over a tool's real result happens.
"""

# TODO: from config import MODEL_NAME, BASE_URL, GITHUB_TOKEN, MAX_STEPS
# TODO: from memory import Memory
# TODO: from tools import TOOL_SCHEMAS, TOOL_REGISTRY

# TODO: SYSTEM_PROMPT = "..."

# TODO: class BudgetAgent:
# TODO:     def __init__(self): ...
# TODO:     def run(self, goal, max_steps=None): ...
