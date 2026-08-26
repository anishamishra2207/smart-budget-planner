# Smart Budget Planner

CSE476 CA1 — Project 1, Topic T1 (Personal Budget Assistant)

> Structure created from the approved architecture. Implementation is not
> filled in yet — see each file's docstring for what will go inside it.

## Project structure

```
smart-budget-planner/
├── agent.py            # the plan-act loop (BudgetAgent class)
├── tools.py              # add_expense(item, amount), get_summary(category)
├── memory.py              # Memory class: expenses, balance, trace
├── config.py               # API key, model name, constants
├── requirements.txt
├── .env.example
├── .gitignore
├── tests/
│   ├── test_tools.py        # unit tests for the two tools
│   └── test_memory.py        # unit tests for memory persistence
└── notebooks/
    └── demo.ipynb              # graded demo: 3 scenarios + traces
```

## Setup (once implemented)
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env`, add your `GITHUB_TOKEN`.
3. Run `pytest tests/` to check the tools and memory in isolation.
4. Open `notebooks/demo.ipynb` and run all cells for the full agent demo.

## Tools, memory, honest failure
*(To be written once implementation is complete — see project brief:
name the two tools, describe what memory does, and one honest failure.)*

## Who did what (fill in for submission)
- **[Name 1]:**
- **[Name 2]:**
- **[Name 3]:**
