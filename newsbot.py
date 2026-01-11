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

def get_latest_dw_summary():
    """
    ライブ配信をスキップし、字幕が取得可能な最新動画から要約を生成する
    """
    try:
        # ライブを除外するために content_type="videos" を指定し、最新5件を取得
        videos = scrapetube.get_channel("UCknLrEdhRCp1aegoMqRaCZg", limit=5, content_type="videos")
        
        summary_text = ""
        
        for video in videos:
            video_id = video['videoId']
            try:
                # 字幕取得を試みる（ライブ中はここでエラーになるため次の動画へ行く）
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                transcript_text = " ".join([i['text'] for i in transcript_list])

                # Geminiで詳細な英語ニュース要約を生成
                prompt = (
                    f"As a professional news editor, summarize this DW News transcript in 50-70 words. "
                    f"Focus on the main event, location, and significance. "
                    f"Use sophisticated English and output only the summary in a single continuous line: "
                    f"{transcript_text[:12000]}"
                )
                
                response = llm.complete(prompt)
                summary_text = str(response.text).strip().replace("\n", " ")
                
                # 正常に取得できたらループを終了
                if summary_text:
                    break
            except:
                # 字幕がない（ライブ中やアップ直後）場合は次の動画へ
                continue

        # 全動画試してもダメだった場合のバックアップ
        if not summary_text:
            summary_text = "WORLD NEWS UPDATE: DW CONTINUES COVERAGE OF EVOLVING GLOBAL EVENTS. STAY TUNED FOR IN-DEPTH ANALYSIS AND BREAKING REPORTS FROM OUR CORRESPONDENTS WORLDWIDE."

    except Exception as e:
        summary_text = "LIVE: DW NEWS SERVICE IS CURRENTLY STREAMING. MONITORING GLOBAL DEVELOPMENTS FOR LATEST SUMMARIES."

    return summary_text.upper() # すべて大文字で報道感を出す

# ニュース内容の取得
news_text = get_latest_dw_summary()

# --- ニュースティッカー用HTML/CSS (指定のトーン) ---
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
        font-size: 13px;
        letter-spacing: 1px;
        z-index: 10;
        font-weight: bold;
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
        animation: scroll-left 45s linear infinite;
    }}

    @keyframes scroll-left {{
        0% {{ transform: translateX(0); }}
        100% {{ transform: translateX(-100%); }}
    }}

    .separator {{
        color: #bdc3c7;
        margin: 0 25px;
        font-weight: bold;
    }}
</style>

<div class="ticker-container">
    <div class="breaking-label">DW NEWS BRIEF</div>
    <div class="ticker-content">
        <div class="scrolling-text">
            {news_text} <span class="separator">|</span> 
            LATEST UPDATES FROM DW NEWS SERVICE <span class="separator">|</span>
            GENKAI AI MONITORING SYSTEM ACTIVE <span class="separator">|</span>
        </div>
    </div>
</div>
"""

# Streamlit上でHTMLを表示（高さは40pxに最適化）
components.html(ticker_html, height=40)
