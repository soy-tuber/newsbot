import streamlit as st
import streamlit.components.v1 as components
import scrapetube
import time
from datetime import datetime

st.set_page_config(layout="wide")

if "news_history" not in st.session_state:
    st.session_state.news_history = []
if "last_update" not in st.session_state:
    st.session_state.last_update = 0

def fetch_latest_titles():
    try:
        videos = scrapetube.get_channel("UCknLrEdhRCp1aegoMqRaCZg", limit=5, content_type="videos")
        video_list = list(videos)[:5]
        
        news_items = []
        for i, video in enumerate(video_list):
            # タイトルデータの取得
            title_data = video.get('title', {})
            
            # 辞書構造(runs)からテキストのみを抽出
            if isinstance(title_data, dict) and 'runs' in title_data:
                # runs[0]['text'] に実際のタイトル文字列が入っています
                raw_title = title_data['runs'][0].get('text', 'NO TEXT')
            elif isinstance(title_data, dict) and 'RUNS' in title_data:
                # 大文字の場合の予備対応
                raw_title = title_data['RUNS'][0].get('TEXT', 'NO TEXT')
            else:
                raw_title = str(title_data)
            
            # きれいに整形
            news_item = raw_title.strip().replace('\n', ' ').upper()
            news_items.append(news_item)
            # st.write(f"  {i+1}: {news_item}") # 必要ならコメント解除
        
        return news_items
    except Exception as e:
        st.error(f"❌ エラー: {str(e)}")
        return ["DW NEWS: FETCH ERROR"]

def get_combined_news_briefs():
    now = time.time()
    # 1分ごと更新（デバッグ用）
    if now - st.session_state.last_update > 60 or not st.session_state.news_history:
        st.session_state.news_history = fetch_latest_titles()
        st.session_state.last_update = now
    
    return "  ■  ".join(st.session_state.news_history[-5:])

# メイン実行
news_text = get_combined_news_briefs()
last_update = datetime.fromtimestamp(st.session_state.last_update).strftime("%H:%M")

# スマホ最適化ティッカー（高速・ラベル狭小）
ticker_html = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@700&display=swap');
body {{ margin: 0; background: transparent; overflow: hidden; }}
.ticker-container {{
    width: 100%; background: #2c3e50; color: #ecf0f1; height: 36px;
    display: flex; align-items: center; font-family: 'Roboto+Condensed', sans-serif;
}}
.label {{ 
    background: #7f8c8d; padding: 0 8px; height: 100%; display: flex;
    align-items: center; font-size: 11px; font-weight: bold; min-width: 85px;
    line-height: 1.1;
}}
.ticker-content {{ flex: 1; overflow: hidden; white-space: nowrap; padding-right: 5px; }}
.scrolling-text {{
    display: inline-block; padding-left: 100%; font-size: 12px; letter-spacing: 0.3px;
    animation: scroll-left 25s linear infinite; /* 超高速 */
}}
@keyframes scroll-left {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-100%); }} }}
</style>
<div class="ticker-container">
    <div class="label">DW {last_update}</div>
    <div class="ticker-content">
        <div class="scrolling-text">{news_text} | ONLINE</div>
    </div>
</div>
"""
components.html(ticker_html, height=36)

# デバッグ情報（小さく）
st.caption(f"ニュース数: {len(st.session_state.news_history)}件 | 更新: {last_update} | テキストプレビュー: {news_text[:60]}...")