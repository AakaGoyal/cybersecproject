import streamlit as st
from typing import List, Dict, Tuple, Optional
from io import StringIO
import csv
import datetime as dt

# ─────────────────────────────────────────────────────────────
# Page setup & compact theme
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="SME Cybersecurity Self-Assessment", layout="wide")

st.markdown("""
<style>
  .block-container {max-width: 1160px; padding-top: 10px;}
  header {visibility: hidden;} /* trims built-in header gap */
  h1,h2,h3,h4 {margin:.25rem 0 .55rem}
  .lead {color:#374151; margin:.2rem 0 .6rem}
  .hint {color:#3b4757; font-size:.95rem; font-style:italic; margin:.25rem 0 .65rem}
  .explain {color:#1f2937; font-size:1.02rem; margin:.30rem 0 .75rem}
  .explain small {display:block; color:#475569; font-style:italic}
  .pill {display:inline-block;border-radius:999px;padding:.18rem .55rem;border:1px solid #e5e7eb;font-size:.9rem;color:#374151;background:#fff}
  .chip {display:inline-flex;align-items:center;gap:.35rem;border-radius:999px;padding:.18rem .6rem;border:1px solid #e5e7eb;margin-right:.35rem;font-weight:600}
  .green{background:#e8f7ee;color:#0f5132;border-color:#cceedd}
  .amber{background:#fff5d6;color:#8a6d00;border-color:#ffe7ad}
  .red{background:#ffe5e5;color:#842029;border-color:#ffcccc}
  .card {border:1px solid #e6e8ec;border-radius:12px;padding:12px;background:#fff}
  .sticky {position: sticky; top: 10px;}
  .btnrow {margin-top:.5rem}
  /* Traffic-light radio dots */
  .dot {width:14px;height:14px;border-radius:999px;display:inline-block;margin-right:.4rem;vertical-align:-2px;border:2px solid #e5e7eb}
  .dot.green{background:#22c55e;border-color:#22c55e}
  .dot.amber{background:#f59e0b;border-color:#f59e0b}
  .dot.red{background:#ef4444;border-color:#ef4444}
  /* tighten radio spacing */
  div[data-baseweb="radio"] > div {gap:.55rem;}
  /* progress bar spacing */
  .stProgress {margin-top:.25rem;margin-bottom:.75rem}
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
CRITICAL_SYSTEMS = ["ERP (Enterprise Resource Planning)", "Point of Sale (PoS)",
                    "CRM (Customer Relationship Management)", "EHR (Electronic Health Record)",
                    "CMS (Content Management System)", "Other (type below)"]
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
# State (with no default pre-selections for radios)
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
    work_mode="",  # <- radios start blank
    # Context
    critical_systems=[], critical_systems_other="",
    primary_work_env=WORK_ENVIRONMENTS[1],
    remote_ratio=REMOTE_RATIO[1],
    data_types=[], cross_border=CROSS_BORDER[0],
    certifications=["None"], certifications_other="",
    bp_card_payments="",
    # Baseline Q1–Q9 (all blank)
    bp_it_manager="", bp_inventory="", bp_byod="", bp_sensitive="",
    df_website="", df_https="", df_email="", df_social="", df_review="",
    detailed_sections=[], detailed_scores={},
)
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# ─────────────────────────────────────────────────────────────
# Small helpers
# ─────────────────────────────────────────────────────────────
def progress(step:int, total:int=3, label:str=""):
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

    # Accept both "" and None as "blank"
    current = st.session_state.get(key, "")
    idx = 0
    if current in options:
        idx = 1 + options.index(current)  # shift by placeholder

    selected_ui = st.radio(
        label,
        ui_options,
        index=idx,
        key=ui_key,
        horizontal=horizontal,
        help=help,
    )

    # Map back to real value and persist
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
    {"id":"ai_pw","t":"🔑 Are strong passwords required for all accounts?","h":"Use at least 10–12 characters; avoid reuse; password manager helps."},
    {"id":"ai_mfa","t":"🛡️ Is Multi-Factor Authentication (MFA) enabled for key accounts?","h":"Start with email, admin and finance; authenticator app or security key."},
    {"id":"ai_admin","t":"🧰 Are admin rights limited to only those who need them?","h":"Grant temporarily; review quarterly; monitor admin sign-ins."},
    {"id":"ai_shared","t":"👥 Are shared accounts avoided or controlled?","h":"Prefer named accounts; if shared, rotate passwords and log usage."},
    {"id":"ai_leavers","t":"🚪 Are old or unused accounts removed promptly?","h":"Disable same day a person leaves; reclaim devices and keys."},
])
SECTION_4 = section("Device & Data", [
    {"id":"dd_lock","t":"🔒 Are all devices protected with a password or PIN?","h":"Enable auto-lock ≤10 minutes and find-my-device."},
    {"id":"dd_fde","t":"💽 Is full-disk encryption enabled on laptops and mobiles?","h":"BitLocker, FileVault, Android/iOS device encryption."},
    {"id":"dd_edr","t":"🧿 Is reputable antivirus/EDR installed and active on all devices?","h":"Microsoft Defender, CrowdStrike, SentinelOne."},
    {"id":"dd_backup","t":"📦 Are important business files backed up regularly?","h":"3-2-1 rule: 3 copies, 2 media, 1 offsite (cloud counts)."},
    {"id":"dd_restore","t":"🧪 Are backups tested so you know restore works?","h":"Try restoring one file/VM quarterly."},
    {"id":"dd_usb","t":"🧰 Are staff trained to handle suspicious files/USBs?","h":"Block unknown USBs; preview links before clicking."},
    {"id":"dd_wifi","t":"📶 Are company devices separated from personal on Wi-Fi?","h":"Use separate SSIDs (Corp vs Guest); VLANs where possible."},
])
SECTION_5 = section("System & Software Updates", [
    {"id":"su_os_auto","t":"♻️ Are operating systems kept up to date automatically?","h":"Turn on auto-update; MDM helps enforce."},
    {"id":"su_apps","t":"🧩 Are business apps updated regularly?","h":"Browsers, accounting, CRM, PoS; prefer auto-update channels."},
    {"id":"su_unsupported","t":"⛔ Any devices running unsupported/outdated systems?","h":"Replace/upgrade old OS versions; isolate until replaced."},
    {"id":"su_review","t":"🗓️ Do you have a monthly reminder to review updates?","h":"Calendar task, RMM/MSP report, or patch-Tuesday checklist."},
])
SECTION_6 = section("Incident Preparedness", [
    {"id":"ip_report","t":"📣 Do employees know how to report incidents or suspicious activity?","h":"Phishing mailbox (phish@), Slack ‘#security’, service desk."},
    {"id":"ip_plan","t":"📝 Do you have a simple incident response plan?","h":"1-page checklist: who to call, what to collect, who to notify."},
    {"id":"ip_log","t":"🧾 Are incident details recorded when they occur?","h":"What/when/who/impact; template in your ticketing system helps."},
    {"id":"ip_contacts","t":"📇 Are key contacts known for emergencies?","h":"Internal IT, MSP, cyber insurer, legal, data-protection contact."},
    {"id":"ip_test","t":"🎯 Have you tested or simulated a cyber incident?","h":"30-minute tabletop twice a year; refine afterwards."},
])
SECTION_7 = section("Vendor & Cloud", [
    {"id":"vc_cloud","t":"☁️ Do you use cloud tools to store company data?","h":"M365, Google Workspace, Dropbox, sector SaaS (ERP, EHR, PoS)."},
    {"id":"vc_mfa","t":"🔐 Are cloud accounts protected with MFA and strong passwords?","h":"Enforce tenant-wide MFA; require it for all admins."},
    {"id":"vc_review","t":"🔎 Do you review how vendors protect your data?","h":"Check DPA, data location, certifications (ISO 27001, SOC 2)."},
    {"id":"vc_access","t":"📜 Do you track which suppliers have access to systems/data?","h":"Maintain a shared list; remove unused integrations."},
    {"id":"vc_notify","t":"🚨 Will vendors notify you promptly if they have a breach?","h":"Breach-notification clause + tested contact path."},
])
SECTION_9 = section("Governance", [
    {"id":"gov_policy","t":"📘 Do you have a short, written security policy approved by leadership?","h":"One page is enough: passwords, MFA, updates, incident steps, data handling."},
    {"id":"gov_roles","t":"🧭 Are responsibilities clear (who owns what)?","h":"Name an internal owner or MSP; list backups and escalation."},
    {"id":"gov_risk","t":"🧮 Do you review key risks at least once a year?","h":"Simple register: likelihood × impact; 3–5 top items is fine."},
    {"id":"gov_training","t":"🎓 Is basic security training mandatory for all staff?","h":"New starters + annual refresh; track completion."},
    {"id":"gov_records","t":"🗂️ Do you keep basic records (assets, vendors, incidents, backups)?","h":"Not fancy — a shared sheet is fine; reviewed quarterly."},
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
    # Basic profile
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
    # Baseline answers
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
    # Detailed (if any)
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
# UI — Step 1
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 1":
    progress(1, label="Business basics")
    st.markdown("## 🧭 Tell us about the business")
    st.caption("Just the basics (≈2 minutes).")
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

        # Radios with NO preselection (safe placeholder)
        radio_none("🧭 Work mode *", WORK_MODE, key="work_mode", horizontal=True)

        st.markdown("#### 🧱 Operational context (recommended)")
        cA, cB = st.columns(2)
        with cA:
            st.session_state.critical_systems = st.multiselect("🧩 Critical systems in use",
                CRITICAL_SYSTEMS, default=st.session_state.critical_systems)
            if "Other (type below)" in st.session_state.critical_systems:
                st.session_state.critical_systems_other = st.text_input("✍️ Specify other system", value=st.session_state.critical_systems_other)
            st.session_state.primary_work_env = st.radio("🏗️ Primary work environment", WORK_ENVIRONMENTS,
                horizontal=True, index=WORK_ENVIRONMENTS.index(st.session_state.primary_work_env))
            st.session_state.remote_ratio = st.radio("🏡 Remote work ratio", REMOTE_RATIO,
                horizontal=True, index=REMOTE_RATIO.index(st.session_state.remote_ratio))
        with cB:
            st.session_state.data_types = st.multiselect("🔍 Types of personal data handled", DATA_TYPES, default=st.session_state.data_types)
            st.session_state.cross_border = st.radio("🌐 Cross-border data flows", CROSS_BORDER, horizontal=True,
                                                     index=CROSS_BORDER.index(st.session_state.cross_border))
            st.session_state.certifications = st.multiselect("🔒 Certifications / schemes", CERTIFICATION_OPTIONS,
                                                              default=st.session_state.certifications)
            if "Other (type below)" in st.session_state.certifications:
                st.session_state.certifications_other = st.text_input("✍️ Specify other scheme", value=st.session_state.certifications_other)

        radio_none("💳 Do you accept or process card payments (online or in-store)?",
                   ["Yes","No","Not sure"], key="bp_card_payments", horizontal=True)

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
# UI — Step 2 (Baseline Q1–Q9)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 2":
    progress(2, label="Your current practices")
    st.markdown("## 🧪 Your current practices")
    st.caption("Answer the 9 quick checks. No trick questions.")

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
                       key="bp_it_manager", horizontal=True)
            st.markdown('<div class="hint">Includes laptops/phones, Wi-Fi, email, website, point-of-sale, cloud apps, file storage/backup.</div>', unsafe_allow_html=True)

            radio_none("**Q2. 📋 Do you keep a simple list of company devices (laptops, phones, servers)?**",
                       ["Yes","Partially","No","Not sure"], key="bp_inventory", horizontal=True)
            st.markdown('<div class="hint">An asset list helps find forgotten or unmanaged equipment.</div>', unsafe_allow_html=True)

            radio_none("**Q3. 📱 Do people use personal devices for work (Bring Your Own Device)?**",
                       ["Yes","Sometimes","No","Not sure"], key="bp_byod", horizontal=True)
            st.markdown('<div class="hint">Example: reading work email on a personal phone or laptop.</div>', unsafe_allow_html=True)

            radio_none("**Q4. 🔐 Do you handle sensitive customer or financial data?**",
                       ["Yes","No","Not sure"], key="bp_sensitive", horizontal=True)
            st.markdown('<div class="hint">e.g., payment details, personal records, signed contracts.</div>', unsafe_allow_html=True)

        with tab2:
            radio_none("**Q5. 🕸️ Do you have a public website?**",
                       ["Yes","No"], key="df_website", horizontal=True)
            radio_none("**Q6. 🔒 Is your website HTTPS (padlock in the browser)?**",
                       ["Yes","Partially","No","Not sure"], key="df_https", horizontal=True)
            st.markdown('<div class="hint">Why: HTTPS encrypts traffic and builds visitor trust; search engines expect it.</div>', unsafe_allow_html=True)

            radio_none("**Q7. ✉️ Do you use business email addresses?**",
                       ["Yes","Partially","No"], key="df_email", horizontal=True)
            st.markdown('<div class="hint">Personal email raises phishing and takeover risk; custom domains + MFA are safer.</div>', unsafe_allow_html=True)

            radio_none("**Q8. 📣 Is your business active on social media?**",
                       ["Yes","No"], key="df_social", horizontal=True)

            radio_none("**Q9. 🔎 Do you regularly check what’s public about the company or staff online?**",
                       ["Yes","Sometimes","No"], key="df_review", horizontal=True)
            st.markdown('<div class="hint">Contact details, staff lists, screenshots can reveal systems.</div>', unsafe_allow_html=True)

    with prev:
        st.write(""); st.write("")
        st.button("⬅ Back to Step 1", on_click=lambda: st.session_state.update({"page":"Step 1"}))
        required = ["bp_it_manager","bp_inventory","bp_byod","bp_sensitive","df_website","df_https","df_email","df_social","df_review"]
        missing=[k for k in required if not st.session_state.get(k)]
        st.button("Finish Initial Assessment ➜", type="primary", disabled=len(missing)>0,
                  on_click=lambda: st.session_state.update({"page":"Step 3"}))

# ─────────────────────────────────────────────────────────────
# UI — Step 3 (Summary + route to Detailed)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 3":
    progress(3, label="Summary")
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
        st.button("⬅ Back", on_click=lambda: st.session_state.update({"page":"Step 2"}))
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
            for q in sec["questions"]:
                radio_none(q["t"], ["Yes","Partially","No","Not sure"], key=q["id"], horizontal=True)
                st.markdown(f"<div class='hint'>💡 {q['h']}</div>", unsafe_allow_html=True)

    cA, cB = st.columns(2)
    with cA:
        st.button("⬅ Back to Summary", on_click=lambda: st.session_state.update({"page":"Step 3"}))
    with cB:
        def _finish():
            st.session_state["detailed_scores"]={s["id"]: section_score(s) for s in ALL_SECTIONS}
            st.session_state["page"]="Report"
        st.button("Finish & see recommendations ➜", type="primary", on_click=_finish)

# ─────────────────────────────────────────────────────────────
# UI — Report + Exports
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Report":
    st.markdown("## 🗺️ Recommendations & Section Status")
    scores = st.session_state.get("detailed_scores", {})
    if scores:
        cols = st.columns(len(scores))
        lookup = {s["id"]: s for s in ALL_SECTIONS}
        for (sid,_), col in zip(scores.items(), cols):
            emoji,label,klass = section_light(lookup[sid])
            with col:
                st.markdown(
                    f"<div class='card'><b>{sid}</b>"
                    f"<div class='hint'>Status: <span class='pill {klass}'>{emoji} {label}</span></div></div>",
                    unsafe_allow_html=True
                )
    else:
        st.caption("No detailed scores yet.")

    # Simple action plan (numbered lists)
    st.markdown("### 1) Quick wins (do these first)")
    quick=[]
    if st.session_state.df_website=="Yes" and st.session_state.df_https!="Yes":
        quick.append("Enable HTTPS and force redirect (HTTP→HTTPS).")
    if st.session_state.df_email in ("No","Partially"):
        quick.append("Move to business email (M365/Google) and enforce MFA.")
    if st.session_state.bp_inventory not in ("Yes","Partially"):
        quick.append("Start a simple device inventory and enable full-disk encryption on laptops.")
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
    # Exports
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
