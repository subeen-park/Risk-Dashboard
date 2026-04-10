

🗂️ Jira Aging Analyzer: 리소스 정체 구간 분석 대시보드 🗂️
> "데이터를 통해 프로젝트의 병목을 선제적으로 발견하고 의사결정을 지원합니다."
본 프로젝트는 Jira API를 활용하여 프로젝트 내 정체된 티켓을 실시간으로 탐지하고, 담당자 및 업무 유형별 리소스 병목 현황을 시각화하는 PM 전용 리스크 관리 관제탑입니다.
기존에 작성해 드린 README 구성에 설치 및 실행 방법을 구체화하여 통합한 최종 버전입니다. 이 내용을 그대로 README.md 파일에 사용하시면 됩니다

---

## 1. 기획 배경
* **기존 문제점:** 프로젝트 규모가 커지면서 관리 대상 티켓이 수천 건(4,000건+)에 달해, 어떤 작업이 어디서 멈춰있는지 PM이 일일이 확인하기 불가능해졌습니다.
* **리스크:** 특정 담당자에게 업무가 몰리거나 의사결정이 지연되어 티켓이 방치되는 현상이 발생해도, 전체 지표에 가려져 선제적 대응이 어렵습니다.
* **해결 아이디어:** Jira API를 통해 모든 티켓의 업데이트 기록을 분석, 설정한 임계치(예: 3일) 이상 멈춰있는 티켓만 골라내어 **'담당자별/유형별 병목 현황'**을 시각화합니다.

## 2. 주요 기능 
* **동적 정체탐지 시스템**
    * `위험 경고 슬라이더`: PM이 상황에 맞춰 '정체'의 기준(3일~14일)을 실시간으로 조절하며 리스크 수준을 시뮬레이션 가능.
    * `상태별 필터링`: '해결/완료'를 제외한 순수 활성 티켓 중 실제 정체 중인 작업만 정밀 타격하여 데이터 신뢰도 확보.

* **병목 담당자 Top 10 리더보드**
    * `실시간 리스크 랭킹`: 정체 티켓을 가장 많이 보유한 담당자 10명을 즉시 식별하여 리소스 재배치 근거 마련.
    * `상세 보기 팝업`: 담당자 이름을 클릭하면 해당 인원의 지연 티켓 목록과 사유를 별도 창(Dialog)으로 띄워 심층 분석 지원.

* **업무유형별 병목 시각화**
    * `상태가 아닌 유형 기준`: '대기/진행' 같은 단순 상태가 아니라 버그/개선/작업 등 업무 성격별 정체 일수 총합을 막대 그래프로 제공.
    * `교차 분석`: 어떤 유형의 업무가 프로젝트 전반의 속도를 갉아먹고 있는지 구조적 분석 가능.

## 3. 기술 스택 
* **Language:** Python 3.x
* **Frontend:** Streamlit (Web Dashboard Framework)
* **API & Data:** Jira Software SDK, Pandas
* **Optimization:** Streamlit Cache (TTL 600s) 적용으로 대용량 데이터 조회 속도 최적화


## 4. 설치 및 실행 방법 (Installation)

1. **Repository Clone**
    ```bash
    git clone [https://github.com/subeen-park/Jira-Aging-Analyzer.git](https://github.com/subeen-park/Jira-Aging-Analyzer.git)
    cd Jira-Aging-Analyzer
    ```

2. **필수 라이브러리 설치**
    ```bash
    pip install streamlit pandas jira plotly
    ```

3. **환경 설정 (Secrets)**
    `.streamlit/secrets.toml` 파일을 생성하고 아래 정보를 입력합니다. (해당 파일은 보안을 위해 `.gitignore`에 등록되어 있습니다.)
    ```toml
    JIRA_EMAIL = "your-email@example.com"
    JIRA_TOKEN = "your-jira-api-token"
    JIRA_SERVER = "[https://your-domain.atlassian.net/](https://your-domain.atlassian.net/)"
    TARGET_PROJECT = "YOUR_PROJECT_KEY"
    ```

4. **대시보드 실행**
    ```bash
    streamlit run aging_report.py
    ```


💡 PM의 한마디 (Insight)
PM의 역할은 단순히 '일해달라'고 독촉하는 것이 아니라, '왜 일이 안 돌아가는지'를 데이터를 통해 증명하고 그 방해물을 치워주는 것이라 생각합니다. 
이 툴은 팀원 개개인을 비난하기 위함이 아니라, 우리 팀의 프로세스 중 어느 곳에 윤활유가 필요한지 찾아내는 조직의 체력 검진 도구입니다.


👤 Contact
Name: [subeen park]
Role: Project Manager / QA
GitHub: [https://github.com/subeen-park]
