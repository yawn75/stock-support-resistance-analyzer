#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주식 지지선/저항선 분석 프로그램
Support and Resistance Level Analyzer
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import yfinance as yf
from scipy.signal import argrelextrema
from datetime import datetime, timedelta
import warnings
import argparse
import requests
import re
import FinanceDataReader as fdr
warnings.filterwarnings('ignore')

# 한국 주식 종목 리스트 캐시 (초기에 한번만 로드)
_KRX_STOCK_LIST = None

# 한글 폰트 설정
def setup_korean_font():
    """시스템에서 사용 가능한 한글 폰트 찾아서 설정"""
    import os
    from pathlib import Path

    # 일반적인 한글 폰트 경로들
    font_paths = [
        '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
        '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf',
        '/usr/share/fonts/truetype/nanum/NanumSquare.ttf',
        '/System/Library/Fonts/AppleGothic.ttf',
        '~/.fonts/NanumGothic.ttf',
    ]

    # 존재하는 폰트 파일 찾기
    for font_path in font_paths:
        font_path = os.path.expanduser(font_path)
        if os.path.exists(font_path):
            try:
                # 폰트를 matplotlib에 등록
                font_prop = fm.FontProperties(fname=font_path)
                font_name = font_prop.get_name()

                plt.rcParams['font.family'] = font_name
                plt.rcParams['axes.unicode_minus'] = False

                # 폰트 매니저에 추가
                fm.fontManager.addfont(font_path)
                return True
            except Exception as e:
                continue

    # 폰트를 찾지 못한 경우 기본 설정
    print("⚠ 한글 폰트를 찾을 수 없습니다. 그래프에서 한글이 깨질 수 있습니다.")
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False
    return False

# 한글 폰트 설정 실행
setup_korean_font()

# 주요 종목 로컬 매핑 (폴백용)
# API 검색 실패 시 또는 빠른 접근을 위해 사용
COMMON_TICKERS = {
    # 한국 지수
    'KOSPI': '^KS11',
    'KOSDAQ': '^KQ11',
    '코스피': '^KS11',
    '코스닥': '^KQ11',
    '코스피지수': '^KS11',
    '코스닥지수': '^KQ11',

    # 한국 주요 종목 (코스피)
    '삼성전자': '005930.KS',
    '삼성전자우': '005935.KS',
    'SK하이닉스': '000660.KS',
    'LG에너지솔루션': '373220.KS',
    '삼성바이오로직스': '207940.KS',
    '삼성바이오': '207940.KS',
    '현대차': '005380.KS',
    '현대자동차': '005380.KS',
    '기아': '000270.KS',
    'POSCO홀딩스': '005490.KS',
    'POSCO': '005490.KS',
    '포스코': '005490.KS',
    '네이버': '035420.KS',
    'NAVER': '035420.KS',
    '카카오': '035720.KS',
    'LG화학': '051910.KS',
    '삼성SDI': '006400.KS',
    '현대모비스': '012330.KS',
    '셀트리온': '068270.KS',
    'SK이노베이션': '096770.KS',
    'KB금융': '105560.KS',
    '신한지주': '055550.KS',
    '하나금융지주': '086790.KS',
    '우리금융지주': '316140.KS',
    'LG전자': '066570.KS',
    '삼성물산': '028260.KS',
    '삼성생명': '032830.KS',
    'KT&G': '033780.KS',
    'SK': '034730.KS',
    '기업은행': '024110.KS',
    'HMM': '011200.KS',
    '포스코퓨처엠': '003670.KS',
    'SK텔레콤': '017670.KS',
    'KT': '030200.KS',
    'LG': '003550.KS',
    '한국전력': '015760.KS',
    '한전': '015760.KS',
    'NAVER': '035420.KS',

    # 한국 코스닥
    '셀트리온헬스케어': '091990.KQ',
    '에코프로비엠': '247540.KQ',
    '에코프로': '086520.KQ',
    '알테오젠': '196170.KQ',
    '엘앤에프': '066970.KQ',
    'HLB': '028300.KQ',
    '카카오게임즈': '293490.KQ',

    # 미국 주요 종목 (한글)
    '애플': 'AAPL',
    '마이크로소프트': 'MSFT',
    '엔비디아': 'NVDA',
    '테슬라': 'TSLA',
    '아마존': 'AMZN',
    '구글': 'GOOGL',
    '메타': 'META',
    '넷플릭스': 'NFLX',
    '인텔': 'INTC',
    '나이키': 'NKE',
    '디즈니': 'DIS',
}


def search_ticker_yahoo(query):
    """
    Yahoo Finance를 통해 종목 검색 (yfinance.Search 사용)

    Parameters:
    -----------
    query : str
        검색어 (종목명, 티커 등) - 영문 검색어 권장

    Returns:
    --------
    list : 검색 결과 리스트
    """
    try:
        # yfinance Search 기능 사용
        search = yf.Search(query, max_results=5)
        quotes = search.quotes

        results = []
        for quote in quotes:
            symbol = quote.get('symbol', '')
            name = quote.get('shortname') or quote.get('longname', '')
            exchange = quote.get('exchange', '')
            quote_type = quote.get('quoteType', '')

            # 주식만 필터링
            if quote_type in ['EQUITY', 'ETF']:
                results.append({
                    'symbol': symbol,
                    'name': name,
                    'exchange': exchange,
                    'type': quote_type
                })

        return results
    except Exception as e:
        print(f"Yahoo Finance 검색 오류: {e}")
        return []


def get_krx_stock_list():
    """
    한국 주식 종목 리스트 가져오기 (캐시 사용)

    Returns:
    --------
    DataFrame : 한국 주식 종목 리스트
    """
    global _KRX_STOCK_LIST

    if _KRX_STOCK_LIST is None:
        try:
            print("한국 주식 종목 리스트 로딩 중...")
            _KRX_STOCK_LIST = fdr.StockListing('KRX')
            print(f"✓ {len(_KRX_STOCK_LIST)}개 종목 로드 완료")
        except Exception as e:
            print(f"종목 리스트 로딩 실패: {e}")
            _KRX_STOCK_LIST = pd.DataFrame()

    return _KRX_STOCK_LIST


def search_korean_stock(query):
    """
    한국 주식 검색 (FinanceDataReader 활용)

    Parameters:
    -----------
    query : str
        검색어 (한글 종목명 또는 종목코드)

    Returns:
    --------
    list : 검색 결과 리스트
    """
    try:
        krx = get_krx_stock_list()

        if krx.empty:
            return []

        results = []

        # 종목명으로 검색 (부분 일치)
        matched = krx[krx['Name'].str.contains(query, na=False, case=False)]

        # 종목코드로도 검색
        if query.isdigit():
            code_matched = krx[krx['Code'] == query]
            matched = pd.concat([matched, code_matched]).drop_duplicates()

        # 결과를 리스트로 변환
        for _, row in matched.head(5).iterrows():
            code = row['Code']
            name = row['Name']
            market = row['Market']

            # Yahoo Finance 형식으로 변환
            if market == 'KOSPI':
                symbol = f"{code}.KS"
            elif market == 'KOSDAQ':
                symbol = f"{code}.KQ"
            else:
                symbol = f"{code}.KS"  # 기본값

            results.append({
                'symbol': symbol,
                'name': name,
                'code': code,
                'market': market
            })

        return results
    except Exception as e:
        print(f"한국 주식 검색 오류: {e}")
        return []


def verify_ticker(symbol):
    """
    종목 코드가 유효한지 확인

    Parameters:
    -----------
    symbol : str
        종목 코드

    Returns:
    --------
    bool : 유효 여부
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.history(period='5d')
        return not info.empty
    except:
        return False


def get_ticker_info(ticker_input):
    """
    종목명 또는 코드를 입력받아 종목 정보 반환

    Parameters:
    -----------
    ticker_input : str
        종목명(한글/영문) 또는 종목 코드

    Returns:
    --------
    tuple : (종목코드, 종목명, 통화)
    """
    # 1. 로컬 매핑에서 정확히 일치하는 것 찾기
    if ticker_input in COMMON_TICKERS:
        symbol = COMMON_TICKERS[ticker_input]
        print(f"\n✓ '{ticker_input}' 발견: {symbol}")

        # 지수인지 확인
        if symbol.startswith('^'):
            # 지수 정보 가져오기
            try:
                ticker_obj = yf.Ticker(symbol)
                info = ticker_obj.info
                name = info.get('longName', info.get('shortName', ticker_input))
                # 한국 지수는 KRW (포인트)
                if symbol in ['^KS11', '^KQ11']:
                    return symbol, name, 'KRW'
                else:
                    currency = info.get('currency', 'USD')
                    return symbol, name, currency
            except:
                return symbol, ticker_input, 'KRW' if symbol in ['^KS11', '^KQ11'] else 'USD'

        # 한국 주식인지 확인
        elif symbol.endswith('.KS') or symbol.endswith('.KQ'):
            return symbol, ticker_input, 'KRW'
        else:
            # 티커 정보 가져오기
            try:
                ticker_obj = yf.Ticker(symbol)
                info = ticker_obj.info
                name = info.get('longName', info.get('shortName', ticker_input))
                currency = info.get('currency', 'USD')
                return symbol, name, currency
            except:
                return symbol, ticker_input, 'USD'

    # 1-2. 부분 매칭 시도 (예: '우리금융' -> '우리금융지주')
    matches = []
    for key in COMMON_TICKERS:
        if ticker_input in key or key in ticker_input:
            matches.append((key, COMMON_TICKERS[key]))

    if matches:
        # 가장 짧은 이름을 선택 (정확도가 높음)
        matches.sort(key=lambda x: len(x[0]))
        matched_name, symbol = matches[0]
        print(f"\n✓ '{ticker_input}' -> '{matched_name}' 발견: {symbol}")
        # 한국 주식인지 확인
        if symbol.endswith('.KS') or symbol.endswith('.KQ'):
            return symbol, matched_name, 'KRW'
        else:
            try:
                ticker_obj = yf.Ticker(symbol)
                info = ticker_obj.info
                name = info.get('longName', info.get('shortName', matched_name))
                currency = info.get('currency', 'USD')
                return symbol, name, currency
            except:
                return symbol, matched_name, 'USD'

    # 2. 이미 올바른 형식의 종목 코드인지 확인
    # (예: 005930.KS, AAPL 등)
    if re.match(r'^[A-Z0-9]+(\.(KS|KQ))?$', ticker_input):
        print(f"\n종목 코드 확인 중: {ticker_input}")
        if verify_ticker(ticker_input):
            print(f"✓ 유효한 종목 코드입니다.")
            # 종목 정보 가져오기
            try:
                ticker_obj = yf.Ticker(ticker_input)
                info = ticker_obj.info
                name = info.get('longName', info.get('shortName', ticker_input))
                currency = info.get('currency', 'KRW' if ticker_input.endswith(('.KS', '.KQ')) else 'USD')
                return ticker_input, name, currency
            except:
                currency = 'KRW' if ticker_input.endswith(('.KS', '.KQ')) else 'USD'
                return ticker_input, ticker_input, currency
        else:
            print(f"⚠ 유효하지 않은 종목 코드입니다.")

    # 3. 한글이 포함되어 있으면 한국 주식 검색 (FinanceDataReader)
    if re.search(r'[가-힣]', ticker_input):
        print(f"\n'{ticker_input}' 한국 주식 검색 중...")
        kr_results = search_korean_stock(ticker_input)

        if kr_results:
            print("\n검색 결과:")
            for i, result in enumerate(kr_results, 1):
                print(f"  {i}. {result['name']} ({result['code']}) - {result['market']}")

            # 첫 번째 결과 사용
            result = kr_results[0]
            symbol = result['symbol']
            name = result['name']
            print(f"\n✓ '{name}' 발견: {symbol}")
            return symbol, name, 'KRW'
        else:
            print(f"\n✗ '{ticker_input}' 검색 결과 없음")
            print("\n해결 방법:")
            print("  1. 정확한 종목명 입력 (예: 삼성전자, 카카오)")
            print("  2. 종목 코드 직접 입력 (예: 005930.KS)")
            raise ValueError(f"종목을 찾을 수 없습니다: {ticker_input}")

    # 4. 영문 검색 (Yahoo Finance - yfinance.Search)
    print(f"\n'{ticker_input}' 검색 중...")
    yahoo_results = search_ticker_yahoo(ticker_input)

    if yahoo_results:
        print("검색 결과:")
        for i, result in enumerate(yahoo_results, 1):
            print(f"  {i}. {result['name']} ({result['symbol']}) - {result['exchange']}")

        # 첫 번째 결과 사용
        result = yahoo_results[0]
        symbol = result['symbol']
        name = result['name']
        print(f"\n✓ '{name}' 발견: {symbol}")

        # 통화 정보 가져오기
        try:
            ticker_obj = yf.Ticker(symbol)
            info = ticker_obj.info
            currency = info.get('currency', 'USD')
        except:
            currency = 'KRW' if symbol.endswith(('.KS', '.KQ')) else 'USD'

        return symbol, name, currency

    # 5. 모든 검색 실패 시 에러 메시지
    print(f"\n✗ '{ticker_input}' 검색 결과 없음")
    print("\n해결 방법:")
    print("  1. 정확한 영문 종목명 사용 (예: Apple, Microsoft)")
    print("  2. 종목 코드 직접 입력 (예: AAPL, MSFT)")
    print("  3. 한국 주식은 영문명 사용 (예: Samsung, Hyundai)")

    raise ValueError(f"종목을 찾을 수 없습니다: {ticker_input}")


class SupportResistanceAnalyzer:
    """지지선/저항선 분석 클래스"""

    def __init__(self, ticker, start_date, end_date=None, ticker_name=None, currency=None):
        """
        초기화

        Parameters:
        -----------
        ticker : str
            종목 코드 (예: '005930.KS', 'AAPL')
        start_date : str
            시작 날짜 (YYYY-MM-DD)
        end_date : str, optional
            종료 날짜 (YYYY-MM-DD), 기본값은 오늘
        ticker_name : str, optional
            종목명 (예: '삼성전자', 'Apple Inc.')
        currency : str, optional
            통화 (예: 'KRW', 'USD')
        """
        self.ticker = ticker
        self.ticker_name = ticker_name or ticker
        self.currency = currency or 'KRW'
        self.start_date = start_date
        self.end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        self.df = None
        self.support_levels = []
        self.resistance_levels = []
        
    def fetch_data(self):
        """주가 데이터 가져오기"""
        print(f"데이터 수집 중: {self.ticker} ({self.start_date} ~ {self.end_date})")
        ticker_obj = yf.Ticker(self.ticker)
        self.df = ticker_obj.history(start=self.start_date, end=self.end_date)
        if self.df.empty:
            raise ValueError(f"데이터를 가져올 수 없습니다. 종목 코드를 확인하세요: {self.ticker}")
        print(f"데이터 수집 완료: {len(self.df)}개 데이터")
        return self.df
    
    def find_pivots(self, column='Close', order=5):
        """
        피봇 포인트(극값) 찾기
        
        Parameters:
        -----------
        column : str
            분석할 컬럼 (기본값: 'Close')
        order : int
            피봇을 찾을 때 비교할 주변 데이터 개수
        
        Returns:
        --------
        local_min : array
            지지선 후보 (로컬 최소값)
        local_max : array
            저항선 후보 (로컬 최대값)
        """
        # 로컬 최소값 (지지선 후보)
        local_min_idx = argrelextrema(self.df[column].values, np.less_equal, order=order)[0]
        local_min = self.df[column].iloc[local_min_idx].values
        
        # 로컬 최대값 (저항선 후보)
        local_max_idx = argrelextrema(self.df[column].values, np.greater_equal, order=order)[0]
        local_max = self.df[column].iloc[local_max_idx].values
        
        return local_min, local_max, local_min_idx, local_max_idx
    
    def cluster_levels(self, levels, tolerance=0.02):
        """
        비슷한 가격대를 클러스터링하여 주요 지지/저항선 찾기
        
        Parameters:
        -----------
        levels : array
            가격 레벨들
        tolerance : float
            클러스터링 허용 오차 (2% = 0.02)
        
        Returns:
        --------
        clustered_levels : list
            클러스터링된 주요 레벨과 빈도수
        """
        if len(levels) == 0:
            return []
        
        levels_sorted = np.sort(levels)
        clusters = []
        current_cluster = [levels_sorted[0]]
        
        for level in levels_sorted[1:]:
            # 현재 클러스터의 평균값과 비교
            cluster_mean = np.mean(current_cluster)
            if abs(level - cluster_mean) / cluster_mean <= tolerance:
                current_cluster.append(level)
            else:
                clusters.append(current_cluster)
                current_cluster = [level]
        
        clusters.append(current_cluster)
        
        # 각 클러스터의 평균값과 빈도수 계산
        clustered_levels = []
        for cluster in clusters:
            avg_level = np.mean(cluster)
            count = len(cluster)
            clustered_levels.append((avg_level, count))
        
        # 빈도수로 정렬 (많이 나타날수록 강한 지지/저항선)
        clustered_levels.sort(key=lambda x: x[1], reverse=True)
        
        return clustered_levels
    
    def analyze(self, order=5, tolerance=0.02, max_levels=5):
        """
        지지선/저항선 분석
        
        Parameters:
        -----------
        order : int
            피봇 찾기 파라미터
        tolerance : float
            클러스터링 허용 오차
        max_levels : int
            표시할 최대 지지/저항선 개수
        """
        if self.df is None:
            self.fetch_data()
        
        print("\n지지선/저항선 분석 중...")
        
        # 피봇 포인트 찾기
        local_min, local_max, min_idx, max_idx = self.find_pivots(order=order)
        
        print(f"발견된 지지선 후보: {len(local_min)}개")
        print(f"발견된 저항선 후보: {len(local_max)}개")
        
        # 지지선 클러스터링
        support_clusters = self.cluster_levels(local_min, tolerance)
        self.support_levels = [level for level, count in support_clusters[:max_levels]]
        
        # 저항선 클러스터링
        resistance_clusters = self.cluster_levels(local_max, tolerance)
        self.resistance_levels = [level for level, count in resistance_clusters[:max_levels]]
        
        # 현재가
        current_price = self.df['Close'].iloc[-1]

        # 통화 기호 설정
        # 지수인지 확인
        is_index = self.ticker.startswith('^')

        if self.currency == 'USD':
            currency_symbol = '$'
            price_format = lambda x: f"${x:,.2f}"
        elif self.currency == 'KRW':
            if is_index:
                currency_symbol = 'pt'
                price_format = lambda x: f"{x:,.2f}pt"
            else:
                currency_symbol = '원'
                price_format = lambda x: f"{x:,.0f}원"
        else:
            currency_symbol = self.currency
            price_format = lambda x: f"{x:,.2f} {self.currency}"

        # 결과 출력
        print("\n" + "="*60)
        print(f"종목: {self.ticker_name} ({self.ticker})")
        print(f"현재가: {price_format(current_price)}")
        print("="*60)

        print("\n[주요 저항선 (Resistance Levels)]")
        print("-" * 60)
        for i, (level, count) in enumerate(resistance_clusters[:max_levels], 1):
            distance = ((level - current_price) / current_price) * 100
            strength = "강함" if count >= 3 else "보통" if count >= 2 else "약함"
            print(f"{i}차 저항선: {price_format(level):>15} | "
                  f"현재가 대비: {distance:>+6.2f}% | "
                  f"강도: {strength} (터치 {count}회)")

        print("\n[주요 지지선 (Support Levels)]")
        print("-" * 60)
        for i, (level, count) in enumerate(support_clusters[:max_levels], 1):
            distance = ((level - current_price) / current_price) * 100
            strength = "강함" if count >= 3 else "보통" if count >= 2 else "약함"
            print(f"{i}차 지지선: {price_format(level):>15} | "
                  f"현재가 대비: {distance:>+6.2f}% | "
                  f"강도: {strength} (터치 {count}회)")

        print("="*60)
        
        return {
            'support': support_clusters[:max_levels],
            'resistance': resistance_clusters[:max_levels],
            'current_price': current_price
        }
    
    def plot(self, figsize=(14, 8)):
        """
        지지선/저항선 그래프 그리기

        Parameters:
        -----------
        figsize : tuple
            그래프 크기
        """
        if self.df is None:
            print("데이터가 없습니다. analyze()를 먼저 실행하세요.")
            return

        fig, ax = plt.subplots(figsize=figsize)

        # 주가 차트
        ax.plot(self.df.index, self.df['Close'], label='Close Price',
                linewidth=1.5, color='#2E86AB', alpha=0.8)

        # 현재가
        current_price = self.df['Close'].iloc[-1]

        # 통화별 포맷 설정
        is_index = self.ticker.startswith('^')

        if self.currency == 'USD':
            price_label_format = lambda x: f'${x:,.2f}'
            y_axis_format = lambda x, p: f'${x:,.0f}'
            currency_label = 'USD'
        elif self.currency == 'KRW':
            if is_index:
                price_label_format = lambda x: f'{x:,.2f}pt'
                y_axis_format = lambda x, p: f'{x:,.1f}'
                currency_label = 'Points'
            else:
                price_label_format = lambda x: f'{x:,.0f}'
                y_axis_format = lambda x, p: f'{x:,.0f}'
                currency_label = 'KRW'
        else:
            price_label_format = lambda x: f'{x:,.2f}'
            y_axis_format = lambda x, p: f'{x:,.2f}'
            currency_label = self.currency

        ax.axhline(y=current_price, color='black', linestyle='--',
                   linewidth=1, label=f'Current: {price_label_format(current_price)}', alpha=0.7)

        # 저항선 그리기
        colors_resistance = ['#A23B72', '#C73E1D', '#F18F01', '#8B4513', '#DC143C']
        for i, level in enumerate(self.resistance_levels):
            color = colors_resistance[i % len(colors_resistance)]
            ax.axhline(y=level, color=color, linestyle='-',
                      linewidth=2, label=f'R{i+1}: {price_label_format(level)}', alpha=0.6)

        # 지지선 그리기
        colors_support = ['#06A77D', '#2E8B57', '#20B2AA', '#3CB371', '#00CED1']
        for i, level in enumerate(self.support_levels):
            color = colors_support[i % len(colors_support)]
            ax.axhline(y=level, color=color, linestyle='-',
                      linewidth=2, label=f'S{i+1}: {price_label_format(level)}', alpha=0.6)

        # 그래프 꾸미기
        ax.set_title(f'{self.ticker_name} - Support & Resistance Levels',
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel(f'Price ({currency_label})', fontsize=12)
        ax.legend(loc='best', fontsize=10, framealpha=0.9)
        ax.grid(True, alpha=0.3)

        # y축 포맷
        ax.yaxis.set_major_formatter(plt.FuncFormatter(y_axis_format))

        plt.tight_layout()
        filename = f'{self.ticker}_support_resistance.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"\n그래프 저장 완료: {filename}")
        plt.show()

        return fig


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='주식 지지선/저항선 분석 프로그램',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  %(prog)s 삼성전자                # 한글 종목명
  %(prog)s 005930.KS              # 종목 코드
  %(prog)s AAPL                   # 티커 심볼
  %(prog)s 네이버 -d 180           # 180일 데이터
  %(prog)s TSLA -o 10 -t 0.02     # 민감도 조정

종목 검색 방식:
  1. 로컬 캐시: 주요 종목은 즉시 검색 (빠름)
  2. 한글 검색: FinanceDataReader로 전체 한국 주식 검색 가능
  3. 영문 검색: Yahoo Finance로 전세계 주식 검색
  4. 종목 코드: 직접 입력 (005930.KS, AAPL 등)

검색 예시:
  한국 지수: 코스피, KOSPI, 코스닥, KOSDAQ
  한국 주식: 삼성전자, 카카오, 두산, LG전자 등 (한글 가능!)
  미국 주식: Apple, Microsoft, Tesla, AAPL 등
  종목 코드: 005930.KS, 000660.KS, AAPL, TSLA, ^KS11 등

※ 한국 주식은 약 2,800개 전체 종목 검색 가능
※ KOSPI/KOSDAQ 지수 분석 지원
        """
    )

    parser.add_argument('ticker', type=str, help='종목명 또는 종목 코드 (예: 삼성전자, 005930.KS, 애플, AAPL)')
    parser.add_argument('-d', '--days', type=int, default=365,
                        help='분석 기간 (일) (기본값: 365)')
    parser.add_argument('-o', '--order', type=int, default=7,
                        help='피봇 민감도 (클수록 적은 피봇) (기본값: 7)')
    parser.add_argument('-t', '--tolerance', type=float, default=0.015,
                        help='클러스터링 허용 오차 (기본값: 0.015)')
    parser.add_argument('-m', '--max-levels', type=int, default=5,
                        help='표시할 최대 지지/저항선 개수 (기본값: 5)')

    args = parser.parse_args()

    print("="*60)
    print("주식 지지선/저항선 분석 프로그램")
    print("Support & Resistance Level Analyzer")
    print("="*60)

    try:
        # 종목 정보 가져오기 (코드, 이름, 통화)
        ticker, ticker_name, currency = get_ticker_info(args.ticker)
    except ValueError as e:
        print(f"\n오류: {e}")
        return

    start_date = (datetime.now() - timedelta(days=args.days)).strftime('%Y-%m-%d')

    # 분석기 생성
    analyzer = SupportResistanceAnalyzer(ticker, start_date, ticker_name=ticker_name, currency=currency)

    # 데이터 가져오기
    analyzer.fetch_data()

    # 지지선/저항선 분석
    results = analyzer.analyze(order=args.order, tolerance=args.tolerance, max_levels=args.max_levels)

    # 그래프 그리기
    analyzer.plot()

    print("\n매매 판단 가이드:")
    print("-" * 60)
    print("• 저항선 근처: 매도 또는 관망 구간 (상승 저항 예상)")
    print("• 지지선 근처: 매수 또는 관망 구간 (하락 지지 예상)")
    print("• 저항선 돌파: 강한 상승 신호 (추가 상승 가능)")
    print("• 지지선 이탈: 강한 하락 신호 (추가 하락 가능)")
    print("-" * 60)


if __name__ == "__main__":
    main()
