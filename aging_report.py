import streamlit as st
import pandas as pd
from jira import JIRA
from datetime import datetime, timezone
import plotly.express as px
import time

# ==========================================
# 0. 페이지 설정 및 초기 로딩
# ==========================================
st.set_page_config(page_title="리소스 리스크 관제탑", page_icon="💭", layout="wide")

if 'loaded' not in st.session_state:
    loading_placeholder = st.empty()
    with loading_placeholder.container():
        st.markdown("<br><br><br><br><br><h2 style='text-align: center; color: #7C3AED;'>Jira 데이터 동기화 중...</h2>", unsafe_allow_html=True)
        progress_bar = st.progress(0)
        for percent_complete in range(100):
            time.sleep(0.01) 
            progress_bar.progress(percent_complete + 1)
    loading_placeholder.empty()
    st.session_state.loaded = True

# ==========================================
# 1. 설정 및 데이터 추출 (✨ 가장 안정적인 엔진으로 롤백!)
# ==========================================
JIRA_SERVER = st.secrets["JIRA_SERVER"]
TARGET_PROJECT = st.secrets["TARGET_PROJECT"]

@st.cache_resource
def init_jira():
    return JIRA(server=JIRA_SERVER, basic_auth=(st.secrets["JIRA_EMAIL"], st.secrets["JIRA_TOKEN"]))

@st.cache_data(ttl=600)
def get_aging_data(project_key):
    jira = init_jira()
    
    # [롤백] 조회 기간을 다시 -90d로 넓히고, 해결된 상태는 철저히 제외합니다.
    query = f'project = "{project_key}" AND status NOT IN ("Done", "완료", "Closed", "Resolved", "해결") AND updated >= -90d'
    target_fields = "summary,status,assignee,updated,issuetype,duedate"
    
    # [롤백] maxResults=False 로 되돌려 데이터 누락 없이 지라에서 끝까지 긁어옵니다.
    issues = jira.search_issues(query, maxResults=False, fields=target_fields)
    
    data = []
    now = datetime.now(timezone.utc)
    today_date = now.date()

    for issue in issues:
        last_updated = datetime.strptime(issue.fields.updated, '%Y-%m-%dT%H:%M:%S.%f%z')
        aging_days = (now - last_updated).days
        
        due_date_str = getattr(issue.fields, 'duedate', None)
        is_overdue = False
        if due_date_str:
            due_date_obj = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            if due_date_obj < today_date: is_overdue = True

        data.append({
            "업무유형": issue.fields.issuetype.name,
            "티켓번호": issue.key,
            "요약": issue.fields.summary,
            "담당자": issue.fields.assignee.displayName if issue.fields.assignee else "미정",
            "현재상태": issue.fields.status.name,
            "정체기간(일)": aging_days,
            "기한": due_date_str if due_date_str else "누락 🚨",
            "지연여부": "지연 됨 ❌" if is_overdue else ("정상" if due_date_str else "-"),
            "링크": f"{JIRA_SERVER}browse/{issue.key}"
        })
    return pd.DataFrame(data)

# ==========================================
# 2. 팝업(Dialog) 함수 (Top 10 상세 보기용)
# ==========================================
@st.dialog("상세 리스크 현황", width="large")
def show_assignee_details(assignee_name, df):
    st.markdown(f"### 👤 {assignee_name}님의 정체/지연 티켓 목록")
    target_df = df[df["담당자"] == assignee_name].sort_values(by="정체기간(일)", ascending=False)
    st.dataframe(
        target_df[["티켓번호", "요약", "현재상태", "정체기간(일)", "링크"]], 
        column_config={"요약": st.column_config.TextColumn("작업 요약", width="large"), "링크": st.column_config.LinkColumn("Jira")},
        use_container_width=True, hide_index=True
    )

# ==========================================
# 3. 대시보드 UI (최신 상하 배치 레이아웃 유지)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    div[data-testid="metric-container"] {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; padding: 15px; border-radius: 12px;
    }
    div.stButton > button:first-child { border-color: #7C3AED; color: #7C3AED; border-radius: 8px; }
    div.stButton > button:first-child:hover { background-color: #7C3AED; color: white; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h2 style='color: #1E293B;'>Project Manager <span style='font-size:12px; color:#7C3AED;'>TOOLS</span></h2>", unsafe_allow_html=True)
    st.caption("리소스 리스크 관제탑")
    st.divider()
    st.markdown("**👤 PM 포트폴리오**")
    st.caption("© 2026 SOOP PM")

st.markdown("### 🗂️ 리소스 정체 구간(Aging) 분석 대시보드")
raw_df = get_aging_data(TARGET_PROJECT)

if not raw_df.empty:
    with st.container(border=True):
        risk_threshold = st.slider("⚠️ 위험 경고 기준 (해당 일수 이상 정체된 티켓)", 1, 14, 3)

    high_risk_df = raw_df[raw_df["정체기간(일)"] >= risk_threshold]

    st.write("")
    m1, m2, m3 = st.columns(3)
    m1.metric("총 관리 대상", f"{len(raw_df)}건")
    m2.metric("⚠️ 정체 리스크", f"{len(high_risk_df)}건", delta=f"{risk_threshold}일+", delta_color="inverse")
    m3.metric("최대 정체", f"{raw_df['정체기간(일)'].max()}일" if not raw_df.empty else "0일")

    st.write("")

# 3. 🏆 병목 담당자 Top 10 (메인 화면 상단 유지)
    st.markdown(f"**🏆 병목 담당자 Top 10 (클릭 시 상세 팝업)**")
    if not high_risk_df.empty:
        top_assignees = high_risk_df['담당자'].value_counts().head(10).reset_index()
        top_assignees.columns = ['담당자', '건수']
        cols = st.columns(5)
        for i, row in top_assignees.iterrows():
            with cols[i % 5]:
                with st.container(border=True):
                    st.write(f"**{i+1}. {row['담당자']}**")
                    st.caption(f"🚨 {row['건수']}건")
                    
                    # 👇 이 두 줄이 실수로 빠져있었습니다! 다시 추가해 주세요! 👇
                    if st.button("🔍 상세 보기", key=f"btn_top10_{i}", use_container_width=True):
                        show_assignee_details(row['담당자'], high_risk_df)
    
    st.divider()

    tab_aging, tab_due = st.tabs(["⏳ 정체 티켓 (Aging)", "🚨 일정 리스크"])

    with tab_aging:
        with st.container(border=True):
            st.markdown(f"**⚠️ {risk_threshold}일 이상 정체 명단**")
            
            c_empty, c_search = st.columns([1, 1])
            with c_search:
                all_assignees = sorted(high_risk_df["담당자"].unique()) if not high_risk_df.empty else []
                selected_assignees = st.multiselect("👤 담당자 검색/필터링", options=all_assignees, placeholder="이름을 선택하세요...")

            list_df = high_risk_df[high_risk_df["담당자"].isin(selected_assignees)] if selected_assignees else high_risk_df

            if list_df.empty:
                st.info("조건에 맞는 정체 티켓이 없습니다.")
            else:
                issue_types = sorted(list_df["업무유형"].unique())
                sub_tabs = st.tabs([f"{itype} ({len(list_df[list_df['업무유형'] == itype])})" for itype in issue_types])
                for i, t in enumerate(sub_tabs):
                    with t:
                        filtered_df = list_df[list_df["업무유형"] == issue_types[i]]
                        st.dataframe(
                            filtered_df[["티켓번호", "요약", "담당자", "현재상태", "정체기간(일)", "링크"]].sort_values(by="정체기간(일)", ascending=False), 
                            column_config={"요약": st.column_config.TextColumn("작업 요약", width="large"), "링크": st.column_config.LinkColumn("Jira", display_text="열기")},
                            use_container_width=True, hide_index=True
                        )

        st.write("")

        with st.container(border=True):
            st.markdown("**📊 업무유형별 병목(Bottleneck) 현황**")
            chart_df = raw_df[raw_df["담당자"].isin(selected_assignees)] if selected_assignees else raw_df
            
            fig = px.bar(chart_df, x="업무유형", y="정체기간(일)", color="현재상태", 
                         color_discrete_sequence=px.colors.qualitative.Pastel,
                         labels={"정체기간(일)": "정체 일수 총합", "업무유형": "이슈 유형"})
            fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=450)
            st.plotly_chart(fig, use_container_width=True)

    with tab_due:
        missing_dates_df = raw_df[raw_df["기한"] == "누락 🚨"]
        overdue_df = raw_df[raw_df["지연여부"] == "지연 됨 ❌"]

        with st.container(border=True):
            st.markdown("### ❓ 기한(Due Date) 누락 작업")
            if missing_dates_df.empty: st.success("누락된 티켓이 없습니다!")
            else: st.dataframe(missing_dates_df[["티켓번호", "요약", "담당자", "링크"]], column_config={"요약": st.column_config.TextColumn("작업 요약", width="large"), "링크": st.column_config.LinkColumn("Jira", display_text="열기")}, use_container_width=True, hide_index=True)
            
        st.write("")
        
        with st.container(border=True):
            st.markdown("### ⏰ 기한(Due Date) 지연 작업")
            if overdue_df.empty: st.success("지연된 티켓이 없습니다!")
            else: st.dataframe(overdue_df[["티켓번호", "요약", "담당자", "기한", "링크"]], column_config={"요약": st.column_config.TextColumn("작업 요약", width="large"), "링크": st.column_config.LinkColumn("Jira", display_text="열기")}, use_container_width=True, hide_index=True)

else:
    st.info("조건에 맞는 데이터가 없습니다.")