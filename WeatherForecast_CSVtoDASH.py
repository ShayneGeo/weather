import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Fire Weather Forecast Viewer", layout="wide")

st.title("🔥 Fire Weather Forecast Viewer")

# --- File Upload or Default ---
default_path = r"C:\Users\magst\Downloads\wildfire_forecast_2025-07-16_06-01.csv"
uploaded_file = st.file_uploader("Upload CSV from Forecast Script", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
elif default_path:
    try:
        df = pd.read_csv(default_path)
        st.info(f"Using default file: `{default_path}`")
    except Exception as e:
        st.error(f"Failed to load default file: {e}")
        st.stop()
else:
    st.warning("Please upload a CSV file to continue.")
    st.stop()

# --- IRWIN ID Input ---
irwin_id = st.text_input("Enter IRWIN ID (e.g., {2F080B1D-203B-467C-A116-2B0887558CB2})")

if st.button("🔍 Show Weather Forecast") and irwin_id:
    fire = df[df['IrwinID'].str.contains(irwin_id, case=False, na=False)]

    if fire.empty:
        st.warning("No fire found with that IRWIN ID.")
    else:
        fire = fire.squeeze()

        st.subheader(f"🔥 {fire['IncidentName']}")
        st.markdown(f"**📍 Location:** ({fire['latitude']:.4f}, {fire['longitude']:.4f})  \n"
                    f"**📏 Size:** {fire['IncidentSize']} acres  \n"
                    f"**🆔 IRWIN ID:** {fire['IrwinID']}  \n"
                    f"**🔗 Forecast URL:** [{fire['forecastURL']}]({fire['forecastURL']})")

        st.subheader("🌤️ 7-Day Forecast Summary")
        for i in range(7):
            start_raw = fire.get(f'startTime_{i}')
            end_raw = fire.get(f'endTime_{i}')

            try:
                start = datetime.fromisoformat(start_raw)
                end = datetime.fromisoformat(end_raw)
                day_name = start.strftime('%A')
                date_label = start.strftime('%B %d, %Y')
                hour_range = f"{start.strftime('%H:%M')}–{end.strftime('%H:%M')}"
                time_label = f"{day_name}, {date_label} | {hour_range}"
            except:
                time_label = f"{start_raw} to {end_raw}"

            st.markdown(f"**--- Period {i+1} ---**")
            st.markdown(f"🕓 `{time_label}`  \n"
                        f"🌡️ Temp: {fire.get(f'temperature_{i}', 'N/A')}°F | "
                        f"Dewpoint: {fire.get(f'dewpoint_{i}', 'N/A')}°C  \n"
                        f"💨 Wind: {fire.get(f'windSpeed_{i}', 'N/A')} from {fire.get(f'windDirection_{i}', 'N/A')}  \n"
                        f"🔎 {fire.get(f'shortForecast_{i}', 'N/A')}  \n"
                        f"📝 {fire.get(f'detailedForecast_{i}', 'N/A')}")

        st.subheader("🧾 Fire Weather Forecast Discussion")
        st.markdown("🔗 [What is this?](https://www.weather.gov/okx/fireexplanation)")
        st.write(fire.get("discussion", "No discussion available"))

# Footer
st.markdown("---")
st.caption("Built for fire situational awareness.")
