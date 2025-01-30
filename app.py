import streamlit as st
from groq import Groq
from serpapi import GoogleSearch
from pytrends.request import TrendReq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

# Initialize Clients
client = Groq(api_key=GROQ_API_KEY)
pytrends = TrendReq()

# Streamlit Page Config
st.set_page_config(page_title="Smart News Summarizer", page_icon="📰", layout="wide")
st.title("📰 Smart News Summarizer")

# Sidebar
st.sidebar.header("Settings")
country_codes = {
    "India 🇮🇳": "IN",
    "United States 🇺🇸": "US",
    "United Kingdom 🇬🇧": "GB",
    "Canada 🇨🇦": "CA",
    "Germany 🇩🇪": "DE",
    "France 🇫🇷": "FR",
    "Australia 🇦🇺": "AU",
    "Japan 🇯🇵": "JP",
    "Brazil 🇧🇷": "BR"
}
country = st.sidebar.selectbox("🌍 Select Country", list(country_codes.keys()))
country_code = country_codes[country]

# Function to Fetch News
def get_news_articles(query, country="IN"):
    """Fetch top 5 news articles based on topic and region (last 2 months)."""
    search = GoogleSearch({
        "q": query,
        "tbm": "nws",
        "gl": country,  # Region-specific results
        "tbs": "qdr:m2",  # Fetches news from the past 2 months
        "api_key": SERP_API_KEY
    })
    results = search.get_dict()
    articles = results.get("news_results", [])[:5]  # Get top 5 articles
    
    news_list = []
    for article in articles:
        title = article["title"]
        link = article["link"]
        snippet = article.get("snippet", "No summary available.")
        news_list.append(f"**{title}**\n📌 {snippet}\n🔗 [Read more]({link})\n")
    
    return news_list

# Function to Summarize News
def summarize_articles(articles):
    """Summarize extracted news in bullet points using Groq's Llama-3.3."""
    messages = [
        {"role": "system", "content": "Summarize the given news articles in crisp bullet points."},
        {"role": "user", "content": "\n\n".join(articles)}
    ]
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    
    return completion.choices[0].message.content

# Function to Get Trending Topics
def get_trending_topics(country_code):
    """Fetch top 10 trending Google searches in the selected country."""
    pytrends.build_payload(kw_list=[], geo=country_code)
    trending_data = pytrends.trending_searches(pn=country_code)
    return trending_data.head(10)[0].tolist()

# Search Mode
st.subheader("🔍 Search for News")
topic = st.text_input("Enter a News Topic (or leave blank for trending topics):")

# Trending Mode Button
if st.button("🔥 Get Top 10 Trending Topics"):
    with st.spinner("Fetching trending topics..."):
        trending_topics = get_trending_topics(country_code)
        st.success("Here are the top 10 trending topics:")
        for i, trend in enumerate(trending_topics, 1):
            st.write(f"{i}. {trend}")

# Fetch and Summarize News
if st.button("📰 Get News Summary"):
    with st.spinner("Fetching latest news..."):
        if topic:
            news_articles = get_news_articles(topic, country_code)
        else:
            trending_topics = get_trending_topics(country_code)
            topic = trending_topics[0]  # Pick the top trending topic
            news_articles = get_news_articles(topic, country_code)
        
        summarized_news = summarize_articles(news_articles)
        
        # Display Results
        st.subheader(f"🗞️ News Summary for: **{topic.capitalize()}**")
        st.markdown(summarized_news, unsafe_allow_html=True)
