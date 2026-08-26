"""
config.py
-----------------------------------------------------------------------------
PURPOSE
This is the project's single "settings" file. Nothing here decides agent
behavior — it only holds values other files need (API key, model name,
default limits) so they aren't hardcoded or repeated in agent.py / tools.py.
Keeping config separate means a teammate can change the model or the
starting balance without touching any logic.

WHAT WILL EVENTUALLY GO HERE
- Loading GITHUB_TOKEN (or your chosen lane's key) from the .env file using
  python-dotenv.
- The model name string (e.g. "gpt-4o-mini") as one named constant, so it's
  changed in exactly one place.
- The API base_url for whichever lane you use (GitHub Models / Foundry).
- A small constant for the loop's max_steps (safety limit on the plan-act
  loop, so a confused model can't loop forever).
- Optionally, a DEFAULT_CURRENCY = "INR" constant, since the project uses ₹.

WHICH CSE476 REQUIREMENT THIS SATISFIES
None directly — this file exists for code quality / separation of concerns,
which supports the "Implementation" rubric line indirectly (clean,
understandable code), but it isn't itself a graded requirement (no tool, no
memory, no loop lives here).
"""

# TODO: from dotenv import load_dotenv; load_dotenv()
# TODO: import os
# TODO: GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# TODO: MODEL_NAME = "gpt-4o-mini"
# TODO: BASE_URL = "https://models.inference.ai.azure.com"
# TODO: MAX_STEPS = 6
# TODO: DEFAULT_CURRENCY = "INR"
