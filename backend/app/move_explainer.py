from openai import APIStatusError, OpenAI
from app.config import OPENAI_API_KEY

MODEL = "gpt-4o-mini" 

prompt = """You explain daily stock price/volume movements for a stock-tracking
dashboard. You will be given real data about one ticker's move today and any SEC filings
found near that date. nothing else.

Ground your answer ONLY in the data given. If a relevant filing exists (especially an 8-K,
which companies file for material events), mention it as a plausible reason. If no filing
is present, say plainly that the cause isn't confirmed by the available data, and note the
move itself without inventing a reason.

Keep it to 2-3 sentences, English, no bullet points. Never give investment advice,
a prediction, or a buy/sell opinion. you're explaining what already happened, not what to
do about it."""

class ExplainError(Exception):
    pass

def explain_move(symbol: str, name: str, sector: str, move_type: str,
                 value: float, filings: list[dict]) -> str:

    # check if the api key is there
    if not OPENAI_API_KEY:
        raise ExplainError("OPENAI_API_KEY is not set yet")

    client = OpenAI(api_key=OPENAI_API_KEY)

    # make the filing info into a string
    if filings:
        filings_info = ""
        for f in filings:
            filings_info += f"- {f['form']} filed {f['filed_date']}\n"
    else:
        filings_info = "(no SEC filings found within a day of this move)"

    user_prompt = f"""Ticker: {symbol} ({name})

Sector: {sector}
Move type: {move_type}
Value: {value}

Recent SEC filings near this date:
{filings_info}"""

    try:
        response = client.chat.completions.create(
            model= MODEL,
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            max_tokens=150
        )

    except APIStatusError as e:
        raise ExplainError(
            f"OpenAI request failed: {e.message}"
        ) from e

    answer = response.choices[0].message.content

    return answer