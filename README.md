# 📈 주식 지지선/저항선 분석 프로그램

Support & Resistance Level Analyzer for Stock Trading

Python 기반 주식 차트 기술적 분석 도구

---

## ✨ 주요 기능

### 🎯 핵심 기능
- **자동 지지선/저항선 탐지**: 로컬 최소값/최대값 기반 피봇 포인트 자동 탐색
- **스마트 검색**: 한글 종목명으로 검색 가능 (예: "삼성전자", "코스피")
- **전체 종목 지원**: 한국 2,800+ 종목, 미국/전세계 주식, KOSPI/KOSDAQ 지수
- **다국어 지원**: 한글 그래프 출력 지원 (나눔고딕 폰트)
- **CLI 인터페이스**: 간단한 명령어로 즉시 분석

### 💡 지원 대상
- 🇰🇷 **한국 주식**: 코스피/코스닥 전체 종목 (2,800+)
- 🇰🇷 **한국 지수**: KOSPI, KOSDAQ
- 🇺🇸 **미국 주식**: NASDAQ, NYSE 전체 종목
- 🌍 **글로벌 주식**: 전세계 주요 거래소

---

## 🚀 빠른 시작

### 1. 설치

```bash
pip install yfinance pandas numpy scipy matplotlib FinanceDataReader
```

### 2. 실행

```bash
# 한글 종목명으로 검색
python support_resistance_analyzer.py 삼성전자

# 영문 종목명으로 검색
python support_resistance_analyzer.py Apple

# 종목 코드로 검색
python support_resistance_analyzer.py 005930.KS
python support_resistance_analyzer.py AAPL

# 지수 분석
python support_resistance_analyzer.py 코스피
python support_resistance_analyzer.py KOSDAQ

# 옵션 사용
python support_resistance_analyzer.py 삼성전자 -d 180    # 180일 데이터
python support_resistance_analyzer.py AAPL -d 90 -o 10   # 90일, 민감도 10
```

### 3. 도움말

```bash
python support_resistance_analyzer.py -h
```

---

## 📊 사용 예시

### 한국 주식
```bash
python support_resistance_analyzer.py 삼성전자
python support_resistance_analyzer.py SK하이닉스
python support_resistance_analyzer.py 카카오
python support_resistance_analyzer.py 네이버
```

### 한국 지수
```bash
python support_resistance_analyzer.py 코스피
python support_resistance_analyzer.py KOSDAQ
python support_resistance_analyzer.py ^KS11
```

### 미국 주식
```bash
python support_resistance_analyzer.py Apple
python support_resistance_analyzer.py AAPL
python support_resistance_analyzer.py Tesla
python support_resistance_analyzer.py NVDA
```

---

## ⚙️ 명령어 옵션

```bash
python support_resistance_analyzer.py [종목명] [옵션]
```

### 옵션 설명

| 옵션 | 설명 | 기본값 | 예시 |
|------|------|--------|------|
| `-d, --days` | 분석 기간 (일) | 365 | `-d 180` |
| `-o, --order` | 피봇 민감도 (클수록 적은 피봇) | 7 | `-o 10` |
| `-t, --tolerance` | 클러스터링 허용 오차 | 0.015 | `-t 0.02` |
| `-m, --max-levels` | 최대 지지/저항선 개수 | 5 | `-m 3` |

### 사용 예시

```bash
# 삼성전자 180일 데이터 분석
python support_resistance_analyzer.py 삼성전자 -d 180

# 애플 90일 데이터, 민감도 높게
python support_resistance_analyzer.py AAPL -d 90 -o 10

# 코스피 1년 데이터, 주요 레벨만 3개
python support_resistance_analyzer.py 코스피 -d 365 -m 3
```

---

## 📈 출력 예시

### 한국 주식
```
============================================================
종목: 삼성전자 (005930.KS)
현재가: 99,200원
============================================================

[주요 저항선 (Resistance Levels)]
------------------------------------------------------------
1차 저항선:         71,929원 | 현재가 대비: -27.49% | 강도: 보통 (터치 2회)
2차 저항선:         56,995원 | 현재가 대비: -42.55% | 강도: 약함 (터치 1회)

[주요 지지선 (Support Levels)]
------------------------------------------------------------
1차 지지선:         53,333원 | 현재가 대비: -46.24% | 강도: 약함 (터치 1회)
2차 지지선:         56,599원 | 현재가 대비: -42.94% | 강도: 약함 (터치 1회)

그래프 저장 완료: 005930.KS_support_resistance.png
```

### 미국 주식
```
============================================================
종목: Apple Inc. (AAPL)
현재가: $269.77
============================================================

[주요 저항선 (Resistance Levels)]
------------------------------------------------------------
1차 저항선:         $213.38 | 현재가 대비: -20.90% | 강도: 강함 (터치 3회)
2차 저항선:         $203.69 | 현재가 대비: -24.50% | 강도: 약함 (터치 1회)

[주요 지지선 (Support Levels)]
------------------------------------------------------------
1차 지지선:         $195.23 | 현재가 대비: -27.63% | 강도: 보통 (터치 2회)
2차 지지선:         $225.84 | 현재가 대비: -16.28% | 강도: 보통 (터치 2회)

그래프 저장 완료: AAPL_support_resistance.png
```

### 지수
```
============================================================
종목: KOSPI Composite Index (^KS11)
현재가: 4,026.45pt
============================================================

[주요 저항선 (Resistance Levels)]
------------------------------------------------------------
1차 저항선:      2,548.68pt | 현재가 대비: -36.70% | 강도: 강함 (터치 3회)

[주요 지지선 (Support Levels)]
------------------------------------------------------------
1차 지지선:      3,139.81pt | 현재가 대비: -22.02% | 강도: 강함 (터치 3회)

그래프 저장 완료: ^KS11_support_resistance.png
```

---

## 🔍 검색 기능

### 1. 로컬 캐시 (빠름)
주요 50+ 종목은 즉시 검색
```bash
python support_resistance_analyzer.py 삼성전자
python support_resistance_analyzer.py 애플
```

### 2. 전체 한국 주식 (FinanceDataReader)
약 2,800개 전체 한국 상장 종목 검색 가능
```bash
python support_resistance_analyzer.py 두산
python support_resistance_analyzer.py 하이브
```

### 3. 전세계 주식 (Yahoo Finance)
영문 종목명으로 검색
```bash
python support_resistance_analyzer.py Tesla
python support_resistance_analyzer.py Microsoft
```

### 4. 직접 입력
종목 코드를 정확히 알고 있다면
```bash
python support_resistance_analyzer.py 005930.KS
python support_resistance_analyzer.py AAPL
python support_resistance_analyzer.py ^KS11
```

---

## 💡 매매 전략 가이드

### 1. 저항선 돌파 (Breakout)
```
저항선 상향 돌파 + 거래량 증가
→ 강한 상승 신호 🚀
→ 매수 타이밍
```

### 2. 지지선 이탈 (Breakdown)
```
지지선 하향 이탈 + 거래량 증가
→ 강한 하락 신호 📉
→ 손절 타이밍
```

### 3. 박스권 거래
```
지지선 ↔ 저항선 횡보
→ 지지선 근처: 매수 기회
→ 저항선 근처: 매도 기회
```

### 4. 강도 해석
- **강함 (3회 이상 터치)**: 높은 신뢰도, 중요한 레벨
- **보통 (2회 터치)**: 중간 신뢰도, 참고
- **약함 (1회 터치)**: 낮은 신뢰도, 보조 참고

---

## 🎯 트레이딩 스타일별 설정

### 단기 트레이딩
```bash
python support_resistance_analyzer.py 삼성전자 -d 90 -o 5 -m 7
```
- 짧은 기간 (90일)
- 높은 민감도 (order=5)
- 많은 레벨 (7개)

### 스윙 트레이딩
```bash
python support_resistance_analyzer.py 삼성전자 -d 180 -o 7 -m 5
```
- 중간 기간 (180일)
- 균형잡힌 민감도 (order=7)
- 적당한 레벨 (5개)

### 중장기 투자
```bash
python support_resistance_analyzer.py 삼성전자 -d 365 -o 10 -m 3
```
- 긴 기간 (365일)
- 낮은 민감도 (order=10)
- 핵심 레벨만 (3개)

---

## 🛠️ 기술 스택

- **Python 3.8+**
- **yfinance**: Yahoo Finance 데이터 수집
- **FinanceDataReader**: 한국 주식 데이터 및 검색
- **pandas**: 데이터 처리
- **numpy**: 수치 계산
- **scipy**: 피봇 포인트 탐지
- **matplotlib**: 그래프 시각화

---

## 📁 파일 구조

```
resistences/
├── support_resistance_analyzer.py   # 메인 프로그램
├── README.md                        # 이 파일
├── .gitignore                       # Git 제외 파일
└── *.png                           # 생성된 그래프 (git 제외)
```

---

## ⚠️ 주의사항

1. **지지/저항선은 절대적이지 않습니다**
   - 돌파/이탈 가능성 항상 존재
   - 다른 기술적 지표와 병행 사용 권장

2. **거래량 확인 필수**
   - 거래량 없는 돌파/이탈은 신뢰도 낮음

3. **펀더멘털 고려**
   - 뉴스, 공시, 실적 등 확인
   - 기술적 분석만으로 판단 금물

4. **리스크 관리**
   - 손절매 라인 설정 필수
   - 분산 투자 고려

5. **투자 책임**
   - 본 프로그램은 참고용 도구입니다
   - 모든 투자 결정과 손실은 본인 책임입니다

---

## 🔧 문제 해결

### Q1. 한글 폰트가 깨져요
```
→ 시스템에 나눔 폰트 설치 필요
→ Ubuntu/Debian: sudo apt install fonts-nanum
→ 또는 프로그램이 자동으로 폰트 감지
```

### Q2. 종목을 찾을 수 없어요
```
→ 정확한 종목명 입력 (띄어쓰기 확인)
→ 영문명으로 시도 (예: Doosan)
→ 종목 코드로 직접 입력 (예: 005930.KS)
```

### Q3. 데이터를 가져올 수 없어요
```
→ 인터넷 연결 확인
→ yfinance 업데이트: pip install -U yfinance
→ 올바른 종목 코드 확인
```

### Q4. 지지/저항선이 너무 많거나 적어요
```
많을 때: order 값 증가 (8~10)
적을 때: order 값 감소 (3~5)
```

---

## 📞 주요 종목 코드 참고

### 한국 주요 종목
```
삼성전자: 005930.KS    카카오: 035720.KS
SK하이닉스: 000660.KS  네이버: 035420.KS
현대차: 005380.KS      셀트리온: 068270.KS
```

### 미국 주요 종목
```
AAPL   Apple          MSFT   Microsoft
GOOGL  Google         AMZN   Amazon
TSLA   Tesla          NVDA   NVIDIA
META   Meta           NFLX   Netflix
```

### 지수
```
KOSPI: ^KS11 또는 "코스피"
KOSDAQ: ^KQ11 또는 "코스닥"
```

---

## 📄 라이선스

MIT License

---

## 📝 버전 히스토리

### v2.0 (2025-11)
- ✨ CLI 인터페이스 추가
- ✨ 한글 종목명 검색 지원 (FinanceDataReader)
- ✨ KOSPI/KOSDAQ 지수 분석 지원
- ✨ 자동 통화 인식 (KRW/USD)
- ✨ 한글 폰트 자동 설정
- ✨ 전체 한국 주식 2,800+ 종목 검색
- 🐛 그래프 한글 깨짐 수정
- 🐛 종목명 표시 개선

### v1.0 (2024-11)
- 초기 버전 출시
- 지지/저항선 자동 탐지
- 시각화 및 리포트 생성

---

**Happy Trading! 📈💰**

*이 도구는 교육 및 참고 목적으로만 사용하세요. 투자 결정에 대한 책임은 전적으로 사용자에게 있습니다.*
