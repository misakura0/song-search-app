import streamlit as st
import pandas as pd
import random

# スプレッドシートのCSV URL（すでにあるやつ）
SPREADSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/17PoDP9PwRxogzLAP281mMOUv05y5o9EHXZ56lf3C6Zk/export?format=csv"

# ✅ キャッシュ付きでデータを読み込む関数
@st.cache_data
def load_data():
    return pd.read_csv(SPREADSHEET_CSV_URL)

# ✅ 最新データを取得
df = load_data()

def keyword_match(text, keywords):
    if pd.isna(text):
        return False
    text = str(text).lower()
    return all(kw in text for kw in keywords)

# --- UI ---
st.title("⚔️ミュージカル刀剣乱舞　曲名・歌唱者・公演検索")

# ✅ 再読み込みボタン（押すとキャッシュがクリアされて最新読み込み）
if st.button("🔄 データを再読み込み"):
    st.cache_data.clear()
    
# 入力フォーム
title_query = st.text_input("🔍 曲名で検索（部分一致可）")
singer_query = st.text_input("🎤歌唱者で検索（部分一致・複数名対応）")

# データ読み込み
df = load_data()

# クエリ処理
keywords_title = [kw.strip().lower() for kw in title_query.split()] if title_query else []
keywords_singer = [kw.strip().lower() for kw in singer_query.split()] if singer_query else []

# フィルター処理
def row_matches(row):
    title_match = keyword_match(row["曲名"], keywords_title) if keywords_title else True
    singer_match = keyword_match(row["歌唱者"], keywords_singer) if keywords_singer else True
    return title_match and singer_match

results = df[df.apply(row_matches, axis=1)]

# 🎭 公演名で絞り込みセレクトボックス（重複を除く）
if not results.empty and "公演名" in results.columns:
    unique_stages = sorted(results["公演名"].dropna().unique().tolist())
    selected_stage = st.selectbox(" 公演名で絞り込み", ["すべて"] + unique_stages)

    if selected_stage != "すべて":
        results = results[results["公演名"] == selected_stage]

# 📊 検索結果の表表示
st.write(f"🔎 一致した結果：{len(results)}件")

if not results.empty:
    expected_cols = ["曲名", "歌唱者", "公演名", "見られるところ", "備考"]
    existing_cols = [col for col in expected_cols if col in results.columns]
    st.dataframe(results[existing_cols])

    # 🎵 曲名＋公演名のセットで選択肢を作成（曲名が重複しても識別できるように）
    results["選択キー"] = results["曲名"] + "（" + results["公演名"] + "）"
    selected_key = st.selectbox("🔍 詳細を見たい曲を選んでください", results["選択キー"])

    # 🔍 ハイライト処理を適用
highlighted_results = results.copy()
highlighted_results["曲名"] = highlighted_results["曲名"].apply(lambda x: highlight_keywords(x, keywords_title))
highlighted_results["歌唱者"] = highlighted_results["歌唱者"].apply(lambda x: highlight_keywords(x, keywords_singer))

# 📊 表示を HTML で整形（太字ハイライト付き）
st.markdown(highlighted_results[existing_cols].to_html(escape=False, index=False), unsafe_allow_html=True)
    # 選択された行を抽出して表示
    selected_row = results[results["選択キー"] == selected_key].iloc[0]

    # 📝 詳細表示（マークダウンで整形）
    st.markdown("### 🎶 詳細情報")
    st.markdown(f" 曲名: {selected_row['曲名']}")
    st.markdown(f" 歌唱者: {selected_row['歌唱者']}")
    st.markdown(f" 公演名: {selected_row['公演名']}")
    st.markdown(f" 見られるところ: {selected_row['見られるところ']}")
    st.markdown(f" 備考: {selected_row['備考']}")

# 🎲 ランダムで1件表示
if not results.empty:
    if st.button("🎲 ランダムに1件表示する"):
        random_row = results.sample(1).iloc[0]
        st.markdown("### 🎯 ランダム表示結果")
        for col in ["曲名", "歌唱者", "公演名", "見られるところ", "備考"]:
            if col in random_row:
                st.write(f"**{col}**: {random_row[col]}")
else:
    st.info("一致するデータが見つかりませんでした。")

