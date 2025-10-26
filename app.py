# app.py — SME Cybersecurity Self-Assessment (single file)
# Includes: Awareness & AI Risk domain, 0–100 five-band maturity (light weighting),
# standards mapping, guided simulations, privacy notice, and CSV/Markdown exports.

import csv
from io import StringIO
from typing import List, Dict, Tuple, Optional
import datetime as dt
import streamlit as st

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
  .hint {color:#394b63; font-size:.98rem; font-style:italic; margin:.25rem 0 .75rem; line-height:1.4}
  .pill {display:inline-block;border-radius:999px;padding:.18rem .55rem;border:1px solid #e5e7eb;font-size:.9rem;color:#374151;background:#fff}
  .chip {display:inline-flex;align-items:center;gap:.35rem;border-radius:999px;padding:.18rem .6rem;border:1px solid var(--line);margin-right:.35rem;font-weight:600}
  .green{background:var(--green-bg);color:#0f5132;border-color:#cceedd}
  .amber{background:var(--amber-bg);color:#8a6d00;border-color:#ffe7ad}
  .red{background:var(--red-bg);color:#842029;border-color:#ffcccc}
  .card {border:1px solid var(--line);border-radius:14px;padding:14px;background:#fff}
  .sticky {position: sticky; top: 10px;}
  .score-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px}
  @media (max-width:1100px){ .score-grid{grid-template-columns:repeat(3,minmax(0,1fr));} }
  @media (max-width:700px){ .score-grid{grid-template-columns:repeat(2,minmax(0,1fr));} }
  .score-card{border:1px solid var(--line);border-radius:16px;padding:14px;background:#fff}
  .score-title{font-weight:700;margin-bottom:.25rem}
  .meter{height:8px;border-radius:999px;background:#f1f5f9;overflow:hidden;margin-top:.35rem;border:1px solid #e5e7eb}
  .meter > span{display:block;height:100%}
  .meter.green > span{background:var(--green)}
  .meter.amber > span{background:var(--amber)}
  .meter.red > span{background:var(--red)}
  .status-pill{display:inline-flex;align-items:center;gap:.35rem;padding:.15rem .55rem;border:1px solid var(--line); font-weight:600}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ SME Cybersecurity Self-Assessment")
st.info("**Privacy:** All inputs stay in this session only. No data is sent or stored. Use synthetic or anonymised details if unsure.")

# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────
EMPLOYEE_RANGES = ["1–5", "6–10", "10–25", "26–50", "51–100", "More than 100"]
YEARS_OPTIONS   = ["<1 year", "1–3 years", "3–5 years", "5–10 years", "10+ years"]
WORK_MODE       = ["Local & in-person", "Online / remote", "A mix of both"]
INDUSTRY_OPTIONS = [
    "Retail & Hospitality","Professional / Consulting / Legal / Accounting",
    "Manufacturing / Logistics","Creative / Marketing / IT Services",
    "Health / Wellness / Education","Public sector / Non-profit","Other (type below)",
]
TURNOVER_OPTIONS = [
    "<€100k","€100k–€200k","€200k–€300k","€300k–€400k","€400k–€500k",
    "€500k–€600k","€600k–€700k","€700k–€800k","€800k–€900k","€900k–€1M",
    "€1M–€2M","€2M–€5M","€5M–€10M",">€10M"
]
REGION_OPTIONS = ["EU / EEA", "UK", "United States", "Other / Multi-region"]

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
DATA_TYPES = ["Customer personal data (PII)", "Employee / staff data", "Health / medical data", "Financial / transaction data"]
CROSS_BORDER = ["EU-only", "Includes Non-EU regions", "Unsure"]
CERTIFICATION_OPTIONS = [
    "None","ISO/IEC 27001","Cyber Essentials (UK)","SOC 2","GDPR compliance program",
    "PCI DSS (Payment Card Industry)","HIPAA (US healthcare)","NIS2 readiness","Other (type below)"
]

TURNOVER_TO_SIZE = {**{k:"Micro" for k in TURNOVER_OPTIONS[:11]}, **{"€2M–€5M":"Small","€5M–€10M":"Small",">€10M":"Medium"}}
EMP_RANGE_TO_SIZE = {"1–5":"Micro","6–10":"Micro","10–25":"Small","26–50":"Small","51–100":"Medium","More than 100":"Medium"}

# Five-band model + light weighting + standards mapping
ANSWER_VAL = {"Yes":100, "Partially":50, "Not sure":50, "No":0}
BANDS = [(0,20,"Very Low"),(21,40,"Low"),(41,60,"Moderate"),(61,80,"Good"),(81,100,"Strong")]
DOMAIN_WEIGHT = {
    "Governance":1.2, "Access & Identity":1.3, "Device & Data":1.1,
    "System & Software Updates":1.1, "Incident Preparedness":1.1,
    "Vendor & Cloud":1.0, "Awareness & AI Risk":1.2
}
STD_MAP = {
  "Access & Identity": ["NIST: PR.AC","ISO: A.5/A.8"],
  "Device & Data": ["NIST: PR.DS/PR.IP","ISO: A.8/A.12"],
  "System & Software Updates": ["NIST: PR.IP","ISO: A.8.8/A.12.6"],
  "Incident Preparedness": ["NIST: RS/RC","ISO: A.5.24/A.5.25"],
  "Vendor & Cloud": ["NIST: ID.SC/PR.AT","ISO: A.5.19/A.5.20"],
  "Governance": ["NIST: ID.GV","ISO: A.5 (org controls)"],
  "Awareness & AI Risk": ["NIST: PR.AT/ID.BE","ISO: A.6.3 (awareness)"]
}

# ─────────────────────────────────────────────────────────────
# State (no default pre-selections for radios)
# ─────────────────────────────────────────────────────────────
defaults = dict(
    page="Step 1",
    email_for_report="", person_name="", company_name="",
    sector_label=INDUSTRY_OPTIONS[0], sector_other="", years_in_business=YEARS_OPTIONS[0],
    employee_range=EMPLOYEE_RANGES[0], turnover_label=TURNOVER_OPTIONS[0],
    business_region=REGION_OPTIONS[0], work_mode="",
    critical_systems=[], critical_systems_other="", primary_work_env=WORK_ENVIRONMENTS[1],
    remote_ratio=REMOTE_RATIO[1], data_types=[], cross_border=CROSS_BORDER[0],
    certifications=["None"], certifications_other="", bp_card_payments="",
    bp_it_manager="", bp_inventory="", bp_byod="", bp_sensitive="",
    df_website="", df_https="", df_email="", df_social="", df_review="",
    detailed_sections=[], detailed_scores_pct={}
)
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def progress(step:int, total:int=5, label:str=""):
    pct = max(0, min(step, total)) / total
    st.progress(pct, text=label or f"Step {step} of {total}")

def radio_none(label:str, options:List[str], *, key:str, horizontal:bool=True, help:Optional[str]=None, placeholder: str = "— select —"):
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

def section(title_id, questions): 
    return {"id":title_id, "title":title_id, "questions":questions}

# ─────────────────────────────────────────────────────────────
# Question bank (single file)
# ─────────────────────────────────────────────────────────────
SECTION_3 = section("Access & Identity", [
    {"id":"ai_pw","t":"🔑 Are strong passwords required for all accounts?","h":"Use a password manager; 10–12+ chars per account."},
    {"id":"ai_mfa","t":"🛡️ Is Multi-Factor Authentication (MFA) enabled for key accounts?","h":"Start with email, admin and finance; prefer app or security key over SMS."},
    {"id":"ai_admin","t":"🧰 Are admin rights limited to only those who need them?","h":"Grant temporarily; review quarterly; monitor unusual admin sign-ins."},
    {"id":"ai_shared","t":"👥 Are shared accounts avoided or controlled?","h":"Prefer named accounts; if shared, rotate passwords, enable MFA, and log usage."},
    {"id":"ai_leavers","t":"🚪 Are old or unused accounts removed promptly?","h":"Disable the same day a person leaves; reclaim devices and keys."},
])
SECTION_4 = section("Device & Data", [
    {"id":"dd_lock","t":"🔒 Are all devices protected with a password or PIN?","h":"Turn on auto-lock ≤10 minutes and ‘find my device’."},
    {"id":"dd_fde","t":"💽 Is full-disk encryption enabled on laptops and mobiles?","h":"Use BitLocker, FileVault, or built-in Android/iOS encryption."},
    {"id":"dd_edr","t":"🧿 Is reputable antivirus/EDR installed and active on all devices?","h":"Stops malware and flags risky behaviour (e.g., MS Defender)."},
    {"id":"dd_backup","t":"📦 Are important business files backed up regularly?","h":"Follow 3-2-1: 3 copies, 2 media, 1 offsite."},
    {"id":"dd_restore","t":"🧪 Are backups tested so you know restore works?","h":"Try restoring one file/VM quarterly."},
    {"id":"dd_usb","t":"🧰 Are staff trained to handle suspicious files/USBs?","h":"Default-deny where possible; preview links before clicking."},
    {"id":"dd_wifi","t":"📶 Are company devices separated from personal on Wi-Fi?","h":"Guest vs. corporate networks reduce lateral movement."},
])
SECTION_5 = section("System & Software Updates", [
    {"id":"su_os_auto","t":"♻️ Are operating systems kept up to date automatically?","h":"Turn on auto-update; MDM helps enforce it."},
    {"id":"su_apps","t":"🧩 Are business apps updated regularly?","h":"Prefer auto-update channels."},
    {"id":"su_unsupported","t":"⛔ Any devices running unsupported/outdated systems?","h":"Replace/upgrade or isolate them until replaced."},
    {"id":"su_review","t":"🗓️ Do you have a monthly reminder to review updates?","h":"A 10-minute monthly check catches stragglers."},
])
SECTION_6 = section("Incident Preparedness", [
    {"id":"ip_report","t":"📣 Do employees know how to report incidents or suspicious activity?","h":"Provide a phishing mailbox or service desk route; make it obvious."},
    {"id":"ip_plan","t":"📝 Do you have a simple incident response plan?","h":"One page: who to call, what to collect, who to notify, decision maker."},
    {"id":"ip_log","t":"🧾 Are incident details recorded when they occur?","h":"Capture what/when/who/impact; notes enable learning and proof."},
    {"id":"ip_contacts","t":"📇 Are key contacts known for emergencies?","h":"Internal IT/MSP, cyber insurer, legal, data-protection contact."},
    {"id":"ip_test","t":"🎯 Have you tested or simulated a cyber incident?","h":"A 30-minute tabletop twice a year reveals gaps cheaply."},
])
SECTION_7 = section("Vendor & Cloud", [
    {"id":"vc_cloud","t":"☁️ Do you use cloud tools to store company data?","h":"Know where data lives and who can access it."},
    {"id":"vc_mfa","t":"🔐 Are cloud accounts protected with MFA and strong passwords?","h":"Enforce tenant-wide MFA; require it for all admins."},
    {"id":"vc_review","t":"🔎 Do you review how vendors protect your data?","h":"Check DPAs, security whitepapers and certifications (ISO 27001, SOC 2)."},
    {"id":"vc_access","t":"📜 Do you track which suppliers have access to systems/data?","h":"List integrations and permissions; remove unused ones."},
    {"id":"vc_notify","t":"🚨 Will vendors notify you promptly if they have a breach?","h":"Ensure breach-notification clauses and contacts exist."},
])
SECTION_9 = section("Governance", [
    {"id":"gov_policy","t":"📘 Do you have a short, written security policy approved by leadership?","h":"A page or two: passwords, MFA, updates, incident steps, data handling."},
    {"id":"gov_roles","t":"🧭 Are responsibilities clear (who owns what)?","h":"Name an internal owner or MSP; list backups and escalation paths."},
    {"id":"gov_risk","t":"🧮 Do you review key risks at least once a year?","h":"Simple register: likelihood × impact for top 3–5 items."},
    {"id":"gov_training","t":"🎓 Is basic security training mandatory for all staff?","h":"New starters + annual refresh; track completion."},
    {"id":"gov_records","t":"🗂️ Do you keep basic records (assets, vendors, incidents, backups)?","h":"A shared sheet is fine; the point is visibility and review."},
])
SECTION_AI = section("Awareness & AI Risk", [
    {"id":"ai_phish","t":"🎣 Do staff practise spotting phish/vish/smishing at least quarterly?","h":"Little-and-often beats annual training; rehearse reporting."},
    {"id":"ai_deepfake","t":"🎭 Are deepfake/voice-clone risks covered in training?","h":"Agree a verification backchannel for high-risk requests."},
    {"id":"ai_reporting","t":"📮 Is there a simple way to report suspicious messages?","h":"Mailbox (phish@) or ‘report phish’ button; track usage."},
    {"id":"ai_awareness","t":"🧠 Are AI-generated content risks explained in plain language?","h":"Polished language ≠ trusted request; verify sender/route."},
    {"id":"ai_metrics","t":"📊 Do you review basic awareness metrics?","h":"Completion, reporting rate, time-to-report help tune effort."},
])

ALL_SECTIONS = [SECTION_3, SECTION_4, SECTION_5, SECTION_6, SECTION_7, SECTION_9, SECTION_AI]

# ─────────────────────────────────────────────────────────────
# Scoring
# ─────────────────────────────────────────────────────────────
def section_score_pct(sec:Dict)->float:
    vals=[st.session_state.get(q["id"],"") for q in sec["questions"]]
    if not vals: return 0.0
    return round(sum(ANSWER_VAL.get(v,50) for v in vals)/len(vals),2)

def section_light_from_pct(pct:float)->Tuple[str,str,str]:
    if pct >= 70: return ("🟢","Low","green")
    if pct >= 40: return ("🟡","Medium","amber")
    return ("🔴","High","red")

def overall_maturity(sections:List[Dict])->Tuple[float,str]:
    scores=[section_score_pct(s) for s in sections]
    weights=[DOMAIN_WEIGHT.get(s["id"],1.0) for s in sections]
    total = sum(s*w for s,w in zip(scores,weights))/max(1,sum(weights))
    label = next(lbl for lo,hi,lbl in BANDS if lo <= total <= hi)
    return round(total,2), label

def area_rag_overall():
    sys,ppl,net = area_rag()
    score = sum({"green":0,"amber":1,"red":2}.get(x[1],1) for x in [sys,ppl,net])
    if score<=1: return ("Low","green","Great job — strong digital hygiene.")
    if score<=3: return ("Medium","amber","Balanced setup. A few quick wins will reduce risk fast.")
    return ("High","red","Higher exposure — prioritise quick actions to lower risk.")

# ─────────────────────────────────────────────────────────────
# Export helpers
# ─────────────────────────────────────────────────────────────
def build_markdown_summary()->str:
    sys,ppl,net = area_rag()
    over_txt, over_class, over_msg = area_rag_overall()
    overall_pct, band = overall_maturity(ALL_SECTIONS)
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
    lines.append(f"## Overall digital dependency (heuristic): **{over_txt}**")
    lines.append(f"> {over_msg}")
    lines.append("")
    lines.append(f"## Overall maturity: **{overall_pct}% · {band}**")
    lines.append("")
    lines.append("## At-a-glance")
    lines.append(f"- Systems & devices: {sys[0]}")
    lines.append(f"- People & access: {ppl[0]}")
    lines.append(f"- Online exposure: {net[0]}")
    lines.append("")
    if st.session_state.get("detailed_scores_pct"):
        lines.append("## Section scores (0–100) and tags")
        for sid, pct in st.session_state["detailed_scores_pct"].items():
            emoji,label,_ = section_light_from_pct(pct)
            tags = " · ".join(STD_MAP.get(sid, []))
            lines.append(f"- {sid}: {emoji} {label} — {pct}%  ({tags})")
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
    if st.session_state.get("detailed_scores_pct"):
        rows.append([])
        rows.append(["Section","Score (0–100)"])
        for sid,pct in st.session_state["detailed_scores_pct"].items():
            rows.append([sid, pct])
        overall_pct, band = overall_maturity(ALL_SECTIONS)
        rows.append(["Overall maturity", f"{overall_pct}% · {band}"])
    out = StringIO(); w = csv.writer(out)
    for r in rows: w.writerow(r)
    return out.getvalue().encode("utf-8")

# ─────────────────────────────────────────────────────────────
# UI — Step 1 (Business basics)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 1":
    progress(1, total=5, label="Business basics")
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
    progress(2, total=5, label="Operational context")
    st.markdown("## 🧱 Operational context")
    st.caption("This step captures your core systems and data flows — required to tailor the guidance.")

    cA, cB = st.columns(2)
    with cA:
        st.session_state.critical_systems = st.multiselect("🧩 Critical systems in use *",
            CRITICAL_SYSTEMS, default=st.session_state.critical_systems,
            help="Include collaboration/email (M365 / Google), identity (Entra ID/Okta), business platforms (ERP/CRM/PoS).")
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
    progress(3, total=5, label="Your current practices")
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
# UI — Step 4 (Summary + Simulations)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 4":
    progress(4, total=5, label="Summary & Simulations")
    st.markdown("## 📊 Initial Assessment Summary")
    over_txt, over_class, over_msg = area_rag_overall()
    st.markdown(f"<span class='pill {over_class}'>Overall digital dependency (heuristic): <b>{over_txt}</b></span>", unsafe_allow_html=True)
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

    st.markdown("### 🧪 Guided simulations (safe, read-only)")
    with st.expander("🎣 Invoice phish preview"):
        st.write("From: “Accounts” <accounts@trusted-lookalike.com> — ‘Please review the attached invoice ASAP.’")
        st.write("Cues: display-name spoof, urgent tone, link hover mismatch, attachment from unknown sender.")
        st.write("Action: report via your phish route; verify invoices via a known backchannel.")
    with st.expander("🗣️ CEO voice-clone request"):
        st.write("Scenario: an urgent voice note asking for a payment change.")
        st.write("Cues: urgency + authority; unfamiliar contact method; out-of-hours request.")
        st.write("Action: verify via a known number/channel before acting.")
    with st.expander("🔐 ‘Security alert’ login lure"):
        st.write("Scenario: ‘Your account will be locked. Reset password now.’")
        st.write("Cues: generic greeting; domain mismatch; push to click.")
        st.write("Action: do not click; go to the site directly or use IT’s known route.")

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
                     "🏛️ " if s['id']=='Governance' else
                     "🧠 ")+s["id"] for s in ALL_SECTIONS])
    for tab, sec in zip(tabs, ALL_SECTIONS):
        with tab:
            st.caption({
                "Access & Identity":"Control of user access and authentication.",
                "Device & Data":"How well devices and company data are secured.",
                "System & Software Updates":"Keeping systems patched and supported.",
                "Incident Preparedness":"Readiness to detect, respond, and recover.",
                "Vendor & Cloud":"Security of third-party tools, vendors, and SaaS.",
                "Governance":"Leadership, policy, roles, and record-keeping.",
                "Awareness & AI Risk":"Deception literacy, reporting, and backchannel habits."
            }.get(sec["id"], ""))
            for q in sec["questions"]:
                radio_none(q["t"], ["Yes","Partially","No","Not sure"], key=q["id"], horizontal=True, help=q["h"])
                st.markdown(f"<div class='hint'>💡 {q['h']}</div>", unsafe_allow_html=True)

    cA, cB = st.columns(2)
    with cA:
        st.button("⬅ Back to Summary", on_click=lambda: st.session_state.update({"page":"Step 4"}))
    with cB:
        def _finish():
            scores_pct = {s["id"]: section_score_pct(s) for s in ALL_SECTIONS}
            st.session_state["detailed_scores_pct"] = scores_pct
            st.session_state["page"]="Report"
        st.button("Finish & see recommendations ➜", type="primary", on_click=_finish)

# ─────────────────────────────────────────────────────────────
# UI — Report (Final Dashboard)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Report":
    st.markdown("## 🌟 Recommendations & Section Status")

    scores_pct: Dict[str, float] = st.session_state.get("detailed_scores_pct", {})
    lookup = {s["id"]: s for s in ALL_SECTIONS}

    if scores_pct:
        st.markdown("<div class='score-grid'>", unsafe_allow_html=True)
        for sid, pct in scores_pct.items():
            emoji,label,klass = section_light_from_pct(pct)
            html = f"""
            <div class="score-card">
              <div class="score-title">{sid}</div>
              <div class="status-pill">{emoji} <span>{label}</span></div>
              <div style="font-size:.92rem;color:#475569;margin-top:.35rem">Score: {pct:.2f}/100</div>
              <div class="meter {klass}"><span style="width:{pct}%"></span></div>
              <div style="font-size:.86rem;color:#64748b;margin-top:.25rem">{' · '.join(STD_MAP.get(sid, []))}</div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        overall_pct, band = overall_maturity(ALL_SECTIONS)
        st.markdown(f"### 🔭 Overall maturity: **{overall_pct}% · {band}**")
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
    if (st.session_state.bp_card_payments or "").lower() == "yes":
        nextlvl.append("Confirm PCI DSS responsibilities with your PoS/PSP.")
    nextlvl.append("Document GDPR basics if you handle EU/UK personal data (DPAs, transfers, contact).")
    st.markdown("\n".join([f"{i}. {x}" for i,x in enumerate(nextlvl,1)]))

    st.markdown("---")
    st.markdown("### ⬇️ Export results")
    st.download_button("Download results (CSV)", data=build_csv(), file_name="cyber-assessment-results.csv", mime="text/csv")
    st.download_button("Download summary (Markdown)", data=build_markdown_summary().encode("utf-8"), file_name="cyber-assessment-summary.md", mime="text/markdown")

    cA, cB = st.columns(2)
    with cA:
        st.button("⬅ Back to Detailed", on_click=lambda: st.session_state.update({"page":"Detailed"}))
    with cB:
        st.button("Start over", on_click=lambda: [st.session_state.update(defaults), st.session_state.update({"page":"Step 1"})])
