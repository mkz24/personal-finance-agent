#  Personal Finance Agent

A smart multi-agent web app that reads your real bank statements (PDF or CSV) and returns a full financial report — powered by Google Gemini AI and built with Streamlit.

##  Agents

| Agent | Role |
|---|---|
| **DataFetchAgent** | Loads & normalizes CSV or PDF bank statements |
| **AnalyzerAgent** | Computes income, expenses, and spending categories |
| **PlannerAgent** | Generates a simple monthly/quarterly budget plan |
| **CriticAgent** | AI-powered risk review + chat Q&A via Gemini |
| **ControllerAgent** | Orchestrates all agents via natural-language commands |

##  Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

##  Run in Google Colab

Open `personal_finance_agent_colab.ipynb` in Google Colab for a no-install cloud version using ngrok.

##  Sample Data

Try `sample.csv` to test the app without a real bank statement.

##  Requirements

- Python 3.9+
- Google Gemini API key (free at [aistudio.google.com](https://aistudio.google.com/app/apikey))
- Supports: Chase, Bank of America, Wells Fargo, Navy Federal, Citi, Capital One PDFs & CSVs


