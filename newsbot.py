
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

def get_combined_news_briefs():
    now = time.time()
    # 30分ごと更新（デバッグ用に短縮）
    if now - st.session_state.last_update > 1800 or not st.session_state.news_history:
        st.session_state.news_history = fetch_latest_titles()
        st.session_state.last_update = now
    
    return "  ■  ".join(st.session_state.news_history[-8:])

def fetch_latest_titles():
    """タイトル直取り（AIなし・確実動作）"""
    try:
        videos = scrapetube.get_channel("UCknLrEdhRCp1aegoMqRaCZg", limit=10, content_type="videos")
        video_list = list(videos)[:8]
        
        news_items = []
        for video in video_list:
            title = video.get('title', 'NO TITLE').strip().replace('\n', ' ')
            news_items.append(title[:90].upper())
        
        return news_items
    except:
        return ["DW NEWS: MONITORING GLOBAL DEVELOPMENTS", "CHECK BACK SOON FOR UPDATES"]

news_text = get_combined_news_briefs()
last_update = datetime.fromtimestamp(st.session_state.last_update).strftime("%H:%M")

ticker_html = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@700&display=swap');
body {{ margin: 0; background: transparent; overflow: hidden; }}
.ticker-container {{
    width: 100%; background: linear-gradient(90deg, #2c3e50 0%, #34495e 100%); 
    color: #ecf0f1; height: 42px; display: flex; align-items: center; 
    font-family: 'Roboto+Condensed', sans-serif; border-bottom: 2px solid #7f8c8d;
}}
.label {{ 
    background: #7f8c8d; padding: 0 18px; height: 100%; display: flex;
    align-items: center; font-size: 13px; font-weight: bold; 
    box-shadow: 4px 0 12px rgba(0,0,0,0.4);
}}
.label::after {{ content: 'UPDATED {last_update}JST'; font-size: 10px; margin-left: 8px; opacity: 0.8; }}
.ticker-content {{ flex: 1; overflow: hidden; white-space: nowrap; display: flex; align-items: center; }}
.scrolling-text {{
    display: inline-block; padding-left: 100%; font-size: 14px; letter-spacing: 0.8px;
    animation: scroll-left 70s linear infinite;
}}
@keyframes scroll-left {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-100%); }} }}
.sep {{ color: #bdc3c7; margin: 0 35px; font-weight: bold; }}
</style>
<div class="ticker-container">
    <div class="label">DW NEWS BRIEF</div>
    <div class="ticker-content">
        <div class="scrolling-text">
            {news_text} <span class="sep">|</span> 
            GENKAI AI SYSTEM STATUS: ONLINE <span class="sep">|</span>
        </div>
    </div>
</div>
"""
components.html(ticker_html, height=42)

