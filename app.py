import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium

# 1. API 설정
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash')

st.set_page_config(page_title="재팬 루트 마스터", layout="wide")

st.title("🇯🇵 일본 지역별 맞춤 여행 일정 플래너")

# 2. 사이드바: 여행 정보 입력
with st.sidebar:
    st.header("✈️ 여행 기본 정보")
    days = st.slider("여행 기간 (일)", 1, 14, 3)
    season = st.selectbox("계절", ["봄 (벚꽃)", "여름 (축제)", "가을 (단풍)", "겨울 (눈/온천)"])
    style = st.multiselect("여행 스타일", ["미식", "쇼핑", "역사/문화", "자연/휴양", "인스타 핫플"], default=["미식"])
    budget_level = st.radio("예상 경비 수준", ["가성비", "표준", "럭셔리"])

# 3. 메인: 지역 선택 지도
st.subheader("📍 방문할 지역을 지도로 선택하세요")

# 일본 주요 도시 좌표
cities = {
    "도쿄": [35.6895, 139.6917],
    "오사카": [34.6937, 135.5023],
    "후쿠오카": [33.5902, 130.4017],
    "삿포로": [43.0611, 141.3564],
    "오키나와": [26.2124, 127.6809]
}

m = folium.Map(location=[36.2048, 138.2529], zoom_start=5)
for city, coord in cities.items():
    folium.Marker(
        coord, 
        popup=city, 
        tooltip=city,
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

# 지도 표시 및 클릭 데이터 수집
map_data = st_folium(m, width=1200, height=400)

selected_city = None
if map_data['last_object_clicked_tooltip']:
    selected_city = map_data['last_object_clicked_tooltip']
    st.success(f"선택된 지역: **{selected_city}**")

# 4. 일정 생성 버튼
if selected_city and st.button(f"✨ {selected_city} {days}일 일정 생성하기"):
    with st.spinner(f"{selected_city}의 최적 동선을 계산 중입니다..."):
        
        prompt = f"""
        당신은 일본 여행 전문 가이드입니다.
        지역: {selected_city}
        기간: {days}일
        계절: {season}
        스타일: {', '.join(style)}
        경비수준: {budget_level}

        요구사항:
        1. 일자별 상세 일정을 만드세요.
        2. 각 장소 뒤에 구글맵 링크를 [Google Maps](https://www.google.com/maps/search/?api=1&query=장소이름) 형식으로 첨부하세요.
        3. 전체 예상 경비(항공권 제외 현지 비용)를 엔화(JPY)와 원화(KRW)로 산출하세요.
        4. 해당 계절에 꼭 먹어야 할 음식 3가지를 추천하세요.
        """
        
        response = model.generate_content(prompt)
        st.divider()
        st.markdown(response.text)

elif not selected_city:
    st.info("지도 위의 마커를 클릭하여 여행지를 선택해 주세요.")
