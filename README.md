#  AI-Powered SOC Telemetry Analyzer

![Python]
![Azure Functions]
![OpenAI]


An event-driven Endpoint Detection and Response (EDR) simulation that leverages Generative AI to act as a Tier-1 SOC analyst. This project ingests raw endpoint telemetry, processes it through an Azure Storage Queue, and uses GPT-4o-mini to provide natural-language risk scoring and contextual analysis in real-time.

> 
[[Watch the 60-second Demo Video Here](https://github.com/user-attachments/assets/9df3872e-6946-41fc-a45d-a74c80fb3396)]
---

##  Key Features

* **Event-Driven Architecture:** Decouples data ingestion from analysis using Azure Storage Queues, ensuring no telemetry is lost during traffic spikes.
* **LLM-Powered Context:** Moves beyond rigid keyword matching. The AI analyzes the *context* of a keystroke buffer relative to the application being used (e.g., PowerShell vs. Slack).
* **Real-Time Visualization:** A vanilla JavaScript dashboard utilizing a "High-Water Mark" algorithm to seamlessly prepend fresh alerts without refreshing the page.
* **Cost-Optimized:** Designed to run on Azure Consumption plans or entirely locally via Azure Functions Core Tools.

---

##  System Architecture

1. **Telemetry Simulator (`telemetry_simulator.py`):** Generates mock endpoint logs (User, App, Keystrokes) and pushes them to an Azure Queue.
2. **Ingestion Layer (Azure Queue):** Acts as a buffer to handle high-volume log streams asynchronously.
3. **Analysis Engine (`function_app.py`):** An Azure Function triggered by the queue. It extracts the payload, queries the OpenAI API using strictly typed JSON mode, and calculates a risk score (0.0 - 1.0).
4. **Data Lake (Azure Table Storage):** Stores the AI's verdict using a reverse-chronological RowKey strategy for O(1) retrieval speeds.
5. **SOC Dashboard (`index.html`):** Polls the backend API and dynamically renders alerts using Tailwind CSS and FontAwesome icons.

---



### Prerequisites
* Python 3.11 or 3.12 (Azure Core Tools preview limitation with 3.13+)
* [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local) installed
* An OpenAI API Key
* An Azure Storage Account (or Azurite local emulator)



https://github.com/user-attachments/assets/9df3872e-6946-41fc-a45d-a74c80fb3396

