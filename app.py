import streamlit as st
import io, csv, re
from datetime import datetime
from typing import List, Tuple

# ─────────────────────────────────────────────────────────────
# Page setup & styles
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="SME Cybersecurity Self-Assessment", layout="wide")

st.markdown("""
<style>
  .block-container {max-width: 1180px;}
  h1,h2,h3,h4 {margin:.2rem 0 .6rem}
  .hint {color:#4b5563; font-size:.95rem; font-style:italic; margin:.2rem 0 .6rem}
  .pill {display:inline-block;border-radius:999px;padding:.18rem .55rem;border:1px solid #e5e7eb;font-size:.9rem;color:#374151;background:#fff}
  .chip {display:inline-flex;align-items:center;gap:.35rem;border-radius:999px;padding:.18rem .6rem;border:1px solid #e5e7eb;margin-right:.35rem;font-weight:600}
  .green{background:#e8f7ee;color:#0f5132;border-color:#cceedd}
  .amber{background:#fff5d6;color:#8a6d00;border-color:#ffe7ad}
  .red{background:#ffe5e5;color:#842029;border-color:#ffcccc}
  .card {border:1px solid #e6e8ec;border-radius:12px;padding:10px 12px;background:#fff}
  .sticky {position: sticky; top: 10px;}
  .btnrow {margin-top:.4rem}
  .qgap {margin-top:.85rem}
  /* radio pill dots a bit larger spacing */
  div[data-baseweb="radio"] > div {gap:.65rem;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Options
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
CRITICAL_SYSTEMS = ["ERP", "Point of Sale (PoS)", "Customer Relationship Management (CRM)", "Electronic Health Record (EHR)", "Content Management System (CMS)", "Other (type below)"]
WORK_ENVIRONMENTS = ["Local servers", "Cloud apps", "Hybrid"]
REMOTE_RATIO = ["Mostly on-site", "Hybrid", "Fully remote"]
DATA_TYPES = ["Customer personal data (PII)", "Employee/staff data", "Health/medical data", "Financial/transaction data"]
CROSS_BORDER = ["EU-only", "Includes Non-EU regions", "Unsure"]
CERTIFICATION_OPTIONS = [
    "None","ISO/IEC 27001","Cyber Essentials (UK)","SOC 2",
    "GDPR compliance program","PCI DSS (Payment Cards)","HIPAA (US healthcare)",
    "NIS2 readiness","Other (type below)"
]

# ─────────────────────────────────────────────────────────────
# State
# ─────────────────────────────────────────────────────────────
defaults = dict(
    page="Landing",
    person_name="", company_name="",
    sector_label=INDUSTRY_OPTIONS[0], sector_other="",
    years_in_business=YEARS_OPTIONS[0],
    employee_range=EMPLOYEE_RANGES[0],
    turnover_label=TURNOVER_OPTIONS[0],
    work_mode=WORK_MODE[0],
    business_region=REGION_OPTIONS[0],
    critical_systems=[],
    critical_systems_other="",
    primary_work_env=WORK_ENVIRONMENTS[1],
    remote_ratio=REMOTE_RATIO[1],
    data_types=[],
    cross_border=CROSS_BORDER[0],
    certifications=["None"],
    certifications_other="",
    bp_card_payments="",
    # Baseline (Q1–Q9)
    bp_it_manager="", bp_inventory="", bp_byod="", bp_sensitive="",
    df_website="", df_https="", df_email="", df_social="", df_review="",
    # Tier-2
    detailed_sections=[],
    detailed_scores={},
    # export
    export_email=""
)
for k,v in defaults.items():
    st.session_state.setdefault(k,v)

# ─────────────────────────────────────────────────────────────
# Helpers: value normaliser + no-default radios (traffic pills)
# ─────────────────────────────────────────────────────────────
def _norm(v: str) -> str:
    if not v: return ""
    s = str(v).strip().lower()
    if "not sure" in s or "unsure" in s: return "not sure"
    if "partial" in s: return "partially"
    if s == "no" or s.endswith(" no") or s.startswith("no ") or s.startswith("🔴"):
        return "no"
    if "yes" in s or s.startswith("🟢"):
        return "yes"
    return s

def _radio_none(label, options, *, key, horizontal=True, label_visibility="visible"):
    cur = st.session_state.get(key, None)
    idx = options.index(cur) if cur in options else None
    return st.radio(label, options, key=key, index=idx, horizontal=horizontal, label_visibility=label_visibility)

PILL_OPTS = ["🟢 Yes", "🟡 Partially", "🔴 No", "🤔 Not sure"]
def radio_pills(label, *, key, horizontal=True, label_visibility="visible"):
    return _radio_none(label, PILL_OPTS, key=key, horizontal=horizontal, label_visibility=label_visibility)

def go(page:str):
    st.session_state.page = page
    st.rerun()

# ─────────────────────────────────────────────────────────────
# Derived tags & scoring
# ─────────────────────────────────────────────────────────────
TURNOVER_TO_SIZE = {**{k:"Micro" for k in TURNOVER_OPTIONS[:11]}, **{"€2M–€5M":"Small","€5M–€10M":"Small",">€10M":"Medium"}}
EMP_RANGE_TO_SIZE = {"1–5":"Micro","6–10":"Micro","10–25":"Small","26–50":"Small","51–100":"Medium","More than 100":"Medium"}
INDUSTRY_TAGS = {
    "Retail & Hospitality":"retail",
    "Professional / Consulting / Legal / Accounting":"professional_services",
    "Manufacturing / Logistics":"manufacturing",
    "Creative / Marketing / IT Services":"it_services",
    "Health / Wellness / Education":"health_edu",
    "Public sector / Non-profit":"public_nonprofit",
    "Other (type below)":"other",
}
def resolved_industry():
    return (st.session_state.sector_other or "Other") if st.session_state.sector_label=="Other (type below)" else st.session_state.sector_label

def org_size():
    a = TURNOVER_TO_SIZE.get(st.session_state.turnover_label, "Micro")
    b = EMP_RANGE_TO_SIZE.get(st.session_state.employee_range, a)
    return a if {"Micro":0,"Small":1,"Medium":2}[a] >= {"Micro":0,"Small":1,"Medium":2}[b] else b

def industry_tag(): return INDUSTRY_TAGS.get(resolved_industry(),"other")
def region_tag():
    r = (st.session_state.business_region or "").lower()
    if "eu" in r or "eea" in r: return "eu"
    if "uk" in r: return "uk"
    if "united states" in r or r=="us" or "america" in r: return "us"
    return "other"

def certification_tags():
    tags=set()
    for c in (st.session_state.get("certifications") or []):
        cl=c.lower()
        if "iso" in cl: tags.add("cert:iso27001")
        elif "cyber essentials" in cl: tags.add("cert:ce")
        elif "soc 2" in cl: tags.add("cert:soc2")
        elif "pci" in cl: tags.add("cert:pci")
        elif "hipaa" in cl: tags.add("cert:hipaa")
        elif "nis2" in cl: tags.add("cert:nis2")
        elif "gdpr" in cl: tags.add("cert:gdpr")
        elif "none" in cl: tags.add("cert:none")
        elif "other" in cl: tags.add("cert:other")
    return tags

def compute_tags():
    tags=set()
    tags.update({f"size:{org_size()}", f"industry:{industry_tag()}", f"geo:{region_tag()}"})
    env=st.session_state.primary_work_env
    tags.add("infra:cloud" if env=="Cloud apps" else "infra:onprem" if env=="Local servers" else "infra:hybrid")
    rr=st.session_state.remote_ratio
    tags.add("work:remote" if rr=="Fully remote" else "work:hybrid" if rr=="Hybrid" else "work:onsite")
    for s in st.session_state.critical_systems or []:
        sl=s.lower()
        if "erp" in sl: tags.add("system:erp")
        elif "pos" in sl: tags.add("system:pos")
        elif "crm" in sl: tags.add("system:crm")
        elif "ehr" in sl: tags.add("system:ehr")
        elif "cms" in sl: tags.add("system:cms")
        elif "other" in sl: tags.add("system:other")
    for d in st.session_state.data_types or []:
        dl=d.lower()
        if "customer" in dl: tags.add("data:pii")
        if "employee" in dl: tags.add("data:employee")
        if "health" in dl: tags.add("data:health")
        if "financial" in dl: tags.add("data:financial")
    cb=st.session_state.cross_border
    tags.add("geo:eu_only" if cb=="EU-only" else "geo:unsure" if cb=="Unsure" else "geo:crossborder")
    if _norm(st.session_state.get("bp_sensitive",""))=="yes": tags.add("data:sensitive")
    if _norm(st.session_state.get("bp_card_payments",""))=="yes": tags.add("payments:card")
    tags |= certification_tags()
    return tags

def area_rag():
    inv  = _norm(st.session_state.get("bp_inventory", ""))
    byod = _norm(st.session_state.get("bp_byod", ""))
    email = _norm(st.session_state.get("df_email", ""))
    web  = _norm(st.session_state.get("df_website", ""))
    https = _norm(st.session_state.get("df_https", ""))

    # Systems
    if inv == "yes": sys=("🟢 Good","green")
    elif inv == "partially": sys=("🟡 Partial","amber")
    elif inv in {"no","not sure"}: sys=("🔴 At risk","red")
    else: sys=("⚪ Unknown","")

    # People
    if byod=="no" and email=="yes": ppl=("🟢 Safe","green")
    elif email=="no": ppl=("🔴 At risk","red")
    elif byod in {"yes","partially"} or email in {"partially","not sure"}: ppl=("🟡 Mixed","amber")
    elif byod=="not sure": ppl=("🟡 Mixed","amber")
    else: ppl=("⚪ Unknown","")

    # Exposure
    if web=="yes" and https=="yes": net=("🟢 Protected","green")
    elif web=="yes" and https=="no": net=("🔴 Exposed","red")
    elif web=="yes" and https in {"partially","not sure",""}: net=("🟡 Check","amber")
    elif web=="no": net=("🟢 Low","green")
    else: net=("⚪ Unknown","")

    return sys,ppl,net

def overall_badge():
    sys,ppl,net = area_rag()
    score=sum({"green":0,"amber":1,"red":2}.get(x[1],1) for x in [sys,ppl,net])
    if score<=1: return ("Low","green","Great job — strong digital hygiene.")
    if score<=3: return ("Medium","amber","Balanced setup. A few quick wins will reduce risk fast.")
    return ("High","red","Higher exposure — prioritise quick actions to lower risk.")

# ─────────────────────────────────────────────────────────────
# Sections (Tier-2)
# ─────────────────────────────────────────────────────────────
def section(title_id, qlist):
    return {"id":title_id, "title":title_id, "questions":qlist}

SECTION_3 = section("Access & Identity", [
    {"id":"ai_pw","t":"🔑 Are strong passwords required for all accounts?","h":"Use at least 10–12 characters; avoid reuse. A password manager helps."},
    {"id":"ai_mfa","t":"🛡️ Is Multi-Factor Authentication (MFA) enabled for key accounts?","h":"Start with email, admin and finance; use an authenticator app or security key."},
    {"id":"ai_admin","t":"🧰 Are admin rights limited to only those who need them?","h":"Grant temporarily, review quarterly, monitor admin sign-ins."},
    {"id":"ai_shared","t":"👥 Are shared accounts avoided or controlled?","h":"Prefer named accounts; if shared, rotate passwords and log usage."},
    {"id":"ai_leavers","t":"🚪 Are old or unused accounts removed promptly?","h":"Disable the same day a person leaves; reclaim devices and keys."},
])
SECTION_4 = section("Device & Data", [
    {"id":"dd_lock","t":"🔒 Are all laptops/phones protected with a password or PIN?","h":"Also enable auto-lock (≤10 minutes) and find-my-device."},
    {"id":"dd_fde","t":"💽 Is full-disk encryption enabled on laptops and mobiles?","h":"Windows BitLocker, macOS FileVault, Android/iOS encryption."},
    {"id":"dd_edr","t":"🧿 Is reputable antivirus/EDR installed and active on all devices?","h":"Examples: Microsoft Defender, CrowdStrike, SentinelOne."},
    {"id":"dd_backup","t":"📦 Are important business files backed up regularly?","h":"3-2-1 rule: 3 copies, 2 media, 1 offsite (cloud counts)."},
    {"id":"dd_restore","t":"🧪 Are backups tested so you know restore works?","h":"Try restoring one file/VM quarterly; script it if possible."},
    {"id":"dd_usb","t":"🧰 Are staff trained to handle suspicious files/USBs?","h":"Block unknown USBs; preview links before clicking."},
    {"id":"dd_wifi","t":"📶 Are company devices separated from personal ones on Wi-Fi?","h":"Use separate SSIDs (Corp vs Guest); VLANs where possible."},
])
SECTION_5 = section("System & Software Updates", [
    {"id":"su_os_auto","t":"♻️ Are operating systems kept up to date automatically?","h":"Turn on auto-update in Windows/macOS; MDM helps enforce."},
    {"id":"su_apps","t":"🧩 Are business apps updated regularly?","h":"Browsers, accounting, CRM, PoS; prefer auto-update channels."},
    {"id":"su_unsupported","t":"⛔ Any devices running unsupported/outdated systems?","h":"Replace/upgrade old OS versions; isolate until replaced."},
    {"id":"su_review","t":"🗓️ Do you have a monthly reminder to review updates?","h":"Calendar task, RMM/MSP report, or patch-Tuesday checklist."},
])
SECTION_6 = section("Incident Preparedness", [
    {"id":"ip_report","t":"📣 Do employees know how to report incidents or suspicious activity?","h":"Phishing mailbox (phish@), Slack ‘#security’, service desk."},
    {"id":"ip_plan","t":"📝 Do you have a simple incident response plan?","h":"1-page checklist: who to call, what to collect, who to notify."},
    {"id":"ip_log","t":"🧾 Are incident details recorded when they occur?","h":"What/when/who/impact; template in your ticketing system helps."},
    {"id":"ip_contacts","t":"📇 Are key contacts known for emergencies?","h":"Internal IT, MSP, cyber insurer, legal, data-protection contact."},
    {"id":"ip_test","t":"🎯 Have you tested or simulated a cyber incident?","h":"30-minute tabletop twice a year; refine the plan afterwards."},
])
SECTION_7 = section("Vendor & Cloud", [
    {"id":"vc_cloud","t":"☁️ Do you use cloud tools to store company data?","h":"M365, Google Workspace, Dropbox, sector SaaS (ERP, EHR, PoS)."},
    {"id":"vc_mfa","t":"🔐 Are cloud accounts protected with MFA and strong passwords?","h":"Enforce tenant-wide MFA; require it for all admins."},
    {"id":"vc_review","t":"🔎 Do you review how vendors protect your data?","h":"Check DPA, data location, certifications (ISO 27001, SOC 2)."},
    {"id":"vc_access","t":"📜 Do you track which suppliers have access to systems/data?","h":"Maintain a shared list; remove unused integrations."},
    {"id":"vc_notify","t":"🚨 Will vendors notify you promptly if they have a breach?","h":"Breach-notification clause + contact path tested once a year."},
])
SECTION_8 = section("Awareness & Training", [
    {"id":"at_training","t":"🎓 Have employees received any cybersecurity training?","h":"Short e-learning or live session; track completion."},
    {"id":"at_phish","t":"🐟 Do staff know how to spot phishing or scam emails?","h":"Check sender, link URL, urgency, attachments; report quickly."},
    {"id":"at_onboard","t":"🧭 Are new employees briefed during onboarding?","h":"Add a 15-minute security starter; include password manager."},
    {"id":"at_reminders","t":"📢 Do you share posters, reminders, or tips?","h":"Monthly internal post: MFA, updates, phishing examples."},
    {"id":"at_lead","t":"🤝 Does management actively promote cybersecurity?","h":"Leaders mention it in all-hands; ask for MFA completion."},
])
ALL_SECTIONS=[SECTION_3,SECTION_4,SECTION_5,SECTION_6,SECTION_7,SECTION_8]
BASELINE_IDS={"Access & Identity","Device & Data","System & Software Updates","Awareness & Training"}

def render_section(sec):
    st.markdown(f"### {sec['id']}")
    bullets = {"Access & Identity":["Control of user access and authentication."],
               "Device & Data":["How well devices and company data are secured."],
               "System & Software Updates":["Keeping systems patched and supported."],
               "Incident Preparedness":["Readiness to detect, respond, and recover."],
               "Vendor & Cloud":["Security of third-party tools and online services."],
               "Awareness & Training":["Cybersecurity culture and user awareness."]}[sec["id"]]
    for b in bullets: st.caption(b)
    for q in sec["questions"]:
        st.markdown(f"<div class='qgap'><b>{q['t']}</b></div>", unsafe_allow_html=True)
        radio_pills(" ", key=q["id"], horizontal=True, label_visibility="collapsed")
        st.markdown(f"<div class='hint'>💡 {q['h']}</div>", unsafe_allow_html=True)

def section_score(sec):
    vals=[_norm(st.session_state.get(q["id"],"")) for q in sec["questions"]]
    risk={"yes":0,"partially":1,"not sure":1,"no":2}
    return round(sum(risk.get(v,1) for v in vals)/len(vals),2) if vals else 0.0

def pick_active_sections(tags:set):
    active=set(BASELINE_IDS)
    if "size:Small" in tags or "size:Medium" in tags: active.add("Incident Preparedness")
    if any(t in tags for t in ["infra:cloud","system:pos","geo:crossborder"]): active.add("Vendor & Cloud")
    order=[s["id"] for s in ALL_SECTIONS]
    return [sid for sid in order if sid in active]

def applicable_compliance(tags:set):
    hints=[]
    if any(t in tags for t in ["geo:eu","geo:uk"]) or "data:pii" in tags or "data:employee" in tags:
        hints.append(("GDPR","Regulation (EU/UK)","Likely applies if you process EU/UK personal data. Review DPAs and cross-border transfers."))
    if "payments:card" in tags or "system:pos" in tags or "data:financial" in tags:
        hints.append(("PCI DSS","Industry Standard","If you store/process/transmit card data. PSP-managed PoS may reduce scope."))
    if "data:health" in tags:
        hints.append(("HIPAA","US Regulation","Applies to US covered entities/business associates; otherwise treat as conditional."))
    hints.append(("ISO/IEC 27001","Standard","A clear maturity target and customer trust signal."))
    return hints

# ─────────────────────────────────────────────────────────────
# Export helpers (CSV + Markdown) and optional email (SMTP)
# ─────────────────────────────────────────────────────────────
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def build_summary_payload():
    sys,ppl,net = area_rag()
    payload = {
        "timestamp": datetime.utcnow().isoformat()+"Z",
        "business": st.session_state.get("company_name",""),
        "region": st.session_state.get("business_region",""),
        "industry": resolved_industry(),
        "people_range": st.session_state.get("employee_range",""),
        "years_in_business": st.session_state.get("years_in_business",""),
        "turnover": st.session_state.get("turnover_label",""),
        "work_mode": st.session_state.get("work_mode",""),
        "derived_size": org_size(),
        "systems_status": sys[0],
        "people_status":  ppl[0],
        "exposure_status": net[0],
        "Q1_it_manager": st.session_state.get("bp_it_manager",""),
        "Q2_device_inventory": st.session_state.get("bp_inventory",""),
        "Q3_byod": st.session_state.get("bp_byod",""),
        "Q4_sensitive": st.session_state.get("bp_sensitive",""),
        "Q5_website": st.session_state.get("df_website",""),
        "Q6_https": st.session_state.get("df_https",""),
        "Q7_business_email": st.session_state.get("df_email",""),
        "Q8_social": st.session_state.get("df_social",""),
        "Q9_public_review": st.session_state.get("df_review",""),
    }
    for sid, sc in (st.session_state.get("detailed_scores") or {}).items():
        payload[f"section_{sid}_score"] = sc
    return payload

def make_csv_bytes(row_dict: dict) -> bytes:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(row_dict.keys()))
    writer.writeheader(); writer.writerow(row_dict)
    return buf.getvalue().encode("utf-8")

def make_markdown_summary() -> str:
    sys,ppl,net = area_rag()
    lines = []
    lines += [
        "# SME Cybersecurity Self-Assessment — Summary",
        "",
        "## Snapshot",
        f"- Business: {st.session_state.get('company_name','')}",
        f"- Region: {st.session_state.get('business_region','')}",
        f"- Industry: {resolved_industry()}",
        f"- People: {st.session_state.get('employee_range','')} | Years: {st.session_state.get('years_in_business','')}",
        f"- Turnover: {st.session_state.get('turnover_label','')} | Work mode: {st.session_state.get('work_mode','')}",
        f"- Derived size: {org_size()}",
        "",
        "## At-a-glance",
        f"- Systems & devices: {sys[0]}",
        f"- People & access: {ppl[0]}",
        f"- Online exposure: {net[0]}",
        "",
    ]
    if st.session_state.get("detailed_scores"):
        lines.append("## Section scores")
        for sid, sc in st.session_state["detailed_scores"].items():
            label = "Low" if sc < 0.5 else "Medium" if sc < 1.2 else "High"
            lines.append(f"- {sid}: {label} (score {sc})")
        lines.append("")
    return "\n".join(lines)

def send_email_smtp(to_addr: str, subject: str, body_text: str, attachment_name: str, attachment_bytes: bytes):
    """
    Configure in Streamlit secrets:
      [smtp]
      host="smtp.sendgrid.net"  port="465"
      username="apikey"         password="YOUR_SECRET"
      from="reports@yourdomain.com"
    """
    import smtplib, ssl
    from email.message import EmailMessage
    cfg = st.secrets["smtp"]
    msg = EmailMessage()
    msg["Subject"] = subject; msg["From"] = cfg["from"]; msg["To"] = to_addr
    msg.set_content(body_text)
    msg.add_attachment(attachment_bytes, maintype="text", subtype="csv", filename=attachment_name)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(cfg["host"], int(cfg["port"]), context=context) as server:
        server.login(cfg["username"], cfg["password"]); server.send_message(msg)

# ─────────────────────────────────────────────────────────────
# LANDING
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Landing":
    st.markdown("### 🛡️ SME Cybersecurity Self-Assessment")
    st.markdown("**Assess · Understand · Act — in under 15 minutes.**")
    st.write("Plain-language questions, traceable to NIST/ISO. No data is stored unless you email the report to yourself.")
    st.progress(0.0, text="Step 0 of 3")
    if st.button("Start ➜", type="primary"):
        go("Step 1")

# ─────────────────────────────────────────────────────────────
# STEP 1 — Business profile
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 1":
    st.progress(1/3, text="Step 1 of 3")
    st.markdown("## 🧭 Tell us about the business")
    st.caption("Just the basics (~2 minutes).")

    snap, form = st.columns([1, 2], gap="large")

    with snap:
        st.markdown('<div class="sticky">', unsafe_allow_html=True)
        st.markdown("#### 📸 Snapshot")
        st.markdown(
            f'<div class="card">'
            f'<b>Business:</b> {st.session_state.company_name or "—"}<br>'
            f'<b>Region:</b> {st.session_state.business_region}<br>'
            f'<b>Industry:</b> {resolved_industry()}<br>'
            f'<b>People:</b> {st.session_state.employee_range} · '
            f'<b>Years:</b> {st.session_state.years_in_business}<br>'
            f'<b>Turnover:</b> {st.session_state.turnover_label}<br>'
            f'<b>Work mode:</b> {st.session_state.work_mode}<br>'
            f'<b>Size (derived):</b> {org_size()}</div>', unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with form:
        st.markdown("#### 👤 About you")
        st.session_state.person_name = st.text_input("Your name *", value=st.session_state.person_name)

        st.markdown("#### 🏢 About the business")
        st.session_state.company_name = st.text_input("Business name *", value=st.session_state.company_name)

        c1, c2 = st.columns(2)
        with c1:
            st.session_state.business_region = st.selectbox("🌍 Business location / region *", REGION_OPTIONS,
                                                            index=REGION_OPTIONS.index(st.session_state.business_region))
            st.session_state.sector_label = st.selectbox("🏷️ Industry / service *", INDUSTRY_OPTIONS,
                                                         index=INDUSTRY_OPTIONS.index(st.session_state.sector_label) if st.session_state.sector_label in INDUSTRY_OPTIONS else 0)
            if st.session_state.sector_label == "Other (type below)":
                st.session_state.sector_other = st.text_input("✍️ Type your industry *", value=st.session_state.sector_other)
            else:
                st.session_state.sector_other = ""
            st.session_state.years_in_business = st.selectbox("📅 How long in business? *", YEARS_OPTIONS,
                                                              index=YEARS_OPTIONS.index(st.session_state.years_in_business))
        with c2:
            st.session_state.employee_range = st.selectbox("👥 People (incl. contractors) *",
                                                           EMPLOYEE_RANGES, index=EMPLOYEE_RANGES.index(st.session_state.employee_range))
            st.session_state.turnover_label = st.selectbox("💶 Approx. annual turnover *",
                                                           TURNOVER_OPTIONS, index=TURNOVER_OPTIONS.index(st.session_state.turnover_label))
        st.session_state.work_mode = _radio_none("🧭 Work mode *", WORK_MODE, key="work_mode", horizontal=True)

        st.markdown('<div class="btnrow">', unsafe_allow_html=True)
        cA, cB = st.columns([1,1])
        with cA:
            if st.button("⬅ Back"): go("Landing")
        with cB:
            missing=[]
            if not st.session_state.person_name.strip(): missing.append("name")
            if not st.session_state.company_name.strip(): missing.append("company")
            if st.session_state.sector_label == "Other (type below)" and not st.session_state.sector_other.strip(): missing.append("industry")
            if not missing and st.button("Continue ➜", type="primary"):
                go("Step 2")
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# STEP 2 — Baseline quick checks (Q1–Q9)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 2":
    st.progress(2/3, text="Step 2 of 3")
    st.markdown("## 🧪 Your current practices")
    st.caption("Answer the 9 quick checks. No trick questions.")

    snap, body, prev = st.columns([1, 1.6, 1], gap="large")

    with snap:
        st.markdown('<div class="sticky">', unsafe_allow_html=True)
        st.markdown("#### 📸 Snapshot")
        st.markdown(
            f'<div class="card">'
            f'<b>Business:</b> {st.session_state.company_name}<br>'
            f'<b>Region:</b> {st.session_state.business_region}<br>'
            f'<b>Industry:</b> {resolved_industry()}<br>'
            f'<b>People:</b> {st.session_state.employee_range} · <b>Years:</b> {st.session_state.years_in_business}<br>'
            f'<b>Turnover:</b> {st.session_state.turnover_label} · <b>Size:</b> {org_size()}<br>'
            f'<b>Work mode:</b> {st.session_state.work_mode}</div>', unsafe_allow_html=True
        )
        sys,ppl,net = area_rag()
        st.markdown("#### 🔎 At-a-glance")
        st.markdown(f'<span class="chip {sys[1]}">🖥️ Systems · {sys[0]}</span>'
                    f'<span class="chip {ppl[1]}">👥 People · {ppl[0]}</span>'
                    f'<span class="chip {net[1]}">🌐 Exposure · {net[0]}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with body:
        tab1, tab2 = st.tabs(["🧭 Business profile (Q1–Q4)", "🌐 Digital footprint (Q5–Q9)"])
        with tab1:
            st.markdown("**Q1. 🧑‍💻 Who looks after your IT day-to-day?**")
            _radio_none(" ", ["Self-managed","Outsourced IT","Shared responsibility","Not sure"], key="bp_it_manager", horizontal=True, label_visibility="collapsed")
            st.markdown("<div class='hint'>Laptops/phones, Wi-Fi, email, website, point-of-sale, cloud apps, file storage/backup.</div>", unsafe_allow_html=True)

            st.markdown("**Q2. 📋 Do you keep a simple list of company devices (laptops, phones, servers)?**")
            radio_pills(" ", key="bp_inventory", horizontal=True, label_visibility="collapsed")
            st.markdown("<div class='hint'>An asset list helps find forgotten or unmanaged gear.</div>", unsafe_allow_html=True)

            st.markdown("**Q3. 📱 Do people use personal devices for work (BYOD)?**")
            _radio_none(" ", ["Yes","Sometimes","No","Not sure"], key="bp_byod", horizontal=True, label_visibility="collapsed")
            st.markdown("<div class='hint'>E.g., reading work email on a personal phone or laptop.</div>", unsafe_allow_html=True)

            st.markdown("**Q4. 🔐 Do you handle sensitive customer or financial data?**")
            _radio_none(" ", ["Yes","No","Not sure"], key="bp_sensitive", horizontal=True, label_visibility="collapsed")
            st.markdown("<div class='hint'>Payment details, personal records, contracts.</div>", unsafe_allow_html=True)

        with tab2:
            st.markdown("**Q5. 🕸️ Do you have a public website?**")
            _radio_none(" ", ["Yes","No"], key="df_website", horizontal=True, label_visibility="collapsed")

            st.markdown("**Q6. 🔒 Is your website HTTPS (padlock in the browser)?**")
            _radio_none(" ", ["Yes","Partially","No","Not sure"], key="df_https", horizontal=True, label_visibility="collapsed")
            st.markdown("<div class='hint'>HTTPS encrypts traffic and builds visitor trust.</div>", unsafe_allow_html=True)

            st.markdown("**Q7. ✉️ Do you use business email addresses?**")
            _radio_none(" ", ["Yes","Partially","No"], key="df_email", horizontal=True, label_visibility="collapsed")
            st.markdown("<div class='hint'>Personal Gmail/Yahoo increases phishing risk.</div>", unsafe_allow_html=True)

            st.markdown("**Q8. 📣 Is your business active on social media?**")
            _radio_none(" ", ["Yes","No"], key="df_social", horizontal=True, label_visibility="collapsed")

            st.markdown("**Q9. 🔎 Do you regularly check what’s public about the company or staff online?**")
            _radio_none(" ", ["Yes","Sometimes","No"], key="df_review", horizontal=True, label_visibility="collapsed")
            st.markdown("<div class='hint'>Contact details, staff lists, screenshots can reveal systems.</div>", unsafe_allow_html=True)

    with prev:
        st.write(""); st.write("")
        if st.button("⬅ Back to Step 1"): go("Step 1")
        required = ["bp_it_manager","bp_inventory","bp_byod","bp_sensitive","df_website","df_https","df_email","df_social","df_review"]
        missing = [k for k in required if _norm(st.session_state.get(k, "")) == ""]
        if st.button("Finish Initial Assessment ➜", type="primary", disabled=len(missing)>0): go("Step 3")

# ─────────────────────────────────────────────────────────────
# STEP 3 — Summary
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 3":
    st.progress(3/3, text="Step 3 of 3")
    st.markdown("## 📊 Initial Assessment Summary")
    over_txt, over_class, over_msg = overall_badge()
    st.markdown(f'<span class="pill {over_class}">Overall digital dependency: <b>{over_txt}</b></span>', unsafe_allow_html=True)
    st.caption(over_msg)

    snap, glance = st.columns([1.1, 1.9], gap="large")
    with snap:
        st.markdown("### 📸 Snapshot")
        st.markdown(
            f'<div class="card"><b>Business:</b> {st.session_state.company_name}<br>'
            f'<b>Region:</b> {st.session_state.business_region}<br>'
            f'<b>Industry:</b> {resolved_industry()}<br>'
            f'<b>People:</b> {st.session_state.employee_range} · '
            f'<b>Years:</b> {st.session_state.years_in_business} · '
            f'<b>Turnover:</b> {st.session_state.turnover_label}<br>'
            f'<b>Work mode:</b> {st.session_state.work_mode} · '
            f'<b>Size:</b> {org_size()}</div>', unsafe_allow_html=True
        )
    with glance:
        st.markdown("### 🔎 At-a-glance")
        sys, ppl, net = area_rag()
        g1, g2, g3 = st.columns(3)
        with g1: st.markdown(f'<div class="card"><b>🖥️ Systems & devices</b><div style="margin-top:.35rem">{sys[0]}</div></div>', unsafe_allow_html=True)
        with g2: st.markdown(f'<div class="card"><b>👥 People & access</b><div style="margin-top:.35rem">{ppl[0]}</div></div>', unsafe_allow_html=True)
        with g3: st.markdown(f'<div class="card"><b>🌐 Online exposure</b><div style="margin-top:.35rem">{net[0]}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📚 Likely compliance & standards to consider")
    tags = compute_tags()
    for name, level, note in applicable_compliance(tags):
        st.markdown(f'<div class="card" style="margin-bottom:.5rem"><b>{name}</b> <span class="pill amber" style="margin-left:.4rem">{level}</span><div class="hint">ℹ️ {note}</div></div>', unsafe_allow_html=True)

    st.markdown("")
    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        if st.button("⬅ Back"): go("Step 2")
    with c2:
        if st.button("Start over"):
            for k, v in defaults.items(): st.session_state[k]=v
            go("Landing")
    with c3:
        if st.button("Continue to detailed assessment ➜", type="primary"):
            st.session_state.detailed_sections = pick_active_sections(tags)
            go("Detailed")

# ─────────────────────────────────────────────────────────────
# Detailed Assessment
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Detailed":
    st.progress(3/3, text="Detailed assessment")
    st.markdown("## 🧩 Detailed Assessment")

    active_ids=set(st.session_state.get("detailed_sections", []))
    sections=[s for s in ALL_SECTIONS if s["id"] in active_ids] or [SECTION_3,SECTION_4,SECTION_5,SECTION_8]

    tabs=st.tabs([("🔐 " if s["id"]=='Access & Identity' else "💻 " if s['id']=='Device & Data' else "🧩 " if s['id']=='System & Software Updates' else "🚨 " if s['id']=='Incident Preparedness' else "☁️ " if s['id']=='Vendor & Cloud' else "🧠 ")+s["id"] for s in sections])
    for tab, s in zip(tabs, sections):
        with tab: render_section(s)

    cA, cB = st.columns(2)
    with cA:
        if st.button("⬅ Back to Summary"): go("Step 3")
    with cB:
        if st.button("Finish & see action plan ➜", type="primary"):
            st.session_state["detailed_scores"]={s["id"]: section_score(s) for s in sections}
            go("Report")

# ─────────────────────────────────────────────────────────────
# Final Report — with export (CSV/MD) + optional email
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Report":
    st.progress(1.0, text="Report")
    st.markdown("## 🗺️ Recommendations & Section Scores")

    scores = st.session_state.get("detailed_scores", {})
    if scores:
        cols = st.columns(len(scores))
        for (sid, sc), col in zip(scores.items(), cols):
            level = "green" if sc < 0.5 else "amber" if sc < 1.2 else "red"
            label = "Low" if level=="green" else "Medium" if level=="amber" else "High"
            with col:
                st.markdown(f'<div class="card"><b>{sid}</b><div class="hint">Risk: <span class="pill {level}">{label}</span> (score {sc})</div></div>', unsafe_allow_html=True)
    else:
        st.caption("No detailed scores yet. Complete the detailed assessment to see section scores.")

    st.markdown("---")
    st.markdown("### 🔧 Top actions to consider")
    actions=[]
    if _norm(st.session_state.get("df_website",""))=="yes" and _norm(st.session_state.get("df_https",""))!="yes":
        actions.append("Enable HTTPS and force redirect from HTTP to HTTPS.")
    if _norm(st.session_state.get("df_email","")) in {"no","partially"}:
        actions.append("Move all users to business email (e.g., M365/Google Workspace) and enforce MFA.")
    if _norm(st.session_state.get("bp_inventory","")) not in {"yes","partially"}:
        actions.append("Create a simple device inventory and enable full-disk encryption on laptops.")
    if _norm(st.session_state.get("bp_byod","")) in {"yes"}:
        actions.append("Define a BYOD policy: screen lock, OS updates, encryption, MFA for email/apps.")
    t=compute_tags()
    if any(x in t for x in ["infra:cloud","system:pos","geo:crossborder"]):
        actions.append("Review vendor/cloud contracts: breach notification, MFA on admin, and access logs.")
    if not actions:
        actions.append("Test incident response with a short tabletop exercise and tighten MFA hygiene.")
    st.markdown('<div class="card"><ol style="margin:.25rem 1rem">'+ "".join([f"<li>{x}</li>" for x in actions[:5]]) + "</ol></div>", unsafe_allow_html=True)

    # Exports
    st.markdown("### ⬇️ Export your results")
    payload = build_summary_payload()
    csv_bytes = make_csv_bytes(payload)
    md_text = make_markdown_summary()

    cA, cB, cC = st.columns(3)
    with cA:
        st.download_button("Download CSV", data=csv_bytes, file_name="cyber-assessment-summary.csv", mime="text/csv")
    with cB:
        st.download_button("Download Markdown", data=md_text.encode("utf-8"),
                           file_name="cyber-assessment-summary.md", mime="text/markdown")
    with cC:
        st.caption("Optional email copy:")
        st.session_state.export_email = st.text_input("📧 Email address", value=st.session_state.export_email, label_visibility="collapsed", placeholder="name@example.com")
        if st.button("Email me the CSV ✉️", disabled=not st.session_state.export_email.strip()):
            email = st.session_state.export_email.strip()
            if not EMAIL_RE.match(email):
                st.error("Please enter a valid email address.")
            else:
                try:
                    send_email_smtp(
                        to_addr=email,
                        subject="Your SME Cybersecurity Self-Assessment summary",
                        body_text="Attached is your CSV summary. Thanks for completing the assessment!",
                        attachment_name="cyber-assessment-summary.csv",
                        attachment_bytes=csv_bytes
                    )
                    st.success("Sent! Please check your inbox.")
                except Exception as e:
                    st.error(f"Could not send email: {type(e).__name__}: {e}")

    st.markdown("")
    c1, c2 = st.columns([1,1])
    with c1:
        if st.button("⬅ Back to Detailed"): go("Detailed")
    with c2:
        if st.button("Start over"):
            for k, v in defaults.items(): st.session_state[k]=v
            go("Landing")
