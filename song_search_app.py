import streamlit as st
st.set_page_config(
    page_title="刀ミュ曲名・歌唱者検索アプリ",
    page_icon="⚔️",
    layout="wide",
)
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

# ✅ 公演名選択チップの色をカスタマイズ
st.markdown("""
    <style>
    .stMultiSelect [data-baseweb="tag"] {
        background-color:#e2e3e5!important;
        color: black !important;
    }
    .stMultiSelect [data-baseweb="tag"] svg {
        fill: black !important;
    }
    </style>
""", unsafe_allow_html=True)
# ✅ 説明文
st.title("⚔️ミュージカル刀剣乱舞　曲名・歌唱者・公演検索")
st.markdown("ミュージカル刀剣乱舞の本公演などの2部とお祭り公演で**歌われた曲**、**歌唱者**、**何で見れるか**を簡単に調べられるサイトです。")
st.markdown("例①加州は悲劇誰と歌ったことあるっけ？⇒曲名　美しい悲劇、歌唱者　加州で検索")
st.markdown("  ②鶴丸と豊前が一緒に歌った曲あるかな？円盤出さないと見れないっけ？⇒歌唱者　鶴丸 豊前で検索　など")
with st.expander("【**セトリ対応済み公演**】を表示"):
    st.markdown("トライアル公演、阿津賀志山異聞、幕末天狼傳、in厳島神社、真剣乱舞祭2016、三百年の子守唄、加州清光単騎2017、つわものどもがゆめのあと、真剣乱舞祭2017、結びの音始まりの音、阿津賀志山異聞2018巴里、真剣乱舞祭2018、三百年の子守唄2019、髭切膝丸双騎出陣2019、葵咲本紀、歌合乱舞狂乱2019、静かの海のパライソ、髭切膝丸双騎出陣2020、幕末天狼傳2020、五周年記念壽乱舞音曲祭、東京心覚、江水散花雪、真剣乱舞祭2022、鶴丸国永大倶利伽羅双騎出陣、江おんすていじ新編里見八犬伝、花かげゆれる砥水、㊇乱舞野外祭、江おんすていじぜっぷつあー、陸奥一蓮、参騎出陣、祝玖寿乱舞音曲祭、坂龍飛騰、江 おん すていじぜっぷつあーりぶうと、目出度歌誉花舞十周年祝賀祭")
st.markdown("検索したい**曲名**や**刀剣男士の名前**を入力すると、それに一致したものが下の表に表示されます。")
st.markdown("複数結果が出てきた場合は表の左側の番号を選ぶと、詳細情報が表示されるよ。")
st.markdown("一番下にランダム表示のボタンがあるからルーレットや暇つぶしに使ってね〜！")
st.markdown("データを再読み込みのボタンを押すと表が最新状態になります。")

# ✅ データ取得＆キャッシュ
@st.cache_data
def load_data():
    return pd.read_csv(SPREADSHEET_CSV_URL)

df = load_data()

# ✅ 再読み込みボタン
if st.button("🔄 データを再読み込み"):
    st.cache_data.clear()
    df = load_data()

# ✅ 人数列の追加（歌唱者を「、」で分割して数える）
df["人数"] = df["歌唱者"].fillna("").apply(lambda x: len(x.split("、")))

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

def row_matches(row):
    title_match = keyword_match(row["曲名"], keywords_title) if keywords_title else True
    singer_match = keyword_match(row["歌唱者"], keywords_singer) if keywords_singer else True
    return title_match and singer_match

results = df[df.apply(row_matches, axis=1)]

# ✅ 人数での絞り込みチェックボックス（横並び）
col1, col2, col3 = st.columns(3)
with col1:
    filter_solo = st.checkbox("ソロ", value=True)
with col2:
    filter_duo = st.checkbox("デュオ", value=True)
with col3:
    filter_multi = st.checkbox("3人以上", value=True)

# ✅ 人数フィルターを適用
filters = []
if filter_solo:
    filters.append(results["人数"] == 1)
if filter_duo:
    filters.append(results["人数"] == 2)
if filter_multi:
    filters.append(results["人数"] >= 3)

if filters:
    results = results[pd.concat(filters, axis=1).any(axis=1)]

# ✅ 公演名で絞り込み（複数選択＆「すべて」対応）
if not results.empty and "公演名" in results.columns:
    unique_stages = results["公演名"].dropna().drop_duplicates().tolist()
    stage_options = ["すべて"] + unique_stages
    selected_stages = st.multiselect(" 公演名で絞り込み", stage_options, default=["すべて"])

    if "すべて" not in selected_stages:
        results = results[results["公演名"].isin(selected_stages)]

# ✅ 表の表示
st.write(f"🔎 一致した結果：{len(results)}件")

if not results.empty:
    expected_cols = ["曲名", "歌唱者", "公演名", "見られるところ", "備考"]
    existing_cols = [col for col in expected_cols if col in results.columns]

    st.dataframe(results[existing_cols])

    selected_index = st.selectbox("表から詳細を見たい物の番号を選んでね", results.index.tolist())
    selected_row = results.loc[selected_index]

    st.markdown("### 🎶 詳細情報")
    st.markdown(f"**曲名**: {selected_row['曲名']}")
    st.markdown(f"**歌唱者**: {selected_row['歌唱者']}")
    st.markdown(f"**公演名**: {selected_row['公演名']}")
    st.markdown(f"**見られるところ**: {selected_row['見られるところ']}")
    st.markdown(f"**備考**: {selected_row['備考']}")

    if st.button("🎲 ランダムに1件表示する"):
        random_row = results.sample(1).iloc[0]
        st.markdown("### 🎯 ランダム表示結果")
        for col in expected_cols:
            if col in random_row:
                st.write(f"**{col}**: {random_row[col]}")
else:
    st.info("一致するデータが見つかりませんでした。")

# ✅ フィードバック
st.markdown("---")
st.markdown("⇓⇓⇓ミスを見つけた方や感想のある方は、よかったらこのフォームまでお願いします。")
st.markdown("[フィードバックフォームはこちら](https://forms.gle/Cmpnr2iH8k1eK9kM9)")
