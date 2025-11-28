#!/bin/bash

echo "🔧 Streamlit Cloud 배포 문제 해결 스크립트"
echo "================================================"

# 1. requirements.txt 확인
echo ""
echo "📋 Step 1: requirements.txt 확인 중..."
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt 파일 존재"
    echo ""
    echo "내용:"
    cat requirements.txt
else
    echo "❌ requirements.txt 파일 없음!"
    echo "파일을 생성합니다..."
    cat > requirements.txt << 'REQEOF'
streamlit>=1.28.0
yfinance>=0.2.28
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.17.0
requests>=2.31.0
REQEOF
    echo "✅ requirements.txt 생성 완료"
fi

# 2. Git 상태 확인
echo ""
echo "📋 Step 2: Git 상태 확인 중..."
git status

# 3. 변경사항 커밋
echo ""
echo "📋 Step 3: 변경사항 커밋 및 푸시"
read -p "변경사항을 커밋하고 푸시하시겠습니까? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git add requirements.txt
    git commit -m "Fix: Update requirements.txt for Streamlit Cloud"
    git push origin main
    echo "✅ 푸시 완료!"
    echo ""
    echo "🎉 Streamlit Cloud에서 자동 재배포가 시작됩니다."
    echo "   2-3분 후 앱을 다시 확인하세요."
else
    echo "⏭️  푸시를 건너뜁니다."
fi

echo ""
echo "================================================"
echo "✨ 완료!"
echo ""
echo "다음 단계:"
echo "1. Streamlit Cloud 대시보드 방문"
echo "2. 앱 로그 확인"
echo "3. 'Successfully installed yfinance...' 메시지 확인"
echo ""
