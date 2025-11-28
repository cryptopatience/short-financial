# 🔧 트러블슈팅 가이드

## ❌ ModuleNotFoundError: No module named 'yfinance'

### 원인
Streamlit Cloud에서 패키지가 제대로 설치되지 않았습니다.

### 해결 방법

#### 1단계: requirements.txt 확인
다음 내용이 정확히 포함되어 있는지 확인:

```
streamlit>=1.28.0
yfinance>=0.2.28
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.17.0
requests>=2.31.0
```

#### 2단계: GitHub 업데이트

```bash
# requirements.txt 수정 후
git add requirements.txt
git commit -m "Fix: Update requirements.txt"
git push origin main
```

#### 3단계: Streamlit Cloud 재부팅

**방법 A: 자동 재배포**
- GitHub에 푸시하면 자동으로 재배포됨
- 2-3분 대기

**방법 B: 수동 재부팅**
1. Streamlit Cloud 대시보드 접속
2. 앱 선택
3. ⋮ (점 3개) → "Reboot app" 클릭

#### 4단계: 로그 확인

Streamlit Cloud에서:
1. "Manage app" 클릭
2. "Logs" 탭 선택
3. 설치 로그 확인:
```
Successfully installed yfinance-0.2.xx
Successfully installed pandas-2.x.x
...
```

---

## ❌ 기타 일반적인 오류

### 1. ImportError: cannot import name 'xxx'

**원인:** 패키지 버전 충돌

**해결:**
```bash
# requirements.txt에서 버전 범위 조정
yfinance>=0.2.28,<0.3.0
pandas>=2.0.0,<3.0.0
```

### 2. 앱이 로딩 중 멈춤

**원인:** 메모리 부족 또는 API 타임아웃

**해결:**
```python
# app.py에서 캐시 TTL 늘리기
@st.cache_data(ttl=7200)  # 2시간으로 증가
```

### 3. Yahoo Finance 데이터 없음

**원인:** API 요청 제한

**해결:**
- 요청 횟수 줄이기
- 종목 수 제한
- 캐시 활용

---

## 🚀 빠른 수정 체크리스트

- [ ] requirements.txt 최신화
- [ ] GitHub에 푸시
- [ ] Streamlit Cloud 자동 재배포 확인
- [ ] 로그에서 에러 확인
- [ ] 필요시 수동 Reboot

---

## 💡 예방 팁

### 1. 로컬에서 먼저 테스트

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# 앱 실행
streamlit run app.py
```

### 2. 패키지 버전 고정 (선택)

배포 환경에서 안정적으로 작동 확인 후:

```
streamlit==1.31.0
yfinance==0.2.36
pandas==2.2.0
```

### 3. Python 버전 명시

`.streamlit/config.toml`에 추가:
```toml
[server]
pythonVersion = "3.11"
```

---

## 📞 추가 도움

문제가 계속되면:

1. **Streamlit Community Forum**
   - https://discuss.streamlit.io

2. **GitHub Issues**
   - 프로젝트 저장소에 이슈 생성

3. **로그 공유**
   - Streamlit Cloud 로그 복사
   - 에러 메시지 전체 포함

---

**마지막 업데이트:** 2024-11-28
