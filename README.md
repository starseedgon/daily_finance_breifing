# Daily Finance Briefing

한국·미국 주요 금융 지표를 하나의 정적 HTML 브리핑으로 생성하는 Python CLI입니다.
기본 `fixture` provider는 네트워크를 사용하지 않으므로 로컬과 CI에서 항상 같은 결과를
만듭니다. `fdr` provider는 FinanceDataReader로 최신 실제 데이터를 조회합니다.

## 로컬 실행

```bash
python -m finance_briefing --provider fixture --date 2026-08-15 --output-dir public
```

명령은 `public/2026-08-15.html`, 같은 내용을 가리키는 `public/latest.html`, Pages의
진입점인 `public/index.html`을 생성합니다. 실제 데이터에 필요한 런타임 의존성은 패키지와 함께 설치됩니다.

```bash
python -m pip install -e .
python -m finance_briefing --provider fdr --output-dir public
```

`--date`를 생략하면 UTC 오늘 날짜를 사용합니다. 데이터가 없는 지표는 실패시키지 않고
HTML에 `데이터 없음`으로 표시하며, 실행 로그에는 지표별 기준일과 누락 비율을 기록합니다.

## 테스트

```bash
python -m unittest discover -s tests -v
RUN_FDR_INTEGRATION=1 python -m unittest tests.test_fdr_integration -v
```

integration test는 명시적으로 환경 변수를 설정한 경우에만 네트워크를 사용합니다.

## GitHub Actions / Pages

`.github/workflows/daily-market-summary.yml`은 수동 실행과 평일 UTC 22:20 예약 실행을 지원합니다.
생성 결과를 artifact로 보존하고 GitHub Pages에도 배포합니다. 저장소의 **Settings → Pages**에서
Source를 **GitHub Actions**로 설정해야 합니다. 최초 1~2주는 Actions 로그의 실행 시작 시각,
각 지표의 `as_of`, `missing_ratio`를 관찰한 뒤 예약 실행 시각을 조정하세요.
