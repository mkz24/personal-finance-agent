import streamlit as st
import pandas as pd
import pdfplumber
import re
import io
import os
from dotenv import load_dotenv
from difflib import get_close_matches
import google.generativeai as genai
import fitz

# ---- Load env ----
load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY", "")
if gemini_key:
    genai.configure(api_key=gemini_key)

# ---- Page config ----
st.set_page_config(
    page_title=" Personal Finance Agent",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Custom CSS Theme ----
st.markdown("""
<style>
/* ===== GLOBAL ===== */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }

/* ===== MAIN CONTENT WRAPPER ===== */
.block-container {
    padding: 2rem 2.5rem 3rem 2.5rem !important;
    max-width: 1200px;
}

/* ===== HERO BANNER ===== */
.hero-banner {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(102,126,234,0.4);
}
.hero-banner h1 {
    font-size: 2.8rem;
    font-weight: 800;
    color: white !important;
    margin: 0;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}
.hero-banner p {
    color: rgba(255,255,255,0.88) !important;
    font-size: 1.05rem;
    margin: 0.6rem 0 0 0;
}

/* ===== SECTION HEADERS ===== */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    background: linear-gradient(90deg, rgba(102,126,234,0.15), transparent);
    border-left: 4px solid #667eea;
    border-radius: 0 12px 12px 0;
    padding: 0.8rem 1.2rem;
    margin: 2rem 0 1rem 0;
}
.section-header span {
    font-size: 1.25rem;
    font-weight: 700;
    color: #a78bfa !important;
    letter-spacing: 0.02em;
}

/* ===== METRIC CARDS ===== */
.metric-row { display: flex; gap: 1rem; margin: 1rem 0 1.5rem 0; flex-wrap: wrap; }
.metric-card {
    flex: 1;
    min-width: 160px;
    border-radius: 16px;
    padding: 1.4rem 1.5rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-3px); }
.metric-card.income  { background: linear-gradient(135deg, #11998e, #38ef7d); }
.metric-card.expense { background: linear-gradient(135deg, #ee0979, #ff6a00); }
.metric-card.net-pos { background: linear-gradient(135deg, #4776e6, #8e54e9); }
.metric-card.net-neg { background: linear-gradient(135deg, #c94b4b, #4b134f); }
.metric-card .label  { font-size: 0.75rem; font-weight: 600; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 0.1em; }
.metric-card .value  { font-size: 1.9rem; font-weight: 800; color: white; margin-top: 0.3rem; }

/* ===== RESULT CARDS ===== */
.result-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.2);
}
.result-card h4 {
    color: #a78bfa !important;
    font-size: 1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.8rem;
    border-bottom: 1px solid rgba(167,139,250,0.3);
    padding-bottom: 0.5rem;
}
.result-card p, .result-card li { color: #d1d5db !important; line-height: 1.7; }

/* ===== BUTTONS ===== */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1rem !important;
    border: none !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.4) !important;
}

/* ===== FILE UPLOADER ===== */
[data-testid="stFileUploader"] {
    background: rgba(102,126,234,0.08) !important;
    border: 2px dashed rgba(102,126,234,0.5) !important;
    border-radius: 16px !important;
    padding: 1rem !important;
}

/* ===== DATAFRAME ===== */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
}

/* ===== CHAT ===== */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    margin-bottom: 0.5rem !important;
}
[data-testid="stChatInputContainer"] {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(102,126,234,0.5) !important;
}

/* ===== SIDEBAR STEPS ===== */
.sidebar-step {
    background: rgba(102,126,234,0.15);
    border-left: 3px solid #667eea;
    border-radius: 0 10px 10px 0;
    padding: 0.6rem 1rem;
    margin-bottom: 0.6rem;
    font-size: 0.9rem;
    color: #c4b5fd !important;
}
.sidebar-step.done {
    background: rgba(17,153,142,0.15);
    border-color: #11998e;
    color: #6ee7b7 !important;
}

/* ===== INFO/SUCCESS/WARNING OVERRIDES ===== */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: none !important;
}

/* ===== ALL TEXT ===== */
h1,h2,h3,h4,h5,h6,p,li,label,span,.stMarkdown {
    color: #e2e8f0;
}
</style>
""", unsafe_allow_html=True)

# ---- Session state ----
for key in ["df", "analyzed_df", "summary", "plan", "critique", "chat_history",
            "income_val", "expense_val", "net_val"]:
    if key not in st.session_state:
        st.session_state[key] = None
if st.session_state.chat_history is None:
    st.session_state.chat_history = []

# ============================================================
# HELPERS
# ============================================================

def clean_amount(raw):
    if raw is None:
        return None
    s = str(raw).strip().replace(',', '').replace('$', '').replace(' ', '')
    if not s:
        return None
    if s.endswith('-'):
        s = '-' + s[:-1]
    s = re.sub(r'^\((.+)\)$', r'-\1', s)
    try:
        return float(s)
    except ValueError:
        return None

def pymupdf_extract_text(file_bytes):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        full_text = ""
        for page in doc:
            full_text += page.get_text() + "\n"
        doc.close()
        return full_text if full_text.strip() else None
    except Exception as e:
        st.warning(f" PyMuPDF extraction failed: {e}")
        return None

def parse_text_to_transactions(text):
    rows = []
    date_pat = r'(\d{1,2}[/\-]\d{1,2}(?:[/\-]\d{2,4})?|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2})'
    money_pat = r'(-?\$?[\d,]+\.\d{2}-?)'
    line_re = re.compile(rf'^{date_pat}\s+(.+?)\s+{money_pat}(?:\s+{money_pat})?(?:\s+{money_pat})?\s*$')
    for line in text.splitlines():
        line = line.strip()
        m = line_re.match(line)
        if m:
            date = m.group(1)
            desc = m.group(2).strip()
            raw_amounts = [g for g in [m.group(3), m.group(4), m.group(5)] if g]
            amt = clean_amount(raw_amounts[0]) if raw_amounts else None
            bal = clean_amount(raw_amounts[-1]) if len(raw_amounts) > 1 else None
            if amt is None:
                continue
            if desc.lower() in ["transaction detail", "description", "details"]:
                continue
            rows.append({"Date": date, "Description": desc, "Amount": amt, "Balance": bal})
    return rows

def is_text_pdf(file_bytes):
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            if len((page.extract_text() or "").strip()) > 50:
                return True
    return False

# ============================================================
# PDF PARSING
# ============================================================

def parse_pdf_statement(uploaded_file):
    rows = []
    file_bytes = uploaded_file.read()
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                if not table or len(table) < 2:
                    continue
                header = [str(c).strip().lower() if c else f"col_{i}" for i, c in enumerate(table[0])]
                if not any(any(k in h for k in ["date","col_0"]) for h in header):
                    continue
                for row in table[1:]:
                    if not any(cell and str(cell).strip() for cell in row):
                        continue
                    rd = {header[i]: str(cell).strip() if cell else "" for i, cell in enumerate(row) if i < len(header)}
                    date_val = desc_val = amt_val = bal_val = ""
                    for k, v in rd.items():
                        if "date" in k: date_val = v
                        elif any(x in k for x in ["transaction detail","description","memo","merchant","payee","details","desc","name"]): desc_val = v
                        elif any(x in k for x in ["amount($)","amount","debit","withdrawal","charge"]):
                            if not amt_val: amt_val = v
                        elif any(x in k for x in ["balance($)","balance"]): bal_val = v
                    if not date_val and "col_0" in rd: date_val = rd["col_0"]
                    if not desc_val and "col_1" in rd: desc_val = rd["col_1"]
                    if not amt_val and "col_2" in rd: amt_val = rd["col_2"]
                    if not bal_val and "col_3" in rd: bal_val = rd["col_3"]
                    if not date_val or date_val.lower() in ["date",""]: continue
                    if desc_val.lower() in ["beginning balance","ending balance","transaction detail"]: continue
                    if not re.search(r'\d{1,2}[-/]\d{1,2}', date_val): continue
                    ca = clean_amount(amt_val)
                    if ca is None: continue
                    rows.append({"Date": date_val, "Description": desc_val, "Amount": ca, "Balance": clean_amount(bal_val)})
    if rows:
        df = pd.DataFrame(rows)
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df["Balance"] = pd.to_numeric(df["Balance"], errors="coerce")
        return df
    if is_text_pdf(file_bytes):
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            full_text = "".join((p.extract_text() or "") + "\n" for p in pdf.pages)
        rows = parse_text_to_transactions(full_text)
        if rows: return pd.DataFrame(rows)
    mupdf_text = pymupdf_extract_text(file_bytes)
    if mupdf_text:
        rows = parse_text_to_transactions(mupdf_text)
        if rows:
            st.success(" PyMuPDF extracted transactions!")
            return pd.DataFrame(rows)
    st.error(" Could not extract transactions. Try downloading a fresh PDF from your bank.")
    return None

# ============================================================
# AGENT CLASSES
# ============================================================

class DataFetchAgent:
    def fetch_data(self, uploaded_file):
        fname = uploaded_file.name.lower()
        if fname.endswith(".pdf"):
            with st.spinner(" Parsing PDF bank statement..."):
                df = parse_pdf_statement(uploaded_file)
            if df is None or df.empty:
                st.error(" Could not extract transactions. Try downloading directly from your bank.")
                return None
            st.success(f" PDF parsed! Found **{len(df)} transactions**.")
        else:
            df = pd.read_csv(uploaded_file)
            st.success(f" CSV loaded! Found **{len(df)} rows**.")

        if fname.endswith(".pdf") and "Amount" in df.columns:
            st.session_state.df = df
            return df

        money_keys = ["amount","cost","price","debit","credit","charge","total","txn_amt","withdrawal","deposit"]
        desc_keys  = ["desc","merchant","payee","description","vendor","name","memo","details","transaction"]
        date_keys  = ["date","period","trans","posted","value date"]
        acct_keys  = ["account","category","type","class"]

        def find_best(colnames, keywords):
            for col in colnames:
                if any(k in col.lower() for k in keywords): return col
            hit = get_close_matches(" ".join(c.lower() for c in colnames), keywords, n=1, cutoff=0.5)
            if hit:
                for col in colnames:
                    if hit[0] in col.lower(): return col
            return None

        cols = list(df.columns)
        amount_col = find_best(cols, money_keys)
        desc_col   = find_best(cols, desc_keys)
        date_col   = find_best(cols, date_keys)
        acct_col   = find_best(cols, acct_keys)
        if amount_col is None:
            nc = df.select_dtypes(include="number").columns
            if len(nc): amount_col = nc[0]
        if desc_col is None:
            oc = df.select_dtypes(include="object").columns
            if len(oc): desc_col = oc[0]

        rename_map = {}
        if amount_col: rename_map[amount_col] = "Amount"
        if desc_col:   rename_map[desc_col]   = "Description"
        if date_col:   rename_map[date_col]   = "Date"
        if acct_col:   rename_map[acct_col]   = "Account"
        df = df.rename(columns=rename_map)

        if "Amount" not in df.columns or "Description" not in df.columns:
            st.error(" Could not find Amount/Description columns.")
            return None

        df["Amount"] = pd.to_numeric(
            df["Amount"].astype(str).str.replace(r'[\$,]','',regex=True).str.strip(),
            errors="coerce"
        )
        df = df.dropna(subset=["Amount"])
        st.session_state.df = df
        return df


class AnalyzerAgent:
    def analyze(self, df):
        if df is None or df.empty:
            return "No data loaded yet.", None, 0, 0, 0
        data = df.copy()
        data["Category"] = data["Account"] if "Account" in data.columns else "General"
        if "Account" in data.columns:
            acc = data["Account"].str.lower()
            income   = data.loc[acc == "income",   "Amount"].sum()
            expenses = data.loc[acc == "expenses",  "Amount"].sum()
        else:
            income   = data.loc[data["Amount"] > 0, "Amount"].sum()
            expenses = data.loc[data["Amount"] < 0, "Amount"].sum()
        expenses_abs = abs(expenses)
        net = income - expenses_abs
        by_cat = (
            data[data["Amount"] < 0]
            .groupby("Category")["Amount"].sum().abs()
            .sort_values(ascending=False)
        )
        summary_lines = []
        if not by_cat.empty:
            for cat, amt in by_cat.items():
                summary_lines.append(f"- **{cat}**: ${amt:,.2f}")
        else:
            summary_lines.append("- No expense rows detected.")
        summary = "\n".join(summary_lines)
        return summary, data, income, expenses_abs, net


class PlannerAgent:
    def plan(self, df):
        if df is None or df.empty:
            return "Run Analyze first."
        if "Account" in df.columns:
            total_exp = abs(df.loc[df["Account"].str.lower() == "expenses", "Amount"].sum())
        else:
            total_exp = abs(df.loc[df["Amount"] < 0, "Amount"].sum())
        monthly_exp = total_exp / 3.0
        return (
            f"**Quarterly expenses:** ${total_exp:,.2f}\n\n"
            f"**Monthly average:** ${monthly_exp:,.2f}\n\n"
            f"**Suggested 3-month emergency fund:** ${monthly_exp*3:,.2f}\n\n"
            f"💡 **Tips:**\n"
            f"- Save 10–20% of income toward your emergency fund each month.\n"
            f"- Find your biggest expense category and try cutting it by 10%.\n"
            f"- Automate transfers to savings on payday."
        )


class CriticAgent:
    def critique(self, plan_text, df):
        if df is None:
            return "No data available."
        if "Account" in df.columns:
            total_exp = abs(df.loc[df["Account"].str.lower() == "expenses", "Amount"].sum())
            income    = df.loc[df["Account"].str.lower() == "income",   "Amount"].sum()
        else:
            total_exp = abs(df.loc[df["Amount"] < 0, "Amount"].sum())
            income    = df.loc[df["Amount"] > 0, "Amount"].sum()
        net = income - total_exp
        risks = []
        if total_exp > 20000: risks.append(" **High expenses detected** — review your biggest categories.")
        if income == 0:       risks.append(" **No income rows found** — make sure deposits are included.")
        if net < 0:           risks.append(f" **Negative net (${net:,.2f})** — you're spending more than you earn!")
        return "\n\n".join(risks) if risks else " **Plan looks solid!** No major risks detected."

    def ask_ai(self, question, df, api_key):
        if not api_key:
            return " Gemini API key not found. Add GEMINI_API_KEY to your .env file."
        if df is not None and not df.empty:
            if "Account" in df.columns:
                income   = df.loc[df["Account"].str.lower() == "income",   "Amount"].sum()
                expenses = df.loc[df["Account"].str.lower() == "expenses", "Amount"].sum()
            else:
                income   = df.loc[df["Amount"] > 0, "Amount"].sum()
                expenses = df.loc[df["Amount"] < 0, "Amount"].sum()
            top_desc = (df[df["Amount"] < 0].nlargest(5,"Amount",keep="all")["Description"].tolist()
                        if "Description" in df.columns else [])
            ctx = (
                f"Income: ${income:,.2f} | Expenses: ${abs(expenses):,.2f} | "
                f"Net: ${income-abs(expenses):,.2f} | "
                f"Top transactions: {', '.join(str(d) for d in top_desc)}"
            )
        else:
            ctx = "No bank statement uploaded yet."
        prompt = (
            "You are an expert personal finance advisor embedded in a finance app. "
            "Answer clearly and helpfully in plain English with specific advice.\n\n"
            f"User's financial data: {ctx}\n\nUser question: {question}"
        )
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            return model.generate_content(prompt).text
        except Exception as e:
            return f" Gemini error: {str(e)}"


# ---- Instantiate agents ----
fetcher  = DataFetchAgent()
analyzer = AnalyzerAgent()
planner  = PlannerAgent()
critic   = CriticAgent()

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 1.5rem 0;'>
        <div style='font-size:3rem;'>💰</div>
        <div style='font-size:1.2rem; font-weight:800; color:#a78bfa;'>Finance Agent</div>
        <div style='font-size:0.75rem; color:#94a3b8; margin-top:0.3rem;'>AI-Powered Budget Analyzer</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("###  How It Works")

    steps = [
        ("Upload your bank statement (PDF or CSV)", st.session_state.df is not None),
        ("Click Analyze to see income vs. expenses", st.session_state.analyzed_df is not None),
        ("Click Plan to get a savings strategy", st.session_state.plan is not None),
        ("Click Critique to spot financial risks", st.session_state.critique is not None),
        ("Ask the AI Critic anything about your finances", False),
    ]
    for icon, text, done in steps:
        cls = "done" if done else ""
        st.markdown(
            f'<div class="sidebar-step {cls}">{icon} {text}</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("###Supported Banks")
    st.markdown("""
    - Chase &nbsp;•&nbsp; Bank of America
    - Wells Fargo &nbsp;•&nbsp; Citi
    - Capital One &nbsp;•&nbsp; Navy Federal
    - Any CSV with Amount column
    """)

    st.markdown("---")
    if st.button("🔄 Reset Everything", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("CIS 4394 · Multi-Agent Finance App")

# ============================================================
# MAIN CONTENT
# ============================================================

# Hero Banner
st.markdown("""
<div class="hero-banner">
    <h1> Personal Finance Agent</h1>
    <p>Upload your bank statement · Get AI-powered insights · Take control of your money</p>
</div>
""", unsafe_allow_html=True)

# ---- SECTION 1: Upload ----
st.markdown('<div class="section-header"><span> Step 1 — Upload Your Bank Statement</span></div>', unsafe_allow_html=True)

upload_col, info_col = st.columns([2, 1])
with upload_col:
    uploaded = st.file_uploader(
        "Drop your PDF or CSV here",
        type=["csv", "pdf"],
        label_visibility="collapsed"
    )
with info_col:
    st.markdown("""
    <div class="result-card">
        <h4> Supported Formats</h4>
        <p> <b>PDF</b> — Direct bank export<br>
         <b>CSV</b> — Any bank statement<br>
         Data stays on your machine</p>
    </div>
    """, unsafe_allow_html=True)

if uploaded is not None:
    df_result = fetcher.fetch_data(uploaded)
    if df_result is not None:
        st.markdown("** Preview (first 10 rows):**")
        st.dataframe(df_result.head(10), use_container_width=True, height=280)

# ---- SECTION 2: Run Agents ----
st.markdown('<div class="section-header"><span>⚡ Step 2 — Run the AI Agents</span></div>', unsafe_allow_html=True)

btn_col1, btn_col2, btn_col3 = st.columns(3)

with btn_col1:
    st.markdown("""
    <div class="result-card" style="text-align:center; margin-bottom:0.5rem;">
        <h4>🔍 Analyzer</h4>
        <p style="font-size:0.82rem;">Breaks down income vs. expenses by category</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("▶ Run Analyze", use_container_width=True, key="btn_analyze"):
        if st.session_state.df is None:
            st.warning(" Upload a file first!")
        else:
            with st.spinner("🔍 Analyzing your finances..."):
                summary, analyzed_df, inc, exp, net = analyzer.analyze(st.session_state.df)
            st.session_state.summary      = summary
            st.session_state.analyzed_df  = analyzed_df
            st.session_state.income_val   = inc
            st.session_state.expense_val  = exp
            st.session_state.net_val      = net
            st.success(" Analysis complete!")

with btn_col2:
    st.markdown("""
    <div class="result-card" style="text-align:center; margin-bottom:0.5rem;">
        <h4>📈 Planner</h4>
        <p style="font-size:0.82rem;">Builds a savings plan from your data</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("▶ Run Plan", use_container_width=True, key="btn_plan"):
        if st.session_state.analyzed_df is None:
            st.warning(" Run Analyze first!")
        else:
            with st.spinner("📈 Building your plan..."):
                st.session_state.plan = planner.plan(st.session_state.analyzed_df)
            st.success(" Plan ready!")

with btn_col3:
    st.markdown("""
    <div class="result-card" style="text-align:center; margin-bottom:0.5rem;">
        <h4>🧐 Critic</h4>
        <p style="font-size:0.82rem;">Spots financial risks and red flags</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("▶ Run Critique", use_container_width=True, key="btn_critique"):
        if st.session_state.analyzed_df is None:
            st.warning(" Run Analyze first!")
        else:
            with st.spinner("🧐 Reviewing your plan..."):
                st.session_state.critique = critic.critique(
                    st.session_state.plan or "", st.session_state.analyzed_df
                )
            st.success(" Critique ready!")

# ---- SECTION 3: Results ----
st.markdown('<div class="section-header"><span> Step 3 — Your Results</span></div>', unsafe_allow_html=True)

# Metric Cards
if st.session_state.income_val is not None:
    inc = st.session_state.income_val
    exp = st.session_state.expense_val
    net = st.session_state.net_val
    net_class = "net-pos" if net >= 0 else "net-neg"
    net_icon  = "📈" if net >= 0 else "📉"
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card income">
            <div class="label"> Total Income</div>
            <div class="value">${inc:,.0f}</div>
        </div>
        <div class="metric-card expense">
            <div class="label"> Total Expenses</div>
            <div class="value">${exp:,.0f}</div>
        </div>
        <div class="metric-card {net_class}">
            <div class="label">{net_icon} Net Balance</div>
            <div class="value">${net:,.0f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Tabs for results
if any([
    st.session_state.summary,
    st.session_state.plan,
    st.session_state.critique,
    st.session_state.analyzed_df is not None
]):
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary", "📈 Plan", "🧐 Critique", "📄 Raw Data"])

    with tab1:
        if st.session_state.summary:
            st.markdown('<div class="result-card"><h4> Expense Breakdown by Category</h4>', unsafe_allow_html=True)
            st.markdown(st.session_state.summary)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Run **Analyze** to see your expense breakdown here.")

    with tab2:
        if st.session_state.plan:
            st.markdown('<div class="result-card"><h4> Your Financial Plan</h4>', unsafe_allow_html=True)
            st.markdown(st.session_state.plan)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Run **Plan** to see your personalized savings strategy.")

    with tab3:
        if st.session_state.critique:
            st.markdown('<div class="result-card"><h4> Risk Assessment</h4>', unsafe_allow_html=True)
            st.markdown(st.session_state.critique)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Run **Critique** to see financial risk flags.")

    with tab4:
        if st.session_state.analyzed_df is not None:
            st.dataframe(st.session_state.analyzed_df, use_container_width=True)
        else:
            st.info("Run **Analyze** to see the full processed data table.")

# ---- SECTION 4: AI Chat ----
st.markdown('<div class="section-header"><span> Step 4 — Ask the AI Finance Advisor</span></div>', unsafe_allow_html=True)

st.markdown("""
<div class="result-card" style="margin-bottom:1rem;">
    <h4>💬 AI Critic Chat</h4>
    <p>Ask anything about your finances. The AI reads your actual statement data and answers like a personal finance advisor.</p>
</div>
""", unsafe_allow_html=True)

chat_container = st.container()
with chat_container:
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

user_q = st.chat_input(" Ask me anything... e.g. 'Why are my expenses so high?' or 'How do I save $500/month?'")
if user_q:
    st.session_state.chat_history.append({"role": "user", "content": user_q})
    with st.chat_message("user"):
        st.markdown(user_q)
    with st.chat_message("assistant"):
        with st.spinner(" Thinking..."):
            active_df = st.session_state.analyzed_df if st.session_state.analyzed_df is not None else st.session_state.df
            answer = critic.ask_ai(user_q, active_df, gemini_key)
        st.markdown(answer)
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
