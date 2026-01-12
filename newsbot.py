
import streamlit as st
import streamlit.components.v1 as components
import scrapetube
import time
from datetime import datetime

st.set_page_config(layout="wide")

# ========== デバッグ情報（必ず表示） ==========
st.markdown("## 🔍 DEBUG INFO")
st.write("**1. 初期化チェック**")
st.write(f"- news_history: {len(st.session_state.get('news_history', []))}件")
st.write(f"- last_update: {getattr(st.session_state, 'last_update', 0)}")

# 強制更新テストボタン
if st.button("🔄 強制更新実行"):
    st.session_state.news_history = []
    st.session_state.last_update = 0
    st.rerun()

def fetch_latest_titles():
    st.markdown("### 📺 fetch_latest_titles実行中...")
    try:
        st.write("scrapetube実行...")
        videos = scrapetube.get_channel("UCknLrEdhRCp1aegoMqRaCZg", limit=5, content_type="videos")
        video_list = list(videos)[:5]
        st.write(f"✅ 動画取得: {len(video_list)}件")
        
        news_items = []
        for i, video in enumerate(video_list):
            title = video.get('title', 'NO TITLE').strip().replace('\n', ' ')
            news_item = title[:80].upper()
            news_items.append(news_item)
            st.write(f"  {i+1}: {news_item}")
        
        st.success("✅ fetch_latest_titles完了")
        return news_items
    except Exception as e:
        st.error(f"❌ fetch_latest_titlesエラー: {str(e)}")
        return ["DW NEWS ERROR"]

def get_combined_news_briefs():
    st.markdown("### ⚙️ get_combined_news_briefs実行中...")
    
    if "news_history" not in st.session_state:
        st.session_state.news_history = []
    if "last_update" not in st.session_state:
        st.session_state.last_update = 0
        
    now = time.time()
    should_update = now - st.session_state.last_update > 60 or not st.session_state.news_history  # 1分ごと
    
    st.write(f"- now: {now:.0f}, last_update: {st.session_state.last_update:.0f}")
    st.write(f"- should_update: {should_update}")
    
    if should_update:
        st.session_state.news_history = fetch_latest_titles()
        st.session_state.last_update = now
        st.write("✅ ニュース更新完了")
    
    news_text = "  ■  ".join(st.session_state.news_history[-5:])
    st.write(f"**最終ニューステキスト**: `{news_text[:100]}...`")
    return news_text

# メイン実行
st.markdown("---")
news_text = get_combined_news_briefs()
last_update = datetime.fromtimestamp(getattr(st.session_state, 'last_update', 0)).strftime("%H:%M") if st.session_state.get('last_update') else "NEVER"

# シンプルティッカー（日時短縮・高速スクロール）
ticker_html = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@700&display=swap');
body {{ margin: 0; background: transparent; overflow: hidden; }}
.ticker-container {{
    width: 100%; background: #2c3e50; color: #ecf0f1; height: 38px;
    display: flex; align-items: center; font-family: 'Roboto+Condensed', sans-serif;
}}
.label {{ 
    background: #7f8c8d; padding: 0 12px; height: 100%; display: flex;
    align-items: center; font-size: 12px; font-weight: bold; min-width: 110px;
}}
.ticker-content {{ flex: 1; overflow: hidden; white-space: nowrap; padding-right: 10px; }}
.scrolling-text {{
    display: inline-block; padding-left: 100%; font-size: 13px; letter-spacing: 0.5px;
    animation: scroll-left 35s linear infinite; /* 2倍速 */
}}
@keyframes scroll-left {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-100%); }} }}
</style>
<div class="ticker-container">
    <div class="label">DW NEWS<br><span style='font-size:10px'>{last_update}</span></div>
    <div class="ticker-content">
        <div class="scrolling-text">{news_text} | ONLINE</div>
    </div>
</div>
"""
components.html(ticker_html, height=38)

st.markdown("---")
st.caption("🔘 強制更新ボタン押して「最終ニューステキスト」に内容確認")
