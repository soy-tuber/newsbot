import streamlit as st
import streamlit.components.v1 as components
from youtube_transcript_api import YouTubeTranscriptApi
import scrapetube
from llama_index.llms.google_genai import GoogleGenAI

# --- Streamlit Basic Config ---
st.set_page_config(layout="wide")

# APIキーの取得
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Error: GEMINI_API_KEY is not set in Streamlit Secrets.")
    st.stop()

# 最新のGoogleGenAIクラスを使用
llm = GoogleGenAI(model="models/gemini-2.5-flash", api_key=api_key)

@st.cache_data(ttl=900)
def get_combined_news_briefs():
    try:
        # 最新の動画を6件スキャンして3件の要約を目指す
        videos = scrapetube.get_channel("UCknLrEdhRCp1aegoMqRaCZg", limit=6, content_type="videos")
        
        all_summaries = []
        
        for video in videos:
            if len(all_summaries) >= 3:
                break
                
            video_id = video['videoId']
            try:
                # 字幕取得
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                transcript_text = " ".join([i['text'] for i in transcript_list])

                # 要約生成
                prompt = (
                    f"Summarize this DW news transcript into one professional sentence (approx 40 words). "
                    f"Focus on key facts and significance: {transcript_text[:8000]}"
                )
                
                response = llm.complete(prompt)
                summary = str(response.text).strip().replace("\n", " ").upper()
                all_summaries.append(summary)
            except:
                continue # 字幕がない（ライブ中など）は飛ばす

        if not all_summaries:
            return "DW NEWS: MONITORING LATEST GLOBAL DEVELOPMENTS. CHECK BACK SHORTLY FOR UPDATES."
        
        return "  ■  ".join(all_summaries)

    except Exception as e:
        return "DW NEWS SERVICE: CURRENTLY UPDATING GLOBAL REPORTS."

# ニュース内容の取得
news_text = get_combined_news_briefs()

# --- ニュースティッカー用HTML/CSS (指定のトーン) ---
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
        box-sizing: border-box;
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
        box-shadow: 3px 0 10px rgba(0,0,0,0.3);
        white-space: nowrap;
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
        font-size: 14px;
        letter-spacing: 0.8px;
        animation: scroll-left 60s linear infinite;
    }}

    @keyframes scroll-left {{
        0% {{ transform: translateX(0); }}
        100% {{ transform: translateX(-100%); }}
    }}

    .sep {{ color: #bdc3c7; margin: 0 30px; font-weight: bold; }}
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

# HTMLを表示
components.html(ticker_html, height=45)
