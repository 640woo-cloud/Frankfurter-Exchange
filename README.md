# 💱 Frankfurter-Exchange · 실시간 환율 챗봇

[Frankfurter Exchange Rates API](https://frankfurter.dev/)와 Streamlit으로 만든 환율 조회 웹앱입니다.
"100달러는 원화로 얼마야?"처럼 자연어로 질문하면 최신 일별 기준 환율로 환산해 줍니다.

## 실행 방법

```bash
python -m venv .venv
.venv\Scripts\activate        # Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
copy .env.example .env        # Git Bash: cp .env.example .env
streamlit run app.py
```

## API Key 관리

- Frankfurter API는 **API 키가 필요 없습니다.**
- 그래도 설정값(API URL, 키)은 코드에 하드코딩하지 않고 `.env`(로컬) 또는 `.streamlit/secrets.toml`(Streamlit Cloud 배포)에서 읽도록 구성했습니다.
- `.env`, `secrets.toml`은 `.gitignore`에 포함되어 GitHub에 올라가지 않습니다. 저장소에는 `.env.example`만 올립니다.

## 파일 구성

| 파일 | 설명 |
|---|---|
| `app.py` | Streamlit 챗봇 UI 및 Frankfurter API 호출 |
| `currency_parser.py` | 자연어 질문에서 금액·통화를 추출하는 파서 |
| `requirements.txt` | 패키지 목록 |
| `.env.example` | 환경변수 예시 |
