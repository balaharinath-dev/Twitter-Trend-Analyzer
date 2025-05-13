import os
from dotenv import load_dotenv
from google import genai
import streamlit as st

load_dotenv()
def summarize_with_gemini(tweets_data):
    api_key = st.secrets("GEMINI_API_KEY")
    if not api_key:
        return {"error": "API key not found. Please set GEMINI_API_KEY in your .env file."}

    client = genai.Client(api_key=api_key)

    tweets = tweets_data.get("tweets", [])
    if not tweets:
        return {"error": "No tweets to summarize."}

    contents = """You are MarketIntel-Synth.

INPUT:
A JSON array called **tweets**, each element containing the full text of a tweet and any embedded URLs.

TASK:
1. Visit every URL, extract the full article text, and ignore non-article links.
2. Aggregate insights across **all** articles (no per-tweet reports).
3. If you find any products then search them on web and get current prices and list them in rupees by conversion  (use websearch here)
4. Need data which is relevant for advertising company

OUTPUT (Markdown only — no extra text):

Summary


## Key Insights 
- …

## Product Highlights and their prices
- …

## Content Recommendations
- …

## Current Market Trends
- …

## Marketing Tactics
- …

## Predicted Next Big Trends and Trend Analysis
- …

## Target Audience 
- …

STRICT RULES:
- Use exactly the seven H2 headings above in that order.
- Under each heading provide **bullet points only** (• or -), max 8 bullets per section, each ≤ 140 characters.
- Include only information that matters for market analysis (news, launches, features, pricing, partnerships, regulations).
- Do **not** mention tweets, URLs, authors, publish dates, or the analysis process.
- No apologies, disclaimers, or references to being an AI.
- If a heading has no content, write “*None detected*” under it.
"""
    for tweet in tweets:
        text = tweet.get("text", "")
        url = tweet.get("url", "")
        contents += f"{text} ({url})\n"

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
        )

        # Debugging: Check if we received the response correctly
        if not response or not hasattr(response, 'text'):
            return {"error": "Failed to receive a valid response from Gemini."}

        return {"summary": response.text}

    except Exception as e:
        return {"error": "Failed to summarize", "details": str(e)}

# def summarize_with_gemini(tweets_data):
#     api_key = os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         return {"error": "API key not found. Please set GOOGLE_API_KEY in your .env file."}

#     client = genai.Client(api_key=api_key)

#     tweets = tweets_data.get("tweets", [])
#     if not tweets:
#         return {"error": "No tweets to summarize."}

#     contents = """You are MarketIntel-Synth.

# INPUT:
# A JSON array called **tweets**, each element containing the full text of a tweet and any embedded URLs.

# TASK:
# 1. Visit every URL, extract the full article text, and ignore non-article links.
# 2. Aggregate insights across **all** articles (no per-tweet reports).

# OUTPUT (Markdown only — no extra text):

# ## Key Insights
# - …

# ## Product Highlights
# - …

# ## Current Market Trends
# - …

# ## Predicted Next Big Trends
# - …

# STRICT RULES:
# - Use H1 heading for Key Insights
# - Use exactly the four H2 headings above in that order.
# - Under each heading provide **bullet points only** (• or -), max 8 bullets per section, each ≤ 140 characters.
# - Include only information that matters for market analysis (news, launches, features, pricing, partnerships, regulations).
# - Do **not** mention tweets, URLs, authors, publish dates, or the analysis process.
# - No apologies, disclaimers, or references to being an AI.
# - If a heading has no content, write “*None detected*” under it.
# """
#     for tweet in tweets:
#         text = tweet.get("text", "")
#         url = tweet.get("url", "")
#         contents += f"{text} ({url})\n"

#     try:
#         response = client.models.generate_content(
#             model="gemini-2.0-flash",
#             contents=contents,
#         )
#         return {"summary": response.text}
#     except Exception as e:
#         return {"error": "Failed to summarize", "details": str(e)}
