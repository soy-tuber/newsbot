import streamlit as st
import streamlit.components.v1 as components
from youtube_transcript_api import YouTubeTranscriptApi
import scrapetube
from llama_index.llms.gemini import Gemini

# Streamlitの基本設定
st.set_page_config(layout="wide")
# Gemini APIキーを環境変数から取得
import os

# Geminiの設定 (環境変数から取得)
# 英語で要約するように指示
llm = Gemini(model="models/gemini-2.5-flash", api_key=os.environ["GEMINI_API_KEY"])

def get_latest_dw_summary():
    # scrapetubeはチャンネルID指定だが、@dwnewsのIDはUCknLrEdhRCp1aegoMqRaCZg
    # 今後他のチャンネルにも拡張可能
    videos = scrapetube.get_channel("UCknLrEdhRCp1aegoMqRaCZg", limit=1)
    video = next(videos)
    video_id = video['videoId']
    video_url = f"https://youtu.be/{video_id}"

    try:
        # 2. 字幕の取得
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([i['text'] for i in transcript_list])

        # 3. LlamaIndex (Gemini) で英語1行要約
        prompt = (
            f"Analyze the following transcript from DW News and provide a detailed, professional news ticker summary in English. "
            f"Focus on key facts: Who, What, Where, and the Significance. "
            f"The summary must be a single continuous line, around 40-60 words, suitable for a breaking news crawler: {transcript_text[:10000]}"
        )
        summary = llm.complete(prompt).text
    except Exception as e:
        summary = "Live: Checking latest updates from DW News..."

    return summary.strip()

# ニュース内容の取得
news_text = get_latest_dw_summary()

# --- ニュースティッカー用HTML/CSS ---

# --- ニュースティッカー用HTML/CSS (トーン抑えめ) ---
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
        box-shadow: 3px 0 10px rgba(0,0,0,0.3); /* 柔らかい影 */
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
        font-size: 15px; /* 小さめの文字 */
        letter-spacing: 0.5px;
        animation: scroll-left 35s linear infinite; /* 長文に合わせて少し遅く */
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

# Streamlit上でHTMLを表示
components.html(ticker_html, height=60)