import streamlit as st
import json
from pydantic import BaseModel, Field
from typing import Literal
import ollama

# 1. Page Configuration
st.set_page_config(page_title="SLM Log Incident Parser", layout="wide")
st.title("⚡ SLM Incident Analyzer")
st.caption("Powered by local Llama 3.2 (1B) + Pydantic Structured Outputs")

# 2. Schema Definition
class IncidentReport(BaseModel):
    service_name: str = Field(description="Name of the affected service")
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(description="Severity tier")
    error_code: str = Field(description="Specific exception name or error code")
    root_cause_summary: str = Field(description="1-sentence cause")
    recommended_action: str = Field(description="1-sentence mitigation")

# 3. Layout Columns
col1, col2 = st.columns(2)

default_log = """[2026-09-15 14:22:01.402] ERROR [payments-gateway-worker-3] 
DatabaseConnectionTimeoutException: Unable to acquire connection from pool 'PostgresPool-Prod' after 30000ms.
Active connections: 100/100. Threads waiting: 42. Client requests dropping with HTTP 504."""

with col1:
    st.subheader("Input Log")
    raw_log = st.text_area("Paste raw log text here:", value=default_log, height=220)
    analyze_btn = st.button("Analyze Log", type="primary")

with col2:
    st.subheader("Structured Extraction")
    if analyze_btn and raw_log.strip():
        with st.spinner("Analyzing with local SLM..."):
            try:
                system_prompt = """You are a DevOps log analysis agent.
Extract incident details strictly matching the schema.

Example:
Log: "[ERROR] [auth-svc] TokenExpiredException: Key expired at 12:00"
Output format target:
- error_code: TokenExpiredException
"""
                response = ollama.chat(
                    model="llama3.2:1b",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Extract details from this log:\n{raw_log}"}
                    ],
                    format=IncidentReport.model_json_schema(),
                    options={"temperature": 0.0}
                )

                # Validate against Pydantic schema
                data = IncidentReport.model_validate_json(response['message']['content'])

                # Metrics / Badges
                sev_color = "🔴" if data.severity in ["HIGH", "CRITICAL"] else "🟡"
                st.markdown(f"### {sev_color} {data.severity} — `{data.service_name}`")
                
                st.markdown(f"**Error Code:** `{data.error_code}`")
                st.markdown(f"**Root Cause:** {data.root_cause_summary}")
                st.markdown(f"**Action:** {data.recommended_action}")

                with st.expander("View Raw JSON Schema Output"):
                    st.json(json.loads(response['message']['content']))

            except Exception as e:
                st.error(f"Extraction failed: {e}")
