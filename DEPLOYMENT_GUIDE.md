# 🚀 Streamlit Cloud 배포 가이드

## 목차
1. [사전 준비](#사전-준비)
2. [GitHub 설정](#github-설정)
3. [Streamlit Cloud 배포](#streamlit-cloud-배포)
4. [Secrets 설정](#secrets-설정)
5. [트러블슈팅](#트러블슈팅)

---

## 사전 준비

### 필요한 것들
- ✅ GitHub 계정
- ✅ Streamlit Cloud 계정 (무료)
- ✅ Git 설치 (로컬)

### 계정 생성
1. **GitHub**: https://github.com
2. **Streamlit Cloud**: https://streamlit.io/cloud (GitHub 계정으로 로그인)

---

## GitHub 설정

### 1. 저장소 생성

```bash
# 로컬에서 작업
cd streamlit_app

# Git 초기화
git init

# GitHub에 새 저장소 생성 후 연결
git remote add origin https://github.com/YOUR_USERNAME/mag7-dashboard.git

# 첫 커밋
git add .
git commit -m "Initial commit: MAG 7+2 Dashboard"
git push -u origin main
```

### 2. .gitignore 확인

반드시 `.gitignore`에 다음이 포함되어 있는지 확인:
```
.streamlit/secrets.toml
.env
*.pyc
```

⚠️ **중요**: `secrets.toml`은 절대 Git에 올리지 마세요!

---

## Streamlit Cloud 배포

### 1. Streamlit Cloud 접속

1. https://streamlit.io/cloud 접속
2. GitHub 계정으로 로그인
3. "New app" 버튼 클릭

### 2. 앱 설정

**Repository 설정:**
```
Repository: YOUR_USERNAME/mag7-dashboard
Branch: main
Main file path: app.py
```

**App URL (선택사항):**
```
사용자 정의 URL: mag7-dashboard (또는 원하는 이름)
```

### 3. Advanced Settings (선택사항)

**Python version:**
```
Python 3.11
```

**Secrets:**
아직 설정하지 마세요. 다음 섹션에서 설정합니다.

### 4. Deploy 클릭!

- 초기 배포는 5-10분 소요
- 로그를 보면서 진행 상황 확인

---

## Secrets 설정

### 1. Streamlit Cloud에서 Secrets 추가

배포 완료 후:

1. 앱 대시보드에서 "⚙️ Settings" 클릭
2. "Secrets" 탭 선택
3. 다음 내용 입력:

```toml
[passwords]
admin = "your_secure_password_here"
user1 = "password123"
demo = "demo1234"
```

### 2. 보안 강화 팁

**강력한 비밀번호 생성:**
```python
import secrets
import string

def generate_password(length=16):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for i in range(length))

print(generate_password())
```

**권장 설정:**
```toml
[passwords]
admin = "xK9#mP2$vL5@qR8!"
analyst = "nF4%dH7&wT1^zY3*"
viewer = "bG6!cJ9#sM2@lP5$"
```

### 3. 사용자별 권한 관리 (선택사항)

추후 권한 시스템을 추가하려면:

```toml
[passwords]
admin = "password1"

[roles]
admin = "full_access"
```

---

## 배포 후 확인

### 1. URL 접속

```
https://YOUR_APP_NAME.streamlit.app
```

### 2. 로그인 테스트

- 설정한 ID/PW로 로그인 시도
- 잘못된 비밀번호로 오류 메시지 확인

### 3. 기능 테스트

- ✅ 데이터 로딩
- ✅ 차트 렌더링
- ✅ 종목 선택
- ✅ CSV 다운로드

---

## 업데이트 방법

### 코드 변경 시

```bash
# 로컬에서 수정 후
git add .
git commit -m "Update: 설명"
git push origin main
```

- Streamlit Cloud가 자동으로 감지하고 재배포
- 약 2-3분 소요

### Secrets 변경 시

1. Streamlit Cloud 대시보드
2. Settings → Secrets
3. 내용 수정 후 Save
4. 앱 자동 재시작

---

## 트러블슈팅

### 문제 1: 앱이 시작되지 않음

**증상:**
```
ModuleNotFoundError: No module named 'xxx'
```

**해결:**
1. `requirements.txt` 확인
2. 필요한 패키지 추가
3. Git push

### 문제 2: 로그인 실패

**증상:**
```
StreamlitAPIException: st.secrets has no attribute "passwords"
```

**해결:**
1. Settings → Secrets 확인
2. `[passwords]` 섹션 추가
3. 최소 1개 사용자 추가

### 문제 3: 데이터 로딩 느림

**증상:**
- 페이지 로딩이 매우 느림

**해결:**
1. 캐싱 확인: `@st.cache_data` 사용
2. TTL 조정: `ttl=3600` (1시간)
3. 불필요한 API 호출 제거

### 문제 4: FINRA 데이터 없음

**증상:**
```
FINRA 데이터: N/A
```

**해결:**
- 정상 (FINRA는 가끔 접속 불가)
- Yahoo Finance 데이터만으로도 분석 가능
- 나중에 자동 재시도

### 문제 5: 앱이 자주 멈춤

**증상:**
- "Streamlit is running" 상태에서 멈춤

**해결:**
1. 무료 플랜 리소스 제한 확인
2. 데이터 크기 줄이기
3. 캐싱 최적화

---

## 무료 플랜 제한사항

### Streamlit Cloud 무료 플랜
- ✅ 공개 앱 무제한
- ✅ 1개 프라이빗 앱
- ⚠️ 1GB 메모리
- ⚠️ 1 CPU
- ⚠️ 휴면 시간 (7일 미사용 시)

### 리소스 최적화 팁
1. 캐싱 적극 활용
2. 대용량 데이터 로드 최소화
3. 차트 수 제한
4. 불필요한 API 호출 제거

---

## 도메인 연결 (선택사항)

### 커스텀 도메인 사용

1. 도메인 구매 (예: GoDaddy, Namecheap)
2. Streamlit Cloud Pro 구독 필요
3. CNAME 레코드 설정:
```
CNAME   dashboard   your-app.streamlit.app
```

### 무료 대안
- Streamlit 제공 URL 사용: `https://app-name.streamlit.app`
- URL 단축 서비스: bit.ly, tinyurl

---

## 모니터링

### 앱 상태 확인

**Streamlit Cloud 대시보드:**
- ✅ 앱 실행 상태
- ✅ 리소스 사용량
- ✅ 에러 로그
- ✅ 방문자 수 (Pro)

### 로그 확인

```
Settings → Logs
```

- 실시간 로그 스트리밍
- 에러 추적
- 디버깅

---

## 보안 체크리스트

배포 전 확인:

- [ ] secrets.toml이 .gitignore에 포함
- [ ] Git 히스토리에 비밀번호 없음
- [ ] 강력한 비밀번호 사용
- [ ] 프로덕션 환경에서 테스트 계정 제거
- [ ] API 키 노출 여부 확인

---

## 다음 단계

### 고급 기능 추가
1. **사용자 권한 시스템**
   - 읽기 전용 / 전체 권한 구분
   
2. **알림 기능**
   - 목표가 도달 시 알림
   - 이메일/Slack 연동

3. **백테스팅**
   - 과거 신호 검증
   - 수익률 시뮬레이션

4. **자동 리포트**
   - 주간/월간 리포트 생성
   - PDF 다운로드

---

## 참고 자료

- [Streamlit 공식 문서](https://docs.streamlit.io)
- [Streamlit Cloud 문서](https://docs.streamlit.io/streamlit-community-cloud)
- [Plotly 문서](https://plotly.com/python/)
- [yfinance 문서](https://github.com/ranaroussi/yfinance)

---

## 도움이 필요하신가요?

- 📧 이슈 등록: GitHub Issues
- 💬 커뮤니티: [Streamlit Forum](https://discuss.streamlit.io)
- 📖 문서: 이 가이드의 "트러블슈팅" 섹션

---

**배포 성공을 기원합니다! 🚀**
