"""Assistant context and request contract tests; no network calls."""
import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from openai import OpenAIError

from portfolio_lens.analytics import metrics, portfolio_values
from portfolio_lens.assistant import AssistantError, answer_question, build_context


def test_context_matches_calculated_portfolio(prices):
    weights = pd.Series({"A": .5, "B": .5})
    values = portfolio_values(prices, weights, 100)
    context = json.loads(build_context(prices, weights, values, metrics(values), 100, "Buy and hold", 0))
    assert context["final_value_usd"] == 150
    assert context["profit_usd"] == 50
    assert context["portfolio_metrics"]["Total return"] == .5
    assert context["stocks"]["B"]["metrics"]["Total return"] == 1
    assert context["stocks"]["A"]["initial_weight"] == .5
    assert context["start_date"] == "2020-01-01"
    assert "price_history" not in context


def test_context_converts_undefined_metrics_to_null(prices):
    prices = prices.iloc[:2]
    weights = pd.Series({"A": .5, "B": .5})
    values = portfolio_values(prices, weights, 100)
    context = build_context(prices, weights, values, metrics(values), 100, "Buy and hold", 0)
    assert json.loads(context)["portfolio_metrics"]["Sharpe ratio"] is None
    assert "NaN" not in context


def test_request_uses_context_bounded_history_and_no_storage():
    with patch("portfolio_lens.assistant.OpenAI") as constructor:
        client = constructor.return_value.__enter__.return_value
        client.responses.create.return_value = SimpleNamespace(output_text="  Your return is 10%.  ")
        history = [{"role": "user", "content": str(index)} for index in range(20)]
        answer = answer_question("Explain returns", '{"Total return": 0.1}', history, "test-key")
    assert answer == "Your return is 10%."
    constructor.assert_called_once_with(api_key="test-key", timeout=30.0, max_retries=0)
    args = client.responses.create.call_args.kwargs
    assert args["store"] is False
    assert args["max_output_tokens"] == 1200
    assert len(args["input"]) == 12
    assert args["input"][0]["role"] == "developer"
    assert args["input"][1]["content"] == "10"


@pytest.mark.parametrize("question,context,key", [("", "{}", "test"), ("x" * 3001, "{}", "test"), ("Hi", "{}", ""), ("Hi", "x" * 60001, "test")], ids=["empty-question", "long-question", "missing-key", "large-context"])
def test_invalid_requests_never_call_api(question, context, key):
    with patch("portfolio_lens.assistant.OpenAI") as constructor:
        with pytest.raises(AssistantError):
            answer_question(question, context, [], key)
        constructor.assert_not_called()


def test_api_failure_hides_internal_details():
    with patch("portfolio_lens.assistant.OpenAI") as constructor:
        constructor.return_value.__enter__.return_value.responses.create.side_effect = OpenAIError("sensitive internal details")
        with pytest.raises(AssistantError) as failure:
            answer_question("Explain", "{}", [], "test")
    assert "sensitive" not in str(failure.value)


def test_empty_response_reports_failure():
    with patch("portfolio_lens.assistant.OpenAI") as constructor:
        constructor.return_value.__enter__.return_value.responses.create.return_value = SimpleNamespace(output_text="")
        with pytest.raises(AssistantError, match="no answer"):
            answer_question("Explain", "{}", [], "test")
