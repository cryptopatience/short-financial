# 📊 MAG 7+2 종합 분석 대시보드

Magnificent Seven + Bitcoin Exposure 종목에 대한 실시간 기술적 분석 및 공매도 분석 Streamlit 대시보드

## 🌟 주요 기능

### 1. **종합 대시보드**
- 9개 종목 (MAG 7 + COIN + IBIT) 실시간 순위
- 기술적 점수 + 공매도 점수 = 종합 투자 점수
- 주요 지표 한눈에 확인

### 2. **기술적 분석 (Anchored VWAP)**
- 분기별 VWAP 기준 분석
- VWAP 대비 가격 위치
- 시가총액 vs 분기 수익률 분석

### 3. **공매도 분석**
- Yahoo Finance: 공매도 잔고 데이터
- FINRA: 일별 공매도 거래량 데이터
- 두 지표 비교 분석

### 4. **시계열 분석**
- 최근 60일 공매도 추세
- 변동성 분석 (Box Plot)
- 종목별 추세 비교

### 5. **상세 데이터**
- 전체 데이터 테이블
- CSV 다운로드 기능
- 데이터 출처 정보

## 📦 분석 대상 종목

### Magnificent Seven
- **AAPL** - Apple Inc.
- **MSFT** - Microsoft Corporation
- **GOOGL** - Alphabet Inc.
- **AMZN** - Amazon.com Inc.
- **NVDA** - NVIDIA Corporation
- **META** - Meta Platforms Inc.
- **TSLA** - Tesla Inc.

### Bitcoin Exposure
- **COIN** - Coinbase Global Inc. (암호화폐 거래소)
- **IBIT** - iShares Bitcoin Trust ETF (BTC 현물 ETF)

## 🚀 빠른 시작

### 로컬 실행

1. **저장소 클론**
```bash
git clone <your-repo-url>
cd streamlit_app
```

2. **가상환경 생성 및 활성화**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **패키지 설치**
```bash
pip install -r requirements.txt
```

4. **비밀번호 설정**
`.streamlit/secrets.toml` 파일을 편집하여 사용자 계정 설정:
```toml
[passwords]
admin = "your_password"
user1 = "password123"
```

5. **앱 실행**
```bash
streamlit run app.py
```

6. **브라우저에서 접속**
```
http://localhost:8501
```

## 🌐 Streamlit Cloud 배포

자세한 배포 방법은 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)를 참조하세요.

### 간단 요약
1. GitHub에 코드 푸시
2. [Streamlit Cloud](https://streamlit.io/cloud) 접속
3. "New app" 클릭
4. 저장소 연결
5. Secrets 설정 (passwords)
6. Deploy!

## 🔐 로그인 시스템

- 다중 사용자 지원
- 세션 기반 인증
- `secrets.toml`에서 계정 관리
- 로그아웃 기능

### 기본 계정 (변경 필수!)
```
ID: admin
PW: your_secure_password_here
```

## 📊 데이터 소스

- **주가 데이터**: Yahoo Finance API (`yfinance`)
- **공매도 잔고**: Yahoo Finance
- **공매도 거래량**: FINRA Daily Short Volume
- **업데이트 주기**: 1시간 캐싱

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **Data**: pandas, numpy
- **Visualization**: Plotly
- **Market Data**: yfinance
- **Short Data**: FINRA API

## 📁 프로젝트 구조

```
streamlit_app/
├── app.py                      # 메인 애플리케이션
├── requirements.txt            # Python 패키지
├── .streamlit/
│   └── secrets.toml           # 비밀번호 설정 (Git 제외)
├── .gitignore                 # Git 무시 파일
├── README.md                  # 이 파일
├── DEPLOYMENT_GUIDE.md        # 배포 가이드
└── CHANGES.md                 # 변경 사항
```

## 💡 사용 팁

### 데이터 새로고침
- 사이드바의 "🔄 데이터 새로고침" 버튼 클릭
- 캐시를 지우고 최신 데이터 로드

### 종목 선택
- 사이드바에서 원하는 종목만 선택 가능
- 비교 분석 시 유용

### CSV 다운로드
- "상세 데이터" 탭에서 전체 데이터 다운로드
- Excel에서 추가 분석 가능

## 🔧 커스터마이징

### 종목 추가
`app.py`의 `MAG7_STOCKS` 딕셔너리에 추가:
```python
'NEW': {
    'name': 'Company Name',
    'description': '설명',
    'sector': 'Sector',
    'industry': 'Industry'
}
```

### 점수 계산 로직 변경
`calculate_buy_score()` 및 `calculate_short_score()` 함수 수정

### 테마 변경
`.streamlit/config.toml` 파일 생성:
```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
```

## ⚠️ 주의사항

1. **secrets.toml은 절대 Git에 커밋하지 마세요!**
2. 프로덕션에서는 강력한 비밀번호 사용
3. API 요청 제한 주의 (yfinance, FINRA)
4. 캐시 TTL은 1시간 (필요시 조정)

## 📝 라이선스

MIT License

## 🤝 기여

Pull Request 환영합니다!

## 📧 문의

이슈 등록 또는 이메일로 연락주세요.

---

**Made with ❤️ using Streamlit**
