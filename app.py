import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium

# 1. API 설정 (보안)
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Secrets에서 API 키를 설정해주세요.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash')

st.set_page_config(page_title="간편 일본 여행 가이드", layout="wide")

st.title("🇯🇵 심플 일본 여행 플래너")

# 2. 사이드바: 최소한의 정보만 입력
with st.sidebar:
    st.header("📋 여행 정보")
    days = st.slider("여행 기간", 1, 7, 3)
    season = st.selectbox("계절", ["봄", "여름", "가을", "겨울"])
    style = st.radio("테마", ["관광 중심", "맛집 탐방", "여유로운 휴식"])

# 3. 지도 설정 (일본 주요 도시)
st.subheader("📍 지역 선택 (마커를 클릭하세요)")

m = folium.Map(location=[36.2048, 138.2529], zoom_start=5)
cities = {
    "도쿄": [35.6895, 139.6917],
    "오사카": [34.6937, 135.5023],
    "후쿠오카": [33.5902, 130.4017],
    "삿포로": [43.0611, 141.3564]
}

for city, coord in cities.items():
    folium.Marker(coord, popup=city, tooltip=city).add_to(m)

map_data = st_folium(m, width=1000, height=400)

selected_city = map_data.get('last_object_clicked_tooltip')

# 4. 일정 생성 (캐싱 적용으로 쿼터 절약)
@st.cache_data
def get_simple_plan(city, d, s, stl):
    prompt = f"{city} {d}일 {s} 여행 {stl} 테마로 가볼만한 곳 위주로 요약해줘."
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "사용량 초과입니다. 잠시 후 다시 시도해주세요."

if selected_city:
    st.success(f"선택됨: {selected_city}")
    if st.button(f"{selected_city} 일정 보기"):
        with st.spinner("일정 생성 중..."):
            plan = get_simple_plan(selected_city, days, season, style)
            st.divider()
            st.markdown(plan)
else:
    st.info("지도의 마커를 클릭하면 일정을 볼 수 있습니다.")
