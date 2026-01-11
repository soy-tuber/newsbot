import streamlit as st
import streamlit.components.v1 as components
from youtube_transcript_api import YouTubeTranscriptApi
import scrapetube
from llama_index.llms.google_genai import GoogleGenAI

# Streamlitの基本設定
st.set_page_config(layout="wide")

# APIキーの取得（Secretsから安全に取得）
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Error: GEMINI_API_KEY is not set in Streamlit Secrets.")
    st.stop()

# 最新のGoogleGenAIクラスを使用（Gemini 2.5 Flash）
llm = GoogleGenAI(model="models/gemini-2.5-flash", api_key=api_key)

def get_latest_dw_summary():
    try:
        # 1. DW News (Channel ID: UCknLrEdhRCp1aegoMqRaCZg) から最新動画を取得
        videos = scrapetube.get_channel("UCknLrEdhRCp1aegoMqRaCZg", limit=1)
        video = next(videos)
        video_id = video['videoId']
        
        # 2. 字幕の取得
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([i['text'] for i in transcript_list])

        # 3. Geminiで詳細な英語ニュース要約を生成
        prompt = (
            f"Context: You are a senior news editor for a global broadcast network. "
            f"Task: Summarize the following news transcript into a high-density, professional breaking news crawler text. "
            f"Requirements: Use sophisticated English, focus on facts (Who, What, Where, Why), "
            f"approx 50-70 words, single continuous line. "
            f"Transcript: {transcript_text[:12000]}"
        )
        response = llm.complete(prompt)
        summary = response.text
    except Exception as e:
        # エラー時のバックアップ表示
        summary = "WORLD NEWS UPDATE: DW continues coverage of evolving global events. Stay tuned for in-depth analysis and breaking reports from our correspondents worldwide."

    return summary.strip().replace("\n", " ")

# ニュース内容の取得
news_text = get_latest_dw_summary()

# --- ニュースティッカー用HTML/CSS (より小さく、密度高く) ---
ticker_html = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@700&display=swap');
    
    body {{ margin: 0; background: transparent; overflow: hidden; }}
    
    .ticker-container {{
        width: 100%;
        background-color: #1a252f; /* さらに深い紺色 */
        color: #f8f9fa;
        height: 35px; /* 高さを少し抑える */
        display: flex;
        align-items: center;
        font-family: 'Roboto Condensed', sans-serif;
        border-top: 1px solid #2c3e50;
        border-bottom: 2px solid #e74c3c; /* 警告色の赤 */
    }}
    
    .label {{
        background: #e74c3c;
        padding: 0 12px;
        height: 100%;
        display: flex;
        align-items: center;
        font-size: 12px;
        letter-spacing: 1.5px;
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
        font-size: 13px; /* 小さめのフォントで密度を出す */
        letter-spacing: 0.8px;
        animation: scroll-left 50s linear infinite; /* 長文用にかなりゆっくり流す */
        text-transform: uppercase; /* すべて大文字にして速報感を出す */
    }}

    @keyframes scroll-left {{
        0% {{ transform: translateX(0); }}
        100% {{ transform: translateX(-100%); }}
    }}

    .sep {{
        color: #f1c40f; /* 金色の区切り線 */
        margin: 0 25px;
        font-weight: bold;
    }}
</style>

<div class="ticker-container">
    <div class="label">DW BREAKING</div>
    <div class="ticker-content">
        <div class="scrolling-text">
            {news_text} <span class="sep">■</span> 
            LATEST GLOBAL UPDATES FROM DW NEWS <span class="sep">■</span>
            GENKAI AI MONITORING SYSTEM ACTIVE <span class="sep">■</span>
        </div>
    </div>
</div>
"""

# 表示
components.html(ticker_html, height=45)
