import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# 페이지 설정
st.set_page_config(
    page_title="화성 지형 탐사 & 기상 관측소",
    page_icon="🚀",
    layout="wide"
)

# API 키 설정 (secrets.toml 우선, 없을 경우 제공된 API 키 기본 사용)
API_KEY = st.secrets.get("NASA_API_KEY", "GQKzD8DdCTg8nppRqGprmCPqNCMbPJphJCd6g8bh")

st.title("🚀 화성 지형 탐사 & 인사이트 기상 관측소")
st.caption("NASA Open API 및 WMTS 타일 서비스를 활용한 인터랙티브 우주 탐사 앱")

# 탭 구성
tab1, tab2 = st.tabs(["🌍 행성 지형 탐사 (WMTS)", "🌡️ 화성 기상 관측 (InSight)"])

# ---------------------------------------------------------
# TAB 1: WMTS 연동 행성 지형 지도
# ---------------------------------------------------------
with tab1:
    st.header("화성 및 달 인터랙티브 지형 지도")
    st.write("NASA Trek WMTS 타일 레이어를 통해 화성과 달의 고해상도 표면을 탐사할 수 있습니다.")
    
    col_select, _ = st.columns([1, 2])
    with col_select:
        selected_body = st.selectbox("탐사할 천체를 선택하세요", ["화성 (Mars)", "달 (Moon)"])
    
    if selected_body == "화성 (Mars)":
        tile_url = "https://trek.nasa.gov/tiles/Mars/EQ/Mars_Viking_MDIM21_ClrIndex_global_232m/1.0.0/default/default028mm/{z}/{y}/{x}.jpg"
        attr = "NASA Trek / JPL"
        init_location = [0, 0]
        zoom_start = 2
    else:
        tile_url = "https://trek.nasa.gov/tiles/Moon/EQ/LRO_LROC_WAC_Global_100m_June2013/1.0.0/default/default028mm/{z}/{y}/{x}.jpg"
        attr = "NASA Trek / LROC"
        init_location = [0, 0]
        zoom_start = 2

    # Folium 지도 생성
    m = folium.Map(
        location=init_location,
        zoom_start=zoom_start,
        tiles=tile_url,
        attr=attr,
        crs="EPSG3857"
    )

    # 주요 탐사선 착륙 위치 마커 추가
    if selected_body =# ---------------------------------------------------------
# TAB 1: OpenPlanetary 타일 연동 행성 지형 지도
# ---------------------------------------------------------
with tab1:
    st.header("화성 및 달 인터랙티브 지형 지도")
    st.write("OpenPlanetaryMap의 Web Mercator 타일을 적용하여 화성과 달의 지형을 탐사합니다.")
    
    col_select, _ = st.columns([1, 2])
    with col_select:
        selected_body = st.selectbox("탐사할 천체를 선택하세요", ["화성 (Mars - Viking Color)", "화성 (Mars - MOLA Elevation)", "달 (Moon)"])
    
    # Folium과 100% 호환되는 OpenPlanetary 타일 URL
    if "Viking" in selected_body:
        tile_url = "https://s3-eu-west-1.amazonaws.com/whereonmars.cartodb.net/celestia_mars-viking-mosaics/{z}/{x}/{y}.png"
        attr = "OpenPlanetaryMap / NASA Viking Mosaic"
        init_location = [0, 0]
        zoom_start = 2
    elif "MOLA" in selected_body:
        tile_url = "https://s3-eu-west-1.amazonaws.com/whereonmars.cartodb.net/mola-color/{z}/{x}/{y}.png"
        attr = "OpenPlanetaryMap / NASA MOLA Elevation"
        init_location = [0, 0]
        zoom_start = 2
    else:
        tile_url = "https://s3-eu-west-1.amazonaws.com/whereonmars.cartodb.net/moon-color/{z}/{x}/{y}.png"
        attr = "OpenPlanetaryMap / USGS Moon Map"
        init_location = [0, 0]
        zoom_start = 2

    # Folium 지도 생성 (max_zoom=5 로 제한하여 미지원 타일 요청 방지)
    m = folium.Map(
        location=init_location,
        zoom_start=zoom_start,
        max_zoom=5,
        tiles=tile_url,
        attr=attr
    )

    # 주요 탐사선 착륙 위치 마커
    if "Mars" in selected_body:
        folium.Marker(
            [4.5, 135.6],
            popup="InSight 착륙지 (Elysium Planitia)",
            tooltip="InSight Lander",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)
        folium.Marker(
            [18.4, 77.5],
            popup="Perseverance 로버 (Jezero Crater)",
            tooltip="Perseverance Rover",
            icon=folium.Icon(color="orange", icon="star")
        ).add_to(m)
        folium.Marker(
            [-4.6, 137.4],
            popup="Curiosity 로버 (Gale Crater)",
            tooltip="Curiosity Rover",
            icon=folium.Icon(color="blue", icon="flag")
        ).add_to(m)

    st_folium(m, width="100%", height=550)
# ---------------------------------------------------------
# TAB 2: 인사이트(InSight) 화성 기상 데이터 시각화
# ---------------------------------------------------------
with tab2:
    st.header("인사이트(InSight) 화성 기상 관측 데이터")

    @st.cache_data(ttl=3600)
    def fetch_mars_weather(api_key):
        url = f"https://api.nasa.gov/insight_weather/?api_key={api_key}&feedtype=json&ver=1.0"
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            st.error(f"API 호출 중 오류가 발생했습니다: {e}")
        return None

    weather_data = fetch_mars_weather(API_KEY)

    if weather_data and "sol_keys" in weather_data and weather_data["sol_keys"]:
        sol_keys = weather_data["sol_keys"]
        
        parsed_data = []
        for sol in sol_keys:
            sol_info = weather_data.get(sol, {})
            temp_info = sol_info.get("AT", {})
            wind_info = sol_info.get("HWS", {})
            press_info = sol_info.get("PRE", {})
            
            parsed_data.append({
                "Sol (화성일)": sol,
                "평균 기온 (°C)": temp_info.get("av"),
                "최저 기온 (°C)": temp_info.get("mn"),
                "최고 기온 (°C)": temp_info.get("mx"),
                "평균 풍속 (m/s)": wind_info.get("av"),
                "평균 기압 (Pa)": press_info.get("av")
            })
        
        df = pd.DataFrame(parsed_data)

        # 요약 메트릭 표시
        latest_sol = df.iloc[-1]
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("최근 관측 Sol", f"Sol {latest_sol['Sol (화성일)']}")
        
        avg_temp = latest_sol['평균 기온 (°C)']
        col2.metric("평균 기온", f"{avg_temp:.1f} °C" if pd.notnull(avg_temp) else "N/A")
        
        avg_wind = latest_sol['평균 풍속 (m/s)']
        col3.metric("평균 풍속", f"{avg_wind:.1f} m/s" if pd.notnull(avg_wind) else "N/A")
        
        avg_press = latest_sol['평균 기압 (Pa)']
        col4.metric("평균 기압", f"{avg_press:.1f} Pa" if pd.notnull(avg_press) else "N/A")

        st.markdown("---")
        st.subheader("📊 화성일(Sol)별 기온 추이")
        
        fig_temp = px.line(
            df, 
            x="Sol (화성일)", 
            y=["최저 기온 (°C)", "평균 기온 (°C)", "최고 기온 (°C)"],
            markers=True,
            color_discrete_sequence=["#00b4d8", "#e76f51", "#f4a261"]
        )
        fig_temp.update_layout(xaxis_title="화성일 (Sol)", yaxis_title="기온 (°C)", hovermode="x unified")
        st.plotly_chart(fig_temp, use_container_width=True)

        with st.expander("📄 전체 수집 데이터 보기"):
            st.dataframe(df, use_container_width=True)
            
    else:
        st.info("💡 InSight API에서 수집된 최근 데이터가 없어 샘플 시각화 데이터로 대체 표시합니다.")
        
        sample_df = pd.DataFrame({
            "Sol (화성일)": ["575", "576", "577", "578", "579"],
            "평균 기온 (°C)": [-61.2, -62.5, -61.0, -63.1, -62.8],
            "최저 기온 (°C)": [-95.1, -96.0, -94.8, -97.2, -96.5],
            "최고 기온 (°C)": [-12.5, -13.1, -11.8, -14.0, -13.2],
            "평균 풍속 (m/s)": [4.8, 5.2, 4.5, 5.0, 4.9]
        })
        
        fig_sample = px.line(
            sample_df, 
            x="Sol (화성일)", 
            y=["최저 기온 (°C)", "평균 기온 (°C)", "최고 기온 (°C)"], 
            markers=True,
            title="[샘플] Sol별 화성 기온 추이"
        )
        st.plotly_chart(fig_sample, use_container_width=True)
        st.dataframe(sample_df, use_container_width=True)
