"""
Claude Advisor orchestration layer.
Sends messages to Claude API with tool definitions, handles tool_use rounds.
"""
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import anthropic
from advisor.prompts import SYSTEM_PROMPT
from advisor import tools as advisor_tools

# Model
MODEL = "claude-sonnet-4-20250514"

# Tool schemas for Claude API
TOOL_SCHEMAS = [
    {
        "name": "query_database",
        "description": (
            "Execute a read-only SQL SELECT query against the Victoria Royals concession database. "
            "Tables: transactions (date, time, category, item, qty, price_point_name, location, "
            "estimated_price, estimated_revenue, hour, minute, game_period, season) and "
            "games (date, opponent, day_of_week, attendance, season, is_playoff, promo_event, note, "
            "total_units, total_transactions, total_estimated_revenue, units_per_cap, revenue_per_cap). "
            "Only SELECT queries are permitted. Results limited to 100 rows."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "The SQL SELECT query to execute.",
                }
            },
            "required": ["sql"],
        },
    },
    {
        "name": "get_forecast",
        "description": (
            "Get an ML-powered demand forecast for an upcoming game. Returns predicted total units, "
            "revenue, per-category and per-item breakdowns. Provide opponent name, day of week, "
            "and expected attendance."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "opponent": {
                    "type": "string",
                    "description": "Opponent team name (e.g., 'Vancouver', 'Kelowna').",
                },
                "day_of_week": {
                    "type": "string",
                    "description": "Day of the week (e.g., 'Fri', 'Sat', 'Wed').",
                },
                "attendance": {
                    "type": "integer",
                    "description": "Expected attendance.",
                },
                "month": {
                    "type": "integer",
                    "description": "Month number (1-12). Optional, defaults to current month.",
                },
                "is_playoff": {
                    "type": "boolean",
                    "description": "Whether this is a playoff game. Defaults to false.",
                },
                "promo_event": {
                    "type": "string",
                    "description": "Promotional event type. One of: Dollar Dog Night, Family Night, School Night, Taco Tuesday, Playoff, Regular. Defaults to Regular.",
                },
            },
            "required": ["opponent", "day_of_week", "attendance"],
        },
    },
    {
        "name": "get_game_summary",
        "description": (
            "Get a complete summary of a past game date including attendance, revenue, per-cap metrics, "
            "category breakdown, stand breakdown, top items, period breakdown, and WHL benchmark comparison. "
            "Date format: YYYY-MM-DD."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "game_date": {
                    "type": "string",
                    "description": "Game date in YYYY-MM-DD format.",
                }
            },
            "required": ["game_date"],
        },
    },
    {
        "name": "get_prep_sheet",
        "description": (
            "Generate a complete game-day preparation sheet. Returns item prep quantities with buffer, "
            "stand opening assignments, staffing recommendations, and comparable past games. "
            "Use this when someone asks what to prepare for an upcoming game."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "opponent": {
                    "type": "string",
                    "description": "Opponent team name.",
                },
                "day_of_week": {
                    "type": "string",
                    "description": "Day of the week (e.g., 'Fri', 'Sat').",
                },
                "attendance": {
                    "type": "integer",
                    "description": "Expected attendance.",
                },
                "promo_event": {
                    "type": "string",
                    "description": "Promotional event type. Defaults to Regular.",
                },
            },
            "required": ["opponent", "day_of_week", "attendance"],
        },
    },
    {
        "name": "get_product_recommendations",
        "description": (
            "Get product bundle and combo deal recommendations based on market-basket affinity analysis. "
            "Returns suggested bundles with pricing, estimated revenue impact, and top co-purchased item pairs. "
            "No parameters needed."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]

# Map tool names to functions
TOOL_FUNCTIONS = {
    "query_database": lambda args: advisor_tools.query_database(args["sql"]),
    "get_forecast": lambda args: advisor_tools.get_forecast(
        opponent=args["opponent"],
        day_of_week=args["day_of_week"],
        attendance=args["attendance"],
        month=args.get("month"),
        is_playoff=args.get("is_playoff", False),
        promo_event=args.get("promo_event", "Regular"),
    ),
    "get_game_summary": lambda args: advisor_tools.get_game_summary(args["game_date"]),
    "get_prep_sheet": lambda args: advisor_tools.get_prep_sheet(
        opponent=args["opponent"],
        day_of_week=args["day_of_week"],
        attendance=args["attendance"],
        promo_event=args.get("promo_event", "Regular"),
    ),
    "get_product_recommendations": lambda args: advisor_tools.get_product_recommendations(),
}


def _execute_tool(name: str, input_args: dict) -> dict:
    """Execute a tool by name and return the result as a dict."""
    fn = TOOL_FUNCTIONS.get(name)
    if not fn:
        return {"error": f"Unknown tool: {name}"}
    try:
        return fn(input_args)
    except Exception as e:
        return {"error": f"Tool {name} failed: {str(e)}"}


def chat(messages: list) -> tuple:
    """
    Send messages to Claude with tools and handle tool_use rounds.

    Args:
        messages: List of message dicts [{"role": "user"/"assistant", "content": ...}, ...]

    Returns:
        (response_text: str, updated_messages: list, tool_calls: list)
        tool_calls is a list of {"name": str, "input": dict, "result": dict} for UI display.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return (
            "I need an Anthropic API key to function. Please set the ANTHROPIC_API_KEY environment variable.",
            messages,
            [],
        )

    client = anthropic.Anthropic(api_key=api_key)
    tool_calls_log = []

    # Work with a copy of messages
    working_messages = list(messages)

    max_rounds = 5
    for _round in range(max_rounds):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOL_SCHEMAS,
                messages=working_messages,
            )
        except anthropic.APIError as e:
            error_msg = f"API error: {str(e)}"
            return error_msg, messages, tool_calls_log

        # Check if response contains tool_use blocks
        has_tool_use = any(block.type == "tool_use" for block in response.content)

        if not has_tool_use or response.stop_reason == "end_of_turn":
            # Extract text from response
            text_parts = []
            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)

            final_text = "\n".join(text_parts) if text_parts else ""

            # Append assistant response to messages
            working_messages.append({"role": "assistant", "content": response.content})
            return final_text, working_messages, tool_calls_log

        # Handle tool_use blocks
        assistant_content = response.content
        working_messages.append({"role": "assistant", "content": assistant_content})

        tool_results = []
        for block in assistant_content:
            if block.type == "tool_use":
                result = _execute_tool(block.name, block.input)
                tool_calls_log.append({
                    "name": block.name,
                    "input": block.input,
                    "result": result,
                })
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, default=str),
                })

        working_messages.append({"role": "user", "content": tool_results})

    # If we exhausted rounds, extract whatever text we have
    text_parts = []
    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)

    final_text = "\n".join(text_parts) if text_parts else "I ran out of processing steps. Please try a simpler question."
    return final_text, working_messages, tool_calls_log
