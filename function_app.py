import azure.functions as func
import logging
import json
import os
import uuid
from datetime import datetime, timezone
from openai import OpenAI
from azure.data.tables import TableClient
from azure.core.exceptions import ResourceExistsError

app = func.FunctionApp()

client = OpenAI()

@app.queue_trigger(arg_name="msg", queue_name="uam-telemetry-queue", connection="AzureWebJobsStorage") 
def analyze_telemetry(msg: func.QueueMessage):
    
    payload = msg.get_body().decode('utf-8')
    log_data = json.loads(payload)
    
    user = log_data.get("user", "Unknown")
    app_name = log_data.get("application", "Unknown")
    keystrokes = log_data.get("keystroke_buffer", "")
    
    logging.info(f" INCOMING: {user} in {app_name}")
    
    try:
        # Force OpenAI to return a structured JSON object for our Threat Score
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={ "type": "json_object" }, 
            messages=[
                {
                    "role": "system", 
                    "content": "You are a SOC analyst. Analyze the telemetry. You MUST respond in JSON format with exactly three keys: 'verdict' (String: exactly 'MALICIOUS' or 'BENIGN'), 'score' (Float: between 0.00 and 1.00 indicating threat level), and 'reason' (String: short explanation)."
                },
                {"role": "user", "content": f"Application: {app_name}\nKeystrokes: {keystrokes}"}
            ],
            max_completion_tokens=100,
            temperature=0.2
        )
        
        # Parse the JSON response
        ai_data = json.loads(response.choices[0].message.content)
        verdict = ai_data.get("verdict", "UNKNOWN")
        score = float(ai_data.get("score", 0.0))
        reason = ai_data.get("reason", "No reason provided")
        
        logging.info(f" AI: {verdict} ({score}) - {reason}")
        
        # Save to Database
        table_client = TableClient.from_connection_string(
            conn_str=os.getenv("AzureWebJobsStorage"), 
            table_name="SecurityAlertsV3"
        )
        
        try:
            table_client.create_table()
        except ResourceExistsError:
            pass 
            
        alert_entity = {
            "PartitionKey": "AI_Alert",
            "RowKey": str(uuid.uuid4()), 
            "User": user,
            "Application": app_name,
            "Keystrokes": keystrokes,
            "Verdict": verdict,
            "Score": score,
            "Reason": reason
        }
        
        table_client.upsert_entity(entity=alert_entity)

    except Exception as e:
        logging.error(f"❌ Analysis Failed: {e}")

# ==========================================
#  HTTP TRIGGER FOR THE DASHBOARD
# ==========================================

@app.route(route="get_alerts", auth_level=func.AuthLevel.ANONYMOUS)
def get_alerts(req: func.HttpRequest) -> func.HttpResponse:
    try:
        table_client = TableClient.from_connection_string(
            conn_str=os.getenv("AzureWebJobsStorage"), 
            table_name="SecurityAlertsV3"
        )
        
        alerts = []
        for entity in table_client.list_entities():
            alerts.append({
                "ID": entity.get("RowKey", "N/A")[:8],
                "User": entity.get("User", "Unknown"),
                "Application": entity.get("Application", "Unknown"),
                "Keystrokes": entity.get("Keystrokes", "Unknown"),
                "Verdict": entity.get("Verdict", "Unknown"),
                "Score": entity.get("Score", 0.0),      
                "Reason": entity.get("Reason", ""),     
            })
            
        return func.HttpResponse(json.dumps(alerts), mimetype="application/json", status_code=200, headers={"Access-Control-Allow-Origin": "*"})
    except Exception as e:
        if "TableNotFound" in str(e):
             return func.HttpResponse("[]", mimetype="application/json", status_code=200, headers={"Access-Control-Allow-Origin": "*"})
        return func.HttpResponse(f"Error: {str(e)}", status_code=500, headers={"Access-Control-Allow-Origin": "*"})