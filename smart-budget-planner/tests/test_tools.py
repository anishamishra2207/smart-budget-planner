"""
tests/test_tools.py
-----------------------------------------------------------------------------
PURPOSE
Unit tests for the two tools in isolation, with NO LLM involved. These
tests exist to prove the tools themselves are correct (right math, right
return values) independently of whether the model calls them correctly —
this separation makes debugging much easier: if the notebook demo behaves
oddly, you can run these tests first to rule out a bug in the tools before
suspecting the LLM's tool-calling choices.

WHAT WILL EVENTUALLY GO HERE
- test_add_expense_logs_correctly(): create a Memory, call add_expense
  directly, assert memory.expenses has one entry with the right amount.
- test_get_summary_totals_correctly(): log two expenses, call get_summary,
  assert the returned total matches the sum.
- test_get_summary_category_filter(): log expenses in two categories,
  assert a category-filtered summary only counts that category.
- test_remaining_balance_after_expenses(): set a starting balance, log an
  expense, assert memory.remaining_balance() subtracts correctly — this is
  the number the affordability decision depends on, so it's the most
  important test in this file.

WHICH CSE476 REQUIREMENT THIS SATISFIES
- Not a rubric line item by itself, but it is what lets you PROVE, ahead of
  the demo/viva, that "at least two working tools" really work — giving
  you confidence before you show the LLM-driven run to your teacher.
"""

# TODO: import pytest
# TODO: from memory import Memory
# TODO: from tools import add_expense, get_summary

# TODO: def test_add_expense_logs_correctly(): ...
# TODO: def test_get_summary_totals_correctly(): ...
# TODO: def test_get_summary_category_filter(): ...
# TODO: def test_remaining_balance_after_expenses(): ...
