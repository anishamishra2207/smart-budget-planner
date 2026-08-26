"""
tests/test_memory.py
-----------------------------------------------------------------------------
PURPOSE
Unit tests for the Memory class on its own — checking that facts actually
persist the way the assignment requires ("remembers every expense during
the session so that category totals remain correct"), without needing an
agent or an LLM running at all.

WHAT WILL EVENTUALLY GO HERE
- test_memory_starts_empty(): a fresh Memory has no expenses and no
  starting balance set.
- test_expenses_persist_across_multiple_calls(): call add_expense() three
  separate times (simulating three separate user turns), assert all three
  are still present afterwards — this is the literal "remembers earlier
  turns" behavior, tested directly.
- test_trace_records_steps_in_order(): call log_step() a few times, assert
  print_trace()/self.trace preserves the order they were added in.

WHICH CSE476 REQUIREMENT THIS SATISFIES
- "Memory so it remembers earlier turns in the same conversation" — this
  file is the direct, automated proof of that requirement, separate from
  the notebook's manual/visual demonstration of the same thing.
"""

# TODO: from memory import Memory

# TODO: def test_memory_starts_empty(): ...
# TODO: def test_expenses_persist_across_multiple_calls(): ...
# TODO: def test_trace_records_steps_in_order(): ...
