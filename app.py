import streamlit as st
from typing import List, Dict, Tuple, Optional
from io import StringIO
import csv
import datetime as dt
import math

# ─────────────────────────────────────────────────────────────
# Page setup & compact theme
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="SME Cybersecurity Self-Assessment", layout="wide")

st.markdown("""
<style>
  :root{
    --fg:#1f2937; --muted:#475569; --soft:#6b7280;
    --line:#e6e8ec; --card:#ffffff;
    --green:#16a34a; --amber:#f59e0b; --red:#ef4444;
    --green-bg:#e8f7ee; --amber-bg:#fff5d6; --red-bg:#ffe5e5;
  }
  .block-container {max-width: 1160px; padding-top: 10px;}
  header {visibility: hidden;}
  h1,h2,h3,h4 {margin:.25rem 0 .55rem; color:var(--fg)}
  .lead {color:#374151; margin:.2rem 0 .6rem}
  .hint {color:#394b63; font-size:.98rem; font-style:italic; margin:.25rem 0 .75rem; line-height:1.4}
  .explain {color:#1f2937; font-size:1.02rem; margin:.30rem 0 .75rem}
  .explain small {display:block; color:#475569; font-style:italic}
  .pill {display:inline-block;border-radius:999px;padding:.18rem .55rem;border:1px solid #e5e7eb;font-size:.9rem;color:#374151;background:#fff}
  .chip {display:inline-flex;align-items:center;gap:.35rem;border-radius:999px;padding:.18rem .6rem;border:1px solid var(--line);margin-right:.35rem;font-weight:600}
  .green{background:var(--green-bg);color:#0f5132;border-color:#cceedd}
  .amber{background:var(--amber-bg);color:#8a6d00;border-color:#ffe7ad}
  .red{background:var(--red-bg);color:#842029;border-color:#ffcccc}
  .card {border:1px solid var(--line);border-radius:14px;padding:14px;background:var(--card)}
  .sticky {position: sticky; top: 10px;}
  .btnrow {margin-top:.5rem}
  /* Tighten gaps */
  .stProgress {margin-top:.25rem;margin-bottom:.75rem}
  /* Form typography — ensure question > option */
  .stRadio > label, .stSelectbox > label, .stMultiselect > label {font-weight:700; font-size:1.05rem !important; color:var(--fg)}
  div[role="radiogroup"] label p, .stSelectbox p, .stMultiselect p {font-size:1rem !important;}
  /* Dashboard cards */
  .score-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px}
  @media (max-width:1100px){ .score-grid{grid-template-columns:repeat(3,minmax(0,1fr));} }
  @media (max-width:700px){ .score-grid{grid-template-columns:repeat(2,minmax(0,1fr));} }
  .score-card{border:1px solid var(--line);border-radius:16px;padding:14px;background:#fff;}
  .score-title{font-weight:700;margin-bottom:.25rem}
  .meter{height:8px;border-radius:999px;background:#f1f5f9;overflow:hidden;margin-top:.35rem;border:1px solid #e5e7eb}
  .meter > span{display:block;height:100%}
  .meter.green > span{background:var(--green)}
  .meter.amber > span{background:var(--amber)}
  .meter.red > span{background:var(--red)}
  .status-pill{display:inline-flex;align-items:center;gap:.35rem;padding:.15rem .55rem;border-radius:999px;border:1px solid var(--line); font-weight:600}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────
EMPLOYEE_RANGES = ["1–5", "6–10", "10–25", "26–50", "51–100", "More than 100"]
YEARS_OPTIONS   = ["<1 year", "1–3 years", "3–5 years", "5–10 years", "10+ years"]
WORK_MODE       = ["Local & in-person", "Online / remote", "A mix of both"]
INDUSTRY_OPTIONS = [
    "Retail & Hospitality",
    "Professional / Consulting / Legal / Accounting",
    "Manufacturing / Logistics",
    "Creative / Marketing / IT Services",
    "Health / Wellness / Education",
    "Public sector / Non-profit",
    "Other (type below)",
]
TURNOVER_OPTIONS = [
    "<€100k","€100k–€200k","€200k–€300k","€300k–€400k","€400k–€500k",
    "€500k–€600k","€600k–€700k","€700k–€800k","€800k–€900k","€900k–€1M",
    "€1M–€2M","€2M–€5M","€5M–€10M",">€10M"
]

REGION_OPTIONS = ["EU / EEA", "UK", "United States", "Other / Multi-region"]

# Expanded to capture Microsoft 365 / Office & more
CRITICAL_SYSTEMS = [
    "Microsoft 365 / Office 365", "SharePoint / OneDrive", "Exchange / Outlook (cloud)",
    "Google Workspace (Gmail/Drive)", "On-prem Active Directory", "Azure AD / Entra ID",
    "Okta / SSO provider", "VPN / Remote access", "Endpoint management (MDM/RMM)",
    "ERP (Enterprise Resource Planning)", "Point of Sale (PoS)", "CRM (Customer Relationship Management)",
    "EHR / Practice system", "Accounting / Finance (e.g., Xero/QuickBooks)",
    "Source control / DevOps (GitHub/GitLab/Bitbucket)", "E-commerce platform",
    "Payment gateway / PSP", "CMS (WordPress/Drupal/etc.)", "Other (type below)"
]
WORK_ENVIRONMENTS = ["Local servers", "Cloud apps", "Hybrid"]
REMOTE_RATIO = ["Mostly on-site", "Hybrid", "Fully remote"]
DATA_TYPES = ["Customer personal data (PII)", "Employee / staff data",
              "Health / medical data", "Financial / transaction data"]
CROSS_BORDER = ["EU-only", "Includes Non-EU regions", "Unsure"]
CERTIFICATION_OPTIONS = [
    "None", "ISO/IEC 27001", "Cyber Essentials (UK)", "SOC 2", "GDPR compliance program",
    "PCI DSS (Payment Card Industry)", "HIPAA (US healthcare)", "NIS2 readiness", "Other (type below)"
]

# ─────────────────────────────────────────────────────────────
# State (no default pre-selections for radios)
# ─────────────────────────────────────────────────────────────
defaults = dict(
    page="Step 1",
    email_for_report="",
    person_name="", company_name="",
    sector_label=INDUSTRY_OPTIONS[0], sector_other="",
    years_in_business=YEARS_OPTIONS[0],
    employee_range=EMPLOYEE_RANGES[0],
    turnover_label=TURNOVER_OPTIONS[0],
    business_region=REGION_OPTIONS[0],

    # Step 1
    work_mode="",

    # NEW Step 2 – Operational context (mandatory)
    critical_systems=[], critical_systems_other="",
    primary_work_env=WORK_ENVIRONMENTS[1],
    remote_ratio=REMOTE_RATIO[1],
    data_types=[], cross_border=CROSS_BORDER[0],
    certifications=["None"], certifications_other="",
    bp_card_payments="",

    # Step 3 – Baseline Q1–Q9
    bp_it_manager="", bp_inventory="", bp_byod="", bp_sensitive="",
    df_website="", df_https="", df_email="", df_social="", df_review="",

    # Detailed & report
    detailed_sections=[], detailed_scores={},
)
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# ─────────────────────────────────────────────────────────────
# Small helpers
# ─────────────────────────────────────────────────────────────
def progress(step:int, total:int=4, label:str=""):
    pct = max(0, min(step, total)) / total
    st.progress(pct, text=label or f"Step {step} of {total}")

def radio_none(label:str, options:List[str], *, key:str, horizontal=True, help:str|None=None, placeholder: str = "— select —"):
    """
    Radio with no preselected value using a placeholder entry so Streamlit always
    sees a valid selection. Stores the 'real' value in st.session_state[key].
    Returns the real value ("" if unselected).
    """
    ui_key = f"{key}__ui"
    ui_options = [placeholder] + list(options)
    current = st.session_state.get(key, "")
    idx = 0
    if current in options:
        idx = 1 + options.index(current)
    selected_ui = st.radio(label, ui_options, index=idx, key=ui_key, horizontal=horizontal, help=help)
    real_val = "" if selected_ui == placeholder else selected_ui
    st.session_state[key] = real_val
    return real_val

TURNOVER_TO_SIZE = {**{k:"Micro" for k in TURNOVER_OPTIONS[:11]}, **{"€2M–€5M":"Small","€5M–€10M":"Small",">€10M":"Medium"}}
EMP_RANGE_TO_SIZE = {"1–5":"Micro","6–10":"Micro","10–25":"Small","26–50":"Small","51–100":"Medium","More than 100":"Medium"}

def org_size()->str:
    a = TURNOVER_TO_SIZE.get(st.session_state.turnover_label, "Micro")
    b = EMP_RANGE_TO_SIZE.get(st.session_state.employee_range, a)
    order = {"Micro":0,"Small":1,"Medium":2}
    return a if order[a] >= order[b] else b

def resolved_industry():
    return (st.session_state.sector_other or "Other") if st.session_state.sector_label=="Other (type below)" else st.session_state.sector_label

def area_rag():
    inv=(st.session_state.bp_inventory or "").lower()
    sys=("🟢 Good","green") if inv=="yes" else ("🟡 Partial","amber") if inv=="partially" else ("🔴 At risk","red") if inv in {"no","not sure"} else ("⚪ Unknown","")
    byod=(st.session_state.bp_byod or "").lower(); email=(st.session_state.df_email or "").lower()
    if byod=="no" and email=="yes": ppl=("🟢 Safe","green")
    elif email=="no": ppl=("🔴 At risk","red")
    elif byod in {"yes","sometimes"} or email=="partially": ppl=("🟡 Mixed","amber")
    else: ppl=("⚪ Unknown","")
    web=(st.session_state.df_website or "").lower(); https=(st.session_state.df_https or "").lower()
    if web=="yes" and https=="yes": net=("🟢 Protected","green")
    elif web=="yes" and https=="no": net=("🔴 Exposed","red")
    elif web=="yes" and https=="not sure": net=("🟡 Check","amber")
    elif web=="no": net=("🟢 Low","green")
    else: net=("⚪ Unknown","")
    return sys,ppl,net

def overall_badge():
    sys,ppl,net = area_rag()
    score = sum({"green":0,"amber":1,"red":2}.get(x[1],1) for x in [sys,ppl,net])
    if score<=1: return ("Low","green","Great job — strong digital hygiene.")
    if score<=3: return ("Medium","amber","Balanced setup. A few quick wins will reduce risk fast.")
    return ("High","red","Higher exposure — prioritise quick actions to lower risk.")

# ─────────────────────────────────────────────────────────────
# Section registry (incl. Governance)
# ─────────────────────────────────────────────────────────────
def section(title_id, questions): return {"id":title_id, "title":title_id, "questions":questions}

SECTION_3 = section("Access & Identity", [
    {"id":"ai_pw","t":"🔑 Are strong passwords required for all accounts?","h":"Why it matters: weak or reused passwords are a top cause of breaches. Aim for 10–12+ characters, unique per account, ideally with a password manager."},
    {"id":"ai_mfa","t":"🛡️ Is Multi-Factor Authentication (MFA) enabled for key accounts?","h":"MFA blocks most phishing takeovers. Start with email, admin and finance accounts; prefer an authenticator app or security key over SMS."},
    {"id":"ai_admin","t":"🧰 Are admin rights limited to only those who need them?","h":"Fewer admins = smaller blast radius. Grant temporarily, review quarterly, and monitor unusual admin sign-ins."},
    {"id":"ai_shared","t":"👥 Are shared accounts avoided or controlled?","h":"Named accounts give accountability. If you must share, rotate passwords, enable MFA and log usage."},
    {"id":"ai_leavers","t":"🚪 Are old or unused accounts removed promptly?","h":"Leaver accounts are easy doors in. Disable same day a person leaves; reclaim devices and keys."},
])
SECTION_4 = section("Device & Data", [
    {"id":"dd_lock","t":"🔒 Are all devices protected with a password or PIN?","h":"Stolen devices are common. Turn on auto-lock ≤10 minutes and ‘find my device’ so you can wipe remotely."},
    {"id":"dd_fde","t":"💽 Is full-disk encryption enabled on laptops and mobiles?","h":"Encryption protects data at rest. Use BitLocker, FileVault, or built-in Android/iOS encryption."},
    {"id":"dd_edr","t":"🧿 Is reputable antivirus/EDR installed and active on all devices?","h":"Stops malware and flags risky behaviour. Examples: Microsoft Defender, CrowdStrike, SentinelOne."},
    {"id":"dd_backup","t":"📦 Are important business files backed up regularly?","h":"Backups turn disasters into hiccups. Follow 3-2-1: 3 copies, 2 media, 1 offsite (cloud counts)."},
    {"id":"dd_restore","t":"🧪 Are backups tested so you know restore works?","h":"Backups you can’t restore aren’t backups. Try restoring one file/VM quarterly."},
    {"id":"dd_usb","t":"🧰 Are staff trained to handle suspicious files/USBs?","h":"Unknown USBs and links are common entry points. Default-deny where possible; preview links before clicking."},
    {"id":"dd_wifi","t":"📶 Are company devices separated from personal on Wi-Fi?","h":"Guest vs. corporate networks reduce lateral movement; VLANs help where possible."},
])
SECTION_5 = section("System & Software Updates", [
    {"id":"su_os_auto","t":"♻️ Are operating systems kept up to date automatically?","h":"Most breaches exploit known bugs. Turn on auto-update; an MDM helps enforce it."},
    {"id":"su_apps","t":"🧩 Are business apps updated regularly?","h":"Browsers, accounting, CRM, PoS — prefer auto-update channels to close holes quickly."},
    {"id":"su_unsupported","t":"⛔ Any devices running unsupported/outdated systems?","h":"Old OS versions don’t get fixes. Replace/upgrade or isolate them until replaced."},
    {"id":"su_review","t":"🗓️ Do you have a monthly reminder to review updates?","h":"A 10-minute monthly check catches stragglers. Calendar task or RMM report is enough."},
])
SECTION_6 = section("Incident Preparedness", [
    {"id":"ip_report","t":"📣 Do employees know how to report incidents or suspicious activity?","h":"Fast reporting shrinks impact. Provide a phishing mailbox (phish@), #security channel, or service desk route."},
    {"id":"ip_plan","t":"📝 Do you have a simple incident response plan?","h":"One page beats none: who to call, what to collect, who to notify, decision maker."},
    {"id":"ip_log","t":"🧾 Are incident details recorded when they occur?","h":"Notes enable learning and insurance/legal proof. Capture what/when/who/impact."},
    {"id":"ip_contacts","t":"📇 Are key contacts known for emergencies?","h":"Internal IT, MSP, cyber insurer, legal, data-protection contact — keep numbers handy."},
    {"id":"ip_test","t":"🎯 Have you tested or simulated a cyber incident?","h":"A 30-minute tabletop twice a year reveals gaps cheaply. Adjust the plan afterwards."},
])
SECTION_7 = section("Vendor & Cloud", [
    {"id":"vc_cloud","t":"☁️ Do you use cloud tools to store company data?","h":"Cloud is fine if configured well. Know where data lives and who can access it."},
    {"id":"vc_mfa","t":"🔐 Are cloud accounts protected with MFA and strong passwords?","h":"Enforce tenant-wide MFA; require it for all admins. Weak cloud creds = easy wins for attackers."},
    {"id":"vc_review","t":"🔎 Do you review how vendors protect your data?","h":"Check DPAs, security whitepapers and certifications (ISO 27001, SOC 2)."},
    {"id":"vc_access","t":"📜 Do you track which suppliers have access to systems/data?","h":"Keep a simple list of integrations and permissions; remove unused ones."},
    {"id":"vc_notify","t":"🚨 Will vendors notify you promptly if they have a breach?","h":"Make sure breach-notification and contact routes are in the contract."},
])
SECTION_9 = section("Governance", [
    {"id":"gov_policy","t":"📘 Do you have a short, written security policy approved by leadership?","h":"A page or two is enough: passwords, MFA, updates, incident steps, data handling."},
    {"id":"gov_roles","t":"🧭 Are responsibilities clear (who owns what)?","h":"Name an internal owner or MSP. List backups and escalation paths."},
    {"id":"gov_risk","t":"🧮 Do you review key risks at least once a year?","h":"Simple register: likelihood × impact. Focus on the top 3–5 items."},
    {"id":"gov_training","t":"🎓 Is basic security training mandatory for all staff?","h":"New starters + annual refresh. Track completion in any system."},
    {"id":"gov_records","t":"🗂️ Do you keep basic records (assets, vendors, incidents, backups)?","h":"A shared sheet works — the point is visibility and regular review."},
])

ALL_SECTIONS = [SECTION_3, SECTION_4, SECTION_5, SECTION_6, SECTION_7, SECTION_9]

def section_score(sec):
    vals=[st.session_state.get(q["id"],"") for q in sec["questions"]]
    risk={"Yes":0,"Partially":1,"Not sure":1,"No":2}
    return round(sum(risk.get(v,1) for v in vals)/len(vals),2) if vals else 0.0

def section_light(sec)->Tuple[str,str,str]:
    sc = section_score(sec)
    if sc < 0.5: return ("🟢","Low","green")
    if sc < 1.2: return ("🟡","Medium","amber")
    return ("🔴","High","red")

# ─────────────────────────────────────────────────────────────
# Export helpers
# ─────────────────────────────────────────────────────────────
def build_markdown_summary()->str:
    sys,ppl,net = area_rag()
    over_txt, over_class, over_msg = overall_badge()
    lines=[]
    lines.append("# SME Cybersecurity Self-Assessment — Summary")
    lines.append("")
    lines.append(f"- Generated: {dt.datetime.utcnow().isoformat(timespec='seconds')}Z")
    lines.append("")
    lines.append("## Snapshot")
    lines.append(f"- Business: {st.session_state.company_name}")
    lines.append(f"- Region: {st.session_state.business_region}")
    lines.append(f"- Industry: {resolved_industry()}")
    lines.append(f"- People: {st.session_state.employee_range} | Years: {st.session_state.years_in_business}")
    lines.append(f"- Turnover: {st.session_state.turnover_label} | Work mode: {st.session_state.work_mode or '—'}")
    lines.append(f"- Derived size: {org_size()}")
    lines.append("")
    lines.append(f"## Overall digital dependency: **{over_txt}**")
    lines.append(f"> {over_msg}")
    lines.append("")
    lines.append("## At-a-glance")
    lines.append(f"- Systems & devices: {sys[0]}")
    lines.append(f"- People & access: {ppl[0]}")
    lines.append(f"- Online exposure: {net[0]}")
    lines.append("")
    if st.session_state.get("detailed_scores"):
        lines.append("## Section scores")
        for sid,sc in st.session_state["detailed_scores"].items():
            sec = [s for s in ALL_SECTIONS if s["id"]==sid][0]
            emoji,label,_ = section_light(sec)
            lines.append(f"- {sid}: {emoji} {label} (score {sc})")
        lines.append("")
    return "\n".join(lines)

def build_csv()->bytes:
    rows=[]
    rows.append(["Field","Value"])
    basics = {
        "Business": st.session_state.company_name,
        "Region": st.session_state.business_region,
        "Industry": resolved_industry(),
        "People": st.session_state.employee_range,
        "Years": st.session_state.years_in_business,
        "Turnover": st.session_state.turnover_label,
        "Work mode": st.session_state.work_mode or "",
        "Size (derived)": org_size(),
    }
    for k,v in basics.items(): rows.append([k, v])
    rows.append([])
    rows.append(["Baseline Q1–Q9","Answer"])
    base = {
        "Q1 IT oversight": st.session_state.bp_it_manager,
        "Q2 Device inventory": st.session_state.bp_inventory,
        "Q3 BYOD": st.session_state.bp_byod,
        "Q4 Sensitive data": st.session_state.bp_sensitive,
        "Q5 Website": st.session_state.df_website,
        "Q6 HTTPS": st.session_state.df_https,
        "Q7 Business email": st.session_state.df_email,
        "Q8 Social presence": st.session_state.df_social,
        "Q9 Public info checks": st.session_state.df_review,
    }
    for k,v in base.items(): rows.append([k, v])
    if st.session_state.get("detailed_scores"):
        rows.append([])
        rows.append(["Section","Risk score"])
        for sid,sc in st.session_state["detailed_scores"].items():
            rows.append([sid, sc])
    out = StringIO()
    w = csv.writer(out)
    for r in rows: w.writerow(r)
    return out.getvalue().encode("utf-8")

# ─────────────────────────────────────────────────────────────
# UI — Step 1 (Business basics)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 1":
    progress(1, total=4, label="Business basics")
    st.markdown("## 🧭 Tell us about the business")
    st.caption("Just the essentials — this sets context for the recommendations.")

    snap, form = st.columns([1, 2], gap="large")
    with snap:
        st.markdown('<div class="sticky">', unsafe_allow_html=True)
        st.markdown("#### 📸 Snapshot")
        st.markdown(
            f"<div class='card'><b>Business:</b> {st.session_state.company_name or '—'}<br>"
            f"<b>Region:</b> {st.session_state.business_region}<br>"
            f"<b>Industry:</b> {resolved_industry()}<br>"
            f"<b>People:</b> {st.session_state.employee_range} · <b>Years:</b> {st.session_state.years_in_business}<br>"
            f"<b>Turnover:</b> {st.session_state.turnover_label}<br>"
            f"<b>Work mode:</b> {st.session_state.work_mode or '—'}<br>"
            f"<b>Size (derived):</b> {org_size()}</div>", unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with form:
        st.markdown("#### 👤 About you")
        st.session_state.email_for_report = st.text_input("📧 Email for report (optional, for sending later)", value=st.session_state.email_for_report)
        st.session_state.person_name = st.text_input("Your name *", value=st.session_state.person_name)

        st.markdown("#### 🏢 About the business")
        st.session_state.company_name = st.text_input("Business name *", value=st.session_state.company_name)

        c1, c2 = st.columns(2)
        with c1:
            st.session_state.business_region = st.selectbox("🌍 Business location / region *", REGION_OPTIONS, index=REGION_OPTIONS.index(st.session_state.business_region))
            st.session_state.sector_label = st.selectbox("🏷️ Industry / service *", INDUSTRY_OPTIONS,
                index=INDUSTRY_OPTIONS.index(st.session_state.sector_label) if st.session_state.sector_label in INDUSTRY_OPTIONS else 0)
            if st.session_state.sector_label == "Other (type below)":
                st.session_state.sector_other = st.text_input("✍️ Type your industry *", value=st.session_state.sector_other)
            else:
                st.session_state.sector_other = ""
            st.session_state.years_in_business = st.selectbox("📅 How long in business? *", YEARS_OPTIONS,
                index=YEARS_OPTIONS.index(st.session_state.years_in_business))
        with c2:
            st.session_state.employee_range = st.selectbox("👥 People (incl. contractors) *", EMPLOYEE_RANGES,
                index=EMPLOYEE_RANGES.index(st.session_state.employee_range))
            st.session_state.turnover_label = st.selectbox("💶 Approx. annual turnover *", TURNOVER_OPTIONS,
                index=TURNOVER_OPTIONS.index(st.session_state.turnover_label))

        radio_none("🧭 Work mode *", WORK_MODE, key="work_mode", horizontal=True,
                   help="Where most work happens — influences risk and recommendations.")

        missing=[]
        if not st.session_state.person_name.strip(): missing.append("name")
        if not st.session_state.company_name.strip(): missing.append("company")
        if st.session_state.sector_label=="Other (type below)" and not st.session_state.sector_other.strip():
            missing.append("industry")
        if not st.session_state.work_mode: missing.append("work mode")

        cA, cB = st.columns(2)
        with cA:
            st.button("Start over", on_click=lambda: [st.session_state.update(defaults)])
        with cB:
            st.button("Continue ➜", type="primary", disabled=len(missing)>0,
                      on_click=lambda: st.session_state.update({"page":"Step 2"}))

# ─────────────────────────────────────────────────────────────
# UI — Step 2 (Operational context — mandatory)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 2":
    progress(2, total=4, label="Operational context")
    st.markdown("## 🧱 Operational context")
    st.caption("This step captures your core systems and data flows — required to tailor the guidance.")

    cA, cB = st.columns(2)
    with cA:
        st.session_state.critical_systems = st.multiselect("🧩 Critical systems in use *",
            CRITICAL_SYSTEMS, default=st.session_state.critical_systems,
            help="Include collaboration/email suites (e.g., **Microsoft 365**, **Google Workspace**), identity systems (e.g., **Entra ID/Azure AD**, **Okta**), and business platforms (ERP/CRM/PoS).")
        if "Other (type below)" in st.session_state.critical_systems:
            st.session_state.critical_systems_other = st.text_input("✍️ Specify other system", value=st.session_state.critical_systems_other)
        st.session_state.primary_work_env = st.radio("🏗️ Primary work environment *", WORK_ENVIRONMENTS,
            horizontal=True, index=WORK_ENVIRONMENTS.index(st.session_state.primary_work_env),
            help="Where your key apps and files mainly live.")
        st.session_state.remote_ratio = st.radio("🏡 Remote work ratio *", REMOTE_RATIO,
            horizontal=True, index=REMOTE_RATIO.index(st.session_state.remote_ratio),
            help="Helps gauge device and access risks.")
    with cB:
        st.session_state.data_types = st.multiselect("🔍 Types of personal data handled *",
            DATA_TYPES, default=st.session_state.data_types,
            help="Tick all that apply. Sensitive data calls for stronger controls.")
        st.session_state.cross_border = st.radio("🌐 Cross-border data flows *", CROSS_BORDER, horizontal=True,
                                                 index=CROSS_BORDER.index(st.session_state.cross_border),
                                                 help="Do you transfer or store data outside the EU/UK?")
        st.session_state.certifications = st.multiselect("🔒 Certifications / schemes",
                                                          CERTIFICATION_OPTIONS, default=st.session_state.certifications,
                                                          help="Any frameworks you align with or are pursuing.")
        if "Other (type below)" in st.session_state.certifications:
            st.session_state.certifications_other = st.text_input("✍️ Specify other scheme", value=st.session_state.certifications_other)

    radio_none("💳 Do you accept or process card payments (online or in-store)? *",
               ["Yes","No","Not sure"], key="bp_card_payments", horizontal=True,
               help="PCI DSS responsibilities vary by setup (gateway vs PoS vs e-commerce).")

    missing=[]
    if not st.session_state.critical_systems: missing.append("critical systems")
    if not st.session_state.data_types: missing.append("data types")
    if not st.session_state.bp_card_payments: missing.append("card payments")

    cA, cB = st.columns(2)
    with cA:
        st.button("⬅ Back to Step 1", on_click=lambda: st.session_state.update({"page":"Step 1"}))
    with cB:
        st.button("Continue ➜", type="primary", disabled=len(missing)>0,
                  on_click=lambda: st.session_state.update({"page":"Step 3"}))

# ─────────────────────────────────────────────────────────────
# UI — Step 3 (Baseline Q1–Q9)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 3":
    progress(3, total=4, label="Your current practices")
    st.markdown("## 🧪 Your current practices")
    st.caption("Nine quick checks. Each hint explains the ‘why’ so the action is clear.")

    snap, body, prev = st.columns([1, 1.7, 1], gap="large")
    with snap:
        st.markdown('<div class="sticky">', unsafe_allow_html=True)
        st.markdown("#### 📸 Snapshot")
        st.markdown(
            f"<div class='card'><b>Business:</b> {st.session_state.company_name}<br>"
            f"<b>Region:</b> {st.session_state.business_region}<br>"
            f"<b>Industry:</b> {resolved_industry()}<br>"
            f"<b>People:</b> {st.session_state.employee_range} · <b>Years:</b> {st.session_state.years_in_business}<br>"
            f"<b>Turnover:</b> {st.session_state.turnover_label} · <b>Size:</b> {org_size()}<br>"
            f"<b>Work mode:</b> {st.session_state.work_mode}</div>", unsafe_allow_html=True
        )
        sys,ppl,net = area_rag()
        st.markdown("#### 🔎 At-a-glance")
        st.markdown(f"<span class='chip {sys[1]}'>🖥️ Systems · {sys[0]}</span>"
                    f"<span class='chip {ppl[1]}'>👥 People · {ppl[0]}</span>"
                    f"<span class='chip {net[1]}'>🌐 Exposure · {net[0]}</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with body:
        tab1, tab2 = st.tabs(["🧭 Business profile (Q1–Q4)", "🌐 Digital footprint (Q5–Q9)"])

        with tab1:
            radio_none("**Q1. 🧑‍💻 Who looks after your IT day-to-day?**",
                       ["Self-managed","Outsourced IT","Shared responsibility","Not sure"],
                       key="bp_it_manager", horizontal=True,
                       help="Clear ownership prevents gaps. Even a simple rota with an MSP works.")
            st.markdown('<div class="hint">Includes laptops/phones, Wi-Fi, email, website, point-of-sale, cloud apps, file storage/backup.</div>', unsafe_allow_html=True)

            radio_none("**Q2. 📋 Do you keep a simple list of company devices (laptops, phones, servers)?**",
                       ["Yes","Partially","No","Not sure"], key="bp_inventory", horizontal=True,
                       help="Asset lists help you patch, insure and recover quickly.")
            st.markdown('<div class="hint">Keep model/owner/OS/update status. A shared sheet is fine to start.</div>', unsafe_allow_html=True)

            radio_none("**Q3. 📱 Do people use personal devices for work (Bring Your Own Device)?**",
                       ["Yes","Sometimes","No","Not sure"], key="bp_byod", horizontal=True,
                       help="Personal devices need minimum rules (screen lock, updates, disk encryption).")
            st.markdown('<div class="hint">Example: checking work email on a personal phone or laptop.</div>', unsafe_allow_html=True)

            radio_none("**Q4. 🔐 Do you handle sensitive customer or financial data?**",
                       ["Yes","No","Not sure"], key="bp_sensitive", horizontal=True,
                       help="Handling PII, finance or health data raises the bar for controls.")
            st.markdown('<div class="hint">Think payment details, personal records, signed contracts, health records.</div>', unsafe_allow_html=True)

        with tab2:
            radio_none("**Q5. 🕸️ Do you have a public website?**",
                       ["Yes","No"], key="df_website", horizontal=True,
                       help="Web presence increases attack surface and brand risk.")
            radio_none("**Q6. 🔒 Is your website HTTPS (padlock in the browser)?**",
                       ["Yes","Partially","No","Not sure"], key="df_https", horizontal=True,
                       help="HTTPS protects visitors and is a trust signal. Many hosts enable it for free.")
            st.markdown('<div class="hint">Redirect HTTP→HTTPS and renew certificates automatically.</div>', unsafe_allow_html=True)

            radio_none("**Q7. ✉️ Do you use business email addresses?**",
                       ["Yes","Partially","No"], key="df_email", horizontal=True,
                       help="Custom domains + MFA improve deliverability and security.")
            st.markdown('<div class="hint">Personal mailboxes are hard to secure and easy to spoof.</div>', unsafe_allow_html=True)

            radio_none("**Q8. 📣 Is your business active on social media?**",
                       ["Yes","No"], key="df_social", horizontal=True,
                       help="Social accounts are common takeover targets — use strong passwords & MFA.")

            radio_none("**Q9. 🔎 Do you regularly check what’s public about the company or staff online?**",
                       ["Yes","Sometimes","No"], key="df_review", horizontal=True,
                       help="Periodic checks help catch exposed credentials or oversharing.")
            st.markdown('<div class="hint">Search engines, company profiles, staff bios, screenshots can reveal systems.</div>', unsafe_allow_html=True)

    with prev:
        st.write(""); st.write("")
        st.button("⬅ Back to Step 2", on_click=lambda: st.session_state.update({"page":"Step 2"}))
        required = ["bp_it_manager","bp_inventory","bp_byod","bp_sensitive","df_website","df_https","df_email","df_social","df_review"]
        missing=[k for k in required if not st.session_state.get(k)]
        st.button("Finish Initial Assessment ➜", type="primary", disabled=len(missing)>0,
                  on_click=lambda: st.session_state.update({"page":"Step 4"}))

# ─────────────────────────────────────────────────────────────
# UI — Step 4 (Summary)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 4":
    progress(4, total=4, label="Summary")
    st.markdown("## 📊 Initial Assessment Summary")
    over_txt, over_class, over_msg = overall_badge()
    st.markdown(f"<span class='pill {over_class}'>Overall digital dependency: <b>{over_txt}</b></span>", unsafe_allow_html=True)
    st.caption(over_msg)

    snap, glance = st.columns([1.1, 1.9], gap="large")
    with snap:
        st.markdown("### 📸 Snapshot")
        st.markdown(
            f"<div class='card'><b>Business:</b> {st.session_state.company_name}<br>"
            f"<b>Region:</b> {st.session_state.business_region}<br>"
            f"<b>Industry:</b> {resolved_industry()}<br>"
            f"<b>People:</b> {st.session_state.employee_range} · <b>Years:</b> {st.session_state.years_in_business} · "
            f"<b>Turnover:</b> {st.session_state.turnover_label}<br>"
            f"<b>Work mode:</b> {st.session_state.work_mode} · <b>Size:</b> {org_size()}</div>", unsafe_allow_html=True
        )

    with glance:
        st.markdown("### 🔎 At-a-glance")
        sys,ppl,net = area_rag()
        st.markdown(f"<span class='chip {sys[1]}'>🖥️ Systems · {sys[0]}</span>"
                    f"<span class='chip {ppl[1]}'>👥 People · {ppl[0]}</span>"
                    f"<span class='chip {net[1]}'>🌐 Exposure · {net[0]}</span>", unsafe_allow_html=True)

    st.markdown("---")
    c1,c2,c3 = st.columns([1,1,2])
    with c1:
        st.button("⬅ Back", on_click=lambda: st.session_state.update({"page":"Step 3"}))
    with c2:
        st.button("Start over", on_click=lambda: [st.session_state.update(defaults), st.session_state.update({"page":"Step 1"})])
    with c3:
        st.button("Continue to detailed assessment ➜", type="primary",
                  on_click=lambda: st.session_state.update({"detailed_sections":[s["id"] for s in ALL_SECTIONS],
                                                            "page":"Detailed"}))

    st.markdown("### ⬇️ Export initial summary")
    md = build_markdown_summary()
    st.download_button("Download summary (Markdown)", data=md.encode("utf-8"),
                       file_name="cyber-assessment-summary.md", mime="text/markdown")

# ─────────────────────────────────────────────────────────────
# UI — Detailed
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Detailed":
    st.markdown("## 🧩 Detailed Assessment")
    tabs = st.tabs([("🔐 " if s["id"]=='Access & Identity' else
                     "💻 " if s['id']=='Device & Data' else
                     "🧩 " if s['id']=='System & Software Updates' else
                     "🚨 " if s['id']=='Incident Preparedness' else
                     "☁️ " if s['id']=='Vendor & Cloud' else
                     "🏛️ ")+s["id"] for s in ALL_SECTIONS])
    for tab, sec in zip(tabs, ALL_SECTIONS):
        with tab:
            st.caption({"Access & Identity":"Control of user access and authentication.",
                        "Device & Data":"How well devices and company data are secured.",
                        "System & Software Updates":"Keeping systems patched and supported.",
                        "Incident Preparedness":"Readiness to detect, respond, and recover.",
                        "Vendor & Cloud":"Security of third-party tools, vendors, and SaaS.",
                        "Governance":"Leadership, policy, roles, and record-keeping."}[sec["id"]])
            for q in sec["questions"]]:
                radio_none(q["t"], ["Yes","Partially","No","Not sure"], key=q["id"], horizontal=True,
                           help=q["h"])
                st.markdown(f"<div class='hint'>💡 {q['h']}</div>", unsafe_allow_html=True)

    cA, cB = st.columns(2)
    with cA:
        st.button("⬅ Back to Summary", on_click=lambda: st.session_state.update({"page":"Step 4"}))
    with cB:
        def _finish():
            st.session_state["detailed_scores"]={s["id"]: section_score(s) for s in ALL_SECTIONS}
            st.session_state["page"]="Report"
        st.button("Finish & see recommendations ➜", type="primary", on_click=_finish)

# ─────────────────────────────────────────────────────────────
# UI — Report (Final Dashboard)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Report":
    st.markdown("## 🌟 Recommendations & Section Status")

    scores = st.session_state.get("detailed_scores", {})
    lookup = {s["id"]: s for s in ALL_SECTIONS}

    if scores:
        st.markdown("<div class='score-grid'>", unsafe_allow_html=True)
        # Build pretty status cards
        for sid, sc in scores.items():
            emoji,label,klass = section_light(lookup[sid])
            pct = min(100, max(0, int((2 - sc)/2 * 100)))  # 0 (High risk) .. 100 (Low risk)
            html = f"""
            <div class="score-card">
              <div class="score-title">{sid}</div>
              <div class="status-pill">{emoji} <span>{label}</span></div>
              <div style="font-size:.92rem;color:#475569;margin-top:.35rem">Risk score: {sc:.2f}</div>
              <div class="meter {klass}"><span style="width:{pct}%"></span></div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.caption("No detailed scores yet.")

    st.markdown("### 1) Quick wins (do these first)")
    quick=[]
    if st.session_state.df_website=="Yes" and st.session_state.df_https!="Yes":
        quick.append("Enable HTTPS and force redirect (HTTP→HTTPS).")
    if st.session_state.df_email in ("No","Partially"):
        quick.append("Move to business email (M365/Google) and enforce MFA.")
    if st.session_state.bp_inventory not in ("Yes","Partially"):
        quick.append("Start a device inventory and enable full-disk encryption on laptops.")
    st.markdown("\n".join([f"{i}. {x}" for i,x in enumerate(quick or ['No urgent quick wins detected.'],1)]))

    st.markdown("### 2) Foundations to build this quarter")
    foundations=[
        "Turn on automatic OS & app updates; remove unsupported systems.",
        "Automate backups and test a restore quarterly.",
        "Publish a simple BYOD rule: screen lock, OS updates, disk encryption, MFA for email.",
    ]
    st.markdown("\n".join([f"{i}. {x}" for i,x in enumerate(foundations,1)]))

    st.markdown("### 3) Next-level / compliance alignment")
    nextlvl=[]
    if any(k in (st.session_state.bp_card_payments or "").lower() for k in ["yes"]):
        nextlvl.append("Confirm PCI DSS responsibilities with your PoS/PSP.")
    nextlvl.append("Document GDPR basics if you handle EU/UK personal data (DPAs, transfers, contact).")
    st.markdown("\n".join([f"{i}. {x}" for i,x in enumerate(nextlvl,1)]))

    st.markdown("---")
    st.markdown("### ⬇️ Export results")
    st.download_button("Download results (CSV)", data=build_csv(), file_name="cyber-assessment-results.csv",
                       mime="text/csv")
    st.download_button("Download summary (Markdown)", data=build_markdown_summary().encode("utf-8"),
                       file_name="cyber-assessment-summary.md", mime="text/markdown")

    cA, cB = st.columns(2)
    with cA:
        st.button("⬅ Back to Detailed", on_click=lambda: st.session_state.update({"page":"Detailed"}))
    with cB:
        st.button("Start over", on_click=lambda: [st.session_state.update(defaults), st.session_state.update({"page":"Step 1"})])
