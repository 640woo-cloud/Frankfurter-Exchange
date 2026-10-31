import os

import requests
import streamlit as st
from dotenv import load_dotenv

from currency_parser import CURRENCY_NAMES_KO, parse_query

load_dotenv()


def get_config(key: str, default: str = "") -> str:
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception: 
        pass
    return os.getenv(key, default)


API_BASE = get_config("FRANKFURTER_API_URL", "https://api.frankfurter.dev/v1")
API_KEY = get_config("FRANKFURTER_API_KEY")   


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_rate(base: str, target: str) -> dict:
    headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
    resp = requests.get(
        f"{API_BASE}/latest",
        params={"base": base, "symbols": target},
        headers=headers,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def fmt(value: float) -> str:
    return f"{value:,.2f}".rstrip("0").rstrip(".")


def answer(question: str) -> str:
    q = parse_query(question)
    if q is None:
        return (
            "어떤 통화인지 알아듣지 못했어요. 😅\n\n"
            "예: `100달러는 원화로 얼마야?`, `5만원은 엔화로?`, `1유로 환율`"
        )
    if q.base == q.target:
        return "기준 통화와 대상 통화가 같아요. 다른 통화로 물어봐 주세요."

    try:
        data = fetch_rate(q.base, q.target)
    except requests.RequestException as e:
        return f"환율 정보를 가져오지 못했어요: `{e}`"

    rate = data["rates"][q.target]
    result = q.amount * rate
    base_ko = CURRENCY_NAMES_KO.get(q.base, q.base)
    target_ko = CURRENCY_NAMES_KO.get(q.target, q.target)

    return (
        f"{fmt(q.amount)}{base_ko}({q.base})는 **{fmt(result)}{target_ko}({q.target})** 입니다.\n\n"
        f"- **기준 통화:** {q.base}\n"
        f"- **대상 통화:** {q.target}\n"
        f"- **1 {q.base} 환율:** {fmt(rate)} {q.target}\n"
        f"- **환산 금액:** {fmt(q.amount)} {q.base} = {fmt(result)} {q.target}\n"
        f"- **환율 기준일:** {data['date']}\n\n"
        "참고로 Frankfurter 환율은 실시간 체결가가 아니라 **최신 일별 기준 환율**입니다."
    )


st.set_page_config(page_title="실시간 환율 챗봇", page_icon="💱")

st.markdown(
    """
    <style>
    .block-container { max-width: 820px; }
    h1 { font-weight: 800; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💱 실시간 환율 챗봇")
st.caption(
    "질문할 때마다 Frankfurter의 최신 일별 기준 환율을 조회합니다. 실시간 금융시장 체결가는 아닙니다."
)
st.info("**예시:** `100달러는 원화로 얼마야?`, `1유로는 엔화로 얼마야?`, `5만원은 달러로?`")

with st.sidebar:
    st.header("지원 통화")
    for code, name in CURRENCY_NAMES_KO.items():
        st.write(f"`{code}` {name}")
    if st.button("대화 지우기", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("환율이나 환산할 금액을 자연어로 질문해 보세요."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("환율 조회 중..."):
            reply = answer(prompt)
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
