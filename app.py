# app.py — SME Cybersecurity Self-Assessment (single file)
# Includes: landing, privacy modal, friendlier guidance, “Why it matters” text,
# action-tile recommendations, improved simulations (read-only), CSV/MD export.

from io import StringIO
import csv
import datetime as dt
from typing import List, Dict, Tuple, Optional
import streamlit as st
import html

# ─────────────────────────────────────────────────────────────
# Page setup & styling
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="SME Cybersecurity Self-Assessment", layout="wide")

BRAND_NAME = "SME Cybersecurity Self-Assessment"
BRAND_EMOJI = "🛡️"

st.markdown("""
<style>
  :root{
    --fg:#17212b; --muted:#475569; --soft:#64748b;
    --line:#e6e8ec; --card:#ffffff;
    --green:#16a34a; --amber:#f59e0b; --red:#ef4444; --blue:#2563eb;
    --green-bg:#e8f7ee; --amber-bg:#fff5d6; --red-bg:#ffe5e5; --blue-bg:#e8f1ff;
  }
  .block-container {max-width: 1160px; padding-top: 8px;}
  header {visibility: hidden;}
  h1,h2,h3,h4 {margin:.2rem 0 .5rem; color:var(--fg)}
  .muted{color:var(--muted); font-size:.98rem}
  .hint{color:#394b63; font-size:.95rem; margin:.15rem 0 .6rem}
  .pill{display:inline-flex;align-items:center;gap:.4rem;border-radius:999px;padding:.18rem .6rem;border:1px solid #e5e7eb;background:#fff}
  .chip{display:inline-flex;align-items:center;gap:.35rem;border-radius:999px;padding:.18rem .6rem;border:1px solid var(--line);font-weight:600}
  .green{background:var(--green-bg);color:#0f5132;border-color:#cceedd}
  .amber{background:var(--amber-bg);color:#8a6d00;border-color:#ffe7ad}
  .red{background:var(--red-bg);color:#842029;border-color:#ffcccc}
  .blue{background:var(--blue-bg);color:#123e88;border-color:#cfe0ff}
  .card{border:1px solid var(--line);border-radius:14px;padding:14px;background:#fff}
  .card-pad{padding:18px}
  .snap{min-height:220px}
  .grid-12{display:grid;grid-template-columns:repeat(12,1fr);gap:16px}
  .tile-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
  @media (max-width:1000px){ .tile-grid{grid-template-columns:1fr} }
  .tile{border:1px solid var(--line);border-radius:14px;padding:14px;background:#fff}
  .bar{height:8px;border-radius:999px;background:#f1f5f9;border:1px solid #e5e7eb;overflow:hidden}
  .bar>span{display:block;height:100%}
  .bar.green>span{background:var(--green)}
  .bar.amber>span{background:var(--amber)}
  .bar.red>span{background:var(--red)}
  .tiny-link{font-size:.9rem; color:#334155; text-decoration:underline; cursor:pointer}
  .align-spread{display:flex;align-items:center;justify-content:space-between}
</style>
""", unsafe_allow_html=True)

st.title(f"{BRAND_EMOJI} {BRAND_NAME}")

# ─────────────────────────────────────────────────────────────
# Session defaults
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
    "Microsoft 365 / Office 365","Google Workspace (Gmail/Drive)","SharePoint / OneDrive",
    "Exchange / Outlook (cloud)","On-prem Active Directory","Azure AD / Entra ID",
    "Okta / SSO provider","VPN / Remote access","Endpoint management (MDM/RMM)",
    "ERP (Enterprise Resource Planning)","Point of Sale (PoS)","CRM (Customer Relationship Management)",
    "E-commerce platform","Payment gateway / PSP","CMS (WordPress/Drupal/etc.)",
    "Source control / DevOps (GitHub/GitLab/Bitbucket)","Accounting / Finance (e.g., Xero/QuickBooks)",
    "Other (type below)"
]
WORK_ENVIRONMENTS = ["Local servers", "Cloud apps", "Hybrid"]
REMOTE_RATIO = ["Mostly on-site", "Hybrid", "Fully remote"]
DATA_TYPES = ["Customer personal data (PII)","Employee / staff data","Health / medical data","Financial / transaction data"]
CROSS_BORDER = ["EU-only","Includes Non-EU regions","Unsure"]
CERTIFICATION_OPTIONS = ["None","ISO/IEC 27001","Cyber Essentials (UK)","SOC 2","GDPR compliance program",
                         "PCI DSS (card payments)","NIS2 readiness","Other (type below)"]

TURNOVER_TO_SIZE = {**{k:"Micro" for k in TURNOVER_OPTIONS[:11]}, **{"€2M–€5M":"Small","€5M–€10M":"Small",">€10M":"Medium"}}
EMP_RANGE_TO_SIZE = {"1–5":"Micro","6–10":"Micro","10–25":"Small","26–50":"Small","51–100":"Medium","More than 100":"Medium"}

ANSWER_VAL = {"Yes":100,"Partially":50,"Not sure":50,"No":0}
BANDS = [(0,20,"Very Low"),(21,40,"Low"),(41,60,"Moderate"),(61,80,"Good"),(81,100,"Strong")]
DOMAIN_WEIGHT = {
    "Governance":1.2,"Access & Identity":1.3,"Device & Data":1.1,
    "System & Software Updates":1.1,"Incident Preparedness":1.1,
    "Vendor & Cloud":1.0,"Awareness & AI Risk":1.2
}
STD_MAP = {
  "Access & Identity":["NIST: PR.AC","ISO: A.5/A.8"],
  "Device & Data":["NIST: PR.DS / DE.CM","ISO: A.8/A.12"],
  "System & Software Updates":["NIST: PR.IP","ISO: A.8.8/A.12.6"],
  "Incident Preparedness":["NIST: RS / RC / DE.CM","ISO: A.5.24/A.5.25"],
  "Vendor & Cloud":["NIST: ID.SC / PR.AT","ISO: A.5.19/A.5.20"],
  "Governance":["NIST: ID.GV","ISO: A.5 (org controls)"],
  "Awareness & AI Risk":["NIST: PR.AT / ID.BE","ISO: A.6.3 (awareness)"]
}
WHY_DOMAIN = {
  "Access & Identity":"Most attacks start at sign-in. Strong passwords + MFA + least privilege stop takeovers.",
  "Device & Data":"Lost or infected devices leak data. Encryption and backups keep you safe.",
  "System & Software Updates":"Old software is easy to break. Auto-updates close known holes.",
  "Incident Preparedness":"When something happens, clear steps save time and money.",
  "Vendor & Cloud":"Your security is tied to your suppliers. Know who has access and how they protect data.",
  "Governance":"Short, written decisions make security repeatable and visible.",
  "Awareness & AI Risk":"AI makes fake messages look real. Practise how to spot and report them."
}

defaults = dict(
    page="Landing",
    show_privacy=False,
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
for k,v in defaults.items():
    st.session_state.setdefault(k,v)

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def small_privacy_link():
    colA, colB = st.columns([6,1])
    with colB:
        if st.button("🛡️ Privacy", help="View privacy note"):
            st.session_state.show_privacy = True
    if st.session_state.get("show_privacy"):
        try:
            with st.modal("Privacy"):
                st.write("**All inputs stay within this session; no data is persisted.**")
                st.write("If hosted (e.g., Streamlit Cloud), inputs are processed on the hosting provider and not retained after the session.")
                st.write("Use synthetic or anonymised details if unsure.")
                if st.button("Close"):
                    st.session_state.show_privacy = False
        except Exception:
            # Fallback (older Streamlit): lightweight expander
            with st.expander("Privacy", expanded=True):
                st.write("All inputs stay within this session; no data is persisted.")
                st.session_state.show_privacy = False

def progress(step:int,total:int, label:str=""):
    st.progress(max(0,min(step,total))/total, text=label or f"Step {step} of {total}")

def radio_none(label:str, options:List[str], *, key:str, horizontal:bool=True, help:Optional[str]=None, placeholder:str="— select —"):
    ui_key=f"{key}__ui"
    ui_options=[placeholder]+list(options)
    current=st.session_state.get(key,"")
    idx=0
    if current in options: idx=1+options.index(current)
    selected_ui=st.radio(label, ui_options, index=idx, key=ui_key, horizontal=horizontal, help=help)
    real_val="" if selected_ui==placeholder else selected_ui
    st.session_state[key]=real_val
    return real_val

def org_size()->str:
    a=TURNOVER_TO_SIZE.get(st.session_state.turnover_label,"Micro")
    b=EMP_RANGE_TO_SIZE.get(st.session_state.employee_range,a)
    order={"Micro":0,"Small":1,"Medium":2}
    return a if order[a]>=order[b] else b

def resolved_industry():
    return (st.session_state.sector_other or "Other") if st.session_state.sector_label=="Other (type below)" else st.session_state.sector_label

def section(title_id, questions): 
    return {"id":title_id,"title":title_id,"questions":questions}

def section_score_pct(sec:Dict)->float:
    vals=[st.session_state.get(q["id"],"") for q in sec["questions"]]
    if not vals: return 0.0
    return round(sum(ANSWER_VAL.get(v,50) for v in vals)/len(vals),2)

def section_light_from_pct(pct:float)->Tuple[str,str,str]:
    if pct>=70: return ("🟢","Low","green")
    if pct>=40: return ("🟡","Medium","amber")
    return ("🔴","High","red")

def overall_maturity(sections:List[Dict])->Tuple[float,str]:
    scores=[section_score_pct(s) for s in sections]
    weights=[DOMAIN_WEIGHT.get(s["id"],1.0) for s in sections]
    total=sum(s*w for s,w in zip(scores,weights))/max(1,sum(weights))
    label=next(lbl for lo,hi,lbl in BANDS if lo<=total<=hi)
    return round(total,2), label

def build_csv()->bytes:
    rows=[["Field","Value"]]
    basics={"Business":st.session_state.company_name,"Region":st.session_state.business_region,"Industry":resolved_industry(),
            "People":st.session_state.employee_range,"Years":st.session_state.years_in_business,
            "Turnover":st.session_state.turnover_label,"Work mode":st.session_state.work_mode or "",
            "Size (derived)":org_size()}
    for k,v in basics.items(): rows.append([k,v])
    rows.append([]); rows.append(["Baseline Q1–Q9","Answer"])
    base={"Q1 IT ownership":st.session_state.bp_it_manager,"Q2 Device list":st.session_state.bp_inventory,
          "Q3 BYOD":st.session_state.bp_byod,"Q4 Sensitive data":st.session_state.bp_sensitive,
          "Q5 Website":st.session_state.df_website,"Q6 HTTPS":st.session_state.df_https,
          "Q7 Business email":st.session_state.df_email,"Q8 Social presence":st.session_state.df_social,
          "Q9 Public info reviews":st.session_state.df_review}
    for k,v in base.items(): rows.append([k,v])
    if st.session_state.get("detailed_scores_pct"):
        rows.append([]); rows.append(["Section","Score (0–100)"])
        for sid,pct in st.session_state["detailed_scores_pct"].items(): rows.append([sid,pct])
        overall_pct, band = overall_maturity(ALL_SECTIONS); rows.append(["Overall", f"{overall_pct}% · {band}"])
    out=StringIO(); w=csv.writer(out); [w.writerow(r) for r in rows]
    return out.getvalue().encode("utf-8")

def build_markdown_summary()->str:
    lines=[]
    lines.append(f"# {BRAND_NAME} — Summary")
    lines.append(""); lines.append(f"- Generated: {dt.datetime.utcnow().isoformat(timespec='seconds')}Z"); lines.append("")
    lines.append("## Snapshot")
    lines.append(f"- Business: {st.session_state.company_name}")
    lines.append(f"- Region: {st.session_state.business_region}")
    lines.append(f"- Industry: {resolved_industry()}")
    lines.append(f"- People: {st.session_state.employee_range} | Years: {st.session_state.years_in_business}")
    lines.append(f"- Turnover: {st.session_state.turnover_label} | Work mode: {st.session_state.work_mode or '—'}")
    lines.append(f"- Derived size: {org_size()}"); lines.append("")
    if st.session_state.get("detailed_scores_pct"):
        lines.append("## Section scores (0–100) and tags")
        for sid, pct in st.session_state["detailed_scores_pct"].items():
            emoji,label,_=section_light_from_pct(pct)
            tags=" · ".join(STD_MAP.get(sid,[]))
            lines.append(f"- {sid}: {emoji} {label} — {pct}% ({tags})")
        overall_pct, band = overall_maturity(ALL_SECTIONS)
        lines.append(f"- Overall: **{overall_pct}% · {band}**")
    return "\n".join(lines)

def status_class(pct:float)->str:
    return "green" if pct>=70 else "amber" if pct>=40 else "red"

# ─────────────────────────────────────────────────────────────
# Question bank
# ─────────────────────────────────────────────────────────────
SECTION_3 = section("Access & Identity", [
    {"id":"ai_pw","t":"🔑 Are strong passwords required for all accounts?","h":"Use a password manager. Aim for 12+ characters, unique per account."},
    {"id":"ai_mfa","t":"🛡️ Is multi-factor authentication (MFA) turned on for key accounts?","h":"Start with email, admins and finance tools. App or security key is best."},
    {"id":"ai_admin","t":"🧰 Are admin rights limited to only those who need them?","h":"Give admin only when needed, review quarterly, watch unusual sign-ins."},
    {"id":"ai_shared","t":"👥 Are shared accounts avoided or controlled?","h":"Prefer named accounts. If shared, rotate passwords, enable MFA and log usage."},
    {"id":"ai_leavers","t":"🚪 Are leavers’ accounts removed promptly?","h":"Disable the same day a person leaves. Reclaim devices and keys."},
])
SECTION_4 = section("Device & Data", [
    {"id":"dd_lock","t":"🔒 Are all devices protected with a password or PIN?","h":"Turn on auto-lock ≤10 minutes and ‘find my device’."},
    {"id":"dd_fde","t":"💽 Is full-disk encryption enabled on laptops and phones?","h":"Use BitLocker, FileVault, or built-in Android/iOS encryption."},
    {"id":"dd_edr","t":"🧿 Is reputable antivirus/EDR installed and active?","h":"Defender or similar blocks malware and risky behaviour."},
    {"id":"dd_backup","t":"📦 Are important files backed up regularly?","h":"Follow 3-2-1: 3 copies, 2 media, 1 offsite."},
    {"id":"dd_restore","t":"🧪 Are backups tested so you know a restore works?","h":"Try restoring one file each quarter."},
    {"id":"dd_usb","t":"🧰 Do staff handle suspicious files/USBs safely?","h":"Default-deny where possible; preview links before clicking."},
    {"id":"dd_wifi","t":"📶 Are company devices separated from personal on Wi-Fi?","h":"Guest vs. corporate networks reduce spread."},
])
SECTION_5 = section("System & Software Updates", [
    {"id":"su_os_auto","t":"♻️ Are operating systems kept up to date automatically?","h":"Turn on auto-update; device management helps enforce it."},
    {"id":"su_apps","t":"🧩 Are business apps updated regularly?","h":"Use auto-update channels where possible."},
    {"id":"su_unsupported","t":"⛔ Any devices running unsupported/outdated systems?","h":"Replace/upgrade or isolate until replaced."},
    {"id":"su_review","t":"🗓️ Do you have a monthly reminder to review updates?","h":"A 10-minute check catches stragglers."},
])
SECTION_6 = section("Incident Preparedness", [
    {"id":"ip_report","t":"📣 Do employees know how to report suspicious messages?","h":"Provide one obvious route (mailbox or button)."},
    {"id":"ip_plan","t":"📝 Do you have a one-page incident plan?","h":"Who triages, who isolates, who communicates."},
    {"id":"ip_log","t":"🧾 Are incidents recorded when they happen?","h":"Capture what/when/who/impact; notes enable learning."},
    {"id":"ip_contacts","t":"📇 Are key contacts known for emergencies?","h":"Internal IT/MSP, insurer, legal, data-protection contact."},
    {"id":"ip_test","t":"🎯 Have you practised an incident?","h":"A 30-minute tabletop twice a year reveals gaps cheaply."},
])
SECTION_7 = section("Vendor & Cloud", [
    {"id":"vc_cloud","t":"☁️ Do you know where your cloud tools store data?","h":"List main services and regions if shown."},
    {"id":"vc_mfa","t":"🔐 Are cloud admin accounts protected with MFA?","h":"Enforce tenant-wide MFA; require it for all admins."},
    {"id":"vc_review","t":"🔎 Do you review how vendors protect your data?","h":"Check security pages/certifications (ISO 27001, SOC 2)."},
    {"id":"vc_access","t":"📜 Do you track which suppliers have access?","h":"List integrations and permissions; remove unused ones."},
    {"id":"vc_notify","t":"🚨 Will vendors notify you promptly if they have a breach?","h":"Make sure contracts include this."},
])
SECTION_9 = section("Governance", [
    {"id":"gov_policy","t":"📘 Do you have a short, written security policy approved by leadership?","h":"One or two pages is fine: passwords, MFA, updates, incidents, data handling."},
    {"id":"gov_roles","t":"🧭 Are responsibilities clear (who owns what)?","h":"Name an internal owner or provider; add backups and escalation path."},
    {"id":"gov_risk","t":"🧮 Do you review top risks at least yearly?","h":"Simple register: likelihood × impact for top 3–5 items."},
    {"id":"gov_training","t":"🎓 Is basic security training mandatory for all staff?","h":"New starters + annual refresh; track completion."},
    {"id":"gov_records","t":"🗂️ Do you keep basic records (assets, vendors, incidents, backups)?","h":"A shared sheet is fine; the point is visibility."},
])
SECTION_AI = section("Awareness & AI Risk", [
    {"id":"ai_phish","t":"🎣 Do staff practise spotting fake messages at least quarterly?","h":"Little-and-often beats annual courses. Practise reporting."},
    {"id":"ai_deepfake","t":"🎭 Are deepfake/voice-clone risks covered in training?","h":"Agree a back-channel for high-risk requests."},
    {"id":"ai_reporting","t":"📮 Is there a simple way to report suspicious messages?","h":"Mailbox (phish@) or button; track usage."},
    {"id":"ai_awareness","t":"🧠 Are AI-generated content risks explained in plain language?","h":"Polished language ≠ trusted request. Verify the route."},
    {"id":"ai_metrics","t":"📊 Do you review basic awareness metrics?","h":"Completion, reporting rate, time-to-report help tune effort."},
])

ALL_SECTIONS = [SECTION_3, SECTION_4, SECTION_5, SECTION_6, SECTION_7, SECTION_9, SECTION_AI]

# Suggested actions per domain (for Action Tiles & Top 5)
ACTIONS = {
  "Access & Identity":[
      "Turn on MFA for email, admin and finance tools.",
      "Remove unused accounts; review admin rights quarterly.",
      "Use a password manager and require strong passwords."
  ],
  "Device & Data":[
      "Enable full-disk encryption on laptops/phones.",
      "Back up important files and test a restore each quarter.",
      "Separate guest and company Wi-Fi."
  ],
  "System & Software Updates":[
      "Enable auto-updates for OS and apps.",
      "Replace or isolate unsupported systems.",
      "Add a 10-minute monthly update check."
  ],
  "Incident Preparedness":[
      "Publish a one-page incident plan.",
      "Set up one route to report suspicious messages.",
      "Run a 30-minute practice twice a year."
  ],
  "Vendor & Cloud":[
      "List suppliers with data access and remove unused integrations.",
      "Enforce MFA for all cloud admins.",
      "Check vendor security pages/certifications annually."
  ],
  "Governance":[
      "Approve a short security policy.",
      "Name an owner for security and backups.",
      "Keep simple records of assets, vendors and incidents."
  ],
  "Awareness & AI Risk":[
      "Run short recognition practice each quarter.",
      "Agree a verified back-channel for urgent requests.",
      "Track reporting rates and time-to-report."
  ]
}

# ─────────────────────────────────────────────────────────────
# LANDING (with privacy banner)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Landing":
    progress(1, total=5, label="Landing")
    st.info("**Privacy:** All inputs stay within this session; no data is persisted. If hosted (e.g., Streamlit Cloud), inputs are processed on the hosting provider and not retained after the session. Use synthetic or anonymised details if unsure.")

    st.markdown("### 👋 Welcome")
    st.write("This tool gives SMEs a quick, plain-language view of security posture across seven domains — including **Awareness & AI Risk** — and suggests practical next steps. No jargon, no signup.")

    c1,c2 = st.columns(2)
    with c1:
        st.markdown("#### ✅ What you’ll do")
        st.markdown("- 🪪 Add a few business basics\n- 🧩 Answer quick checks (~8 minutes)\n- 🚦 See a traffic-light dashboard\n- 📄 Export a simple summary")
    with c2:
        st.markdown("#### 🚫 What we don’t do")
        st.markdown("- 🗄️ Store data\n- ✉️ Send live phishing\n- 🧍 Collect personal information")

    st.button("Start ➜", type="primary", on_click=lambda: st.session_state.update({"page":"Step 1"}))

# ─────────────────────────────────────────────────────────────
# STEP 1 — Business basics (privacy banner visible here)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 1":
    progress(2, total=5, label="Business basics")
    st.info("**Privacy:** All inputs stay within this session; no data is persisted. If hosted (e.g., Streamlit Cloud), inputs are processed on the hosting provider and not retained after the session.")
    st.markdown("## 🧭 Tell us about the business")
    st.caption("Just the essentials — this sets context for the recommendations.")

    # three-column aligned layout
    colSnap, colYou, colBiz = st.columns([3,4,5], gap="large")
    with colSnap:
        st.markdown("#### 📸 Snapshot")
        st.markdown(
            f"<div class='card snap'><b>Business:</b> {st.session_state.company_name or '—'}<br>"
            f"<b>Region:</b> {st.session_state.business_region}<br>"
            f"<b>Industry:</b> {resolved_industry()}<br>"
            f"<b>People:</b> {st.session_state.employee_range} · <b>Years:</b> {st.session_state.years_in_business}<br>"
            f"<b>Turnover:</b> {st.session_state.turnover_label}<br>"
            f"<b>Work mode:</b> {st.session_state.work_mode or '—'}<br>"
            f"<b>Size (derived):</b> {org_size()}</div>", unsafe_allow_html=True
        )

    with colYou:
        st.markdown("#### 🙋 About you")
        st.session_state.email_for_report = st.text_input("Email for report (optional, for sending later)", value=st.session_state.email_for_report)
        st.session_state.person_name = st.text_input("Your name *", value=st.session_state.person_name)

    with colBiz:
        st.markdown("#### 🏢 About the business")
        st.session_state.company_name = st.text_input("Business name *", value=st.session_state.company_name)
        c1,c2 = st.columns(2)
        with c1:
            st.session_state.business_region = st.selectbox("Business location / region *", REGIONS:=REGION_OPTIONS, index=REGION_OPTIONS.index(st.session_state.business_region))
            st.session_state.years_in_business = st.selectbox("How long in business? *", YEARS_OPTIONS, index=YEARS_OPTIONS.index(st.session_state.years_in_business))
            st.session_state.sector_label = st.selectbox("Industry / service *", INDUSTRY_OPTIONS, 
                index=INDUSTRY_OPTIONS.index(st.session_state.sector_label) if st.session_state.sector_label in INDUSTRY_OPTIONS else 0)
            if st.session_state.sector_label == "Other (type below)":
                st.session_state.sector_other = st.text_input("Type your industry *", value=st.session_state.sector_other)
            else:
                st.session_state.sector_other = ""
        with c2:
            st.session_state.employee_range = st.selectbox("People (incl. contractors) *", EMPLOYEE_RANGES, index=EMPLOYEE_RANGES.index(st.session_state.employee_range))
            st.session_state.turnover_label = st.selectbox("Approx. annual turnover *", TURNOVER_OPTIONS, index=TURNOVER_OPTIONS.index(st.session_state.turnover_label))

        radio_none("Work mode *", WORK_MODE, key="work_mode", horizontal=True,
                   help="Where most work happens — influences device and access risk.")

    # navigation
    missing=[]
    if not st.session_state.person_name.strip(): missing.append("name")
    if not st.session_state.company_name.strip(): missing.append("company")
    if st.session_state.sector_label=="Other (type below)" and not st.session_state.sector_other.strip(): missing.append("industry")
    if not st.session_state.work_mode: missing.append("work mode")
    st.button("Continue ➜", type="primary", disabled=len(missing)>0, on_click=lambda: st.session_state.update({"page":"Step 2"}))

# ─────────────────────────────────────────────────────────────
# STEP 2 — Operational context (privacy modal link only)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 2":
    progress(3, total=5, label="Operational context")
    small_privacy_link()
    st.markdown("## 🧱 Operational context")
    st.caption("This step captures your core systems and data flows — used to tailor the guidance.")

    cA, cB = st.columns(2)
    with cA:
        st.session_state.critical_systems = st.multiselect("🧩 Critical systems in use *", CRITICAL_SYSTEMS, default=st.session_state.critical_systems)
        st.markdown("<div class='hint'>Pick the services you rely on every day (email, files, finance, sales). This helps us tailor the advice.</div>", unsafe_allow_html=True)
        if "Other (type below)" in st.session_state.critical_systems:
            st.session_state.critical_systems_other = st.text_input("Specify other system", value=st.session_state.critical_systems_other)

        st.session_state.primary_work_env = st.radio("🏗️ Primary work environment *", WORK_ENVIRONMENTS,
            horizontal=True, index=WORK_ENVIRONMENTS.index(st.session_state.primary_work_env))
        st.markdown("<div class='hint'>Where do most files and apps live? On company machines, in cloud tools, or a bit of both?</div>", unsafe_allow_html=True)

        st.session_state.remote_ratio = st.radio("🏡 Remote work ratio *", REMOTE_RATIO,
            horizontal=True, index=REMOTE_RATIO.index(st.session_state.remote_ratio))
        st.markdown("<div class='hint'>Roughly how much work happens off-site? This affects device and access risk.</div>", unsafe_allow_html=True)

    with cB:
        st.session_state.data_types = st.multiselect("🔍 Types of personal data handled *", DATA_TYPES, default=st.session_state.data_types)
        st.markdown("<div class='hint'>Tick any personal or sensitive data you hold (customers, staff, payments).</div>", unsafe_allow_html=True)

        st.session_state.cross_border = st.radio("🌐 Cross-border data flows *", CROSS_BORDER, horizontal=True, index=CROSS_BORDER.index(st.session_state.cross_border))
        st.markdown("<div class='hint'>Do any tools store data outside the EU/UK? If you’re not sure, choose ‘Unsure’.</div>", unsafe_allow_html=True)

        st.session_state.certifications = st.multiselect("🔒 Certifications / schemes", CERTIFICATION_OPTIONS, default=st.session_state.certifications)
        st.markdown("<div class='hint'>Any standards you follow or plan to (e.g., ISO 27001, Cyber Essentials). ‘None’ is fine.</div>", unsafe_allow_html=True)
        if "Other (type below)" in st.session_state.certifications:
            st.session_state.certifications_other = st.text_input("Specify other scheme", value=st.session_state.certifications_other)

    radio_none("💳 Do you accept or process card payments (online or in-store)? *", ["Yes","No","Not sure"], key="bp_card_payments", horizontal=True)
    st.markdown("<div class='hint'>If you take card payments, your setup may have extra security steps. We’ll flag them.</div>", unsafe_allow_html=True)

    missing=[]
    if not st.session_state.critical_systems: missing.append("critical systems")
    if not st.session_state.data_types: missing.append("data types")
    if not st.session_state.bp_card_payments: missing.append("card payments")

    c1,c2 = st.columns(2)
    with c1:
        st.button("⬅ Back to Step 1", on_click=lambda: st.session_state.update({"page":"Step 1"}))
    with c2:
        st.button("Continue ➜", type="primary", disabled=len(missing)>0, on_click=lambda: st.session_state.update({"page":"Step 3"}))

# ─────────────────────────────────────────────────────────────
# STEP 3 — Baseline Q1–Q9 (with friendlier hints)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 3":
    progress(4, total=5, label="Your current practices")
    small_privacy_link()
    st.markdown("## 🧪 Your current practices")

    snap, body = st.columns([1,2], gap="large")
    with snap:
        st.markdown("#### 📸 Snapshot")
        st.markdown(
            f"<div class='card'><b>Business:</b> {st.session_state.company_name}<br>"
            f"<b>Region:</b> {st.session_state.business_region}<br>"
            f"<b>Industry:</b> {resolved_industry()}<br>"
            f"<b>People:</b> {st.session_state.employee_range} · <b>Years:</b> {st.session_state.years_in_business}<br>"
            f"<b>Turnover:</b> {st.session_state.turnover_label} · <b>Size:</b> {org_size()}<br>"
            f"<b>Work mode:</b> {st.session_state.work_mode}</div>", unsafe_allow_html=True
        )

    with body:
        tab1, tab2 = st.tabs(["🧭 Business profile (Q1–Q4)", "🌐 Digital footprint (Q5–Q9)"])
        with tab1:
            radio_none("**Q1. Who looks after your IT day-to-day?**", ["Self-managed","Outsourced IT","Shared responsibility","Not sure"], key="bp_it_manager", horizontal=True)
            st.markdown("<div class='hint'>Someone needs to be clearly responsible for IT, even if it’s shared. A simple plan that says ‘who does what’ avoids gaps.</div>", unsafe_allow_html=True)

            radio_none("**Q2. Do you keep a simple list of company devices (laptops, phones, servers)?**", ["Yes","Partially","No","Not sure"], key="bp_inventory", horizontal=True)
            st.markdown("<div class='hint'>A device list helps you patch, insure and recover quickly.</div>", unsafe_allow_html=True)

            radio_none("**Q3. Do people use personal devices for work (Bring Your Own Device)?**", ["Yes","Sometimes","No","Not sure"], key="bp_byod", horizontal=True)
            st.markdown("<div class='hint'>If personal devices are used, set minimum rules: screen lock, updates, encryption, MFA for email.</div>", unsafe_allow_html=True)

            radio_none("**Q4. Do you handle sensitive customer or financial data?**", ["Yes","No","Not sure"], key="bp_sensitive", horizontal=True)
            st.markdown("<div class='hint'>Payment, personal or health data raise the bar for controls.</div>", unsafe_allow_html=True)

        with tab2:
            radio_none("**Q5. Do you have a public website?**", ["Yes","No"], key="df_website", horizontal=True)
            st.markdown("<div class='hint'>A website increases your attack surface and brand risk.</div>", unsafe_allow_html=True)

            radio_none("**Q6. Is your website HTTPS (padlock in the browser)?**", ["Yes","Partially","No","Not sure"], key="df_https", horizontal=True)
            st.markdown("<div class='hint'>HTTPS protects visitors and is a trust signal. Auto-renew certificates if you can.</div>", unsafe_allow_html=True)

            radio_none("**Q7. Do you use business email addresses?**", ["Yes","Partially","No"], key="df_email", horizontal=True)
            st.markdown("<div class='hint'>Custom domains + MFA improve deliverability and security.</div>", unsafe_allow_html=True)

            radio_none("**Q8. Is your business active on social media?**", ["Yes","No"], key="df_social", horizontal=True)
            st.markdown("<div class='hint'>Turn on MFA and use strong passwords for social accounts.</div>", unsafe_allow_html=True)

            radio_none("**Q9. Do you regularly check what’s public about the company or staff online?**", ["Yes","Sometimes","No"], key="df_review", horizontal=True)
            st.markdown("<div class='hint'>Periodic checks help catch exposed credentials or oversharing.</div>", unsafe_allow_html=True)

    required = ["bp_it_manager","bp_inventory","bp_byod","bp_sensitive","df_website","df_https","df_email","df_social","df_review"]
    missing=[k for k in required if not st.session_state.get(k)]
    st.button("Continue to detailed assessment ➜", type="primary", disabled=len(missing)>0,
              on_click=lambda: st.session_state.update({"detailed_sections":[s["id"] for s in ALL_SECTIONS], "page":"Detailed"}))
    st.button("⬅ Back to Step 2", on_click=lambda: st.session_state.update({"page":"Step 2"}))

# ─────────────────────────────────────────────────────────────
# DETAILED — with “Why it matters” and hints under each question
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Detailed":
    small_privacy_link()
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
            st.caption(WHY_DOMAIN.get(sec["id"], ""))
            for q in sec["questions"]:
                radio_none(q["t"], ["Yes","Partially","No","Not sure"], key=q["id"], horizontal=True)
                st.markdown(f"<div class='hint'>💡 {q['h']}</div>", unsafe_allow_html=True)
            st.caption("Tags: " + " · ".join(STD_MAP.get(sec["id"], [])))

    def _finish():
        scores_pct = {s["id"]: section_score_pct(s) for s in ALL_SECTIONS}
        st.session_state["detailed_scores_pct"] = scores_pct
        st.session_state["page"]="Report"
    st.button("🧪 Preview simulations", on_click=lambda: st.session_state.update({"page":"Simulations"}))
    st.button("Finish & see recommendations ➜", type="primary", on_click=_finish)
    st.button("⬅ Back to Baseline", on_click=lambda: st.session_state.update({"page":"Step 3"}))

# ─────────────────────────────────────────────────────────────
# UI — Report (Final Dashboard) — compact 2-up tiles, Quick Wins on top
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Report":
    # Local CSS for a 2-column grid and compact tiles
    st.markdown("""
    <style>
      .grid-tiles{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
      @media (max-width:900px){.grid-tiles{grid-template-columns:1fr;}}
      .tile{border:1px solid #e6e8ec;background:#fff;border-radius:14px;padding:14px;
            display:flex;flex-direction:column;min-height:170px}
      .tile h4{margin:0 0 .25rem}
      .tile .meta{margin-top:.35rem;font-size:.86rem;color:#64748b}
      .rag{display:inline-flex;gap:.35rem;align-items:center;font-weight:600;
           border-radius:999px;padding:.18rem .55rem;border:1px solid #e6e8ec}
      .rag.green{background:#e8f7ee;color:#0f5132;border-color:#cceedd}
      .rag.amber{background:#fff5d6;color:#8a6d00;border-color:#ffe7ad}
      .rag.red{background:#ffe5e5;color:#842029;border-color:#ffcccc}
      .minibar{height:8px;background:#f1f5f9;border-radius:999px;border:1px solid #e5e7eb;
               overflow:hidden;margin:.35rem 0 .55rem}
      .minibar span{display:block;height:100%}
      .minibar.green span{background:#16a34a}
      .minibar.amber span{background:#f59e0b}
      .minibar.red span{background:#ef4444}
      .why{margin:.1rem 0 .35rem;color:#475569}
      .bullets{margin:.15rem 0 .2rem .95rem}
      .pill{border:1px solid #e6e8ec;border-radius:999px;padding:.08rem .45rem;
            display:inline-flex;gap:.35rem;align-items:center}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("## 🌟 Recommendations & Section Status")

    # Overall maturity + traffic light
    overall_pct, band = overall_maturity(ALL_SECTIONS)
    emoji_overall, risk_label, klass_overall = section_light_from_pct(overall_pct)
    risk_text = {"green":"Low", "amber":"Moderate", "red":"High"}[klass_overall]
    st.markdown(
        f"### 🔭 Overall maturity: **{overall_pct:.1f}% · {band}** "
        f"<span class='rag {klass_overall}'>{emoji_overall} {risk_text} risk</span>",
        unsafe_allow_html=True
    )
    st.caption("Traffic light reflects estimated residual risk; weighted by domain importance.")

    # ===== Quick wins at the very top (with emojis)
    quick = []
    if st.session_state.df_website == "Yes" and st.session_state.df_https != "Yes":
        quick.append("🔒 Enable HTTPS and force redirect (HTTP→HTTPS).")
    if st.session_state.df_email in ("No","Partially"):
        quick.append("📧 Move to business email (M365/Google) and enforce MFA.")
    if st.session_state.bp_inventory not in ("Yes","Partially"):
        quick.append("💻 Start a device inventory and enable full-disk encryption on laptops.")
    # Fill up from low-scoring domains
    scores_pct: Dict[str, float] = st.session_state.get("detailed_scores_pct", {})
    if scores_pct:
        for sid, _ in sorted(scores_pct.items(), key=lambda kv: kv[1]):
            for rec in ACTIONS.get(sid, [])[:2]:
                line = "⚡ " + rec
                if line not in quick:
                    quick.append(line)
                if len(quick) >= 5:
                    break
            if len(quick) >= 5:
                break

    if quick:
        st.markdown("#### 🔧 Top 5 actions (quick wins)")
        st.markdown("\n".join([f"{i}. {x}" for i, x in enumerate(quick[:5], 1)]))
        st.markdown("---")

    # ===== Guard: require scores
    if not scores_pct:
        st.info("Run the detailed assessment to see recommendations.")
    else:
        # Two-up grid of tiles, sorted by lowest score first
        st.markdown("<div class='grid-tiles'>", unsafe_allow_html=True)
        for sid, pct in sorted(scores_pct.items(), key=lambda kv: kv[1]):
            emoji, label, klass = section_light_from_pct(pct)
            tags_text = " · ".join(STD_MAP.get(sid, []))
            recs = ACTIONS.get(sid, [])[:3]  # show up to 3 items, no <details/>

            rec_list = "".join(f"<li>{html.escape(rec)}</li>" for rec in recs)
            why_txt = WHY_DOMAIN.get(sid, "")

            tile_html = f"""
            <div class="tile">
              <div style="display:flex;justify-content:space-between;align-items:center;gap:8px">
                <h4 style="margin:0">{sid}</h4>
                <span class="rag {klass}">{emoji} {label}</span>
              </div>
              <div class="minibar {klass}"><span style="width:{pct:.2f}%"></span></div>
              <small>Score: {pct:.2f}/100</small>
              <div class="why"><b>Do next</b></div>
              <ul class="bullets">{rec_list}</ul>
              <div class="why"><b>Why this matters</b><br>{html.escape(why_txt)}</div>
              <div class="meta"><span class="pill">Tags</span> <span style="margin-left:.35rem">{html.escape(tags_text)}</span></div>
            </div>
            """
            st.markdown(tile_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### ⬇️ Export results")
        st.download_button("Download results (CSV)", data=build_csv(),
                           file_name="cyber-assessment-results.csv", mime="text/csv")
        st.download_button("Download summary (Markdown)",
                           data=build_markdown_summary().encode("utf-8"),
                           file_name="cyber-assessment-summary.md", mime="text/markdown")

        cA, cB, cC = st.columns(3)
        with cA:
            st.button("⬅ Back to Detailed", on_click=lambda: st.session_state.update({"page":"Detailed"}))
        with cB:
            st.button("🧪 View simulations", on_click=lambda: st.session_state.update({"page":"Simulations"}))
        with cC:
            st.button("Start over", on_click=lambda: [st.session_state.update(defaults),
                                                      st.session_state.update({"page":"Step 1"})])
# ─────────────────────────────────────────────────────────────
# UI — Simulations (read-only, friendlier content)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Simulations":
    st.markdown("## 🧪 Guided simulations (safe, read-only)")
    st.caption("These are examples only. No messages are sent and nothing is stored.")

    with st.expander("🎣 Invoice phish preview", expanded=True):
        st.write("**From:** “Accounts” <accounts@trusted-lookalike.com> — “Please review the attached invoice ASAP.”")
        st.write("**What to look for**")
        st.markdown("- Display-name spoofing\n- Urgent tone\n- Link hover doesn’t match the domain\n- Attachment from unknown sender")
        st.write("**What to do**")
        st.markdown("- Use your ‘Report suspicious’ route\n- Verify invoices via a known back-channel (phone/portal), not by replying")

    with st.expander("🗣️ CEO voice-clone request"):
        st.write("**Scenario:** an urgent voice note asking for a payment change.")
        st.write("**What to look for**")
        st.markdown("- Urgency + authority\n- Unfamiliar contact method\n- Out-of-hours request")
        st.write("**What to do**")
        st.markdown("- Call back using a **known** number or channel\n- Use a 2-person approval for payment changes")

    with st.expander("🔐 ‘Security alert’ login lure"):
        st.write("**Scenario:** “Your account will be locked. Reset your password now.”")
        st.write("**What to look for**")
        st.markdown("- Generic greeting\n- Domain mismatch\n- Push to click immediately")
        st.write("**What to do**")
        st.markdown("- Don’t click links in the email\n- Go directly to the site or use your IT’s known route")

    c1, c2 = st.columns(2)
    with c1:
        st.button("⬅ Back to Detailed", on_click=lambda: st.session_state.update({"page":"Detailed"}))
    with c2:
        st.button("Go to report ➜", type="primary", on_click=lambda: st.session_state.update({"page":"Report"}))
