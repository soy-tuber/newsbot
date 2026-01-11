import streamlit as st
import streamlit.components.v1 as components
from youtube_transcript_api import YouTubeTranscriptApi
import scrapetube
from llama_index.llms.google_genai import GoogleGenAI

# --- Streamlit Config ---
st.set_page_config(layout="wide")

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

llm = GoogleGenAI(model="models/gemini-2.5-flash", api_key=api_key)

# 15分間キャッシュして高速化
@st.cache_data(ttl=900)
def get_combined_news_briefs():
    try:
        # 最新の動画を3件取得（確実に字幕があるものを探すため、少し多めの6件からスキャン）
        videos = scrapetube.get_channel("UCknLrEdhRCp1aegoMqRaCZg", limit=6, content_type="videos")
        
        all_summaries = []
        
        for video in videos:
            if len(all_summaries) >= 3: # 3つ取れたら終了
                break
                
            video_id = video['videoId']
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                transcript_text = " ".join([i['text'] for i in transcript_list])

                # 3つなので、1つあたりの情報を少し詳しく（40語程度）にする
                prompt = (
                    f"Analyze this DW news transcript and provide a professional one-sentence summary (approx 40 words). "
                    f"Include key facts and the significance of the event. Output in English: {transcript_text[:8000]}"
                )
                
                response = llm.complete(prompt)
                summary = str(response.text).strip().replace("\n", " ").upper()
                all_summaries.append(summary)
            except:
                continue # 字幕がない動画（ライブ等）はスキップして次を探す

        if not all_summaries:
            return "DW NEWS: MONITORING LATEST GLOBAL DEVELOPMENTS. CHECK BACK SHORTLY FOR UPDATES."
        
        # 3つのニュースを太めのセパレーターで繋ぐ
        return "  ■  ".join(all_summaries)

    except Exception as e:
        return "DW NEWS SERVICE: CURRENTLY UPDATING GLOBAL REPORTS."

# ニュース内容の取得
news_text = get_combined_news_briefs()

# --- ニュースティッカー用HTML/CSS (トーン抑えめ・3連最適化) ---
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
        animation: scroll-left 60s linear infinite; /* 3件なので60秒で快適に読める */
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

components.html(ticker_html, height=40)
