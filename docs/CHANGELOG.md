# Changelog

Daily Stock Analysis의 주요 변경 사항을 기록합니다.

형식은 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)를 참고하며, 버전 관리는 [Semantic Versioning](https://semver.org/) 기준을 따릅니다.

사용자 친화적인 릴리스 요약은 [GitHub Releases](https://github.com/robot0971-art/daily_stock_analysis/releases)에서 확인할 수 있습니다.

## [Unreleased]


- [개선] Web 분석 작업 카드가 AI 리포트 작성 단계의 긴 진행 메시지와 경과 시간을 표시해 장시간 분석이 멈춘 것처럼 보이지 않도록 했습니다.
- [개선] brief/simple/detailed 분석의 LLM 출력 예산을 줄여 일반 분석 요청의 응답 지연을 낮췄습니다.
- [수정] Web 데이터 신뢰도 진단 패널에 남아 있던 중국어 진단 문구를 한국어로 표시하도록 정리했습니다.
- [개선] Windows 로컬 서버 실행 스크립트가 UTF-8 환경을 고정해 한글/중국어 로그 출력 중 서버가 불안정해지지 않도록 했습니다.
- [개선] 미국 주식 뉴스 검색에 Yahoo Finance fallback을 추가하고, 분석 기록에 직접 연결된 뉴스가 없으면 같은 종목의 최근 저장 뉴스나 라이브 검색 결과를 이전 뉴스로 표시하도록 보강했습니다.
- [수정] 분석 기록 전체 초기화 API가 `DELETE /api/v1/history/reset`에서 다시 동작하도록 복구했습니다.
- [문서] `.env.example`에 OpenCode Go LLM 채널 예시를 추가해 Web provider 템플릿과 GitHub Actions 환경 변수 계약을 맞췄습니다.
- [문서] 알림 센터 문서와 Web 설정 도움말 키를 보강해 단계별 계약과 설정 도움말 검증이 통과하도록 정리했습니다.
- [수정] `REPORT_LANGUAGE=zh` 리포트 렌더링 호환성과 분석 API의 agent trace/detail 응답 필드 보존을 복구했습니다.
- [수정] CLI dry-run에서 실제 데이터 저장 성공이 실패로 집계되거나 Feishu 문서 생성 오류가 불필요하게 기록되지 않도록 했습니다.
- [수정] Web AI 상담 화면의 컨텍스트 압축과 이어질문 안내에 남아 있던 이전 중국어 빌드 문구가 한국어로 표시되도록 정적 번들을 갱신했습니다.
- [수정] Web 데이터 신뢰도 패널이 이전 `zh` 리포트 언어 값을 받아도 기본 한국어 라벨로 안전하게 표시되도록 했습니다.
- [개선] 미국 주식 전략 가격대가 원화가 아닌 달러 단위로 표시되도록 하고, 주요 미국 종목을 `애플`, `엔비디아`, `테슬라` 같은 한국어 이름으로도 검색할 수 있게 했습니다.
- [수정] `애플` 같은 한국어 종목명을 직접 분석 요청해도 백엔드가 한글 입력과 자동완성 별칭을 해석하고, 잘못된 입력 안내가 한국어로 표시되도록 했습니다.
- [수정] Web 전략 선택 메뉴와 AI 상담 스킬 목록에서 병음으로 보이던 전략 이름과 설명을 한국어로 표시하도록 했습니다.
- [개선] Web UI의 기본 문서 언어와 초기 제목을 한국어로 고정하고, 이후 영어 UI 선택 기능을 붙일 수 있는 기본 언어 유틸을 추가했습니다.
- [수정] Web 작업 진행 카드와 미국 주식 섹터/산업 태그에 남아 있던 중국어 또는 깨진 인코딩 문구가 한국어로 표시되도록 정리했습니다.
- [개선] 미국 주식 일봉 데이터 기본 우선순위를 yfinance 무료 경로로 고정하고 `US_DAILY_DATA_SOURCE_ORDER`로 선택형 유료/제한 API 우선순위를 바꿀 수 있게 했습니다.
- [개선] AI 종목 리포트가 매수/관망/매도 결론, 판단 이유, 조건 변화, 리스크를 초보자도 이해하기 쉬운 표현으로 설명하도록 프롬프트 규칙을 보강했습니다.
- [개선] Web 종목 자동완성 인덱스에 로컬 한국 종목명을 포함해 `삼성전자` 같은 한국어 종목명으로 KRX 종목을 검색할 수 있게 했습니다.
- [개선] 네이버 증권 공개 목록을 이용해 KOSPI/KOSDAQ 종목명을 자동완성 인덱스에 갱신하는 스크립트를 추가했습니다.
- [수정] Web 분석 진행 카드에 표시되는 작업 대기열과 분석 단계 문구가 중국어로 노출되지 않도록 한국어로 정리했습니다.
- [수정] LLM 분석 요청에 300초 기본 타임아웃과 장시간 대기 안내 문구를 적용해 Web 진행률이 AI 응답 단계에서 멈춘 것처럼 보이지 않도록 했습니다.
- [수정] LLM 스트리밍이 첫 응답 전에 빈 응답으로 실패하면 같은 모델 일반 요청으로 오래 대기하지 않고 다음 fallback 모델로 전환하도록 했습니다.
- [수정] 한국어 최신 리포트에 일부 혼합 언어 문구가 있어도 리포트 상세 데이터와 실행 가격대가 숨겨지지 않도록 했습니다.
- [수정] KIS 시가총액 값을 회전율로 오인하지 않도록 해 한국 종목 데이터 신뢰도 저하 표시와 AI 판단 왜곡을 줄였습니다.
- [개선] 한국 종목 최신 뉴스 검색 결과가 없을 때 종목명 중심의 단순 검색어로 한 번 더 조회하도록 했습니다.
- [개선] 한국어 리포트의 `Hold and watch` 상태값과 진단 상태 문구를 더 자연스러운 한국어로 표시하도록 정리했습니다.
- [개선] Web AI 모델 설정에서 활성 LLM 채널의 `/models` 목록을 일괄 새로고침하고 최신 모델 선택 목록에 바로 반영할 수 있게 했습니다.
- [수정] yfinance가 날짜 index 이름 없이 MultiIndex 일봉 데이터를 반환하는 경우에도 미국/한국 종목 일봉을 `date` 컬럼으로 정규화하도록 수정했습니다.
- [수정] 주요 한국 종목의 로컬 이름 매핑을 추가해 KRX 분석 리포트와 뉴스 검색어가 `005930.KS` 같은 코드 대신 `삼성전자` 같은 종목명을 사용할 수 있게 했습니다.
- [개선] KRX 종목 뉴스 검색이 중국 A주 키워드 대신 한국어 뉴스, 공시, 실적, 증권사 리포트 키워드를 사용하도록 검색 쿼리를 분리했습니다.
- [개선] 한국어 리포트의 고정 라벨, 상태값, 주요 단위를 자연스러운 한국어로 정리하고 중국어 혼합 표현을 줄였습니다.
- [수정] 한국어 모드의 분석 기록 목록과 시장 리뷰 기록에서 이전 중국어/깨진 인코딩 기록이 그대로 노출되지 않도록 보정했습니다.
- [문서] SearXNG 자가 호스팅 운영 가이드를 추가하고 `.env.example`과 `scripts/check_env.py --search` 검색 점검 명령을 보강했습니다.
- [개선] 한국투자증권 KIS Open API 조회 전용 fetcher를 추가해 한국 종목 현재가와 일봉 데이터를 KIS 우선, yfinance fallback 흐름으로 조회할 수 있게 했습니다.
- [개선] 미국 주식 기본 분석에 SEC EDGAR 공시 이력과 XBRL companyfacts 조회를 추가해 API 키 없이 10-K/10-Q/8-K와 핵심 재무 fact를 보강할 수 있게 했습니다.
- [개선] OpenDART adapter를 추가해 한국 종목 fundamental context에 최근 공시와 단일회사 주요계정 재무 데이터를 병합할 수 있게 했습니다.
- [개선] `REPORT_LANGUAGE=ko`를 기본 리포트 언어로 추가하고 Web 리포트 라벨과 AI 분석 프롬프트가 한국어 출력을 우선하도록 정리했습니다.
- [수정] `REPORT_LANGUAGE` 런타임 기본값과 invalid fallback을 설정 스키마와 같은 `ko`/`en`/`zh` 계약에 맞췄습니다.
- [수정] 분석, 알림, 리포트 렌더링의 설정 기반 언어 fallback이 한국어 기본값을 따르도록 맞췄습니다.
- [수정] 한국어 히스토리 Markdown과 단일 종목 알림 리포트의 이벤트/차트 고정 제목이 중국어로 표시되지 않도록 보정했습니다.
- [수정] Web 리포트 컴포넌트가 언어 값이 없을 때 한국어 기본 문구를 사용하고 영어 리포트 언어를 올바르게 정규화하도록 수정했습니다.
- [수정] Web 리포트 개요에서 관련 섹터와 섹터 등락률 섹션이 다시 표시되도록 복구했습니다.
- [수정] 한국어 리포트 모드의 AI 분석 프롬프트, fallback 문구, 설정 주석에 남아 있던 혼합 언어 표현을 자연스러운 한국어로 정리했습니다.
- [수정] 한국어 리포트 언어 확장 중 기존 중국어 리포트 라벨, placeholder, 분석 프롬프트 호환성이 깨지지 않도록 `zh` 동작을 복구했습니다.
- [개선] 분석 기록 전체 초기화 API와 Web 버튼을 추가하고, 현재 KR/US 기본 흐름과 다른 과거 CN/HK 기록을 legacy 배지로 구분할 수 있게 했습니다.
- [수정] Web 분석 입력 예시와 코드 검증을 KR/US 중심으로 조정해 KRX 코드가 중국 A주로 오인되는 일을 줄였습니다.
- [개선] Web 종목 자동완성에서 한국 종목의 `.KS`/`.KQ` suffix와 `KS`/`KQ` prefix 입력을 같은 후보로 매칭하도록 보강했습니다.
- [개선] 기본 분석 흐름을 KR/US 중심으로 전환하고, 6자리 KRX 후보는 `.KS`/`.KQ` 종목으로 yfinance 경로에서 처리하도록 정리했습니다.
- [수정] 리포트 언어 설정의 기본값과 안내를 실제 지원 범위인 `ko`/`en`/`zh` 기준으로 맞췄습니다.
- [수정] Python 3.14 환경에서 백엔드 테스트용 패키지 설치가 tiktoken 0.11.x PyO3 제한으로 실패하지 않도록 tiktoken 0.13.x 대역을 허용했습니다.
- [테스트] A-share, HK, US 종목의 agent history와 chart analysis smoke test를 추가했습니다.
- [테스트] 차트 분석, paper trading, portfolio analysis의 eval fixture와 회귀 검증을 추가했습니다.
- [개선] Agent analysis map에 도구별 호출 수, 성공 수, 실패 수, timeout, cached count, 평균 실행 시간을 집계하는 tool metrics를 추가했습니다.
- [개선] Vision provider가 없거나 Vision 분석이 실패해도 차트 분석 도구가 기존 수치 기반 분석을 유지하고 fallback 사유를 표시하도록 했습니다.
- [개선] Vision 차트 해석에 evidence 블록을 추가해 VLM 근거, confidence, 불확실성, 수치 분석과의 충돌 여부를 구조화했습니다.
- [개선] Web 리포트에 데이터 신뢰도 판단 상태와 통합 리포트 보드를 추가해 confidence, evidence, risk, chart, event, portfolio 상태를 한 화면에서 확인할 수 있게 했습니다.
- [개선] Alert P6에서 관심 종목, 보유 종목, 계좌 연동 규칙 기반 이벤트 알림 범위와 우선순위 처리를 정리했습니다.
- [테스트] 한국어 기준 API, Bot, 로그 메시지와 배포 문서 명령 예시의 회귀 테스트 기본값을 정리했습니다.
- [개선] 종목 리포트에 핵심 근거, 반대 근거, 데이터 한계, 확신도 사유를 표시하는 분석 메타데이터를 추가했습니다.
- [개선] 종목별 이전 분석과 현재 분석을 비교해 투자 가설 상태와 주요 변경점을 리포트에 표시하는 thesis tracking을 추가했습니다.
- [개선] 종목 리포트의 결론, 근거, 반대 근거, 리스크, 데이터 출처를 연결하는 evidence graph 메타데이터를 추가했습니다.
- [개선] 종목별 변동성, 최대 낙폭, 기술적 위험 플래그, 사용자 주의사항을 도출하는 단일 종목 리스크 엔진을 추가했습니다.
- [개선] 백테스트 요약 diagnostics에 confidence bucket별 성과와 리스크 경고 적중률을 추가했습니다.
- [개선] 이벤트 알림 트리거에 우선순위, thesis 훼손 위험, 모니터링 커버리지 메타데이터를 추가했습니다.
- [개선] Agent 도구에 차트 분석 생성과 paper trading 주문 준비 기능을 연결했습니다.
- [개선] 차트 SVG에 가격 날짜 축, 지지와 저항 레이어, RSI 기준선, MACD histogram과 표시 신호 레이어를 추가했습니다.
- [수정] Bot 자연어 라우팅과 플랫폼 어댑터의 사용자 안내 문구에서 중국어 기반 예시와 안내 문구를 줄이고 한국어와 영어 기준으로 정리했습니다.
- [수정] Web 호스트 설정과 API endpoint의 사용자 노출 오류 문구, 로그, Swagger 설명에 남아 있던 중국어 기반 문구를 한국어와 영어 기준으로 정리했습니다.
- [수정] 비동기 분석 작업 서비스와 WebUI 프런트엔드에서 출력물 준비 로그의 깨진 문자열을 한국어로 복구했습니다.
- [수정] Bot 명령 응답과 Agent API 스트리밍 표시명의 깨진 문자열 및 중국어 기반 사용자 노출 문구를 한국어 기준으로 정리했습니다.
- [수정] Web 화면의 깨진 감정 레이어, 구분자, 과거 리포트 표시 문자열을 한국어로 정리했습니다.
- [개선] LLM 채널 추가 화면의 API Key 저장 위치와 연결 테스트의 비저장 동작을 안내했습니다.
- [수정] AI 모델 설정의 Anthropic 관련 설명에 남아 있던 중국어 문구를 한국어로 교체했습니다.
- [수정] 인증 API 오류 문구와 CLI 안내말의 중국어 기반 사용자 노출 문자열을 한국어 기준으로 정리했습니다.
- [수정] 설정 스키마와 안내말의 중국어 문서 링크와 이전 upstream 문서 링크를 현재 저장소의 한국어 기준으로 정리했습니다.
- [문서] LLM 설정 가이드, 테스트 패키징 가이드, provider 운영 가이드, Zeabur 배포 가이드, 문서 인덱스, OpenClaw Skill 연동 가이드를 현재 흐름 기준의 한국어 문서로 정리했습니다.
- [문서] `.env.example`과 LiteLLM YAML 예시의 깨진 주석을 현재 환경 변수 기준 설명으로 정리했습니다.
- [테스트] Windows 환경에서 Docker entrypoint shell 테스트가 `sh` 부재로 실패하지 않도록 건너뛰기 처리를 추가했습니다.
- [테스트] market analyzer 정적 검사에 UTF-8 인코딩을 명시해 Windows 기본 인코딩 오류를 방지했습니다.
- [ci] PR 리뷰 워크플로의 체크 이름과 자동 리뷰 보고서를 한국어로 정리했습니다.
- [ci] 데스크톱 변경 시 `apps/dsa-desktop` 테스트를 실행하는 CI 게이트를 추가했습니다.
- [chore] 언어 아티팩트 검사 스크립트를 추가하고 CI에서 사용자 노출 영역을 검사하도록 연결했습니다.
- [수정] API 오류 메시지와 Bot 명령 응답에 남아 있던 깨진 문구를 한국어로 정리했습니다.
<!-- 새 항목 형식: - [유형] 설명 (유형: 새기능/개선/수정/문서/테스트/chore) -->
<!-- 각 항목은 [Unreleased] 끝에 한 줄씩 추가하고 별도 분류 제목을 만들지 않습니다. -->
- [개선] `scripts/fetch_tushare_stock_list.py`가 A-share 이름의 `XD`/`XR`/`DR`/`N`/`C` 접두어를 보정해 자동완성 갱신 흐름에서 사용할 수 있게 했습니다.
- [수정] 주식 자동완성 인덱스 생성 시 `pypinyin`이 없으면 바로 실패하게 해 병음 필드가 빠진 저품질 인덱스 생성을 막았습니다.
- [수정] Tencent 실시간 거래량을 주 단위로 정규화해 거래량 변화 배율이 과도하게 커져 분석 보고서를 오도하지 않도록 했습니다.
- [문서] #1391 Phase 0 실행 진단 계약 문서를 추가해 `trace_id`, 진단 요약, 핵심 경로 범위, 탈감, fail-open, 보존 경계를 명확히 했습니다.
- [새기능] #1391 Phase 1 실행 진단 최소 경로를 적용해 작업/SSE에 `trace_id`를 추가하고 일봉 및 실시간 시세 `ProviderRun` 스냅샷을 기록합니다.
- [개선] Web 라우트 페이지를 지연 로딩으로 바꿔 초기 번들 크기를 줄이고 라우트 로딩 실패 복구 안내를 추가했습니다.
- [수정] Docker 기본 배포에서 `.env` 단일 파일 마운트를 제거해 WebUI 설정 저장 시 `os.replace`가 마운트 지점에서 `Device or resource busy`를 유발하지 않도록 했습니다.
- [수정] #1391 Phase 0 A-share 코드 소속 경계를 정리해 `SH`/`SZ` 접두어 시나리오의 일관성을 보강하고 관련 fetcher 수정 범위를 명확히 했습니다.
- [개선] Web 전체 보고서 Markdown drawer를 지연 로딩으로 변경했습니다.
- [개선] 시장 단계 추론 기준을 추가하고 장전, 장중, 점심 휴장, 마감 임박, 장후, 비거래일 의미를 명확히 했습니다.
- [새기능] 알림 센터에 P7 시장 신호등 구조화 규칙을 추가해 `market_light_status`와 `market_light_score_drop`를 지원하고 기존 worker, 트리거 이력, 알림, 쿨다운 경로를 재사용합니다.
- [수정] `STOCK_LIST`에서 bare A-share 코드를 사용할 때 Baostock 등 fallback 데이터 소스의 내부 형식 변환을 복구해 사용자 설정은 6자리 코드로 유지되도록 했습니다.
- [문서] 알림 센터 P8 문서와 설정 마무리 설명을 보강해 legacy JSON, 고급 규칙, Web/API, Docker, GitHub Actions, Desktop 경계를 명확히 했습니다.
- [수정] Windows 데스크톱 자동 업데이트가 사용자 재시작 설치 확인 후 설치기를 조용히 실행하고 내장 백엔드 중지 뒤 프로세스 참조를 정리하도록 했습니다.
- [문서] Windows NSIS 업데이트 설치 경로와 백엔드 프로세스 생명주기 정리만 이번 데스크톱 수정 범위임을 명확히 하고, 잘못 포함됐던 `docker/Dockerfile` `npm registry` 변경을 제거했습니다.
- [수정] macOS 데스크톱 런타임 설정을 사용자 데이터 디렉터리로 옮기고, 이전 `.app` 파일 접근이 가능하면 `.env`, 데이터베이스, 로그를 마이그레이션하도록 했습니다.
- [개선] 런타임 시장 단계 컨텍스트 구성과 fallback 테스트를 추가했습니다.
- [문서] AnalysisContextPack P0 컨텍스트 점검 문서를 추가해 필드 품질 상태, 기존 상태 매핑, 첫 pack 경계를 정리했습니다.
- [새기능] #1391 Phase 2 실행 진단 요약을 적용해 사용자용 `RunDiagnosticSummary`, 기록 보고서 진단 API, 탈감 복사 텍스트를 제공합니다.
- [문서] #1391 Phase 2 구조화 감지 알림이 설정 마이그레이션 신호가 아님을 명확히 하고, 새 진단 경로가 LLM 모델/채널 라우팅 설정을 바꾸지 않는다는 경계를 기록했습니다.
- [새기능] #1391 Phase 3 실행 진단 가시성을 적용해 보고서 상세와 작업 패널에서 상태, trace, 복사 가능한 문제 해결 정보를 접어서 보여줍니다.
- [문서] #1391 Phase 3 호환성 설명을 추가해 백엔드 진단 저장, 기록 조회, 알림 회신 경로 변경 경계와 rollback 전략을 정리했습니다.
- [테스트] #1391 Phase 3 백엔드/API 및 Web 회귀 검사를 `./scripts/ci_gate.sh`, 관련 pytest, `npm run lint`, `npm run build`로 정리했습니다.
- [새기능] AnalysisContextPack P1 내부 계약과 탈감 직렬화 테스트를 추가했습니다.
- [수정] Agent/기록 호환 스냅샷에서 관련 보드와 보드 연동 필드 추출을 복구해 새 홈 보고서에서 보드 연동이 빠지던 회귀를 수정했습니다.
- [개선] Web 설정 도움말에 실제 노출/설정 가능한 필드의 안내 문구를 단계적으로 보강했습니다.
- [수정] Web 설정 도움말에서 legacy 알림 JSON 필드명과 조용한 시간대 전달 의미 설명을 수정했습니다.
- [수정] Web 설정 페이지의 데이터 소스, 알림, 시스템, Agent 영역에서 제목/설명/주요 선택지가 빠지던 문제를 수정했습니다.
- [수정] 질문형 상담 세션 전환과 홈 작업 재연결 뒤 Agent/분석 작업 진행 상태가 남을 수 있는 문제를 수정했습니다.
- [새기능] 질문형 상담에 기본 비활성 상태의 대화 컨텍스트 압축을 추가해 Web 스위치, Agent 고급 preset, rolling summary, 최근 원문 보호를 지원합니다.
- [개선] P2-min으로 LLM prompt에 시장 단계 컨텍스트를 주입했습니다.
- [수정] 질문형 single-agent에 provider-aware trace 분리를 추가해 DeepSeek V4 thinking과 tool-call의 `reasoning_content` 및 도구 프로토콜 자료를 다음 턴에도 보존합니다.

## [3.18.0] - 2026-05-21

### What's Changed

- feat: Add alert-center P2-P6, Web strategy selection, HK/US fundamental context, static-report financial sections, and Finnhub / AlphaVantage US-market fallback.
- improve: Refine LiteLLM parameter recovery, yfinance currency/dividend handling, RSI calculation, market-review presentation, stock-news relevance ranking, and report table rendering.
- fix: Harden desktop packaging/update assets, completed analysis-status responses, AlphaVantage pct_chg routing, portfolio realtime snapshots, alert trigger dedupe, DatabaseManager cold start, and fallback pricing registration.
- docs/tests: Add beginner setup and settings-help docs, document compatibility/rollback boundaries, and extend regression coverage for API, alert, packaging, and release paths.

## [3.17.1] - 2026-05-16

### What's Changed

- fix: Add `--publish never` to the Windows and macOS Electron packaging scripts so tag builds only create local artifacts and GitHub Actions handles release upload and publish.

## Previous Releases

이전 릴리스의 상세 변경 이력은 GitHub Releases에서 확인합니다. 오래된 원문에는 깨진 문자열이 포함되어 있어 현재 문서에서는 사용자에게 필요한 수준의 요약만 유지합니다.

- 3.17.x: Web UI, 데이터 공급망, 분석 안정성 개선
- 3.16.x: 포트폴리오 리포트 표시 개선
- 3.15.x: 분석 워크플로와 배포 경험 개선
- 3.14.x 이하: 기본 분석 기능, 알림, 자동화 문서 개선

[Unreleased]: https://github.com/ZhuLinsen/daily_stock_analysis/compare/v3.18.0...HEAD
[3.18.0]: https://github.com/ZhuLinsen/daily_stock_analysis/compare/v3.17.1...v3.18.0
[3.17.1]: https://github.com/ZhuLinsen/daily_stock_analysis/compare/v3.17.0...v3.17.1

