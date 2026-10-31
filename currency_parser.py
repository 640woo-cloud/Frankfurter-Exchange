"""자연어 질문에서 금액과 통화를 추출하는 규칙 기반 파서."""
import re
from dataclasses import dataclass

# 긴 키워드가 먼저 매칭되도록 정렬해서 사용한다 (예: "홍콩달러"가 "달러"보다 먼저).
CURRENCY_ALIASES = {
    "USD": ["미국달러", "미국 달러", "달러화", "달러", "불", "usd"],
    "KRW": ["한국원", "원화", "원", "krw"],
    "JPY": ["일본엔", "엔화", "엔", "jpy"],
    "EUR": ["유로화", "유로", "eur"],
    "CNY": ["위안화", "위안", "인민폐", "cny"],
    "GBP": ["영국파운드", "파운드", "gbp"],
    "HKD": ["홍콩달러", "hkd"],
    "AUD": ["호주달러", "aud"],
    "CAD": ["캐나다달러", "cad"],
    "CHF": ["스위스프랑", "프랑", "chf"],
    "SGD": ["싱가포르달러", "sgd"],
    "THB": ["태국바트", "바트", "thb"],
    "INR": ["인도루피", "루피", "inr"],
}

CURRENCY_NAMES_KO = {
    "USD": "달러", "KRW": "원", "JPY": "엔", "EUR": "유로", "CNY": "위안",
    "GBP": "파운드", "HKD": "홍콩달러", "AUD": "호주달러", "CAD": "캐나다달러",
    "CHF": "스위스프랑", "SGD": "싱가포르달러", "THB": "바트", "INR": "루피",
}

_alias_to_code = {
    alias: code for code, aliases in CURRENCY_ALIASES.items() for alias in aliases
}
_currency_re = re.compile(
    "|".join(re.escape(a) for a in sorted(_alias_to_code, key=len, reverse=True)),
    re.IGNORECASE,
)
_amount_re = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s*(억|만|천)?")
_UNIT = {"억": 100_000_000, "만": 10_000, "천": 1_000}


@dataclass
class Query:
    amount: float
    base: str
    target: str


def parse_query(text: str) -> Query | None:
    """'100달러는 원화로 얼마야?' -> Query(100, 'USD', 'KRW').

    처음 등장한 통화를 기준 통화, 두 번째를 대상 통화로 본다.
    통화가 하나뿐이면 원화(KRW)로 환산하고, 원화만 있으면 달러로 환산한다.
    """
    codes = []
    for m in _currency_re.finditer(text):
        code = _alias_to_code[m.group(0).lower()]
        if code not in codes:
            codes.append(code)
    if not codes:
        return None

    amount = 1.0
    m = _amount_re.search(text)
    if m:
        amount = float(m.group(1).replace(",", ""))
        if m.group(2):
            amount *= _UNIT[m.group(2)]

    base = codes[0]
    if len(codes) >= 2:
        target = codes[1]
    else:
        target = "USD" if base == "KRW" else "KRW"
    return Query(amount=amount, base=base, target=target)
