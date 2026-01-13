import streamlit as st
import json
import pandas as pd
import os
import re

# --------------------------------------------------------------------------
# 1. 페이지 설정 및 디자인
# --------------------------------------------------------------------------
st.set_page_config(page_title="법률 리스크 관리 시스템", layout="wide", page_icon="⚖️")

st.title("⚖️ 기업 맞춤형 법률 리스크 관리 시스템")
st.markdown("##### 🚀 GraphRAG 기반 법률 준수(Compliance) 지원 솔루션")
st.markdown("---")

# --------------------------------------------------------------------------
# 2. 데이터 로드 및 전처리
# --------------------------------------------------------------------------
@st.cache_data
def load_data():
    file_name = 'Law_Graph_Final_v4_risk_propagated.json'
    if not os.path.exists(file_name):
        return None, None
    
    with open(file_name, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    nodes = data.get('nodes', [])
    edges = data.get('edges', [])
    
    df = pd.DataFrame(nodes)
    
    # ARTICLE(조항)만 남기기 및 에러 방지용 컬럼 체크
    if 'node_type' in df.columns:
        df = df[df['node_type'] == 'ARTICLE']
    else:
        # node_type이 아예 없으면 빈 데이터프레임 반환
        return pd.DataFrame(), []
    
    # 결측치 처리 (안전하게)
    if 'risk_level_final' not in df.columns:
        df['risk_level_final'] = 'LOW'
    if 'risk_evidence' not in df.columns:
        df['risk_evidence'] = ''
    if 'law_name' not in df.columns:
        df['law_name'] = ''
    if 'content' not in df.columns:
        df['content'] = ''
        
    return df, edges

nodes_df, edges_data = load_data()

# --------------------------------------------------------------------------
# 3. 사이드바: 기업 프로필 설정
# --------------------------------------------------------------------------
st.sidebar.header("🏢 기업 상세 프로필")

# [설정 1] 업종 선택
industry_map = {
    "건설업": ["건설기계관리법", "건설기술 진흥법", "건설산업기본법", "산업안전보건법"],
    "제조업": ["산업안전보건법", "대기환경보전법", "폐기물관리법", "고압가스 안전관리법"],
    "환경/에너지": ["대기환경보전법", "폐기물관리법", "소방기본법"]
}
industry_options = ["전체 보기"] + list(industry_map.keys())
selected_industry = st.sidebar.selectbox("1. 업종 (Industry)", industry_options)

# [설정 2] 기업 규모
st.sidebar.markdown("---")
size_options = ["전체 보기", "5인 미만", "5인 이상 ~ 50인 미만", "50인 이상 ~ 300인 미만", "300인 이상"]
company_size = st.sidebar.selectbox("2. 기업 규모 (상시 근로자 수)", size_options)
st.sidebar.caption("※ 현재 데이터에는 기업 규모별 적용 여부가 포함되어 있지 않아, 이 항목은 참고용으로만 사용됩니다.")

# [설정 3] 보유 설비 (키워드 매핑)
st.sidebar.markdown("---")
# 설비와 관련된 키워드 정의 (이 단어가 본문에 있으면 필터링)
equipment_keyword_map = {
    "크레인/리프트": ["크레인", "리프트", "기중기", "승강기"],
    "지게차": ["지게차", "운반"],
    "압력용기": ["압력용기", "고압가스", "저장탱크"],
    "소각시설": ["소각", "연소", "배출"],
    "화학물질 저장소": ["화학물질", "유해물질", "저장소", "보관"]
}
equipment_options = list(equipment_keyword_map.keys())
selected_equipment = st.sidebar.multiselect("3. 보유 설비 (관련 조항 검색)", equipment_options)

# [설정 4] 위험도 필터
st.sidebar.markdown("---")
risk_options = ["HIGH", "MEDIUM", "LOW"]
selected_risks = st.sidebar.multiselect(
    "조회할 위험 등급", 
    risk_options, 
    default=["HIGH", "MEDIUM"]
)

# [설정 5] 검색
search_query = st.sidebar.text_input("🔍 키워드 검색")


# --------------------------------------------------------------------------
# 4. 필터링 로직 엔진
# --------------------------------------------------------------------------
if nodes_df is not None and not nodes_df.empty:
    filtered_df = nodes_df.copy()

    # [1] 업종 필터 (법령 이름 기준)
    if selected_industry != "전체 보기":
        target_laws = industry_map.get(selected_industry, [])
        if target_laws:
            filtered_df = filtered_df[filtered_df['law_name'].str.contains('|'.join(target_laws), na=False)]

    # [2] 보유 설비 필터 (본문 내용 기준 - 여기가 핵심!)
    # 설비를 선택했을 때만 로직이 돕니다.
    if selected_equipment:
        # 선택된 설비들의 모든 키워드를 하나로 합칩니다.
        # 예: 크레인 선택 -> ["크레인", "리프트", "기중기", "승강기"]
        target_keywords = []
        for eq in selected_equipment:
            target_keywords.extend(equipment_keyword_map.get(eq, []))
        
        # 키워드 중 하나라도 본문에 포함되어 있으면 추출
        if target_keywords:
            keyword_pattern = '|'.join(target_keywords)
            filtered_df = filtered_df[filtered_df['content'].str.contains(keyword_pattern, na=False)]

    # [3] 위험도 필터
    if selected_risks:
        filtered_df = filtered_df[filtered_df['risk_level_final'].isin(selected_risks)]

    # [4] 검색어 필터
    if search_query:
        filtered_df = filtered_df[filtered_df['content'].str.contains(search_query, na=False)]

    # [5] 정렬
    risk_sort_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "NONE": 3}
    filtered_df['sort_key'] = filtered_df['risk_level_final'].map(risk_sort_order)
    filtered_df = filtered_df.sort_values(by='sort_key')

    # --------------------------------------------------------------------------
    # 5. 메인 대시보드
    # --------------------------------------------------------------------------
    
    # 요약 정보 텍스트 생성
    filter_info = []
    if selected_industry != "전체 보기": filter_info.append(f"업종: {selected_industry}")
    if selected_equipment: filter_info.append(f"설비: {', '.join(selected_equipment)}")
    
    info_text = " / ".join(filter_info) if filter_info else "전체 법령"
    
    st.info(f"📋 **{info_text}** 기준 분석 결과 (총 {len(filtered_df)}건)")

    m1, m2, m3 = st.columns(3)
    high_count = len(filtered_df[filtered_df['risk_level_final']=='HIGH'])
    med_count = len(filtered_df[filtered_df['risk_level_final']=='MEDIUM'])
    
    m1.metric("🔴 치명적 위험", f"{high_count}건")
    m2.metric("🟠 주요 관리 대상", f"{med_count}건")
    m3.metric("🟢 일반 준수 사항", f"{len(filtered_df)-high_count-med_count}건")
    
    st.divider()

  # --------------------------------------------------------------------------
    # [수정됨] 텍스트 하이라이팅 및 데이터 클리닝 함수 (에러 방지 버전)
    # --------------------------------------------------------------------------
    def clean_and_highlight(text, evidence):
        """
        데이터 타입(리스트, 문자열, NaN 등)에 상관없이 안전하게 처리하는 함수
        """
        # 1. None 체크
        if evidence is None:
            return text, None
        
        # 2. 리스트가 아닌 경우에만 isna(NaN) 체크 (리스트에 isna 쓰면 에러남!)
        if not isinstance(evidence, list):
            if pd.isna(evidence):
                return text, None
            if str(evidence).strip() == "":
                return text, None
        
        # 3. 빈 리스트 체크
        if isinstance(evidence, list) and len(evidence) == 0:
            return text, None

        # 4. 문자열로 변환하여 처리 시작
        evidence_str = str(evidence)
        
        # 불필요한 기호 제거
        cleaned_evidence = re.sub(r"[\[\]']", "", evidence_str)
        keywords = [k.strip() for k in cleaned_evidence.split(',')]
        
        stopwords = ["할 수 있다", "하여야 한다", "수 있다", "한다"]
        valid_keywords = [k for k in keywords if k not in stopwords and len(k) > 1]
        
        if not valid_keywords:
            return text, None
            
        highlighted_text = text
        for k in valid_keywords:
            if k in highlighted_text:
                highlighted_text = highlighted_text.replace(k, f":red[**{k}**]")
                
        return highlighted_text, ", ".join(valid_keywords)
    
    # 리스트 출력
    if filtered_df.empty:
        st.warning("조건에 맞는 법률 조항이 없습니다.")
        if selected_equipment:
            st.caption("💡 팁: 선택하신 설비 관련 키워드가 법령 본문에 명시되지 않았을 수 있습니다.")
    else:
        for idx, row in filtered_df.iterrows():
            risk = row['risk_level_final']
            icon = "🔴" if risk == "HIGH" else "🟠" if risk == "MEDIUM" else "🟢"

            law_name = row.get('law_name', '')
            article_no = row.get('article_no', '?')
            title = row['metadata'].get('title', '') if isinstance(row.get('metadata'), dict) else ""

            expander_title = f"{icon} **[{law_name}] 제{article_no}조 {title}**"
            
            with st.expander(expander_title):
                final_content, valid_evidence = clean_and_highlight(row['content'], row.get('risk_evidence', ''))
                
                st.markdown(final_content)
                
                if valid_evidence:
                    st.caption(f"🔎 **AI 리스크 감지:** `{valid_evidence}`")
                
                st.markdown("---")
                c1, c2 = st.columns(2)
                c1.caption(f"ID: {row['node_id']}")
                if row.get('risk_from_penalties_level'):
                    c2.caption(f"⚠️ **처벌 조항 연결됨**")

else:
    st.error("데이터를 불러오지 못했거나 데이터가 비어있습니다.")