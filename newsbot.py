import streamlit as st
import streamlit.components.v1 as components
import scrapetube
import time
from datetime import datetime

st.set_page_config(layout="wide")

if "news_history" not in st.session_state:
    st.session_state.news_history = []
if "last_update" not in st.session_state:
    st.session_state.last_update = 0

def fetch_latest_titles():
    try:
        videos = scrapetube.get_channel("UCknLrEdhRCp1aegoMqRaCZg", limit=12, content_type="videos")
        video_list = list(videos)[:10]
        
        news_items = []
        for video in video_list:
            title_data = video.get('title', {})
            # 🔥 ここが重要！title_data が完全でコロンあり
            if isinstance(title_data, dict) and 'RUNS' in title_data:
                title = title_data['RUNS'][0]['TEXT'] if title_data['RUNS'] else 'NO TITLE'
            else:
                title = str(title_data).strip()
            title = title.strip().replace('\n', ' ')[:90].upper()
            news_items.append(title)
        return news_items
    except:
        return ["DW NEWS: LIVE UPDATES"] * 10

def get_combined_news_briefs():
    now = time.time()
    if now - st.session_state.last_update > 1800 or not st.session_state.news_history:
        st.session_state.news_history = fetch_latest_titles()
        st.session_state.last_update = now
    return "  ■  ".join(st.session_state.news_history[:10])

news_text = get_combined_news_briefs()
last_update = datetime.fromtimestamp(st.session_state.last_update).strftime("%H:%M")

# 43行目付近からの ticker_html 定義を以下のように修正（CSS内の括弧を2重に）
ticker_html = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@700&display=swap');
    body {{ margin: 0; background: transparent; overflow: hidden; padding: 0; }}
    .ticker-container {{
        width: 100%;
        background-color: #2c3e50;
        color: #ecf0f1;
        height: 40px;
        display: flex;
        align-items: center;
        font-family: 'Roboto Condensed', sans-serif;
        border-top: 1px solid #34495e;
        border-bottom: 2px solid #7f8c8d;
    }}
    .label {{
        background: #7f8c8d;
        padding: 0 15px;
        height: 100%;
        display: flex;
        align-items: center;
        font-size: 13px;
        font-weight: bold;
        z-index: 10;
        white-space: nowrap;
    }}
    .ticker-content {{
        flex: 1;
        overflow: hidden;
        white-space: nowrap;
    }}
    .scrolling-text {{
        display: inline-block;
        padding-left: 100%;
        font-size: 14px;
        animation: scroll-left 60s linear infinite;
    }}
    @keyframes scroll-left {{
        0% {{ transform: translateX(0); }}
        100% {{ transform: translateX(-100%); }}
    }}
</style>
<div class="ticker-container">
    <div class="label">DW NEWS BRIEF</div>
    <div class="ticker-content">
        <div class="scrolling-text">
            {news_text}  |  GENKAI AI SYSTEM STATUS: ONLINE  |
        </div>
    </div>
</div>
"""


