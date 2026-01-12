import streamlit as st
import streamlit.components.v1 as components
import scrapetube
import json
import time
from datetime import datetime, timedelta
try:
    from llama_index.llms.google_genai import GoogleGenAI
    HAS_GEMINI = True
except:
    HAS_GEMINI = False

st.set_page_config(layout="wide")

api_key = st.secrets.get("GEMINI_API_KEY", None)
llm = GoogleGenAI(model="models/gemini-2.5-flash", api_key=api_key) if api_key and HAS_GEMINI else None

# セッション状態でニュース履歴管理（最大10件、4時間で更新）
if "news_history" not in st.session_state:
    st.session_state.news_history = []
if "last_update" not in st.session_state:
    st.session_state.last_update = 0

def get_combined_news_briefs():
    # 4時間（14400秒）経過 or 初回なら更新
    now = time.time()
    if now - st.session_state.last_update > 14400 or not st.session_state.news_history:
        st.session_state.news_history = fetch_latest_news()
        st.session_state.last_update = now
    
    # 最新10件を結合
    if st.session_state.news_history:
        return "  ■  ".join(st.session_state.news_history[-10:])
    return "DW NEWS: MONITORING GLOBAL DEVELOPMENTS"

def fetch_latest_news():
    """直近の動画タイトルからAI要約を生成・蓄積"""
    new_summaries = []
    
    try:
        videos = scrapetube.get_channel("UCknLrEdhRCp1aegoMqRaCZg", limit=10, content_type="videos")
        video_list = list(videos)[:5]  # 5件チェックして重複除外
        
        for video in video_list:
            title = video.get('title', '').strip()
            if not title:
                continue
                
            # 既存履歴にない新しいタイトルのみ処理
            if title not in [n.split(' ■ ')[0] for n in st.session_state.news_history]:
                
                # AI要約生成
                if llm:
                    try:
                        prompt = f"""DW News video titled: "{title}"
Create a professional 1-sentence news brief (30-40 words) in UPPERCASE ENGLISH only.
Focus on global impact and key facts:"""
                        
                        response = llm.complete(prompt)
                        summary = str(response.text).strip().replace("\n", " ").upper()
                        if len(summary) > 20:
                            new_summaries.append(summary[:120])
                            continue
                    except:
                        pass
                
                # AI失敗時はタイトル整形
                summary = title[:100].replace('\n', ' ').upper()
                new_summaries.append(summary)
        
        # 履歴に追加（古い順）
        st.session_state.news_history.extend(new_summaries)
        st.session_state.news_history = st.session_state.news_history[-20:]  # 最大20件保持
        
    except:
        pass
    
    return st.session_state.news_history or ["DW NEWS: INITIALIZING GLOBAL FEED"]

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
    align-items: center; font-size: 13px; font-weight: bold; z-index: 10;
    box-shadow: 4px 0 12px rgba(0,0,0,0.4); position: relative;
}}
.label::after {{ content: 'UPDATED {last_update}JST'; font-size: 10px; margin-left: 8px; }}
.ticker-content {{ flex: 1; overflow: hidden; white-space: nowrap; display: flex; align-items: center; }}
.scrolling-text {{
    display: inline-block; padding-left: 100%; font-size: 14px; letter-spacing: 0.8px;
    animation: scroll-left 80s linear infinite; /* 10件なので80秒 */
}}
@keyframes scroll-left {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-100%); }} }}
.sep {{ color: #bdc3c7; margin: 0 35px; font-weight: bold; }}
</style>
<div class="ticker-container">
    <div class="label">DW NEWS BRIEF</div>
    <div class="ticker-content">
        <div class="scrolling-text">
            {news_text} <span class="sep">|</span> 
            GENKAI AI SYSTEM STATUS: ONLINE | LAST UPDATE: {last_update}JST <span class="sep">|</span>
        </div>
    </div>
</div>
"""
components.html(ticker_html, height=42)

