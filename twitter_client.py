import requests
import datetime
import os
import streamlit as st

def fetch_tweets(keyword, pages, weeks, region):
    API_KEY = st.secrets["X_API_KEY"]

    since_time = (datetime.datetime.now() - datetime.timedelta(weeks=weeks)).strftime('%Y-%m-%d_%H:%M:%S_UTC')


    url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
    headers = {
        "X-API-Key": API_KEY
    }

    params = {
        "query": f"{keyword} lang:en {region} filter:media filter:has_engagement since:{since_time}",
        "queryType": "Top",
        "cursor": ""
    }

    all_tweets = []
    try:
        for _ in range(pages):
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            tweets = data.get("tweets", [])
            all_tweets.extend(tweets)

            if data.get("has_next_page") and data.get("next_cursor"):
                params["cursor"] = data["next_cursor"]
            else:
                break  # No more pages available

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request exception occurred: {req_err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return all_tweets
