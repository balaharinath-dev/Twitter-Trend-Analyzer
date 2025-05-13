import pandas as pd
import streamlit as st
from twitter_client import fetch_tweets
from gemini_client import summarize_with_gemini
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from datetime import datetime

# Twitter-like color scheme
TWITTER_BLUE = "#1DA1F2"
LIGHT_BLUE = "#E8F5FE"
DARK_TEXT = "#14171A"
GRAY_TEXT = "#657786"
LIGHT_GRAY = "#F5F8FA"
WHITE = "#FFFFFF"

def set_custom_theme():
    # Set custom theme with CSS to force light mode
    st.markdown("""
    <style>
    /* Force light theme everywhere */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #14171A;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #F5F8FA;
    }
    .css-1d391kg {
        background-color: #F5F8FA;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #1DA1F2;
        color: white;
        border-radius: 20px;
        padding: 10px 20px;
        font-weight: bold;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #0c85d0;
        box-shadow: 0 0 10px rgba(29, 161, 242, 0.5);
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background-color: #E8F5FE;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .css-1wivap2 {
        background-color: #E8F5FE;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #FFFFFF;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #F5F8FA;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        color: #657786;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1DA1F2 !important;
        color: white !important;
    }
    
    /* Container cards */
    .stContainer {
        background-color: #FFFFFF;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Tweet cards */
    .tweet-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #E1E8ED;
        transition: transform 0.2s;
    }
    .tweet-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Override dark theme elements */
    [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF;
    }
    [data-testid="stHeader"] {
        background-color: #FFFFFF;
    }
    [data-testid="stToolbar"] {
        background-color: #FFFFFF;
    }
    [data-testid="stDecoration"] {
        background-color: #1DA1F2;
    }
    
    /* Chart sections */
    .chart-section {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
        border: 1px solid #E1E8ED;
    }
    
    /* Text and paragraph colors */
    p, span, div {
        color: #14171A;
    }
    
    /* Input fields */
    .stTextInput input, .stTextInput textarea, .stSelectbox select {
        border-color: #E1E8ED;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="X Market Analysis", layout="wide")
    set_custom_theme()
    
    # App header with Twitter-like styling
    col1, col2 = st.columns([1, 5])
    with col1:
        st.markdown(f"""
        <div style="font-size: 20px; color: {TWITTER_BLUE}; margin-top: 5px;">
        <img src="https://static.vecteezy.com/system/resources/previews/027/395/710/original/twitter-brand-new-logo-3-d-with-new-x-shaped-graphic-of-the-world-s-most-popular-social-media-free-png.png"/>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <h1 style="color: {DARK_TEXT}; margin-bottom: 0;">Market Analysis</h1>
        <p style="color: {GRAY_TEXT}; margin-top: 0;">Powered by Twitter Data</p>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="height: 1px; background-color: {LIGHT_GRAY}; margin: 15px 0 25px 0;"></div>
    """, unsafe_allow_html=True)

    # Sidebar Configuration Panel
    with st.sidebar:
        
    #     st.sidebar.markdown("""
    #     <style>
    #         .red-button {
    #             display: inline-block;
    #             padding: 0.5em 1em;
    #             color: white !important;
    #             background-color: #1DA1F2 !important;
    #             border-radius: 15px !important;
    #             text-decoration: none !important;
    #             font-weight: bold;
    #             text-align: center;
    #             width: 30%;
    #             margin-bottom: 10px;
    #         }
    #         .red-button:hover {
    #             background-color: #177CC2 !important; /* darker on hover */
    #         }
    #     </style>

    #     <a href="http://localhost:8501" target="_self" class="red-button">Back</a>
    # """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <h3 style="color: {TWITTER_BLUE}; font-weight: bold;">
            <span style="font-size: 24px;">🔍</span> Search Settings
        </h3>
        """, unsafe_allow_html=True)
        
    
        
        keyword = st.text_input("Enter keyword for tweets", placeholder="e.g., cryptocurrency")
        
        col1, col2 = st.columns(2)
        with col1:
            week_option = st.selectbox("Time range", options=["1 week", "2 weeks", "3 weeks", "4 weeks"])
        with col2:
            page_option = st.selectbox("Pages to fetch", options=["1 page", "2 page", "4 page", "7 page"])
        
        region = st.text_input("Region filter", placeholder="e.g., India, USA")
        
        st.markdown("""</div>""", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        run_analysis = st.button("🚀 Fetch and Analyze")

    # Main content
    if run_analysis:
        week_mapping = {"1 week": 1, "2 weeks": 2, "3 weeks": 3, "4 weeks": 4}
        page_mapping = {"1 page": 1, "2 page": 2, "4 page": 4, "7 page": 7}
        selected_weeks = week_mapping[week_option]
        selected_pages = page_mapping[page_option]

        # Create a progress container
        progress_container = st.container()
        with progress_container:
            with st.spinner(f"Fetching tweets about '{keyword}'..."):
                tweets_data = fetch_tweets(keyword, pages=selected_pages, weeks=selected_weeks, region=region)

        # Success message with custom styling
        st.markdown(f"""
        <div style="background-color: #E8F7EF; color: #0C6B58; padding: 12px; border-radius: 8px; 
                    display: flex; align-items: center; margin-bottom: 20px; border-left: 4px solid #0C6B58;">
            <span style="font-size: 20px; margin-right: 8px;">✅</span>
            <span>Successfully fetched {len(tweets_data)} tweets related to "{keyword}"</span>
        </div>
        """, unsafe_allow_html=True)

        # Save data
        os.makedirs("data", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/{keyword}_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(tweets_data, f, ensure_ascii=False, indent=2)

        # Download button with custom styling
        col1, col2 = st.columns([1, 3])
        with col1:
            st.download_button(
                label="⬇️ Download Tweet Data",
                data=json.dumps(tweets_data, indent=2),
                file_name=f"{keyword}_{timestamp}.json",
                mime="application/json"
            )

        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.spinner("Analyzing tweets with Synapt AI..."):
            summary_response = summarize_with_gemini({"tweets": tweets_data})
        
        if "error" in summary_response:
            st.error(summary_response["error"])
        else:
            st.markdown(f"""
            <div style="background-color: {LIGHT_BLUE}; border-radius: 12px; padding: 20px; margin-bottom: 30px; 
                    border: 1px solid {TWITTER_BLUE};">
                <h3 style="color: {TWITTER_BLUE}; margin-top: 0;">
                    <span style="font-size: 24px;">🧠</span> Synapt Insights
                </h3>
                <div style="color: {DARK_TEXT}; line-height: 1.6;">
                    {summary_response.get("summary", "No summary returned.")}
                
            """, unsafe_allow_html=True)

        # Load data to DataFrame
        df = pd.DataFrame(tweets_data)
        df["createdAt"] = pd.to_datetime(df["createdAt"], errors='coerce')
        if "author" in df.columns:
            df["location"] = df["author"].apply(lambda x: x.get("location", "").strip() if isinstance(x, dict) else "")
            df["username"] = df["author"].apply(lambda x: x.get("userName", "Unknown") if isinstance(x, dict) else "Unknown")

        df["engagement"] = (
            df.get("likeCount", 0) +
            df.get("retweetCount", 0) +
            df.get("replyCount", 0) +
            df.get("quoteCount", 0)
        )

        # Tabs for Results
        tab1, tab2, tab3 = st.tabs(["📊 Overview", "📍 Locations", "🔥 Top Tweets"])

        with tab1:
            # Overview metrics
            metrics_cols = st.columns(4)
            with metrics_cols[0]:
                st.metric("Total Tweets", len(df))
            with metrics_cols[1]:
                avg_engagement = int(df["engagement"].mean()) if not df.empty else 0
                st.metric("Avg. Engagement", avg_engagement)
            with metrics_cols[2]:
                unique_users = df["username"].nunique() if "username" in df.columns else 0
                st.metric("Unique Users", unique_users)
            with metrics_cols[3]:
                total_likes = df["likeCount"].sum() if "likeCount" in df.columns else 0
                st.metric("Total Likes", f"{total_likes:,}")
            
            # Create two columns for charts
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                # Engagement pie chart
                st.markdown(f"""
                <div class="chart-section">
                    <h3 style="color: {DARK_TEXT}; margin-top: 0px; font-size: 18px;">
                        <span style="color: {TWITTER_BLUE};">📊</span> Engagement Breakdown
                    </h3>
                </div>
                """, unsafe_allow_html=True)
                
                if not df.empty:
                    engagement_data = [
                        df["likeCount"].fillna(0).sum(),
                        df["retweetCount"].fillna(0).sum(),
                        df["replyCount"].fillna(0).sum(),
                        df["quoteCount"].fillna(0).sum()
                    ]
                    
                    labels = ["Likes", "Retweets", "Replies", "Quotes"]
                    
                    # Check if we have engagement data
                    if sum(engagement_data) > 0:
                        fig_engagement = go.Figure(data=[go.Pie(
                            labels=labels,
                            values=engagement_data,
                            hole=.4,
                            marker=dict(colors=[TWITTER_BLUE, '#6c5ce7', '#00bfa6', '#ff6b6b']),
                            textinfo='label+percent',
                            insidetextorientation='radial',
                            hoverinfo='label+value'
                        )])
                        
                        fig_engagement.update_layout(
                            showlegend=False,
                            plot_bgcolor=WHITE,
                            paper_bgcolor=WHITE,
                            font_color=DARK_TEXT,
                            margin=dict(l=20, r=20, t=20, b=20),
                            height=300,
                            annotations=[
                                dict(
                                    text=f'Total<br>{sum(engagement_data):,}',
                                    x=0.5, y=0.5,
                                    font_size=16,
                                    font_color=DARK_TEXT,
                                    showarrow=False
                                )
                            ]
                        )
                        
                        st.plotly_chart(fig_engagement, use_container_width=True)
                    else:
                        st.info("No engagement data found in the fetched tweets.")
            
            with chart_col2:
                # Hashtags Analysis
                st.markdown(f"""
                <div class="chart-section">
                    <h3 style="color: {DARK_TEXT}; margin-top: 0px; font-size: 18px;">
                        <span style="color: {TWITTER_BLUE};">🏷️</span> Top Hashtags
                    </h3>
                </div>
                """, unsafe_allow_html=True)
                
                hashtags = []
                for entry in tweets_data:
                    tags = entry.get("entities", {}).get("hashtags", [])
                    hashtags.extend([tag["text"].lower() for tag in tags])
                
                if hashtags:
                    hashtags_df = pd.DataFrame(hashtags, columns=["Hashtag"])
                    top_hashtags = hashtags_df["Hashtag"].value_counts().head(5).reset_index()
                    top_hashtags.columns = ["Hashtag", "Count"]
                    
                    fig_hashtags = px.bar(
                        top_hashtags, 
                        x="Hashtag", 
                        y="Count", 
                        title="best performing hashtags",
                        color_discrete_sequence=[TWITTER_BLUE]
                    )
                    fig_hashtags.update_layout(
                        plot_bgcolor=WHITE,
                        paper_bgcolor=WHITE,
                        font_color=DARK_TEXT,
                        title_font_color=DARK_TEXT,
                        margin=dict(l=20, r=20, t=20, b=20),
                        bargap=0.4,
                        height=300,
                        xaxis=dict(
                            title="",
                            tickangle=-30
                        ),
                        yaxis=dict(
                            title="Count"
                        )
                    )
                    st.plotly_chart(fig_hashtags, use_container_width=True)
                else:
                    st.info("No hashtags found in the analyzed tweets.")
                    
            # Activity Timeline
            st.markdown(f"""
            <div class="chart-section">
                <h3 style="color: {DARK_TEXT}; margin-top: 0px; font-size: 18px;">
                    <span style="color: {TWITTER_BLUE};">📅</span> Activity Timeline
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Activity over time
            if len(df) >= 3:
                # Group by date and count tweets
                df['date'] = df['createdAt'].dt.date
                tweet_counts = df.groupby('date').size().reset_index(name='count')
                
                fig_timeline = px.line(
                    tweet_counts, 
                    x='date', 
                    y='count',
                    labels={"date": "Date", "count": "Tweets"}
                )
                
                fig_timeline.update_traces(
                    line_color=TWITTER_BLUE,
                    line_width=3,
                    mode='lines+markers',
                    marker=dict(size=8, color=TWITTER_BLUE)
                )
                
                fig_timeline.update_layout(
                    plot_bgcolor=WHITE,
                    paper_bgcolor=WHITE,
                    font_color=DARK_TEXT,
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=250,
                    xaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(220,220,220,0.4)'
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(220,220,220,0.4)'
                    )
                )
                
                st.plotly_chart(fig_timeline, use_container_width=True)
            else:
                st.info("Not enough data points for timeline visualization.")
                
     

        with tab2:
            st.markdown(f"""
            <h3 style="color: {DARK_TEXT}; margin-top: 10px;">
                <span style="color: {TWITTER_BLUE};">🌍</span> Top Locations
            </h3>
            """, unsafe_allow_html=True)
            
            keyword_lower = keyword.lower()
            keyword_locs = df[df["text"].str.lower().str.contains(keyword_lower, na=False)]
            keyword_locs = keyword_locs[keyword_locs["location"] != ""]
            
            if not keyword_locs.empty:
                top_locs = keyword_locs["location"].value_counts().head(10).reset_index()
                top_locs.columns = ["Location", "Mentions"]
                
                fig_loc = px.bar(
                    top_locs, 
                    x="Location", 
                    y="Mentions", 
                    title=f"Top 10 Locations Discussing '{keyword}'",
                    color_discrete_sequence=[TWITTER_BLUE]
                )
                fig_loc.update_layout(
                    plot_bgcolor=WHITE,
                    paper_bgcolor=WHITE,
                    font_color=DARK_TEXT,
                    title_font_color=DARK_TEXT,
                    margin=dict(l=20, r=20, t=40, b=20),
                    title_x=0.5,
                    bargap=0.4
                )
                st.plotly_chart(fig_loc, use_container_width=True)
                
                

        with tab3:
            st.markdown(f"""
            <h3 style="color: {DARK_TEXT}; margin-top: 10px;">
                <span style="color: {TWITTER_BLUE};">🔥</span> Top Tweets by Engagement
            </h3>
            """, unsafe_allow_html=True)
            
            top_engaged = df.sort_values(by="engagement", ascending=False).head(5)
            
            if not top_engaged.empty:
                for _, row in top_engaged.iterrows():
                    engagement = row.get('engagement', 0)
                    created_at = row['createdAt'].strftime('%b %d, %Y') if pd.notnull(row['createdAt']) else ""
                    
                    st.markdown(f"""
                        <div class="tweet-card">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <div>
                                    <span style="font-weight: bold; color: {DARK_TEXT};">@{row['username']}</span>
                                    <span style="color: {GRAY_TEXT}; margin-left: 5px;">· {created_at}</span>
                                </div>
                                <div style="color: {TWITTER_BLUE}; font-weight: bold;">
                                    {engagement} engagement
                                </div>
                            </div>
                            <p style="font-size: 15px; line-height: 1.5; color: {DARK_TEXT}; margin-bottom: 12px;">
                                {row['text']}
                            </p>
                            <div style="display: flex; justify-content: space-between; color: {GRAY_TEXT};">
                                <span>❤️ {row.get('likeCount', 0)}</span>
                                <span>🔁 {row.get('retweetCount', 0)}</span>
                                <span>💬 {row.get('replyCount', 0)}</span>
                                <span>🔖 {row.get('quoteCount', 0)}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No tweets available to display.")
    else:
        # Display welcome message when app first loads
        st.markdown(f"""
        <div style="text-align: center; padding: 50px 20px; background-color: {LIGHT_BLUE}; border-radius: 12px; margin: 30px 0;">
            <div style="font-size: 70px; margin-bottom: 20px;">📊</div>
            <h2 style="color: {DARK_TEXT}; margin-bottom: 20px;">Welcome to Twitter Market Analysis</h2>
            <p style="color: {GRAY_TEXT}; font-size: 18px; margin-bottom: 30px;">
                Analyze Twitter trends and sentiment to gain valuable market insights.
                Enter your search parameters in the sidebar to get started.
            </p>
            <div style="color: {TWITTER_BLUE}; font-weight: bold;">Use the sidebar to begin your analysis →</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature highlights
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""<h3 style="color: {DARK_TEXT};">Features</h3>""", unsafe_allow_html=True)
        
        cols = st.columns(3)
        with cols[0]:
            st.markdown(f"""
            <div style="background-color: {WHITE}; padding: 20px; border-radius: 10px; height: 200px; 
                      box-shadow: 0 2px 10px rgba(0,0,0,0.05); border: 1px solid {LIGHT_GRAY};">
                <div style="font-size: 30px; color: {TWITTER_BLUE}; margin-bottom: 10px;">🔍</div>
                <h4 style="color: {DARK_TEXT}; margin-bottom: 10px;">Advanced Search</h4>
                <p style="color: {GRAY_TEXT};">Search for specific keywords, regions, and set timeframes to find relevant tweets.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown(f"""
            <div style="background-color: {WHITE}; padding: 20px; border-radius: 10px; height: 200px; 
                      box-shadow: 0 2px 10px rgba(0,0,0,0.05); border: 1px solid {LIGHT_GRAY};">
                <div style="font-size: 30px; color: {TWITTER_BLUE}; margin-bottom: 10px;">🧠</div>
                <h4 style="color: {DARK_TEXT}; margin-bottom: 10px;">AI Insights</h4>
                <p style="color: {GRAY_TEXT};">Synapt AI analyzes tweets to extract meaningful insights and sentiment trends.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with cols[2]:
            st.markdown(f"""
            <div style="background-color: {WHITE}; padding: 20px; border-radius: 10px; height: 200px; 
                      box-shadow: 0 2px 10px rgba(0,0,0,0.05); border: 1px solid {LIGHT_GRAY};">
                <div style="font-size: 30px; color: {TWITTER_BLUE}; margin-bottom: 10px;">📊</div>
                <h4 style="color: {DARK_TEXT}; margin-bottom: 10px;">Visual Analytics</h4>
                <p style="color: {GRAY_TEXT};">Interactive charts and visualizations to help you understand market sentiment.</p>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()