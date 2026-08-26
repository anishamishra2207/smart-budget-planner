"""Unit tests for Smart Budget Planner Agent."""

import pytest
from unittest.mock import MagicMock, patch
from agent import BudgetState, BudgetAgent, Expense


class TestBudgetState:
    """Test the in-memory budget state and expense tracking."""

    def test_initialize_budget_with_valid_amount(self):
        """Valid budget initialization."""
        state = BudgetState(total_budget=1000)
        assert state.total_budget == 1000.0
        assert state.total_spent == 0.0
        assert state.remaining_balance == 1000.0
        assert state.savings_goal is None

    def test_initialize_budget_with_negative_amount_raises_error(self):
        """Negative budget is rejected."""
        with pytest.raises(ValueError, match="total_budget must be non-negative"):
            BudgetState(total_budget=-100)

    def test_add_valid_expense(self):
        """Valid expense is recorded."""
        state = BudgetState(total_budget=1000)
        result = state.add_expense(item="Textbook", amount=150, category="Education")
        
        assert result["message"] == "Added Textbook for $150.00."
        assert result["total_spent"] == 150.0
        assert result["remaining_balance"] == 850.0
        assert result["overspending"] is False
        assert len(state.expenses) == 1
        assert state.expenses[0].item == "Textbook"
        assert state.expenses[0].amount == 150.0
        assert state.expenses[0].category == "Education"

    def test_add_multiple_expenses_accumulate(self):
        """Multiple expenses accumulate correctly."""
        state = BudgetState(total_budget=1000)
        state.add_expense(item="Food", amount=50, category="Food")
        state.add_expense(item="Travel", amount=100, category="Travel")
        state.add_expense(item="Entertainment", amount=75, category="Entertainment")
        
        assert state.total_spent == 225.0
        assert state.remaining_balance == 775.0
        assert len(state.expenses) == 3

    def test_add_expense_with_empty_item_raises_error(self):
        """Empty item name is rejected."""
        state = BudgetState(total_budget=1000)
        with pytest.raises(ValueError, match="item must not be empty"):
            state.add_expense(item="", amount=50)

    def test_add_expense_with_zero_amount_raises_error(self):
        """Zero amount is rejected."""
        state = BudgetState(total_budget=1000)
        with pytest.raises(ValueError, match="amount must be greater than zero"):
            state.add_expense(item="Test", amount=0)

    def test_add_expense_with_negative_amount_raises_error(self):
        """Negative amount is rejected."""
        state = BudgetState(total_budget=1000)
        with pytest.raises(ValueError, match="amount must be greater than zero"):
            state.add_expense(item="Test", amount=-50)

    def test_add_expense_with_empty_category_raises_error(self):
        """Empty category is rejected."""
        state = BudgetState(total_budget=1000)
        with pytest.raises(ValueError, match="category must not be empty"):
            state.add_expense(item="Test", amount=50, category="")

    def test_get_summary_all_expenses(self):
        """Get summary of all expenses."""
        state = BudgetState(total_budget=1000)
        state.add_expense(item="Food A", amount=50, category="Food")
        state.add_expense(item="Food B", amount=30, category="Food")
        state.add_expense(item="Travel", amount=100, category="Travel")
        
        result = state.get_summary()
        
        assert result["total_budget"] == 1000.0
        assert result["total_spent"] == 180.0
        assert result["remaining_balance"] == 820.0
        assert result["category_breakdown"]["Food"] == 80.0
        assert result["category_breakdown"]["Travel"] == 100.0
        assert result["overspending"] is False

    def test_get_summary_specific_category(self):
        """Get summary for a specific category."""
        state = BudgetState(total_budget=1000)
        state.add_expense(item="Food A", amount=50, category="Food")
        state.add_expense(item="Food B", amount=30, category="Food")
        state.add_expense(item="Travel", amount=100, category="Travel")
        
        result = state.get_summary(category="Food")
        
        assert result["total_spent"] == 180.0
        assert result["remaining_balance"] == 820.0
        assert result["category"] == "Food"
        assert result["category_breakdown"]["Food"] == 80.0

    def test_get_summary_empty_category(self):
        """Get summary for category with no expenses."""
        state = BudgetState(total_budget=1000)
        state.add_expense(item="Food", amount=50, category="Food")
        
        result = state.get_summary(category="Travel")
        
        assert result["category"] == "Travel"
        assert result["category_breakdown"] == {}
        assert result["total_spent"] == 50.0

    def test_get_summary_with_overspending(self):
        """Overspending is detected."""
        state = BudgetState(total_budget=100)
        state.add_expense(item="Expensive", amount=150, category="General")
        
        result = state.get_summary()
        
        assert result["total_spent"] == 150.0
        assert result["remaining_balance"] == -50.0
        assert result["overspending"] is True

    def test_set_savings_goal_valid(self):
        """Valid savings goal is set."""
        state = BudgetState(total_budget=1000)
        result = state.set_savings_goal(amount=200)
        
        assert result["message"] == "Savings goal set to $200.00."
        assert result["savings_goal"] == 200.0
        assert result["available_after_savings"] == 800.0
        assert result["savings_goal_at_risk"] is False
        assert state.savings_goal == 200.0

    def test_set_savings_goal_exceeds_budget(self):
        """Savings goal at risk if exceeds remaining balance."""
        state = BudgetState(total_budget=1000)
        state.add_expense(item="Expensive", amount=900, category="General")
        result = state.set_savings_goal(amount=200)
        
        assert result["available_after_savings"] == -100.0
        assert result["savings_goal_at_risk"] is True

    def test_set_savings_goal_zero_or_negative_raises_error(self):
        """Zero or negative savings goal is rejected."""
        state = BudgetState(total_budget=1000)
        with pytest.raises(ValueError, match="savings goal must be greater than zero"):
            state.set_savings_goal(amount=0)
        with pytest.raises(ValueError, match="savings goal must be greater than zero"):
            state.set_savings_goal(amount=-100)

    def test_category_overspending_detection(self):
        """Detect category-specific overspending."""
        state = BudgetState(total_budget=1000)
        state.add_expense(item="Food 1", amount=2000, category="Food")
        
        # Overspending should be detected when we check summary
        result = state.get_summary(category="Food")
        assert result["category_breakdown"]["Food"] == 2000.0
        assert state.remaining_balance < 0

    def test_memory_persists_across_calls(self):
        """Memory persists across multiple operations."""
        state = BudgetState(total_budget=1000)
        
        # First set of operations
        state.add_expense(item="Food", amount=50, category="Food")
        state.add_expense(item="Travel", amount=100, category="Travel")
        state.set_savings_goal(amount=200)
        
        # Verify state after operations
        assert len(state.expenses) == 2
        assert state.total_spent == 150.0
        assert state.savings_goal == 200.0
        
        # Further operations should maintain memory
        summary = state.get_summary()
        assert summary["total_spent"] == 150.0
        assert summary["savings_goal"] == 200.0


class TestBudgetAgent:
    """Test the agent with tool calling and memory."""

    @patch('agent.BudgetAgent._create_client')
    def test_agent_initialization(self, mock_create_client):
        """Agent initializes with budget and tools."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        agent = BudgetAgent(total_budget=1500)
        
        assert agent.state.total_budget == 1500.0
        assert "add_expense" in agent.tools
        assert "get_summary" in agent.tools
        assert "set_savings_goal" in agent.tools
        assert len(agent.message_history) == 1  # system prompt

    @patch('agent.BudgetAgent._create_client')
    def test_agent_call_tool_add_expense(self, mock_create_client):
        """Agent can call add_expense tool."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        agent = BudgetAgent(total_budget=1000)
        result = agent.call_tool("add_expense", item="Lunch", amount=20, category="Food")
        
        assert "Added" in result["message"]
        assert result["total_spent"] == 20.0
        assert result["remaining_balance"] == 980.0

    @patch('agent.BudgetAgent._create_client')
    def test_agent_call_tool_get_summary(self, mock_create_client):
        """Agent can call get_summary tool."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        agent = BudgetAgent(total_budget=1000)
        agent.state.add_expense(item="Food", amount=50, category="Food")
        result = agent.call_tool("get_summary")
        
        assert result["total_budget"] == 1000.0
        assert result["total_spent"] == 50.0
        assert result["remaining_balance"] == 950.0

    @patch('agent.BudgetAgent._create_client')
    def test_agent_call_tool_set_savings_goal(self, mock_create_client):
        """Agent can call set_savings_goal tool."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        agent = BudgetAgent(total_budget=1000)
        result = agent.call_tool("set_savings_goal", amount=300)
        
        assert result["savings_goal"] == 300.0
        assert agent.state.savings_goal == 300.0

    @patch('agent.BudgetAgent._create_client')
    def test_agent_call_unknown_tool_raises_error(self, mock_create_client):
        """Calling unknown tool raises error."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        agent = BudgetAgent(total_budget=1000)
        with pytest.raises(ValueError, match="Unknown tool"):
            agent.call_tool("nonexistent_tool")

    @patch('agent.BudgetAgent._create_client')
    def test_agent_list_tools(self, mock_create_client):
        """Agent lists all available tools."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        agent = BudgetAgent(total_budget=1000)
        tools = agent.list_tools()
        
        assert len(tools) == 4  # add_expense, get_summary, set_savings_goal, set_category_limit
        tool_names = [t["function"]["name"] for t in tools]
        assert "add_expense" in tool_names
        assert "get_summary" in tool_names
        assert "set_savings_goal" in tool_names
        assert "set_category_limit" in tool_names

    @patch('agent.BudgetAgent._create_client')
    def test_agent_message_history_initialization(self, mock_create_client):
        """Agent initializes with system prompt in message history."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        agent = BudgetAgent(total_budget=1000)
        
        assert len(agent.message_history) == 1
        assert agent.message_history[0]["role"] == "system"
        assert "budget" in agent.message_history[0]["content"].lower()

    @patch('agent.BudgetAgent._create_client')
    def test_agent_affordability_check_affordable(self, mock_create_client):
        """Agent correctly checks affordability for affordable expense."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        agent = BudgetAgent(total_budget=1000)
        agent.state.add_expense(item="Food", amount=200, category="Food")
        
        # Check if we can afford 500 more (we have 800 remaining)
        result = agent.call_tool("get_summary")
        assert result["remaining_balance"] == 800.0
        assert 500 <= result["remaining_balance"]

    @patch('agent.BudgetAgent._create_client')
    def test_agent_affordability_check_unaffordable(self, mock_create_client):
        """Agent correctly checks affordability for unaffordable expense."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        agent = BudgetAgent(total_budget=1000)
        agent.state.add_expense(item="Expensive", amount=900, category="General")
        
        # Check if we can afford 500 more (we only have 100 remaining)
        result = agent.call_tool("get_summary")
        assert result["remaining_balance"] == 100.0
        assert 500 > result["remaining_balance"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
