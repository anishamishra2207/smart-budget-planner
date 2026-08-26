"""Smart Budget Planner Agent using Groq's OpenAI-compatible API."""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from dotenv import load_dotenv
import openai


ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=True)

MODEL = "openai/gpt-oss-120b"
GROQ_API_URL = "https://api.groq.com/openai/v1"
SYSTEM_PROMPT = """You are a careful personal budget assistant.
Use the available tools to inspect and update the user's budget. For questions
about whether the user can afford a purchase, call get_summary first, compare
the requested amount with the returned remaining_balance, and explain the
difference and any overspending or savings-goal risk. Do not invent balances.
"""


@dataclass
class Expense:
    """One expense recorded by the assistant."""
    item: str
    amount: float
    category: str


class BudgetState:
    """In-memory budget and expense state."""

    def __init__(self, total_budget: float) -> None:
        if total_budget < 0:
            raise ValueError("total_budget must be non-negative")

        self.total_budget = float(total_budget)
        self.expenses: List[Expense] = []
        self.savings_goal: Optional[float] = None
        self.category_limits: Dict[str, float] = {}  # Category spending limits

    @property
    def total_spent(self) -> float:
        return sum(expense.amount for expense in self.expenses)

    @property
    def remaining_balance(self) -> float:
        return self.total_budget - self.total_spent

    def add_expense(
        self, item: str, amount: float, category: str = "General"
    ) -> Dict[str, Any]:
        """Record an expense and return the updated balance."""
        if not item.strip():
            raise ValueError("item must not be empty")
        if amount <= 0:
            raise ValueError("amount must be greater than zero")
        if not category.strip():
            raise ValueError("category must not be empty")

        expense = Expense(item=item.strip(), amount=float(amount), category=category.strip())
        self.expenses.append(expense)
        return {
            "message": f"Added {expense.item} for ${expense.amount:.2f}.",
            "total_spent": round(self.total_spent, 2),
            "remaining_balance": round(self.remaining_balance, 2),
            "overspending": self.remaining_balance < 0,
        }

    def get_summary(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Return balance, spending breakdown, and overspending information."""
        selected_expenses = self.expenses
        if category is not None:
            selected_expenses = [
                expense
                for expense in self.expenses
                if expense.category.lower() == category.strip().lower()
            ]

        breakdown: Dict[str, float] = {}
        for expense in selected_expenses:
            breakdown[expense.category] = breakdown.get(expense.category, 0.0) + expense.amount

        savings_reserved = self.savings_goal or 0.0
        available_after_savings = self.remaining_balance - savings_reserved
        
        # Get category overspending warnings
        warnings = self.get_category_overspending()
        
        result = {
            "total_budget": round(self.total_budget, 2),
            "total_spent": round(self.total_spent, 2),
            "remaining_balance": round(self.remaining_balance, 2),
            "category": category,
            "category_breakdown": {
                name: round(amount, 2) for name, amount in breakdown.items()
            },
            "savings_goal": self.savings_goal,
            "available_after_savings": round(available_after_savings, 2),
            "overspending": self.remaining_balance < 0,
            "savings_goal_at_risk": available_after_savings < 0,
        }
        
        # Add warnings if any categories are overspent
        if warnings:
            result["category_overspending_warnings"] = warnings
        
        return result

    def set_savings_goal(self, amount: float) -> Dict[str, Any]:
        """Set a savings target and report whether current spending exceeds it."""
        if amount <= 0:
            raise ValueError("savings goal must be greater than zero")

        self.savings_goal = float(amount)
        return {
            "message": f"Savings goal set to ${amount:.2f}.",
            "savings_goal": round(amount, 2),
            "available_after_savings": round(self.remaining_balance - amount, 2),
            "savings_goal_at_risk": self.remaining_balance - amount < 0,
        }

    def set_category_limit(self, category: str, limit: float) -> Dict[str, Any]:
        """Set a spending limit for a specific category."""
        if not category.strip():
            raise ValueError("category must not be empty")
        if limit <= 0:
            raise ValueError("category limit must be greater than zero")

        category = category.strip()
        self.category_limits[category] = float(limit)
        return {
            "message": f"Category limit for '{category}' set to ${limit:.2f}.",
            "category": category,
            "limit": round(limit, 2),
        }

    def get_category_overspending(self) -> Dict[str, Dict[str, Any]]:
        """Check all categories for overspending and return warnings."""
        warnings = {}
        
        # Calculate spending by category
        category_spending: Dict[str, float] = {}
        for expense in self.expenses:
            category_spending[expense.category] = (
                category_spending.get(expense.category, 0.0) + expense.amount
            )
        
        # Check each category against its limit
        for category, limit in self.category_limits.items():
            spent = category_spending.get(category, 0.0)
            if spent > limit:
                overage = spent - limit
                warnings[category] = {
                    "category": category,
                    "limit": round(limit, 2),
                    "spent": round(spent, 2),
                    "overage": round(overage, 2),
                    "warning": f"WARNING: {category} spending has exceeded its limit by ${overage:.2f}.",
                }
        
        return warnings


Tool = Callable[..., Dict[str, Any]]


class BudgetAgent:
    """Tool-calling agent with in-memory state and persistent chat history."""

    def __init__(self, total_budget: float, client: Optional[openai.OpenAI] = None) -> None:
        self.state = BudgetState(total_budget)
        self.tools: Dict[str, Tool] = {
            "add_expense": self.state.add_expense,
            "get_summary": self.state.get_summary,
            "set_savings_goal": self.state.set_savings_goal,
            "set_category_limit": self.state.set_category_limit,
        }
        api_key = os.getenv("GROQ_API_KEY")
        self.client = client or self._create_client(api_key)
        self.message_history: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    @staticmethod
    def _create_client(api_key: Optional[str]) -> openai.OpenAI:
        """Create an OpenAI-compatible client for Groq."""
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is missing. Add it to .env or set it in the environment."
            )
        return openai.OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key,
        )

    def call_tool(self, name: str, **arguments: Any) -> Dict[str, Any]:
        """Dispatch a tool call by name."""
        try:
            tool = self.tools[name]
        except KeyError as exc:
            available = ", ".join(sorted(self.tools))
            raise ValueError(f"Unknown tool '{name}'. Available tools: {available}") from exc
        return tool(**arguments)

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return OpenAI-compatible function tool definitions."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "add_expense",
                    "description": "Log an expense and update the remaining budget.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item": {"type": "string"},
                            "amount": {"type": "number", "exclusiveMinimum": 0},
                            "category": {"type": "string", "default": "General"},
                        },
                        "required": ["item", "amount"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_summary",
                    "description": "Get the remaining balance and category breakdown.",
                    "parameters": {
                        "type": "object",
                        "properties": {"category": {"type": ["string", "null"]}},
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "set_savings_goal",
                    "description": "Set a savings goal and detect whether it is at risk.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "amount": {"type": "number", "exclusiveMinimum": 0}
                        },
                        "required": ["amount"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "set_category_limit",
                    "description": "Set a spending limit for a specific category to detect overspending.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string"},
                            "limit": {"type": "number", "exclusiveMinimum": 0},
                        },
                        "required": ["category", "limit"],
                    },
                },
            },
        ]

    def run_agent_turn(self, user_message: str, max_steps: int = 8) -> str:
        """Run a user turn, resolving tool calls and printing step-by-step trace."""
        self.message_history.append({"role": "user", "content": user_message})

        for step in range(max_steps):
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=self.message_history,
                tools=self.list_tools(),
                tool_choice="auto",
            )
            assistant_message = response.choices[0].message
            message_data = assistant_message.model_dump(exclude_none=True)
            self.message_history.append(message_data)

            if not assistant_message.tool_calls:
                return assistant_message.content or "I could not generate a response."

            # Multi-step Act and Log Trace
            for tool_call in assistant_message.tool_calls:
                arguments = json.loads(tool_call.function.arguments or "{}")
                print(f"  [Step {step + 1} Action] Tool Call -> {tool_call.function.name}({arguments})")

                result = self.call_tool(tool_call.function.name, **arguments)
                print(f"  [Step {step + 1} Observation] Output -> {result}")

                self.message_history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": json.dumps(result),
                    }
                )

        raise RuntimeError("The agent exceeded the maximum number of tool-call steps.")


if __name__ == "__main__":
    budget = float(input("Enter your total budget: $"))
    agent = BudgetAgent(total_budget=budget)
    print("Smart Budget Planner is ready. Type 'quit' to exit.")
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            break
        answer = agent.run_agent_turn(user_input)
        print(f"\nAssistant: {answer}")