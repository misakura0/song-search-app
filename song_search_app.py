import streamlit as st
st.set_page_config(
    page_title="刀ミュ曲名・歌唱者検索",
    page_icon="⚔️",
    layout="wide",
)

import pandas as pd
import random

# ===============================
# GoogleスプレッドシートCSV URL
# ===============================
SPREADSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/17PoDP9PwRxogzLAP281mMOUv05y5o9EHXZ56lf3C6Zk/export?format=csv"

# ===============================
# CSS（表の右上ボタン非表示）
# ===============================
st.markdown("""
<style>
.stDataFrame div[data-testid="stMarkdownContainer"] button {
    display: none !important;
}
.stMultiSelect [data-baseweb="tag"] {
    background-color:#e2e3e5!important;
    color: black !important;
}
.stMultiSelect [data-baseweb="tag"] svg {
    fill: black !important;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# タイトル・説明
# ===============================
st.title("⚔️刀ミュ　セトリ・曲名・歌唱者・公演検索")
st.markdown(
    "ミュージカル刀剣乱舞の本公演・祭りなどで**歌われた曲**、"
    "**歌唱者**、**何で見れるか**を簡単に調べられるサイトです。"
)
st.markdown(
    "１部曲追加中！！"
)


with st.expander("【使い方】"):
    st.markdown("・曲名や刀剣男士名を入力して検索できます（部分一致OK）")
    st.markdown("・複数結果が出た場合、表の番号を選ぶと詳細が表示されます")
with st.expander("【**セトリ対応済み公演**】を表示"): st.markdown("トライアル公演、阿津賀志山異聞、幕末天狼傳、in厳島神社、真剣乱舞祭2016、三百年の子守唄、加州清光単騎2017、つわものどもがゆめのあと、真剣乱舞祭2017、結びの音始まりの音、阿津賀志山異聞2018巴里、真剣乱舞祭2018、三百年の子守唄2019、髭切膝丸双騎出陣2019、葵咲本紀、歌合乱舞狂乱2019、静かの海のパライソ、髭切膝丸双騎出陣2020、幕末天狼傳2020、五周年記念壽乱舞音曲祭、東京心覚、江水散花雪、真剣乱舞祭2022、鶴丸国永大倶利伽羅双騎出陣、江おんすていじ新編里見八犬伝、花かげゆれる砥水、㊇乱舞野外祭、江おんすていじぜっぷつあー、陸奥一蓮、参騎出陣、祝玖寿乱舞音曲祭、坂龍飛騰、江 おん すていじぜっぷつあーりぶうと、目出度歌誉花舞十周年祝賀祭、江おんすていじかうんとだうんぱーてぃー、静かなる夜半の寝ざめ、髭切 単騎出陣 〜夢幻泡影〜 、加州清光 単騎出陣 極")


# ===============================
# データ読み込み（キャッシュ）
# ===============================
@st.cache_data
def load_data():
    return pd.read_csv(SPREADSHEET_CSV_URL)

df = load_data()

if st.button("🔄 データを再読み込み"):
    st.cache_data.clear()
    df = load_data()

# ===============================
# 人数列（歌唱者人数）
# ===============================
df["人数"] = df["歌唱者"].fillna("").apply(lambda x: len(x.split("、")))

# ===============================
# 検索フォーム
# ===============================
title_query = st.text_input("🔍 曲名で検索（部分一致可）")
singer_query = st.text_input("🎤 歌唱者で検索（部分一致・複数名対応）")

def keyword_match(text, keywords):
    if pd.isna(text):
        return False
    text = str(text).lower()
    return all(kw in text for kw in keywords)

keywords_title = [k.strip().lower() for k in title_query.split()] if title_query else []
keywords_singer = [k.strip().lower() for k in singer_query.split()] if singer_query else []

def row_matches(row):
    return (
        (keyword_match(row["曲名"], keywords_title) if keywords_title else True)
        and
        (keyword_match(row["歌唱者"], keywords_singer) if keywords_singer else True)
    )

results = df[df.apply(row_matches, axis=1)]

# ===============================
# 人数フィルター
# ===============================
c1, c2, c3 = st.columns(3)
with c1:
    filter_solo = st.checkbox("ソロ", value=True)
with c2:
    filter_duo = st.checkbox("デュオ", value=True)
with c3:
    filter_multi = st.checkbox("3人以上", value=True)

num_filters = []
if filter_solo:
    num_filters.append(results["人数"] == 1)
if filter_duo:
    num_filters.append(results["人数"] == 2)
if filter_multi:
    num_filters.append(results["人数"] >= 3)

if num_filters:
    results = results[pd.concat(num_filters, axis=1).any(axis=1)]

# ===============================
# 公演名で絞り込み
# ===============================
if not results.empty and "公演名" in results.columns:
    stages = results["公演名"].dropna().unique().tolist()
    stage_options = ["すべて"] + stages
    selected_stages = st.multiselect("🎭 公演名で絞り込み", stage_options, default=["すべて"])

    if "すべて" not in selected_stages:
        results = results[results["公演名"].isin(selected_stages)]

# ===============================
# 区分で絞り込み（←今回追加）
# ===============================
if not results.empty and "区分" in results.columns:
    st.markdown("🎼 曲の区分で絞り込み")

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        chk_1 = st.checkbox("1部", value=True)
    with s2:
        chk_2 = st.checkbox("2部", value=True)
    with s3:
        chk_fes = st.checkbox("祭り", value=True)
    with s4:
        chk_other = st.checkbox("その他", value=True)

    section_filters = []
    if chk_1:
        section_filters.append(results["区分"] == "1部")
    if chk_2:
        section_filters.append(results["区分"] == "2部")
    if chk_fes:
        section_filters.append(results["区分"] == "祭り")
    if chk_other:
        section_filters.append(results["区分"] == "その他")

    if section_filters:
        results = results[pd.concat(section_filters, axis=1).any(axis=1)]

# ===============================
# 結果表示
# ===============================
st.write(f"🔎 一致した結果：{len(results)} 件")

if not results.empty:
    expected_cols = ["曲名", "歌唱者", "公演名", "区分", "見られるところ", "備考"]
    cols = [c for c in expected_cols if c in results.columns]

    st.dataframe(results[cols])

    selected_index = st.selectbox(
        "表から詳細を見たい曲を選んでね",
        results.index.tolist()
    )
    row = results.loc[selected_index]

    st.markdown("### 🎶 詳細情報")
    st.markdown(f"**曲名**：{row['曲名']}")
    st.markdown(f"**歌唱者**：{row['歌唱者']}")
    st.markdown(f"**公演名**：{row['公演名']}")
    st.markdown(f"**区分**：{row['区分']}")
    st.markdown(f"**見られるところ**：{row['見られるところ']}")
    st.markdown(f"**備考**：{row['備考']}")

    if st.button("🎲 ランダムに1曲表示"):
        r = results.sample(1).iloc[0]
        st.markdown("### 🎯 ランダム表示")
        for c in cols:
            st.write(f"**{c}**：{r[c]}")

else:
    st.info("一致するデータが見つかりませんでした。")

# ===============================
# フィードバック
# ===============================
st.markdown("---")
st.markdown("ミス報告・感想はこちら👇")
st.markdown("[フィードバックフォーム](https://forms.gle/Cmpnr2iH8k1eK9kM9)")
