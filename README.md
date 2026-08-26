# Smart Budget Planner Agent

The Smart Budget Planner Agent provides three tools for personal budget management. `add_expense(item: str, amount: float, category: str = "General")` records an expense with its item name, amount, and category, then updates the in-memory totals. `get_summary(category: Optional[str] = None)` reports the remaining budget and category-wise spending totals, optionally limited to one category. `set_savings_goal(amount: float)` stores a target savings amount and reports whether the current budget can support it.

Budget state is tracked by the in-memory `BudgetState` class, which stores the total budget, a list of expense objects, total spending, remaining balance, and savings goal. `BudgetAgent` keeps a `message_history` list containing the system prompt, user messages, assistant tool calls, and tool outputs. This conversation history preserves context across turns, allowing the agent to query current state before answering follow-up financial questions.

During development, the GitHub Models endpoint entered a retirement brownout and returned a 410 error, while an attempted model identifier also produced a 404 model mismatch. The honest fix was to migrate the OpenAI-compatible client to the Groq endpoint and use the `openai/gpt-oss-120b` model, which resolved the endpoint and model compatibility problems while preserving the same tool-calling loop.

Contributor note: Built for the Smart Budget Planner college project, Topic T1.
