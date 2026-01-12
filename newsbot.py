import streamlit as st
import streamlit.components.v1 as components
import scrapetube

st.set_page_config(layout="wide")

# デバッグ情報表示
st.title("🔍 DEBUG INFO")
st.write("### 1. scrapetubeテスト")
try:
    videos = list(scrapetube.get_channel("UCknLrEdhRCp1aegoMqRaCZg", limit=3, content_type="videos"))
    st.write(f"✅ 動画取得成功: {len(videos)}件")
    for i, v in enumerate(videos):
        st.write(f"- {i+1}: {v.get('title', 'NO TITLE')[:80]}")
except Exception as e:
    st.error(f"❌ scrapetubeエラー: {str(e)}")

st.write("### 2. ティッカー表示テスト")
test_text = "TEST ■ THIS IS WORKING PERFECTLY ■ STREAMLIT CLOUD OK"
ticker_html = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@700&display=swap');
body {{ margin: 0; background: transparent; overflow: hidden; }}
.ticker-container {{
    width: 100%; background: #2c3e50; color: #ecf0f1; height: 40px;
    display: flex; align-items: center; font-family: 'Roboto+Condensed', sans-serif;
}}
.label {{ background: #7f8c8d; padding: 0 15px; height: 100%; display: flex; align-items: center; font-size: 13px; font-weight: bold; }}
.ticker-content {{ flex: 1; overflow: hidden; white-space: nowrap; }}
.scrolling-text {{ display: inline-block; padding-left: 100%; font-size: 14px; animation: scroll-left 30s linear infinite; }}
@keyframes scroll-left {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-100%); }} }}
</style>
<div class="ticker-container">
    <div class="label">DW NEWS DEBUG</div>
    <div class="ticker-content">
        <div class="scrolling-text">{test_text}</div>
    </div>
</div>
"""
components.html(ticker_html, height=40)

st.success("✅ デバッグ完了！上記結果を教えてください")
