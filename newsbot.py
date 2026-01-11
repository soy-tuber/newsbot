import streamlit as st
import streamlit.components.v1 as components
from youtube_transcript_api import YouTubeTranscriptApi
import scrapetube
from llama_index.llms.gemini import Gemini

# Streamlitの基本設定
st.set_page_config(layout="wide")

# Geminiの設定 (Streamlit Secretsから取得するように変更)
# 起動時にエラーが出ないよう、try-except または st.secrets.get を推奨
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Please set GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

llm = Gemini(model="models/gemini-2.5-flash", api_key=api_key)

def get_latest_dw_summary():
    try:
        # 1. 動画取得
        videos = scrapetube.get_channel("UCknLrEdhRCp1aegoMqRaCZg", limit=1)
        video = next(videos)
        video_id = video['videoId']
        
        # 2. 字幕の取得
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([i['text'] for i in transcript_list])

        # 3. Geminiで詳細な英語要約
        prompt = (
            f"As a professional news editor, analyze this DW News transcript: {transcript_text[:10000]}. "
            f"Provide a detailed, high-density news ticker summary in English (40-60 words). "
            f"Include the main event, location, and global impact. "
            f"Output only the summary text in a single line."
        )
        summary = llm.complete(prompt).text
    except StopIteration:
        summary = "Error: Could not retrieve latest videos from DW News."
    except Exception as e:
        # 字幕が取得できない動画（ライブ配信中など）の場合のバックアップ
        summary = "Live Update: Breaking news from DW. Coverage continues on the latest global developments."

    return summary.strip()

# ニュース内容の取得
news_text = get_latest_dw_summary()

# --- ニュースティッカー用HTML/CSS (ご提示いただいたPro仕様) ---
ticker_html = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@700&display=swap');
    body {{ margin: 0; background: transparent; overflow: hidden; }}
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
    .breaking-label {{
        background: #7f8c8d;
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
        font-size: 14px; /* さらに少し小さくして密度アップ */
        letter-spacing: 0.5px;
        animation: scroll-left 40s linear infinite; /* 長文用に少しゆっくりに */
    }}
    @keyframes scroll-left {{
        0% {{ transform: translateX(0); }}
        100% {{ transform: translateX(-100%); }}
    }}
    .separator {{ color: #bdc3c7; margin: 0 20px; }}
</style>
<div class="ticker-container">
    <div class="breaking-label">DW NEWS BRIEF</div>
    <div class="ticker-content">
        <div class="scrolling-text">
            {news_text} <span class="separator">|</span> 
            LATEST UPDATES FROM DW NEWS <span class="separator">|</span>
            GENKAI AI AGENT SYSTEM ONLINE
        </div>
    </div>
</div>
"""

components.html(ticker_html, height=40) # 40pxにぴったり合わせる
