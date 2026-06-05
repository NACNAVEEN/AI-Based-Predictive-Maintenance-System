import streamlit as st
import requests
import pandas as pd
import datetime
import os


# Set page configuration
st.set_page_config(
    page_title="Predictive Maintenance Center",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling using markdown
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stAlert {
        border-radius: 8px;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
    }
    h1 {
        color: #1e293b;
        font-family: 'Outfit', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# App Title & Layout
st.title("⚙️ Predictive Maintenance Control Center")
st.markdown("Monitor machine health, predict potential hardware failures, and audit historical telemetry logs in real time.")

# Sidebar Configuration
st.sidebar.header("🔌 Connection Settings")
default_api_url = os.environ.get("API_BASE_URL", "https://ai-based-predictive-maintenance-system.onrender.com")
api_base_url = st.sidebar.text_input(
    "FastAPI API Base URL",
    value=default_api_url,
    help="Enter your local URL (http://localhost:8000) or Render backend URL (https://<app>.onrender.com)"
).strip().rstrip("/")

# Check API health
try:
    response = requests.get(f"{api_base_url}/")
    if response.status_code == 200:
        st.sidebar.success("🟢 Connected to API successfully")
    else:
        st.sidebar.warning(f"🟡 API responded with code: {response.status_code}")
except Exception:
    st.sidebar.error("🔴 Disconnected from API. Please ensure the backend is running.")

# Create tabs
tab_prediction, tab_history = st.tabs(["🔮 Run Diagnostic Prediction", "📊 System Audit Logs"])

# Tab 1: Single Prediction Diagnostic
with tab_prediction:
    st.header("⚡ Diagnostic Telemetry Input")
    st.write("Provide the current operating parameters of the machine to evaluate mechanical risk:")

    # Design layout with columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🛠️ Machine Settings")
        machine_type = st.selectbox("Machine Type (Grade)", ["L", "M", "H"], index=1, help="L = Low grade, M = Medium grade, H = High grade")
        
        # Ranges based on dataset characteristics
        air_temp = st.slider("Air Temperature [K]", min_value=290.0, max_value=315.0, value=298.1, step=0.1, help="Ambient temperature around the machine.")
        process_temp = st.slider("Process Temperature [K]", min_value=290.0, max_value=320.0, value=308.6, step=0.1, help="Operating temperature generated during operation.")

    with col2:
        st.subheader("⚙️ Mechanical Metrics")
        rot_speed = st.number_input("Rotational Speed [rpm]", min_value=1000, max_value=3000, value=1500, step=50, help="Spindle rotational speed.")
        torque = st.slider("Torque [Nm]", min_value=5.0, max_value=80.0, value=40.0, step=0.1, help="Mechanical torque exerted.")
        tool_wear = st.slider("Tool Wear [min]", min_value=0, max_value=250, value=10, step=1, help="Duration of tool usage in minutes.")

    # Calculate engineered features dynamically for visual reference
    temp_diff = round(process_temp - air_temp, 2)
    mech_stress = round(rot_speed * torque, 2)
    wear_stress = round(tool_wear * torque, 2)

    # Display real-time calculated features
    st.markdown("### 🧮 Engineered Feature Previews (Calculated on the fly)")
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    with feat_col1:
        st.metric(label="Temperature Difference [K]", value=f"{temp_diff} K")
    with feat_col2:
        st.metric(label="Mechanical Stress [rpm * Nm]", value=f"{mech_stress:,}")
    with feat_col3:
        st.metric(label="Wear Stress Index [min * Nm]", value=f"{wear_stress:,}")

    # Predict button
    if st.button("🔍 Run Diagnostic Prediction", type="primary", width="stretch"):
        payload = {
            "Type": machine_type,
            "Air_temperature_K": air_temp,
            "Process_temperature_K": process_temp,
            "Rotational_speed_rpm": int(rot_speed),
            "Torque_Nm": torque,
            "Tool_wear_min": int(tool_wear)
        }

        with st.spinner("Analyzing telemetry metrics..."):
            try:
                predict_url = f"{api_base_url}/predict"
                res = requests.post(predict_url, json=payload)
                
                if res.status_code == 200:
                    result = res.json()
                    prediction = result["prediction"]
                    prob = result["failure_probability"]
                    risk = result["risk_category"]

                    st.markdown("---")
                    st.subheader("📊 Diagnostic Diagnosis")

                    res_col1, res_col2 = st.columns([1, 2])

                    with res_col1:
                        # Risk status color codes
                        if risk == "Low":
                            color = "green"
                            bg = "#e6f4ea"
                        elif risk == "Medium":
                            color = "orange"
                            bg = "#fff3cd"
                        elif risk == "High":
                            color = "darkorange"
                            bg = "#ffe8d6"
                        else:
                            color = "red"
                            bg = "#fce8e6"

                        st.markdown(f"""
                            <div class="metric-card" style="background-color: {bg}; border-color: {color}; text-align: center;">
                                <h4 style="color: #495057; margin:0;">Risk Level</h4>
                                <h1 style="color: {color}; margin: 10px 0; font-size: 2.5rem;">{risk}</h1>
                                <p style="color: #6c757d; margin:0;">Probability: {prob:.4%}</p>
                            </div>
                        """, unsafe_allow_html=True)

                    with res_col2:
                        if prediction == 1:
                            st.error(f"⚠️ **FAILURE PREDICTED!**\nThe system detects a critical risk of machine failure. Schedule maintenance immediately to prevent downtime.")
                        else:
                            st.success(f"✅ **SYSTEM HEALTHY**\nThe machine is operating safely. No immediate maintenance is recommended.")

                else:
                    st.error(f"Error calling API. Server returned code {res.status_code}: {res.text}")
            except Exception as e:
                st.error(f"Could not reach API at {api_base_url}. Details: {str(e)}")

# Tab 2: Historical Database Audit Logs
with tab_history:
    st.header("📋 Prediction History & System Logs")
    st.write("Inspect, query, and download all diagnostic logs collected by the system:")

    if st.button("🔄 Refresh Audit Logs"):
        st.rerun()

    try:
        logs_url = f"{api_base_url}/logs"
        res_logs = requests.get(logs_url)
        
        if res_logs.status_code == 200:
            logs_data = res_logs.json()
            
            if logs_data:
                df = pd.DataFrame(logs_data)
                
                # Format created_at to datetime
                df['created_at'] = pd.to_datetime(df['created_at'])
                df = df.sort_values(by='created_at', ascending=False)
                
                # Show key metrics
                total_runs = len(df)
                failures_detected = int(df['prediction'].sum())
                avg_prob = df['failure_probability'].mean()

                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric("Total Diagnostics Run", total_runs)
                stat_col2.metric("Total Failures Flagged", failures_detected, delta=f"{failures_detected/total_runs:.1%}" if total_runs else None, delta_color="inverse")
                stat_col3.metric("Avg Failure Probability", f"{avg_prob:.2%}")

                st.markdown("---")

                # Visual charts
                st.subheader("📈 Risk Progression Timeline")
                timeline_df = df.copy().set_index('created_at')
                # Streamlit built-in chart
                st.line_chart(timeline_df['failure_probability'])

                st.markdown("---")

                st.subheader("🗃️ Raw Telemetry Logs")
                # Filter option
                risk_filter = st.multiselect("Filter by Risk Category", options=["Low", "Medium", "High", "Critical"], default=["Low", "Medium", "High", "Critical"])
                filtered_df = df[df['risk_category'].isin(risk_filter)]
                
                # Show data table
                st.dataframe(filtered_df, width="stretch")

                # Export CSV button
                csv_data = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download filtered logs as CSV",
                    csv_data,
                    "prediction_audit_logs.csv",
                    "text/csv",
                    key='download-csv'
                )

            else:
                st.info("No predictions have been logged in the database yet. Run some diagnostic predictions first!")
        else:
            st.error(f"Error fetching logs. Status code: {res_logs.status_code}")
    except Exception as e:
        st.error(f"Could not connect to database logs at {api_base_url}/logs. Details: {str(e)}")
