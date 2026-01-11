import streamlit as st
import streamlit.components.v1 as components
from youtube_transcript_api import YouTubeTranscriptApi
import scrapetube
from llama_index.llms.google_genai import GoogleGenAI
import os

# Streamlitの基本設定
st.set_page_config(layout="wide")

# APIキーの取得
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY not found in Secrets.")
    st.stop()

# 最新ライブラリでの初期化
llm = GoogleGenAI(model="models/gemini-2.5-flash", api_key=api_key)

def get_latest_dw_summary():
    try:
        # 1. YouTubeから最新動画取得
        videos = scrapetube.get_channel("UCknLrEdhRCp1aegoMqRaCZg", limit=1)
        video = next(videos)
        video_id = video['videoId']
        
        # 2. 字幕の取得
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([i['text'] for i in transcript_list])

        # 3. 要約生成
        prompt = (
            f"As a professional news editor, summarize this DW News transcript in 50-70 words. "
            f"Focus on the main event, location, and significance. "
            f"Output in a single continuous line for a news ticker: {transcript_text[:12000]}"
        )
        
        # response.text で確実に取得
        response = llm.complete(prompt)
        summary = str(response.text).strip()
    except Exception as e:
        # エラー発生時は「Live」メッセージを表示して処理を止めない
        summary = "LIVE: PROVIDING LATEST UPDATES FROM DW NEWS. COVERAGE CONTINUES ON GLOBAL DEVELOPMENTS."

    return summary.replace("\n", " ")

# ニュース取得
news_text = get_latest_dw_summary()

# --- ニュースティッカー用HTML/CSS (ご指定のトーン) ---
ticker_html = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@700&display=swap');

    body {{ margin: 0; background: transparent; overflow: hidden; }}

    .ticker-container {{
        width: 100%;
        background-color: #2c3e50; /* トーンを抑えた紺色 */
        color: #ecf0f1; /* 明るすぎない白 */
        height: 40px;
        display: flex;
        align-items: center;
        font-family: 'Roboto Condensed', sans-serif;
        border-top: 1px solid #34495e; /* トーンを抑えた境界線 */
        border-bottom: 2px solid #7f8c8d; /* アクセントを抑えた下線 */
    }}

    .breaking-label {{
        background: #7f8c8d; /* トーンを抑えたラベル背景 */
        padding: 0 15px;
        height: 100%;
        display: flex;
        align-items: center;
        font-size: 14px;
        letter-spacing: 1px;
        z-index: 10;
        box-shadow: 3px 0 10px rgba(0,0,0,0.3);
    }}

    .ticker-content {{
        flex: 1;
        overflow: hidden;
        white-space: nowrap;
        display: flex;
        align-items: center;
    }}

    .scrolling-text {{
        display: inline-block;
        padding-left: 100%;
        font-size: 14px; /* 小さめの文字 */
        letter-spacing: 0.5px;
        animation: scroll-left 45s linear infinite; /* 長文用に速度調整 */
        text-transform: uppercase;
    }}

    @keyframes scroll-left {{
        0% {{ transform: translateX(0); }}
        100% {{ transform: translateX(-100%); }}
    }}

    .separator {{
        color: #bdc3c7; /* 柔らかいアクセント */
        margin: 0 20px;
    }}
</style>

<div class="ticker-container">
    <div class="breaking-label">DW NEWS BRIEF</div>
    <div class="ticker-content">
        <div class="scrolling-text">
            {news_text} <span class="separator">|</span> 
            LATEST UPDATES FROM DW NEWS SERVICE <span class="separator">|</span>
            GENKAI AI AGENT SYSTEM ONLINE
        </div>
    </div>
</div>
"""

components.html(ticker_html, height=60)
