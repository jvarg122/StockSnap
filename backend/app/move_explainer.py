import json
from openai import APIStatusError, OpenAI
from app.config import OPENAI_API_KEY
from app.move_context import get_price_trend, get_sector_context
from app.sec_edgar import get_filingsNear

MODEL = "gpt-4o-mini"
MaxTool = 4 #fix loop

# tool schemas for the model
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_filings",
            "description": "Get SEC filings for this ticker filed within a day of the move's date. Use this to check for an 8-K (material event) or earnings-related filing that might explain the move.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_price_trend",
            "description": "Get this ticker's price trend over the trailing 10 days, ending on the move's date. Use this to see whether today's move was a sudden spike or part of a longer building trend.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_sector_context",
            "description": "Check whether other tickers in the same sector also moved on the same date. Use this to tell apart a company-specific move from a sector-wide move.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

def run_tool(pick_tool: str, session, symbol: str, target_date):

    # tools
    if pick_tool == "get_filings":

        return get_filingsNear(symbol, target_date)

    if pick_tool == "get_price_trend":
        return get_price_trend(session, symbol, target_date)

    if pick_tool == "get_sector_context":
        return get_sector_context(session, symbol, target_date)

    return {"error": f"unknown tool: {pick_tool}"}

prompt = """You explain daily stock price/volume movements for a stock-tracking
dashboard. You'll be given basic info about one ticker's move today, and you have
tools available to investigate further: checking SEC filings near this date, the
recent price trend, and whether other stocks in the same sector also moved.

Use whichever tools are relevant before answering -- don't guess at something you
could actually check. Ground your final answer ONLY in what the tools return. If
nothing useful turns up, say plainly that the cause isn't confirmed by the
available data, rather than inventing a reason.

Keep your final answer to 2-3 sentences, English, no bullet points. Never
give investment advice, a prediction, or a buy/sell opinion -- you're explaining
what already happened, not what to do about it."""

class ExplainError(Exception):
    pass

def explain_move(session, symbol: str, companyName: str, sector: str, move_type: str,
                 value: float, target_date) -> str:

    # check if the api key is there
    if not OPENAI_API_KEY:
        raise ExplainError("OPENAI_API_KEY is not set yet")

    client = OpenAI(api_key=OPENAI_API_KEY)

    stockQuestion = f"""Ticker: {symbol} ({companyName})
Sector: {sector}
Move type: {move_type}
Value: {value}

Investigate using your available tools, then explain this move.""" #instruction

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": stockQuestion},
    ]

    # tool calling agent 

    try:
        for _ in range(MaxTool):
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
                max_tokens= 300,
            )
            message = response.choices[0].message

            
            if not message.tool_calls:
                return message.content

            messages.append(message.model_dump())

            # run each tool model requests
            for tool_call in message.tool_calls:
                result = run_tool(
                    tool_call.function.name,
                    session,
                    symbol, target_date)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, default=str),
                })

        # answer after tool loop ends 
        response = client.chat.completions.create(
            model=MODEL, 
            messages=messages, 
            max_tokens=300
        )
        return response.choices[0].message.content

    except APIStatusError as e:
        raise ExplainError(
            f"OpenAI request failed: {e.message}"
        ) from e
