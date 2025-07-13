import streamlit as st
import pandas as pd
import random

# ✅ GoogleスプレッドシートCSV URL
SPREADSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/17PoDP9PwRxogzLAP281mMOUv05y5o9EHXZ56lf3C6Zk/export?format=csv"

# ✅ 表の右上のボタンを非表示にするCSS（←ここがポイント！）
st.markdown("""
    <style>
        .stDataFrame div[data-testid="stMarkdownContainer"] button {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# ✅ Google Analytics タグ（オプション）
st.markdown(
    """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-2BXXKLCT4K"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-2BXXKLCT4K');
    </script>
    """,
    unsafe_allow_html=True
)

# ✅ 説明文（タイトルの下）
st.title("⚔️ミュージカル刀剣乱舞　曲名・歌唱者・公演検索")
st.markdown("ミュージカル刀剣乱舞の2部と祭り公演の曲名、歌唱者、見れるところを簡単に調べられるサイトです。")
st.markdown("検索したい**曲名**や**刀剣男士の名前**を入力すると、それに一致したものが下の表に表示されます。")
st.markdown("例①加州は悲劇誰と歌ったことあるっけ？⇒曲名　美しい悲劇、歌唱者　加州で検索")
st.markdown("  ②鶴丸と豊前が一緒に歌った曲あるかな？⇒歌唱者　鶴丸 豊前で検索　など")
st.markdown("複数結果が出てきた場合は表の左側の番号を選ぶと、詳細情報が表示されます。")
st.markdown("一番下にランダム表示のボタンがあるからルーレットや暇つぶしに使ってね〜！")

# ✅ データ取得＆キャッシュ
@st.cache_data
def load_data():
    return pd.read_csv(SPREADSHEET_CSV_URL)

df = load_data()

# ✅ 再読み込みボタン（キャッシュを消して最新取得）
if st.button("🔄 データを再読み込み"):
    st.cache_data.clear()
    df = load_data()

# ✅ 検索フォーム
title_query = st.text_input("🔍 曲名で検索（部分一致可）")
singer_query = st.text_input("🎤歌唱者で検索（部分一致・複数名対応）")

# ✅ キーワード分解
def keyword_match(text, keywords):
    if pd.isna(text):
        return False
    text = str(text).lower()
    return all(kw in text for kw in keywords)

keywords_title = [kw.strip().lower() for kw in title_query.split()] if title_query else []
keywords_singer = [kw.strip().lower() for kw in singer_query.split()] if singer_query else []

# ✅ 検索処理
def row_matches(row):
    title_match = keyword_match(row["曲名"], keywords_title) if keywords_title else True
    singer_match = keyword_match(row["歌唱者"], keywords_singer) if keywords_singer else True
    return title_match and singer_match

results = df[df.apply(row_matches, axis=1)]

# ✅ 公演名絞り込み
if not results.empty and "公演名" in results.columns:
    unique_stages = sorted(results["公演名"].dropna().unique().tolist())
    selected_stage = st.selectbox(" 公演名で絞り込み", ["すべて"] + unique_stages)
    if selected_stage != "すべて":
        results = results[results["公演名"] == selected_stage]

# ✅ 結果表示
st.write(f"🔎 一致した結果：{len(results)}件")

if not results.empty:
    expected_cols = ["曲名", "歌唱者", "公演名", "見られるところ", "備考"]
    existing_cols = [col for col in expected_cols if col in results.columns]

    # ✅ 表表示（右上のダウンロードボタンは非表示！）
    st.dataframe(results[existing_cols])

    # ✅ 詳細表示：行番号で選択
    selected_index = st.selectbox("表から詳細を見たい物の番号を選んでね", results.index.tolist())
    selected_row = results.loc[selected_index]

    st.markdown("### 🎶 詳細情報")
    st.markdown(f"**曲名**: {selected_row['曲名']}")
    st.markdown(f"**歌唱者**: {selected_row['歌唱者']}")
    st.markdown(f"**公演名**: {selected_row['公演名']}")
    st.markdown(f"**見られるところ**: {selected_row['見られるところ']}")
    st.markdown(f"**備考**: {selected_row['備考']}")

    # ✅ ランダム表示
    if st.button("🎲 ランダムに1件表示する"):
        random_row = results.sample(1).iloc[0]
        st.markdown("### 🎯 ランダム表示結果")
        for col in expected_cols:
            if col in random_row:
                st.write(f"**{col}**: {random_row[col]}")
else:
    st.info("一致するデータが見つかりませんでした。")

# ✅ フィードバックフォーム
st.markdown("---")
st.markdown("⇓⇓⇓ミスを見つけた方や感想のある方は、よかったらこのフォームまでお願いします。")
st.markdown("[フィードバックフォームはこちら](https://forms.gle/Cmpnr2iH8k1eK9kM9)")
