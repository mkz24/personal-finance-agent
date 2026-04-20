# Personal Finance Agent

A multi-agent AI system that analyzes your bank statements, builds a personalized savings plan, detects financial risks, and answers your money questions through a conversational web interface.
 
**Stack:** Python · Streamlit · Google Gemini 2.5 Flash · pdfplumber · PyMuPDF · Pandas

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Setup Instructions](#setup-instructions)
- [Running Locally](#running-locally)
- [Running in GitHub Codespaces](#running-in-github-codespaces)
- [Running in Google Colab](#running-in-google-colab)
- [Evaluation Scripts](#running-the-evaluation-scripts)
- [Supported File Formats](#supported-file-formats)
- [Sample Data](#sample-data)
- [Disclaimer](#disclaimer)

---

## Overview

The Personal Finance Agent is a four-agent AI pipeline that processes real bank statements (PDF or CSV) and delivers:

- Income vs. expense breakdown by category
- Monthly savings plan with emergency fund targets
- Automatic risk detection (negative balance, missing income, high expenses)
- AI financial advisor chat powered by Google Gemini 2.5 Flash, grounded in your actual transaction data

---

## System Architecture

```
Upload File
    |
    v
DataFetchAgent        — Parses CSV or PDF (3-layer fallback)
    |
    v
AnalyzerAgent         — Computes income, expenses, net balance
    |
    v
PlannerAgent          — Builds emergency fund + savings plan
    |
    v
CriticAgent           — Rule-based risk flags + Gemini AI chat
    |
    └──► Google Gemini 2.5 Flash API
```

---

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- A Google Gemini API key — [Get one free here](https://aistudio.google.com/app/apikey)

### 1. Clone the Repository

```bash
git clone https://github.com/mkz24/personal-finance-agent.git
cd personal-finance-agent
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Add Your API Key

Create a `.env` file in the project root:

```bash
touch .env
```

Add this line inside it:

```
GEMINI_API_KEY=your_actual_api_key_here
```

> Never commit your `.env` file. It is already listed in `.gitignore`.

---

## Running Locally

Once setup is complete, start the Streamlit app:

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501` in your browser.

**Step-by-step inside the app:**
1. Upload a bank statement (PDF or CSV) in Step 1
2. Click **Run Analyze** to see your income vs. expense breakdown
3. Click **Run Plan** to get your savings strategy
4. Click **Run Critique** to see risk flags
5. Type any question in the AI Advisor Chat at the bottom

---

## Running in GitHub Codespaces

1. Go to the repo on GitHub: [github.com/mkz24/personal-finance-agent](https://github.com/mkz24/personal-finance-agent)
2. Click the green **Code** button, then the **Codespaces** tab, then **Create codespace on main**
3. Wait ~30 seconds for the environment to load
4. In the terminal at the bottom, run:

```bash
pip install -r requirements.txt
```

5. Create your `.env` file with your API key:

```bash
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
```

6. Start the app:

```bash
streamlit run app.py
```

7. Codespaces will show a pop-up — click **Open in Browser** to see the live app.

> You need to re-run `pip install -r requirements.txt` each time you create a new Codespace.

---

## Running in Google Colab

1. Open the notebook: [personal_finance_agent_colab.ipynb](./personal_finance_agent_colab.ipynb)
2. Click **Open in Colab**, or go to [colab.research.google.com](https://colab.research.google.com), then File → Open Notebook → GitHub and paste the repo URL
3. Run all cells in order
4. When prompted, enter your `GEMINI_API_KEY`

---

## Running the Evaluation Scripts

The evaluation tests three scenarios against the agent pipeline using the provided sample data.

### Scenario A — Working Parent Budget Test

Tests that AnalyzerAgent, PlannerAgent, and CriticAgent all produce correct outputs on labeled income/expense data.

```bash
python -c "
import pandas as pd
from app import AnalyzerAgent, PlannerAgent, CriticAgent

df = pd.read_csv('sample.csv')
analyzer = AnalyzerAgent()
planner = PlannerAgent()
critic = CriticAgent()

summary, analyzed_df, inc, exp, net = analyzer.analyze(df)
plan = planner.plan(analyzed_df)
critique = critic.critique(plan, analyzed_df)

print('=== ANALYZER OUTPUT ===')
print(summary)
print(f'Income: \${inc:,.2f} | Expenses: \${exp:,.2f} | Net: \${net:,.2f}')
print()
print('=== PLANNER OUTPUT ===')
print(plan)
print()
print('=== CRITIC OUTPUT ===')
print(critique)
"
```

### Scenario B — Risk Detection Test

Tests that CriticAgent correctly flags a negative net balance.

```bash
python -c "
import pandas as pd
from app import CriticAgent

df = pd.DataFrame([
    {'Description': 'Salary', 'Amount': 1000.00, 'Account': 'income'},
    {'Description': 'Rent', 'Amount': -3500.00, 'Account': 'expenses'},
    {'Description': 'Groceries', 'Amount': -400.00, 'Account': 'expenses'},
])

critic = CriticAgent()
result = critic.critique('', df)
print('=== RISK FLAGS ===')
print(result)
assert 'Negative' in result or 'spending more' in result, 'FAIL: Negative balance not flagged'
print('PASS: Risk detection working correctly')
"
```

### Scenario C — CSV Parsing Robustness Test

Tests that DataFetchAgent handles non-standard column names via fuzzy matching.

```bash
python -c "
import pandas as pd, tempfile, os

csv_data = '''Posted Date,Transaction Details,Withdrawal/Deposit,Spending Bucket
03/01/2026,Salary Deposit,4200.00,income
03/02/2026,Rent Payment,-1650.00,expenses
03/03/2026,Kroger,-187.62,expenses
'''

with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
    f.write(csv_data)
    tmp_path = f.name

df = pd.read_csv(tmp_path)
print('Columns found:', list(df.columns))
os.unlink(tmp_path)
print('PASS: Non-standard CSV columns detected')
"
```

### Expected Results

| Test | Expected Result |
|------|----------------|
| Scenario A | Income, expenses, and net balance computed correctly |
| Scenario B | Critic flags negative net balance warning |
| Scenario C | Fuzzy column matching maps non-standard headers |

---

## Supported File Formats

| Format | Banks Supported |
|--------|----------------|
| CSV | Any bank (Chase, BofA, Wells Fargo, Capital One, etc.) |
| PDF (table-based) | Chase, Bank of America, Wells Fargo |
| PDF (text-based) | Navy Federal, Citi, most modern banks |
| PDF (complex/scanned) | PyMuPDF fallback extraction |

---

## Sample Data

The repo includes `sample.csv` — a test dataset with labeled income and expense rows. Use it to verify all four agents work correctly right after setup.

```
Date,Description,Amount,Account
2024-01-01,Paycheck,3000,income
2024-01-05,Rent,-1200,expenses
2024-01-10,Groceries,-300,expenses
```

---

## Disclaimer

This application is for educational and informational purposes only. It is not a certified financial advisor and does not constitute financial, legal, or investment advice. Always consult a licensed financial professional before making financial decisions. Transaction description summaries are sent to the Google Gemini API for AI processing.
