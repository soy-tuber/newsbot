import streamlit as st
import streamlit.components.v1 as components
from youtube_transcript_api import YouTubeTranscriptApi
import scrapetube
from llama_index.llms.google_genai import GoogleGenAI

st.set_page_config(layout="wide")

# ========== デバッグ用ステップ表示 ==========
st.write("🔍 STEP 1: app start")

api_key = st.secrets.get("GEMINI_API_KEY")
st.write("🔍 STEP 2: got api_key:", bool(api_key))
if not api_key:
    st.error("❌ GEMINI_API_KEY not found.")
    st.stop()

st.write("🔍 STEP 3: before get_combined_news_briefs")

# 15分間キャッシュして高速化（デバッグ中は一旦外す）
@st.cache_data(ttl=900)
def get_combined_news_briefs():
    try:
        st.write("🔍 STEP 3.1: scrapetube getting videos...")
        videos = scrapetube.get_channel("UCknLrEdhRCp1aegoMqRaCZg", limit=6, content_type="videos")
        videos_list = list(videos)
        st.write(f"🔍 STEP 3.2: got {len(videos_list)} videos")
        
        all_summaries = []
        for i, video in enumerate(videos_list):
            if len(all_summaries) >= 3:
                break
            video_id = video['videoId']
            st.write(f"🔍 STEP 3.3: trying video {i+1}: {video_id}")
            
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                st.write(f"🔍 STEP 3.4: transcript OK ({len(transcript_list)} lines)")
                # Gemini呼び出しは一旦スキップ
                all_summaries.append(f"TEST SUMMARY {i+1}")
            except Exception as e:
                st.write(f"🔍 STEP 3.5: transcript failed: {str(e)[:100]}")
                continue

        if not all_summaries:
            return "DW NEWS: NO TRANSCRIPTS FOUND"
        return "  ■  ".join(all_summaries)

    except Exception as e:
        st.write(f"🔍 ERROR in get_combined_news_briefs: {str(e)}")
        return "DW NEWS SERVICE: ERROR OCCURRED"

news_text = get_combined_news_briefs()
st.write("🔍 STEP 4: news_text =", news_text[:200])

st.write("🔍 STEP 5: before components.html")

# シンプルなテストHTML
test_html = """
<style>
.ticker { background: #2c3e50; color: #ecf0f1; padding: 10px; font-family: Arial; }
</style>
<div class="ticker">TEST TICKER: """ + news_text[:100] + """</div>
"""
components.html(test_html, height=50)

st.write("✅ STEP 6: components.html executed")
