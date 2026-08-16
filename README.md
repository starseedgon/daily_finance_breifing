# Daily Finance Briefing

한국·미국 주요 금융 지표를 하나의 정적 HTML 브리핑으로 생성하는 Python CLI입니다.
기본 `fixture` provider는 네트워크를 사용하지 않으므로 로컬과 CI에서 항상 같은 결과를
만듭니다. `fdr` provider는 FinanceDataReader로 최신 실제 데이터를 조회합니다.

## 로컬 실행

```bash
python -m finance_briefing --provider fixture --date 2026-08-15 --output-dir site
```

명령은 `site/2026/08/market-summary-2026-08-15.html`과 동일 경로의 JSON 데이터 및
실행 manifest를 생성합니다. `site/latest.html`과 Pages 진입점인 `site/index.html`은 최신
HTML의 복사본입니다. 실제 데이터는 선택 의존성을 설치해 실행합니다.

```bash
python -m pip install -e '.[live]'
python -m finance_briefing --provider fdr --output-dir site
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

`.github/workflows/publish.yml`은 수동 실행과 평일 UTC 22:20 예약 실행을 지원합니다.
당일 HTML, JSON, 실행 manifest는 일반 Actions artifact로 보존하고, 누적된 `site/` 전체는
공식 Pages artifact 및 배포 액션으로 배포합니다. 과거 일별 결과 보존 전략으로 전용
`gh-pages` 브랜치를 사용합니다. 워크플로는 기존 브랜치 내용을 `site/`에 복원한 뒤 새 결과를
추가하므로 다음 Pages 배포에서도 과거 URL이 유지되며, 기본 소스 브랜치에는 생성 파일을
커밋하지 않습니다.

저장소의 **Settings → Pages**에서 Source를 **GitHub Actions**로 설정하고, `gh-pages` 브랜치만
쓸 수 있는 fine-grained token(Contents: write)을 Actions secret `PAGES_BRANCH_TOKEN`으로
등록해야 합니다. 워크플로 자체의 `GITHUB_TOKEN` 권한은 `contents: read`, `pages: write`,
`id-token: write`로 제한됩니다. 최초 1~2주는 Actions 로그의 실행 시작 시각, 각 지표의
`as_of`, `missing_ratio`를 관찰한 뒤 예약 실행 시각을 조정하세요.
