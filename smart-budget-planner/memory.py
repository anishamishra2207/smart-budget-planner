"""
memory.py
-----------------------------------------------------------------------------
PURPOSE
Defines the Memory class: the single object that holds everything the
agent needs to remember during one session — the starting balance, every
expense logged, the LLM's own conversation history, and a human-readable
trace of every step taken. This object is created once per session and
passed by reference into every tool call, so a fact learned in turn 1 is
still available in turn 5.

STATUS: partially implemented. Only what add_expense() needs is filled in
(expenses storage, total_spent). starting_balance / remaining_balance /
trace logging are implemented as simple placeholders now and will be used
properly once get_summary() and agent.py are built.

WHICH CSE476 REQUIREMENT THIS SATISFIES
- "Memory so it remembers earlier turns in the same conversation" —
  directly. This file IS the memory component.
"""


class Memory:
    def __init__(self):
        self.expenses = []          # list of dicts, one per logged expense
        self.starting_balance = None
        self.chat_history = []      # filled in when agent.py is built
        self.trace = []             # filled in when agent.py is built

    # ---------------- expense storage (needed by add_expense) ----------------
    def add_expense(self, item, amount, category):
        """Append one expense record and return it. This is the ONLY place
        expenses are ever written, so every expense has a consistent shape."""
        entry = {
            "id": len(self.expenses) + 1,   # simple session-local counter, no database needed
            "item": item,
            "amount": amount,
            "category": category,
        }
        self.expenses.append(entry)
        return entry

    def total_spent(self, category=None):
        """Sum of all expenses, optionally filtered by category. Used by
        add_expense's return value now, and will be reused by get_summary()."""
        if category:
            return sum(
                e["amount"] for e in self.expenses
                if e["category"].lower() == category.lower()
            )
        return sum(e["amount"] for e in self.expenses)

    # ---------------- not needed by add_expense yet — placeholders ----------------
    def set_starting_balance(self, amount):
        self.starting_balance = amount

    def remaining_balance(self):
        # TODO: implement fully alongside get_summary()
        if self.starting_balance is None:
            return None
        return self.starting_balance - self.total_spent()

    def log_step(self, text):
        self.trace.append(text)

    def print_trace(self):
        for i, step in enumerate(self.trace, 1):
            print(f"Step {i}: {step}")
