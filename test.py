import json
from pydantic import BaseModel, Field
from typing import Literal
import ollama

class IncidentReport(BaseModel):
    service_name: str = Field(description="Name of the affected service")
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(description="Severity tier")
    error_code: str = Field(description="Specific exception name or error code without punctuation")
    root_cause_summary: str = Field(description="1-sentence cause")
    recommended_action: str = Field(description="1-sentence mitigation")

sample_raw_log = """
[2026-09-15 14:22:01.402] ERROR [payments-gateway-worker-3] 
DatabaseConnectionTimeoutException: Unable to acquire connection from pool 'PostgresPool-Prod' after 30000ms.
Active connections: 100/100. Threads waiting: 42. Client requests dropping with HTTP 504.
"""

# Giving 1B models an explicit example anchors their token generation
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
        {"role": "user", "content": f"Extract details from this log:\n{sample_raw_log}"}
    ],
    format=IncidentReport.model_json_schema(),
    options={"temperature": 0.0}
)

incident = IncidentReport.model_validate_json(response['message']['content'])

print(f"Service:    {incident.service_name}")
print(f"Severity:   {incident.severity}")
print(f"Error Code: {incident.error_code}")
print(f"Cause:      {incident.root_cause_summary}")
print(f"Action:     {incident.recommended_action}")
