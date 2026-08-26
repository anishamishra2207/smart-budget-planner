"""
tools.py
-----------------------------------------------------------------------------
PURPOSE
Holds the required tools as plain Python functions, plus the JSON schemas
that describe them to the LLM. These functions are the agent's ONLY way to
touch real data — the LLM decides WHEN to call them, but the actual
reading/writing happens here, in ordinary Python.

STATUS: add_expense() is implemented below. get_summary() is intentionally
NOT implemented yet (next step).
"""

from memory import Memory


# -----------------------------------------------------------------------------
# Category inference — a small, simple helper so the OFFICIAL signature stays
# exactly add_expense(item, amount), with no extra required parameter, while
# still letting the agent store a category for later category-based
# summaries. This is plain keyword matching, not an LLM call — deliberately
# simple, deterministic, and free.
# -----------------------------------------------------------------------------
CATEGORY_KEYWORDS = {
    "Food":          ["grocery", "groceries", "food", "restaurant", "snack", "lunch",
                       "dinner", "breakfast", "coffee", "tea", "pizza", "meal"],
    "Travel":        ["bus", "train", "taxi", "cab", "uber", "ola", "flight", "fuel",
                       "petrol", "diesel", "travel", "trip", "metro", "auto"],
    "Entertainment": ["movie", "cinema", "netflix", "game", "concert", "party",
                       "subscription", "spotify", "outing"],
    "Education":     ["book", "course", "tuition", "fee", "stationery", "exam"],
    "Health":        ["medicine", "doctor", "hospital", "pharmacy", "gym"],
}


def infer_category(item: str) -> str:
    """Match the expense's item text against known keywords. Falls back to
    'Other' if nothing matches, so category is ALWAYS set (never blank),
    which keeps every later category summary well-defined."""
    item_lower = item.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in item_lower for keyword in keywords):
            return category
    return "Other"


def add_expense(memory: Memory, item: str, amount: float) -> dict:
    """
    REQUIRED TOOL 1 — signature matches the T1 brief exactly: (item, amount).

    Validates the amount, infers a category from the item text, stores the
    expense in the session's Memory object, and returns a structured dict
    describing what happened — not a plain sentence — so the calling LLM
    (and any future code) can read specific fields instead of re-parsing text.
    """
    # ---- validation: amount must be positive ----
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return {
            "status": "error",
            "error": f"Amount must be a number, got: {amount!r}",
            "item": item,
        }

    if amount <= 0:
        return {
            "status": "error",
            "error": f"Amount must be positive, got: {amount}",
            "item": item,
        }

    # ---- category inference (does not touch the required signature) ----
    category = infer_category(item)

    # ---- store in session memory (no database — in-memory Python list) ----
    entry = memory.add_expense(item=item, amount=amount, category=category)

    # ---- structured, agent-readable result ----
    return {
        "status": "success",
        "expense_id": entry["id"],
        "item": entry["item"],
        "amount": entry["amount"],
        "category": entry["category"],
        "total_expenses_logged": len(memory.expenses),
        "running_total_all_categories": memory.total_spent(),
        "message": (
            f"Logged \u20b9{amount:.2f} for '{item}' under category "
            f"'{category}'. Running total: \u20b9{memory.total_spent():.2f}."
        ),
    }


# -----------------------------------------------------------------------------
# REQUIRED TOOL 2 — get_summary(category)
# -----------------------------------------------------------------------------
def get_summary(memory: Memory, category: str = None) -> dict:
    """
    Reads expenses already stored by add_expense() (never writes anything)
    and returns STRUCTURED data — numbers and category breakdowns as real
    dict fields, not a pre-written sentence — so the calling LLM can reason
    over exact values instead of parsing text.

    Two modes:
      - category=None  -> full breakdown across every category, plus which
                           category is the biggest ("top_category").
      - category="X"    -> total spent in just that category (0 if none
                           were ever logged there — not an error).
    """
    # ---- no expenses logged at all yet ----
    if not memory.expenses:
        return {
            "status": "empty",
            "category_filter": category,
            "total_spent": 0,
            "message": "No expenses have been logged yet.",
        }

    # ---- category-specific summary ----
    if category:
        matching = [e for e in memory.expenses if e["category"].lower() == category.lower()]
        total = sum(e["amount"] for e in matching)
        return {
            "status": "success" if matching else "no_expenses_in_category",
            "category_filter": category,
            "total_spent": total,
            "expense_count": len(matching),
            "message": (
                f"\u20b9{total:.2f} spent on '{category}' across {len(matching)} expense(s)."
                if matching else
                f"No expenses have been logged under '{category}' yet."
            ),
        }

    # ---- overall summary across all categories ----
    breakdown = {}
    for e in memory.expenses:
        breakdown[e["category"]] = breakdown.get(e["category"], 0) + e["amount"]

    overall_total = sum(breakdown.values())
    top_category = max(breakdown, key=breakdown.get)   # category consuming the most
    top_amount = breakdown[top_category]

    return {
        "status": "success",
        "category_filter": None,
        "overall_total": overall_total,
        "category_breakdown": breakdown,          # e.g. {"Food": 500, "Travel": 800, ...}
        "number_of_categories": len(breakdown),
        "top_category": top_category,               # answers "which category is highest?"
        "top_category_amount": top_amount,
        "message": (
            f"Total spent: \u20b9{overall_total:.2f} across {len(breakdown)} categories. "
            f"Highest: '{top_category}' at \u20b9{top_amount:.2f}."
        ),
    }


# -----------------------------------------------------------------------------
# OpenAI-style tool schema — only add_expense for now.
# -----------------------------------------------------------------------------
ADD_EXPENSE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "add_expense",
        "description": "Log a new expense for the current session. Amount must be positive.",
        "parameters": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "What was bought, e.g. 'groceries'"},
                "amount": {"type": "number", "description": "Cost of the item, must be > 0"},
            },
            "required": ["item", "amount"],
        },
    },
}

GET_SUMMARY_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_summary",
        "description": (
            "Get spending totals from the current session. Leave category "
            "empty for an overall breakdown across all categories (including "
            "which category is highest), or pass a category name for just "
            "that category's total."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Optional category to filter by, e.g. 'Travel'. Omit for an overall summary.",
                },
            },
            "required": [],
        },
    },
}

TOOL_SCHEMAS = [ADD_EXPENSE_SCHEMA, GET_SUMMARY_SCHEMA]

TOOL_REGISTRY = {
    "add_expense": add_expense,
    "get_summary": get_summary,
}
