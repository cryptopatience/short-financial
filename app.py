import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from io import StringIO
import time

warnings.filterwarnings('ignore')

# ==================== 페이지 설정 ====================
st.set_page_config(
    page_title="MAG 7+2 종합 분석 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 로그인 시스템 ====================
def check_password():
    """비밀번호 확인 및 로그인 상태 관리"""
    if st.session_state.get('password_correct', False):
        return True
    
    st.title("🔒 MAG 7+2 퀀트 대시보드 로그인")
    st.markdown("### Magnificent Seven + Bitcoin Exposure 종합 분석")
    
    with st.form("credentials"):
        username = st.text_input("아이디 (ID)", key="username")
        password = st.text_input("비밀번호 (Password)", type="password", key="password")
        submit_btn = st.form_submit_button("로그인", type="primary")
    
    if submit_btn:
        if username in st.secrets["passwords"] and password == st.secrets["passwords"][username]:
            st.session_state['password_correct'] = True
            st.rerun()
        else:
            st.error("😕 아이디 또는 비밀번호가 올바르지 않습니다.")
    
    return False

if not check_password():
    st.stop()

# ==================== 로그아웃 버튼 ====================
with st.sidebar:
    st.success(f"✅ 로그인 성공!")
    if st.button("🚪 로그아웃"):
        st.session_state['password_correct'] = False
        st.rerun()

# ==================== MAG 7+2 정의 ====================
MAG7_STOCKS = {
    'AAPL': {'name': 'Apple Inc.', 'description': '아이폰, 생태계, 온디바이스 AI', 'sector': 'Technology', 'industry': 'Consumer Electronics'},
    'MSFT': {'name': 'Microsoft Corporation', 'description': '클라우드(Azure), 생성형 AI (OpenAI 대주주)', 'sector': 'Technology', 'industry': 'Software'},
    'GOOGL': {'name': 'Alphabet Inc.', 'description': '구글 검색, 유튜브, AI (Gemini)', 'sector': 'Communication Services', 'industry': 'Internet Content & Information'},
    'AMZN': {'name': 'Amazon.com Inc.', 'description': '전자상거래, 클라우드(AWS) 1위', 'sector': 'Consumer Cyclical', 'industry': 'Internet Retail'},
    'NVDA': {'name': 'NVIDIA Corporation', 'description': 'AI 반도체(GPU) 독점적 지배자', 'sector': 'Technology', 'industry': 'Semiconductors'},
    'META': {'name': 'Meta Platforms Inc.', 'description': '페이스북, 인스타그램, AI(Llama)', 'sector': 'Communication Services', 'industry': 'Internet Content & Information'},
    'TSLA': {'name': 'Tesla Inc.', 'description': '전기차, 자율주행, 로봇', 'sector': 'Consumer Cyclical', 'industry': 'Auto Manufacturers'},
    'COIN': {'name': 'Coinbase Global Inc.', 'description': '미국 최대 암호화폐 거래소, 비트코인 직접 노출', 'sector': 'Financial Services', 'industry': 'Cryptocurrency Exchange'},
    'IBIT': {'name': 'iShares Bitcoin Trust ETF', 'description': 'BlackRock 비트코인 현물 ETF, 순수 BTC 노출', 'sector': 'ETF', 'industry': 'Bitcoin Spot ETF'}
}

# ==================== 유틸리티 함수 ====================
@st.cache_data(ttl=3600)
def get_current_quarter_start():
    now = datetime.now()
    quarter = (now.month - 1) // 3
    quarter_start_month = quarter * 3 + 1
    return datetime(now.year, quarter_start_month, 1)

def calculate_anchored_vwap(df):
    df = df.copy()
    df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['TP_Volume'] = df['Typical_Price'] * df['Volume']
    df['Cumulative_TP_Volume'] = df['TP_Volume'].cumsum()
    df['Cumulative_Volume'] = df['Volume'].cumsum()
    df['Anchored_VWAP'] = df['Cumulative_TP_Volume'] / df['Cumulative_Volume']
    return df

@st.cache_data(ttl=3600)
def get_finra_short_volume_csv(ticker, days_back=10):
    try:
        today = datetime.now()
        short_volume_data = []
        
        for days in range(days_back):
            check_date = today - timedelta(days=days)
            if check_date.weekday() >= 5:
                continue
            
            date_str = check_date.strftime('%Y%m%d')
            url = f"https://cdn.finra.org/equity/regsho/daily/CNMSshvol{date_str}.txt"
            
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    df = pd.read_csv(StringIO(response.text), sep='|')
                    df.columns = df.columns.str.strip()
                    symbol_col = 'Symbol' if 'Symbol' in df.columns else 'symbol'
                    ticker_data = df[df[symbol_col].str.upper() == ticker.upper()]
                    
                    if not ticker_data.empty:
                        row = ticker_data.iloc[0]
                        short_vol = row.get('ShortVolume', row.get('shortVolume', 0))
                        total_vol = row.get('TotalVolume', row.get('totalVolume', 0))
                        
                        if pd.notna(short_vol) and pd.notna(total_vol) and total_vol > 0:
                            short_volume_data.append({
                                'date': check_date.strftime('%Y-%m-%d'),
                                'short_volume': int(short_vol),
                                'total_volume': int(total_vol),
                                'short_ratio': round(short_vol / total_vol * 100, 2)
                            })
            except:
                continue
        
        if short_volume_data:
            df_short = pd.DataFrame(short_volume_data)
            return {
                'ticker': ticker,
                'latest_date': df_short.iloc[0]['date'],
                'latest_short_ratio': df_short.iloc[0]['short_ratio'],
                'avg_short_ratio_10d': round(df_short['short_ratio'].mean(), 2),
                'data_points': len(df_short),
                'historical_data': df_short
            }
        return None
    except:
        return None

@st.cache_data(ttl=3600)
def get_short_interest_from_yfinance(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        short_data = {
            'ticker': ticker,
            'short_ratio': info.get('shortRatio', 0),
            'short_percent_float': info.get('shortPercentOfFloat', 0) * 100 if info.get('shortPercentOfFloat') else 0,
            'shares_short': info.get('sharesShort', 0),
            'shares_short_prior_month': info.get('sharesShortPriorMonth', 0),
        }
        
        if short_data['shares_short_prior_month'] > 0:
            short_data['short_change_pct'] = ((short_data['shares_short'] - short_data['shares_short_prior_month']) / 
                                               short_data['shares_short_prior_month'] * 100)
        else:
            short_data['short_change_pct'] = 0
        return short_data
    except:
        return None

def get_comprehensive_short_data(ticker):
    yf_data = get_short_interest_from_yfinance(ticker)
    finra_data = get_finra_short_volume_csv(ticker, days_back=60)
    
    combined_data = {
        'ticker': ticker, 'short_ratio_days': 0, 'short_percent_float': 0,
        'shares_short_millions': 0, 'short_change_pct': 0, 'daily_short_ratio': 0,
        'avg_daily_short_ratio_10d': 0, 'finra_latest_date': 'N/A',
        'finra_historical': None, 'data_source': []
    }
    
    if yf_data:
        combined_data.update({
            'short_ratio_days': round(yf_data.get('short_ratio', 0), 2),
            'short_percent_float': round(yf_data.get('short_percent_float', 0), 2),
            'shares_short_millions': round(yf_data.get('shares_short', 0) / 1e6, 2),
            'short_change_pct': round(yf_data.get('short_change_pct', 0), 2),
        })
        combined_data['data_source'].append('Yahoo Finance')
    
    if finra_data:
        combined_data['daily_short_ratio'] = finra_data['latest_short_ratio']
        combined_data['avg_daily_short_ratio_10d'] = finra_data['avg_short_ratio_10d']
        combined_data['finra_latest_date'] = finra_data.get('latest_date', 'N/A')
        combined_data['finra_historical'] = finra_data.get('historical_data')
        combined_data['data_source'].append(f"FINRA ({finra_data.get('data_points', 0)}일)")
    
    combined_data['data_source'] = ' + '.join(combined_data['data_source']) if combined_data['data_source'] else 'N/A'
    return combined_data

@st.cache_data(ttl=3600)
def get_quarterly_vwap_analysis(ticker):
    try:
        quarter_start = get_current_quarter_start()
        end_date = datetime.now()
        quarter_num = (quarter_start.month - 1) // 3 + 1

        stock = yf.Ticker(ticker)
        df = stock.history(start=quarter_start, end=end_date)

        if df.empty or len(df) < 5:
            return None

        df = calculate_anchored_vwap(df)
        current_price = df['Close'].iloc[-1]
        current_vwap = df['Anchored_VWAP'].iloc[-1]
        above_vwap_ratio = (df['Close'] > df['Anchored_VWAP']).sum() / len(df) * 100
        
        recent_20 = df['Close'].tail(min(20, len(df)))
        uptrend_strength = (recent_20.diff() > 0).sum() / len(recent_20) * 100 if len(recent_20) > 1 else 50
        
        recent_volume = df['Volume'].tail(5).mean()
        avg_volume = df['Volume'].mean()
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1

        info = stock.info
        quarter_start_price = df['Close'].iloc[0]
        quarter_return = ((current_price - quarter_start_price) / quarter_start_price * 100)

        return {
            'Ticker': ticker, 'Company': MAG7_STOCKS[ticker]['name'],
            'Description': MAG7_STOCKS[ticker]['description'],
            'Current_Price': round(current_price, 2),
            'Anchored_VWAP': round(current_vwap, 2),
            'Quarter_Return_%': round(quarter_return, 2),
            'Price_vs_VWAP_%': round((current_price - current_vwap) / current_vwap * 100, 2),
            'Above_VWAP_Days_%': round(above_vwap_ratio, 1),
            'Uptrend_Strength_%': round(uptrend_strength, 1),
            'Volume_Ratio': round(volume_ratio, 2),
            'Is_Above_VWAP': current_price > current_vwap,
            'Market_Cap': info.get('marketCap', 0),
        }
    except Exception as e:
        return None

def calculate_buy_score(row):
    score = 0
    if row['Is_Above_VWAP']: score += 30
    price_diff = row['Price_vs_VWAP_%']
    if 0 < price_diff <= 5: score += 20
    elif 5 < price_diff <= 10: score += 10
    elif price_diff > 10: score += 5
    if row['Above_VWAP_Days_%'] >= 80: score += 20
    elif row['Above_VWAP_Days_%'] >= 60: score += 15
    if row['Uptrend_Strength_%'] >= 60: score += 15
    elif row['Uptrend_Strength_%'] >= 50: score += 10
    if row['Volume_Ratio'] >= 1.2: score += 15
    elif row['Volume_Ratio'] >= 1.0: score += 10
    return min(score, 100)

def calculate_short_score(row):
    short_pct = row.get('short_percent_float', 0)
    if short_pct < 5: return 20
    elif short_pct < 10: return 15
    elif short_pct < 20: return 10
    else: return 5

# ==================== 메인 앱 ====================
st.title("🌟 MAGNIFICENT SEVEN + BITCOIN EXPOSURE 종합 분석")
st.markdown(f"**데이터 수집 시간:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (KST)")

# 사이드바
with st.sidebar:
    st.header("⚙️ 설정")
    selected_tickers = st.multiselect(
        "분석할 종목 선택",
        list(MAG7_STOCKS.keys()),
        default=list(MAG7_STOCKS.keys())
    )
    
    st.markdown("---")
    if st.button("🔄 데이터 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# 탭 생성
tab1, tab2, tab3 = st.tabs(["📊 종합 대시보드", "🔴 공매도 상세 분석", "📋 데이터"])

# 데이터 수집
with st.spinner("데이터 수집 중..."):
    results = []
    short_data_list = []
    
    progress_bar = st.progress(0)
    for idx, ticker in enumerate(selected_tickers):
        result = get_quarterly_vwap_analysis(ticker)
        if result:
            results.append(result)
        
        short_data = get_comprehensive_short_data(ticker)
        if short_data:
            short_data_list.append(short_data)
        
        progress_bar.progress((idx + 1) / len(selected_tickers))
    progress_bar.empty()

if not results:
    st.error("데이터를 수집하지 못했습니다.")
    st.stop()

df_results = pd.DataFrame(results)
df_short = pd.DataFrame(short_data_list)
df_results = df_results.merge(df_short, left_on='Ticker', right_on='ticker', how='left')
df_results['Market_Cap_Trillion'] = (df_results['Market_Cap'] / 1e12).round(3)
df_results['Buy_Signal_Score'] = df_results.apply(calculate_buy_score, axis=1)
df_results['Short_Score'] = df_results.apply(calculate_short_score, axis=1)
df_results['Total_Investment_Score'] = df_results['Buy_Signal_Score'] + df_results['Short_Score']
df_results = df_results.sort_values('Total_Investment_Score', ascending=False)

# TAB 1: 종합 대시보드
with tab1:
    st.header("📊 종합 투자 순위")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🥇 1위 종목", df_results.iloc[0]['Ticker'], f"{df_results.iloc[0]['Total_Investment_Score']:.0f}/120점")
    with col2:
        above_vwap = len(df_results[df_results['Is_Above_VWAP'] == True])
        st.metric("✅ VWAP 위", f"{above_vwap}개")
    with col3:
        st.metric("📈 평균 분기 수익률", f"{df_results['Quarter_Return_%'].mean():+.1f}%")
    with col4:
        low_short = len(df_results[df_results['short_percent_float'] < 5])
        st.metric("🟢 낮은 공매도", f"{low_short}개")
    
    st.markdown("---")
    
    for idx, row in df_results.iterrows():
        rank = df_results.index.get_loc(idx) + 1
        with st.expander(f"**#{rank} {row['Ticker']} - {row['Company'][:30]}**", expanded=(rank <= 3)):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**🎯 {row['Description']}**")
                st.markdown(f"💰 시가총액: ${row['Market_Cap_Trillion']:.2f}T")
                st.markdown(f"📈 현재가: ${row['Current_Price']:.2f} | VWAP: ${row['Anchored_VWAP']:.2f}")
                st.markdown(f"📊 VWAP 대비: {row['Price_vs_VWAP_%']:+.2f}% | 분기수익률: {row['Quarter_Return_%']:+.2f}%")
                st.markdown(f"🔴 공매도: {row['short_percent_float']:.2f}%")
            with col2:
                score = row['Total_Investment_Score']
                signal = "최우선 매수" if score >= 90 else "강력 매수" if score >= 75 else "눌림목 대기"
                st.metric("종합 점수", f"{score:.0f}/120", signal)
                st.progress(score / 120)

# TAB 2: 공매도 상세 분석
with tab2:
    st.header("🔴 공매도 상세 분석")
    
    # 비교표
    st.subheader("📋 Yahoo Finance vs FINRA 상세 비교")
    comparison_df = df_results[['Ticker', 'Company', 'short_percent_float', 'short_ratio_days', 
                                  'shares_short_millions', 'short_change_pct', 'daily_short_ratio', 
                                  'avg_daily_short_ratio_10d', 'finra_latest_date']].copy()
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("📊 상세 비교 차트")
    
    # 차트 A: Short % of Float
    fig_a = go.Figure()
    colors = ['green' if x < 2 else 'orange' if x < 5 else 'red' for x in df_results['short_percent_float']]
    fig_a.add_trace(go.Bar(x=df_results['Ticker'], y=df_results['short_percent_float'],
                            marker=dict(color=colors), text=df_results['short_percent_float'].round(2),
                            textposition='auto'))
    fig_a.add_hline(y=2, line_dash="dash", line_color="green")
    fig_a.add_hline(y=5, line_dash="dash", line_color="orange")
    fig_a.update_layout(title='YF Short % of Float', height=400, template='plotly_white')
    st.plotly_chart(fig_a, use_container_width=True)
    
    # 차트 B: Days to Cover
    fig_b = go.Figure()
    colors_days = ['green' if x < 2 else 'orange' if x < 3 else 'red' for x in df_results['short_ratio_days']]
    fig_b.add_trace(go.Bar(x=df_results['Ticker'], y=df_results['short_ratio_days'],
                            marker=dict(color=colors_days), text=df_results['short_ratio_days'].round(2),
                            textposition='auto'))
    fig_b.update_layout(title='Days to Cover', height=400, template='plotly_white')
    st.plotly_chart(fig_b, use_container_width=True)
    
    # 차트 C: MoM Change
    fig_c = go.Figure()
    colors_change = ['red' if x > 0 else 'green' for x in df_results['short_change_pct']]
    fig_c.add_trace(go.Bar(x=df_results['Ticker'], y=df_results['short_change_pct'],
                            marker=dict(color=colors_change), text=[f"{x:+.1f}%" for x in df_results['short_change_pct']],
                            textposition='auto'))
    fig_c.add_hline(y=0, line_dash="solid", line_color="black")
    fig_c.update_layout(title='전월 대비 공매도 변화율', height=400, template='plotly_white')
    st.plotly_chart(fig_c, use_container_width=True)
    
    # 차트 D: FINRA Daily
    fig_d = go.Figure()
    colors_finra = ['green' if x < 35 else 'orange' if x < 45 else 'red' for x in df_results['daily_short_ratio']]
    fig_d.add_trace(go.Bar(x=df_results['Ticker'], y=df_results['daily_short_ratio'],
                            marker=dict(color=colors_finra), text=df_results['daily_short_ratio'].round(1),
                            textposition='auto'))
    fig_d.add_hline(y=40, line_dash="dash", line_color="orange")
    fig_d.update_layout(title='FINRA Daily Short %', height=400, template='plotly_white')
    st.plotly_chart(fig_d, use_container_width=True)
    
    # 차트 E: YF vs FINRA 상관관계
    fig_e = px.scatter(df_results, x='short_percent_float', y='daily_short_ratio',
                       size='Market_Cap_Trillion', color='Total_Investment_Score',
                       text='Ticker', color_continuous_scale='RdYlGn',
                       title='YF Short % vs FINRA Daily % 상관관계')
    fig_e.add_hline(y=40, line_dash="dash", line_color="gray")
    fig_e.add_vline(x=5, line_dash="dash", line_color="gray")
    st.plotly_chart(fig_e, use_container_width=True)

# TAB 3: 데이터
with tab3:
    st.header("📋 전체 데이터")
    st.dataframe(df_results, use_container_width=True, hide_index=True)
    
    csv = df_results.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 CSV 다운로드", csv, 
                       f"mag7_analysis_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'><p>📊 MAG 7+2 종합 분석 대시보드 v2.0</p></div>", 
            unsafe_allow_html=True)
