#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 04:56:03 2024

@author: uumin
"""

import requests
import pandas as pd
import time
import os

def save_progress(year, month):
    with open("fetch_progress.txt", "w") as f:
        f.write(f"{year},{month}")

def load_progress():
    if os.path.exists("fetch_progress.txt"):
        with open("fetch_progress.txt", "r") as f:
            year, month = map(int, f.read().strip().split(","))
        return year, month
    return None, None


def get_nyt_articles1(year, month, api_key, max_retries=3):
    """
    Fetches NYT article metadata for a specific year and month with retry and delay for rate limiting.

    Parameters:
    - year (int): The year of the articles (e.g., 1994).
    - month (int): The month of the articles (e.g., 1 for January).
    - api_key (str): Your NYT API key.
    - max_retries (int): Number of retry attempts in case of request failure.

    Returns:
    - DataFrame: A pandas DataFrame with article metadata for the specified month and year.
    """
    url = f"https://api.nytimes.com/svc/archive/v1/{year}/{month}.json?api-key={api_key}"
    retries = 0

    while retries < max_retries:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("response", {}).get("docs", [])

            # Process articles to extract relevant metadata
            article_list = []
            for article in articles:
                # Extract keywords as a comma-separated string
                keywords = ", ".join([kw.get("value", "") for kw in article.get("keywords", [])])
                
                article_data = {
                    "headline": article.get("headline", {}).get("main", ""),
                    "abstract": article.get("abstract", ""),
                    "lead_paragraph": article.get("lead_paragraph", ""),
                    "pub_date": article.get("pub_date", ""),
                    "section_name": article.get("section_name", ""),
                    "type_of_material": article.get("type_of_material", ""),
                    "web_url": article.get("web_url", ""),
                    "keywords": keywords  # Add keywords to article data
                }
                article_list.append(article_data)

            # Convert to DataFrame
            return pd.DataFrame(article_list)
        
        elif response.status_code == 429:
            print(f"Rate limit exceeded. Retrying after 60 seconds...")
            time.sleep(60)
            retries += 1
        else:
            print(f"Error {response.status_code}: Unable to fetch data for {year}-{month}")
            return pd.DataFrame()  # Return an empty DataFrame if an error occurs after retries

def get_nyt_data_for_range1(start_year, end_year, api_key):
    """
    Fetches NYT metadata for all months from start_year to end_year (inclusive), with a limit of 500 requests per day.

    Parameters:
    - start_year (int): The starting year (e.g., 1994).
    - end_year (int): The ending year (e.g., 2024).
    - api_key (str): Your NYT API key.

    Returns:
    - DataFrame: A pandas DataFrame with all articles' metadata for the specified range.
    """
    all_articles = []
    daily_request_count = 0
    max_daily_requests = 500

    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            if daily_request_count >= max_daily_requests:
                print("Daily request limit reached. Please resume tomorrow.")
                return pd.DataFrame(all_articles)  # Stop if daily limit is reached

            print(f"Fetching data for {year}-{month}")
            articles_df = get_nyt_articles(year, month, api_key)
            all_articles.extend(articles_df.to_dict('records'))
            
            daily_request_count += 1
            time.sleep(12)  # 12-second delay to avoid per-minute rate limit

    return pd.DataFrame(all_articles)

def get_nyt_articles(year, month, api_key, max_retries=3):
    url = f"https://api.nytimes.com/svc/archive/v1/{year}/{month}.json?api-key={api_key}"
    retries = 0

    while retries < max_retries:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("response", {}).get("docs", [])

            article_list = []
            for article in articles:
                keywords = ", ".join([kw.get("value", "") for kw in article.get("keywords", [])])
                article_data = {
                    "headline": article.get("headline", {}).get("main", ""),
                    "abstract": article.get("abstract", ""),
                    "lead_paragraph": article.get("lead_paragraph", ""),
                    "pub_date": article.get("pub_date", ""),
                    "section_name": article.get("section_name", ""),
                    "type_of_material": article.get("type_of_material", ""),
                    "web_url": article.get("web_url", ""),
                    "keywords": keywords
                }
                article_list.append(article_data)

            save_progress(year, month)  # Save progress
            return pd.DataFrame(article_list)
        
        elif response.status_code == 429:
            print("Rate limit exceeded. Retrying after 60 seconds...")
            time.sleep(60)
            retries += 1
        else:
            print(f"Error {response.status_code}: Unable to fetch data for {year}-{month}")
            return pd.DataFrame()  # Return empty DataFrame if an error occurs

    # Return empty DataFrame if retries are exhausted
    return pd.DataFrame()

def get_nyt_data_for_range(start_year, end_year, api_key):
    all_articles = []
    last_year, last_month = load_progress()  # Load last progress if available
    daily_request_count = 0
    max_daily_requests = 500

    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            if (last_year is not None) and (year < last_year or (year == last_year and month <= last_month)):
                continue  # Skip already fetched months

            if daily_request_count >= max_daily_requests:
                print("Daily request limit reached. Please resume tomorrow.")
                return pd.DataFrame(all_articles)

            print(f"Fetching data for {year}-{month}")
            articles_df = get_nyt_articles(year, month, api_key)
            
            if not articles_df.empty:  # Only extend if data is available
                all_articles.extend(articles_df.to_dict('records'))
            
            daily_request_count += 1
            time.sleep(12)  # Rate limit delay

    return pd.DataFrame(all_articles)



    return pd.DataFrame(all_articles)
# Example usage
api_key = "v878BGnAS07azMnYGR2HxTnHff7cci4G"  # Replace with your NYT API key
articles_df = get_nyt_data_for_range(2024, 2025, api_key) 

save_dir = "/Users/yueyuemin/Documents/school/QMSS/Thesis/data/raw"
os.makedirs(save_dir, exist_ok=True)

# Save the file
articles_df.to_csv(os.path.join(save_dir, "nyt_articles_2024_2025.csv"), index=False)
print("Data saved to nyt_articles_2024_2025")
