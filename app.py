import streamlit as st
from typing import List, Tuple

# ─────────────────────────────────────────────────────────────
# Page setup & styles
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="SME Cybersecurity Self-Assessment", layout="wide")

st.markdown("""
<style>
  .block-container {max-width: 1160px; padding-top: 2.25rem !important;}
  h1 {font-size: 2.10rem !important;}
  h2 {font-size: 1.55rem !important;}
  h3 {font-size: 1.25rem !important;}
  h4 {font-size: 1.05rem !important;}

  .lead {color:#374151; margin:.35rem 0 .9rem; font-size:1.05rem}

  /* Question line (larger than explanation) */
  .q {font-size: 1.08rem; font-weight: 600; color:#111827; margin:.35rem 0 .35rem}

  /* Explanation (smaller, italic, readable) */
  .hint {color:#374151; font-size:.96rem; margin:.2rem 0 .7rem; font-style:italic}
  .explain {color:#374151; font-size:1.0rem; margin:.25rem 0 .6rem}
  .explain ul {margin:.2rem 0 .2rem 1.1rem}
  .explain li {margin:.1rem 0}

  /* Chips / pills */
  .pill {display:inline-block;border-radius:999px;padding:.18rem .55rem;border:1px solid #e5e7eb;font-size:.9rem;color:#1f2937;background:#fff}
  .chip {display:inline-flex;align-items:center;gap:.35rem;border-radius:999px;padding:.18rem .6rem;border:1px solid #e5e7eb;margin-right:.35rem;font-weight:600}

  /* Traffic lights */
  .green{background:#e8f7ee;color:#0f5132;border-color:#cceedd}
  .amber{background:#fff5d6;color:#8a6d00;border-color:#ffe7ad}
  .red{background:#ffe5e5;color:#842029;border-color:#ffcccc}

  /* Cards / layout */
  .card {border:1px solid #e6e8ec;border-radius:12px;padding:12px;background:#fff}
  .tight {margin-top:.25rem}
  .sticky {position: sticky; top: 12px;}
  .btnrow {margin-top:.4rem}
  .tag {font-size:.75rem;border-radius:8px;padding:.08rem .4rem;border:1px solid #e5e7eb;margin-left:.25rem}

  /* Radios easier to read */
  [data-baseweb="radio"] label {font-size:1.02rem;}

  /* Equal buttons across the app */
  .stButton > button {width:100%; min-height:44px;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Options & text
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
CRITICAL_SYSTEMS = [
    "Enterprise Resource Planning (ERP)",
    "Point of Sale (PoS)",
    "Customer Relationship Management (CRM)",
    "Electronic Health Record (EHR)",
    "Content Management System (CMS)",
    "Other (type below)"
]
WORK_ENVIRONMENTS = ["Local servers", "Cloud apps", "Hybrid"]
REMOTE_RATIO = ["Mostly on-site", "Hybrid", "Fully remote"]
DATA_TYPES = [
    "Customer personal data (PII)",
    "Employee/staff data",
    "Health/medical data",
    "Financial/transaction data"
]
CROSS_BORDER = ["EU-only", "Includes Non-EU regions", "Unsure"]
CERTIFICATION_OPTIONS = [
    "None","ISO/IEC 27001","Cyber Essentials (UK)","SOC 2",
    "GDPR compliance program","PCI DSS (Payment Cards)","HIPAA (US healthcare)",
    "NIS2 readiness","Other (type below)"
]

DATA_TYPE_HELP = {
    "Customer personal data (PII)": "Names, emails, phone numbers, addresses, IDs, online identifiers.",
    "Employee/staff data": "HR info (contracts, payroll, performance, IDs, contact details).",
    "Health/medical data": "Any health info or patient records (diagnosis, treatment, insurance).",
    "Financial/transaction data": "Invoices, bank details, card tokens, PoS records, refunds.",
}

SECTION_INTRO = {
    "Access & Identity": [
        "What this covers: who can access what, how safely (passwords, MFA, admin rights, removing ex-staff).",
        "Why it matters: most breaches start with weak or reused passwords.",
    ],
    "Device & Data": [
        "What this covers: device protection, full-disk encryption, antivirus/EDR, backups and restores.",
        "Why it matters: a lost or stolen device shouldn’t expose your business data.",
    ],
    "System & Software Updates": [
        "What this covers: OS and application updates; avoiding unsupported systems.",
        "Why it matters: patches close well-known holes that attackers scan for.",
    ],
    "Incident Preparedness": [
        "What this covers: reporting, a simple response plan, key contacts, quick practice.",
        "Why it matters: clear steps reduce damage and downtime.",
    ],
    "Vendor & Cloud": [
        "What this covers: MFA on cloud tools, contract terms, who has access, breach notification.",
        "Why it matters: suppliers and SaaS are part of your security posture.",
    ],
    "Awareness & Training": [
        "What this covers: training basics, spotting phishing, onboarding, reminders, leadership support.",
        "Why it matters: people prevent most attacks.",
    ],
}

# ─────────────────────────────────────────────────────────────
# State (defaults)
# ─────────────────────────────────────────────────────────────
defaults = dict(
    page="Landing",
    # Step 1
    person_name="", company_name="",
    sector_label=INDUSTRY_OPTIONS[0], sector_other="",
    years_in_business=YEARS_OPTIONS[0],
    employee_range=EMPLOYEE_RANGES[0],
    turnover_label=TURNOVER_OPTIONS[0],
    work_mode=WORK_MODE[0],
    business_region=REGION_OPTIONS[0],
    # Step 2 (Operating context)
    critical_systems=[], critical_systems_other="",
    primary_work_env=WORK_ENVIRONMENTS[1],
    remote_ratio=REMOTE_RATIO[1],
    data_types=[], cross_border=CROSS_BORDER[0],
    certifications=["None"], certifications_other="",
    bp_card_payments="",
    # Baseline answers
    bp_it_manager="", bp_inventory="", bp_byod="", bp_sensitive="",
    df_website="", df_https="", df_email="", df_social="", df_review="",
    # Tier 2
    detailed_sections=[], detailed_scores={}
)
for k,v in defaults.items():
    st.session_state.setdefault(k,v)

# ─────────────────────────────────────────────────────────────
# Helpers (derivations & UI)
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
    return st.session_state.sector_other or "Other" if st.session_state.sector_label=="Other (type below)" else st.session_state.sector_label

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
        if "(erp)" in sl: tags.add("system:erp")
        elif "(pos)" in sl: tags.add("system:pos")
        elif "(crm)" in sl: tags.add("system:crm")
        elif "(ehr)" in sl: tags.add("system:ehr")
        elif "(cms)" in sl: tags.add("system:cms")
        elif "other" in sl: tags.add("system:other")
    for d in st.session_state.data_types or []:
        dl=d.lower()
        if "customer" in dl: tags.add("data:pii")
        if "employee" in dl: tags.add("data:employee")
        if "health" in dl: tags.add("data:health")
        if "financial" in dl: tags.add("data:financial")
    cb=st.session_state.cross_border
    tags.add("geo:eu_only" if cb=="EU-only" else "geo:unsure" if cb=="Unsure" else "geo:crossborder")
    if (st.session_state.bp_sensitive or "").lower()=="yes": tags.add("data:sensitive")
    if (st.session_state.bp_card_payments or "").lower()=="yes": tags.add("payments:card")
    tags |= certification_tags()
    return tags

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
    score=sum({"green":0,"amber":1,"red":2}.get(x[1],1) for x in [sys,ppl,net])
    if score<=1: return ("Low","green","Great job — strong digital hygiene.")
    if score<=3: return ("Medium","amber","Balanced setup. A few quick wins will reduce risk fast.")
    return ("High","red","Higher exposure — prioritise quick actions to lower risk.")

def go(page): st.session_state.page=page

# emoji radio that stores plain values
def radio_emoji(prompt:str, key:str, *, horizontal=True):
    choices = [("Yes","✅ Yes"), ("Partially","🟡 Partially"), ("No","❌ No"), ("Not sure","🤔 Not sure")]
    plain = [p for p,_ in choices]
    pretty = [d for _,d in choices]
    cur = st.session_state.get(key, "")
    idx = plain.index(cur) if cur in plain else 0
    picked_pretty = st.radio(prompt, pretty, index=idx, horizontal=horizontal, key=f"pretty__{key}")
    st.session_state[key] = next(p for p,d in choices if d == picked_pretty)

# ─────────────────────────────────────────────────────────────
# Sections & questions (Tier-2)
# ─────────────────────────────────────────────────────────────
def section(title_id, qlist):
    return {"id":title_id, "title":title_id, "questions":qlist}

SECTION_3 = section("Access & Identity", [
    {"id":"ai_pw","t":"🔑 Are strong passwords required for all accounts?","h":"Use at least 10–12 characters, avoid reuse. A password manager helps."},
    {"id":"ai_mfa","t":"🛡️ Is Multi-Factor Authentication (MFA) enabled for key accounts?","h":"Start with email, admin and finance; use an authenticator app or security key."},
    {"id":"ai_admin","t":"🧰 Are admin rights limited to only those who need them?","h":"Grant temporarily, review quarterly, monitor admin sign-ins."},
    {"id":"ai_shared","t":"👥 Are shared accounts avoided or controlled?","h":"Prefer named accounts; if shared, rotate passwords and log usage."},
    {"id":"ai_leavers","t":"🚪 Are old or unused accounts removed promptly?","h":"Disable the same day a person leaves; reclaim devices and keys."},
])
SECTION_4 = section("Device & Data", [
    {"id":"dd_lock","t":"🔒 Are all laptops/phones protected with a password or PIN?","h":"Also enable auto-lock (≤10 minutes) and find-my-device."},
    {"id":"dd_fde","t":"💽 Is full-disk encryption enabled on laptops and mobiles?","h":"Windows BitLocker, macOS FileVault, Android/iOS device encryption."},
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
    {"id":"su_review","t":"🗓️ Do you have a monthly reminder to review updates?","h":"Calendar task, RMM/MSP report, or patch-tuesday checklist."},
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
    bullets = SECTION_INTRO.get(sec['id'], [])
    if bullets:
        st.markdown("<div class='explain'><ul>" + "".join([f"<li><i>{b}</i></li>" for b in bullets]) + "</ul></div>", unsafe_allow_html=True)
    for q in sec["questions"]:
        st.markdown(f"<div class='q'>{q['t']}</div>", unsafe_allow_html=True)
        radio_emoji(" ", key=q["id"])
        st.markdown(f"<div class='hint'>💡 {q['h']}</div>", unsafe_allow_html=True)
    st.markdown("")

def section_score(sec):
    vals=[st.session_state.get(q["id"],"") for q in sec["questions"]]
    risk={"Yes":0,"Partially":1,"Not sure":1,"No":2}
    return round(sum(risk.get(v,1) for v in vals)/len(vals),2) if vals else 0.0

def section_light(sec)->Tuple[str,str,str]:
    sc = section_score(sec)
    if sc < 0.5: return ("🟢","Low","green")
    if sc < 1.2: return ("🟡","Medium","amber")
    return ("🔴","High","red")

def pick_active_sections(tags:set):
    active=set(BASELINE_IDS)
    if "size:Small" in tags or "size:Medium" in tags: active.add("Incident Preparedness")
    if any(t in tags for t in ["infra:cloud","system:pos","geo:crossborder"]): active.add("Vendor & Cloud")
    order=[s["id"] for s in ALL_SECTIONS]
    return [sid for sid in order if sid in active]

# ─────────────────────────────────────────────────────────────
# UI helpers — progress bars
# ─────────────────────────────────────────────────────────────
def progress(step: int, total: int = 4, label: str = ""):
    pct = max(0, min(step, total)) / total
    st.progress(pct, text=label or f"Step {step} of {total}")

def detailed_dynamic_progress(active_sections: List[dict]):
    total = sum(len(s["questions"]) for s in active_sections)
    answered = 0
    for s in active_sections:
        for q in s["questions"]:
            if st.session_state.get(q["id"]): answered += 1
    pct = (answered / total) if total else 0
    st.progress(pct, text=f"Detailed assessment — {answered}/{total} answered")

# ─────────────────────────────────────────────────────────────
# LANDING
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Landing":
    progress(0)
    st.markdown("# 🛡️ SME Cybersecurity Self-Assessment")
    st.markdown("<div class='lead'>Assess · Understand · Act — in under 15 minutes.</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.write("• 🗣️ Plain-language questions")
        st.write("• 📚 Traceable to NIST/ISO")
    with c2:
        st.write("• ⏱️ 10–15 minutes")
        st.write("• 🧪 Safe demos of common scams")
    if st.button("Start ➜", type="primary"):
        go("Step 1"); st.rerun()

# ─────────────────────────────────────────────────────────────
# STEP 1 — Business basics
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 1":
    progress(1, label="Business basics")
    st.markdown("## 🧭 Tell us about the business")
    st.caption("Just the basics — the detailed bits come later.")

    snap, form = st.columns([1, 2], gap="large")
    with snap:
        st.markdown('<div class="sticky">', unsafe_allow_html=True)
        st.markdown("#### 📸 Snapshot")
        st.markdown(
            f"<div class='card tight'><b>Business:</b> {st.session_state.company_name or '—'}<br>"
            f"<b>Region:</b> {st.session_state.business_region}<br>"
            f"<b>Industry:</b> {resolved_industry()}<br>"
            f"<b>People:</b> {st.session_state.employee_range} · "
            f"<b>Years:</b> {st.session_state.years_in_business}<br>"
            f"<b>Turnover:</b> {st.session_state.turnover_label}<br>"
            f"<b>Work mode:</b> {st.session_state.work_mode}<br>"
            f"<b>Size (derived):</b> {org_size()}</div>", unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

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
            st.session_state.years_in_business = st.selectbox("📅 How long in business? *",
                                                              YEARS_OPTIONS, index=YEARS_OPTIONS.index(st.session_state.years_in_business))
        with c2:
            st.session_state.employee_range = st.selectbox("👥 People (incl. contractors) *",
                                                           EMPLOYEE_RANGES, index=EMPLOYEE_RANGES.index(st.session_state.employee_range))
            st.session_state.turnover_label = st.selectbox("💶 Approx. annual turnover *",
                                                           TURNOVER_OPTIONS, index=TURNOVER_OPTIONS.index(st.session_state.turnover_label))
        st.session_state.work_mode = st.radio("🧭 Work mode *", WORK_MODE, horizontal=True,
                                              index=WORK_MODE.index(st.session_state.work_mode))

        missing = []
        if not st.session_state.person_name.strip(): missing.append("name")
        if not st.session_state.company_name.strip(): missing.append("company")
        if st.session_state.sector_label == "Other (type below)" and not st.session_state.sector_other.strip():
            missing.append("industry")

        st.markdown('<div class="btnrow">', unsafe_allow_html=True)
        cA, cB = st.columns(2)
        with cA:
            if st.button("⬅ Back"):
                go("Landing"); st.rerun()
        with cB:
            if st.button("Continue ➜", type="primary", disabled=len(missing)>0):
                go("Step 2"); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# STEP 2 — Quick checks + Operating context (optional)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 2":
    progress(2, label="Current practices & setup")
    st.markdown("## 🧪 Your current practices & setup")
    st.caption("Answer the quick checks. The operating context tab is optional and helps tailor advice.")

    snap, body, prev = st.columns([1, 1.65, 1], gap="large")
    with snap:
        st.markdown('<div class="sticky">', unsafe_allow_html=True)
        st.markdown("#### 📸 Snapshot")
        st.markdown(
            f"<div class='card tight'><b>Business:</b> {st.session_state.company_name}<br>"
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
        tab1, tab2, tab3 = st.tabs(["🧭 Quick checks (Q1–Q9)", "🌐 Digital footprint", "🏗️ Operating context (optional)"])

        with tab1:
            st.markdown("<div class='hint'>Use plain answers — we’ll guide you next.</div>", unsafe_allow_html=True)

            st.markdown("<div class='q'>🧑‍💻 Q1. Who looks after your IT day-to-day?</div>", unsafe_allow_html=True)
            st.radio(" ", ["Self-managed","Outsourced IT","Shared responsibility","Not sure"],
                     key="bp_it_manager", horizontal=True, label_visibility="collapsed")
            st.markdown("<div class='hint'>Includes laptops/phones, Wi-Fi, email, website, cloud apps, file storage/backup.</div>", unsafe_allow_html=True)

            st.markdown("<div class='q'>🗂️ Q2. Do you keep a simple list of company devices (laptops, phones, servers)?</div>", unsafe_allow_html=True)
            radio_emoji(" ", key="bp_inventory")
            st.markdown("<div class='hint'>An asset list helps find forgotten or unmanaged gear.</div>", unsafe_allow_html=True)

            st.markdown("<div class='q'>📱 Q3. Do people use personal devices for work (BYOD)?</div>", unsafe_allow_html=True)
            radio_emoji(" ", key="bp_byod")
            st.markdown("<div class='hint'>E.g., reading work email on a personal phone or laptop.</div>", unsafe_allow_html=True)

            st.markdown("<div class='q'>🔐 Q4. Do you handle sensitive customer or financial data?</div>", unsafe_allow_html=True)
            radio_emoji(" ", key="bp_sensitive")
            st.markdown("<div class='hint'>Payment details, personal records, contracts.</div>", unsafe_allow_html=True)

        with tab2:
            st.markdown("<div class='q'>🕸️ Q5. Do you have a public website?</div>", unsafe_allow_html=True)
            st.radio(" ", ["Yes","No"], key="df_website", horizontal=True, label_visibility="collapsed")
            st.markdown("<div class='hint'>Helps assess potential online entry points.</div>", unsafe_allow_html=True)

            st.markdown("<div class='q'>🔒 Q6. Is your website HTTPS (padlock in the browser)?</div>", unsafe_allow_html=True)
            radio_emoji(" ", key="df_https")
            st.markdown("<div class='hint'>HTTPS encrypts traffic and builds visitor trust.</div>", unsafe_allow_html=True)

            st.markdown("<div class='q'>✉️ Q7. Do you use business email addresses?</div>", unsafe_allow_html=True)
            radio_emoji(" ", key="df_email")
            st.markdown("<div class='hint'>Personal Gmail/Yahoo accounts increase phishing risk.</div>", unsafe_allow_html=True)

            st.markdown("<div class='q'>📣 Q8. Is your business active on social media?</div>", unsafe_allow_html=True)
            st.radio(" ", ["Yes","No"], key="df_social", horizontal=True, label_visibility="collapsed")

            st.markdown("<div class='q'>🔎 Q9. Do you regularly check what’s public about the company or staff online?</div>", unsafe_allow_html=True)
            st.radio(" ", ["Yes","Sometimes","No"], key="df_review", horizontal=True, label_visibility="collapsed")
            st.markdown("<div class='hint'>Contact details, staff lists, screenshots can reveal systems.</div>", unsafe_allow_html=True)

        with tab3:
            st.markdown("<div class='hint'>These details help tailor your results. Skip if unsure — you can add later.</div>", unsafe_allow_html=True)
            cA, cB = st.columns(2)
            with cA:
                st.multiselect("🧩 Critical systems in use", CRITICAL_SYSTEMS, key="critical_systems", default=st.session_state.critical_systems)
                if "Other (type below)" in st.session_state.critical_systems:
                    st.text_input("✍️ Specify other system", key="critical_systems_other", value=st.session_state.critical_systems_other)
                st.radio("🏗️ Primary work environment", WORK_ENVIRONMENTS, key="primary_work_env", horizontal=True, index=WORK_ENVIRONMENTS.index(st.session_state.primary_work_env))
                st.radio("🏠 Remote work ratio", REMOTE_RATIO, key="remote_ratio", horizontal=True, index=REMOTE_RATIO.index(st.session_state.remote_ratio))
            with cB:
                st.multiselect("🔎 Types of personal data handled", DATA_TYPES, key="data_types", default=st.session_state.data_types)
                if st.session_state.data_types:
                    st.markdown("<div class='hint'><i>" + "<br>".join([f"• {d}: {DATA_TYPE_HELP[d]}" for d in st.session_state.data_types]) + "</i></div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='hint'><i>Choose any that apply — we’ll tailor compliance notes accordingly.</i></div>", unsafe_allow_html=True)
                st.radio("🌐 Cross-border data flows", CROSS_BORDER, key="cross_border", horizontal=True, index=CROSS_BORDER.index(st.session_state.cross_border))
                st.multiselect("🔒 Certifications / schemes", CERTIFICATION_OPTIONS, key="certifications", default=st.session_state.certifications)
                if "Other (type below)" in st.session_state.certifications:
                    st.text_input("✍️ Specify other scheme", key="certifications_other", value=st.session_state.certifications_other)
                st.radio("💳 Do you accept or process card payments (online or in-store)?", ["Yes","No","Not sure"], key="bp_card_payments",
                         horizontal=True, index=(["Yes","No","Not sure"].index(st.session_state.bp_card_payments) if st.session_state.bp_card_payments else 1))

    with prev:
        st.write(""); st.write("")
        cA, cB = st.columns(2)
        with cA:
            if st.button("⬅ Back to Step 1"):
                go("Step 1"); st.rerun()
        with cB:
            required = ["bp_it_manager","bp_inventory","bp_byod","bp_sensitive","df_website","df_https","df_email","df_social","df_review"]
            missing = [k for k in required if not st.session_state.get(k)]
            if st.button("Continue ➜", type="primary", disabled=len(missing)>0):
                go("Step 3"); st.rerun()

# ─────────────────────────────────────────────────────────────
# STEP 3 — Summary (Initial)
# ─────────────────────────────────────────────────────────────
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

if st.session_state.page == "Step 3":
    progress(3, label="Initial assessment summary")
    st.markdown("## 📊 Initial Assessment Summary")
    over_txt, over_class, over_msg = overall_badge()
    st.markdown(f"<span class='pill {over_class}'>Overall digital dependency: <b>{over_txt}</b></span>", unsafe_allow_html=True)
    st.caption(over_msg)

    snap, glance = st.columns([1.05, 1.95], gap="large")
    with snap:
        st.markdown("### 📸 Snapshot")
        st.markdown(
            f"<div class='card tight'><b>Business:</b> {st.session_state.company_name}<br>"
            f"<b>Region:</b> {st.session_state.business_region}<br>"
            f"<b>Industry:</b> {resolved_industry()}<br>"
            f"<b>People:</b> {st.session_state.employee_range} · "
            f"<b>Years:</b> {st.session_state.years_in_business} · "
            f"<b>Turnover:</b> {st.session_state.turnover_label}<br>"
            f"<b>Work mode:</b> {st.session_state.work_mode} · "
            f"<b>Size:</b> {org_size()}</div>", unsafe_allow_html=True
        )

    with glance:
        st.markdown("### 🔎 At-a-glance")
        sys,ppl,net = area_rag()
        st.markdown(f"<span class='chip {sys[1]}'>🖥️ Systems · {sys[0]}</span>"
                    f"<span class='chip {ppl[1]}'>👥 People · {ppl[0]}</span>"
                    f"<span class='chip {net[1]}'>🌐 Exposure · {net[0]}</span>", unsafe_allow_html=True)
        hints=[]
        if st.session_state.bp_inventory not in ("Yes","Partially"): hints.append("📝 Add/finish your device list.")
        if st.session_state.df_website=='Yes' and st.session_state.df_https!='Yes': hints.append("🔒 Enable HTTPS for your website.")
        if st.session_state.bp_byod in ("Yes","Sometimes"): hints.append("📱 Set simple BYOD + MFA rules.")
        if hints: st.caption(" · ".join(hints))

    st.markdown("---")

    colS, colR = st.columns(2, gap="large")
    with colS:
        st.markdown("### ✅ Strengths")
        strengths=[]
        if st.session_state.df_https=="Yes": strengths.append("Website uses HTTPS (encrypted traffic).")
        if st.session_state.bp_inventory in ("Yes","Partially"): strengths.append("You keep a device list (even partial helps).")
        if not strengths: strengths.append("Solid starting point across core practices.")
        st.markdown("<div class='card'><ul style='margin:.25rem 1rem'>"+ "".join([f"<li>💪 {x}</li>" for x in strengths]) + "</ul></div>", unsafe_allow_html=True)
    with colR:
        st.markdown("### ⚠️ Areas to improve")
        risks=[]
        if st.session_state.df_email in ("No","Partially"): risks.append("Move to business email and enforce MFA.")
        if st.session_state.bp_byod in ("Yes","Sometimes"): risks.append("BYOD needs simple device rules and MFA.")
        if st.session_state.bp_sensitive=="Yes": risks.append("Back up key data and protect access with MFA.")
        if st.session_state.df_website=="Yes" and st.session_state.df_https!="Yes": risks.append("Turn on HTTPS and redirect HTTP→HTTPS.")
        if not risks: risks.append("Test incident response and tighten MFA hygiene.")
        st.markdown("<div class='card'><ul style='margin:.25rem 1rem'>"+ "".join([f"<li>🔧 {x}</li>" for x in risks]) + "</ul></div>", unsafe_allow_html=True)

    st.markdown("### 📚 Likely compliance & standards to consider")
    for name, level, note in applicable_compliance(compute_tags()):
        st.markdown(f"<div class='card' style='margin-bottom:.5rem'><b>{name}</b> <span class='tag'>{level}</span><div class='hint'>ℹ️ {note}</div></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        if st.button("⬅ Back"):
            go("Step 2"); st.rerun()
    with c2:
        if st.button("Start over"):
            for k,v in defaults.items(): st.session_state[k]=v
            go("Landing"); st.rerun()
    with c3:
        if st.button("Continue to detailed assessment ➜", type="primary"):
            st.session_state.detailed_sections = pick_active_sections(compute_tags())
            go("Detailed"); st.rerun()

# ─────────────────────────────────────────────────────────────
# STEP 4 — Detailed (with dynamic progress)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Detailed":
    active_ids=set(st.session_state.get("detailed_sections", []))
    sections=[s for s in ALL_SECTIONS if s["id"] in active_ids] or [SECTION_3,SECTION_4,SECTION_5,SECTION_8]
    detailed_dynamic_progress(sections)

    st.markdown("## 🧩 Detailed Assessment")

    tabs=st.tabs([("🔐 " if s["id"]=='Access & Identity' else "💻 " if s['id']=='Device & Data' else "🧩 " if s['id']=='System & Software Updates' else "🚨 " if s['id']=='Incident Preparedness' else "☁️ " if s['id']=='Vendor & Cloud' else "🧠 ")+s["id"] for s in sections])
    for tab, s in zip(tabs, sections):
        with tab: render_section(s)

    cA, cB = st.columns(2)
    with cA:
        if st.button("⬅ Back to Summary"):
            go("Step 3"); st.rerun()
    with cB:
        if st.button("Finish & see action plan ➜", type="primary"):
            st.session_state["detailed_scores"]={s["id"]: section_score(s) for s in sections}
            go("Report"); st.rerun()

# ─────────────────────────────────────────────────────────────
# REPORT — Action Plan (traffic lights) + robust PDF export
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Report":
    st.markdown("## 🗺️ Action Plan & Section Status")

    scores = st.session_state.get("detailed_scores", {})
    if scores:
        cols = st.columns(len(scores))
        lookup = {s["id"]: s for s in ALL_SECTIONS}
        for (sid, _), col in zip(scores.items(), cols):
            emoji, label, klass = section_light(lookup[sid])
            with col:
                st.markdown(
                    f"<div class='card'><b>{sid}</b>"
                    f"<div class='hint'>Status: <span class='pill {klass}'>{emoji} {label}</span></div></div>",
                    unsafe_allow_html=True
                )
    else:
        st.caption("No detailed sections answered yet. Complete the detailed assessment to see section status.")

    # Tailored action plan
    tags = compute_tags()
    quick: List[str] = []
    foundations: List[str] = []
    nextlvl: List[str] = []

    if st.session_state.df_website=="Yes" and st.session_state.df_https!="Yes":
        quick.append("🔒 Enable HTTPS and force redirect (HTTP→HTTPS). <span class='tag'>High impact</span> <span class='tag'>Low effort</span>")
    if st.session_state.df_email in ("No","Partially"):
        quick.append("📧 Move to business email (M365/Google) and enforce **MFA** for all users. <span class='tag'>High</span> <span class='tag'>Low</span>")
    if st.session_state.bp_inventory not in ("Yes","Partially"):
        quick.append("📋 Start a simple **device inventory** (sheet or MDM export). <span class='tag'>Med</span> <span class='tag'>Low</span>")

    if st.session_state.bp_byod in ("Yes","Sometimes"):
        foundations.append("📱 Publish a **BYOD rule of 5**: screen lock, OS updates, disk encryption, MFA for email, approved apps.")
    foundations.append("🧩 Turn on **automatic OS & app updates**; remove unsupported systems.")
    foundations.append("🗄️ Automate **backups** and **test a restore** quarterly.")

    if any(t in tags for t in ["infra:cloud","system:pos","geo:crossborder"]):
        nextlvl.append("🤝 Review key **vendor contracts**: breach notification, data location/transfer, and admin MFA.")
    if "payments:card" in tags or "system:pos" in tags:
        nextlvl.append("💳 Confirm **PCI DSS** responsibilities with your PoS/PSP (often most of the burden is on the provider).")
    if any(t in tags for t in ["geo:eu","geo:uk"]):
        nextlvl.append("📘 Document **GDPR basics**: Records of Processing, DPAs, and a contact for data requests.")

    st.markdown("### ⚡ Quick wins (do these first)")
    st.markdown("<div class='card'><ul style='margin:.25rem 1rem'>"+ "".join([f"<li>{x}</li>" for x in quick or ['No urgent quick wins detected.']]) +"</ul></div>", unsafe_allow_html=True)
    st.markdown("### 🧱 Foundations to build this quarter")
    st.markdown("<div class='card'><ul style='margin:.25rem 1rem'>"+ "".join([f"<li>{x}</li>" for x in foundations]) +"</ul></div>", unsafe_allow_html=True)
    st.markdown("### 🚀 Next-level / compliance alignment")
    st.markdown("<div class='card'><ul style='margin:.25rem 1rem'>"+ "".join([f"<li>{x}</li>" for x in nextlvl]) +"</ul></div>", unsafe_allow_html=True)

    # cache lists for export text
    st.session_state['_quick_list_cache'] = quick or ["No urgent quick wins detected."]
    st.session_state['_found_list_cache'] = foundations
    st.session_state['_next_list_cache']  = nextlvl

    # ------- Export helpers (PDF first; fallback to Markdown) -------
    def build_markdown_report() -> str:
        sys,ppl,net = area_rag()
        strengths=[]
        if st.session_state.df_https=="Yes": strengths.append("Website uses HTTPS.")
        if st.session_state.bp_inventory in ("Yes","Partially"): strengths.append("You keep a device inventory.")
        if not strengths: strengths.append("Solid starting point across core practices.")
        risks=[]
        if st.session_state.df_email in ("No","Partially"): risks.append("Move to business email and enforce MFA.")
        if st.session_state.bp_byod in ("Yes","Sometimes"): risks.append("BYOD needs simple device rules and MFA.")
        if st.session_state.bp_sensitive=="Yes": risks.append("Back up key data and protect access with MFA.")
        if st.session_state.df_website=="Yes" and st.session_state.df_https!="Yes": risks.append("Enable HTTPS and redirect HTTP→HTTPS.")
        lines = []
        lines.append("# SME Cybersecurity Self-Assessment — Summary & Action Plan")
        lines.append("")
        lines.append("## Snapshot")
        lines.append(f"- Business: {st.session_state.company_name}")
        lines.append(f"- Region: {st.session_state.business_region}")
        lines.append(f"- Industry: {resolved_industry()}")
        lines.append(f"- People: {st.session_state.employee_range} | Years: {st.session_state.years_in_business}")
        lines.append(f"- Turnover: {st.session_state.turnover_label} | Work mode: {st.session_state.work_mode}")
        lines.append(f"- Derived size: {org_size()}")
        lines.append("")
        lines.append("## At-a-glance")
        lines.append(f"- Systems & devices: {sys[0]}")
        lines.append(f"- People & access: {ppl[0]}")
        lines.append(f"- Online exposure: {net[0]}")
        lines.append("")
        lines.append("## Strengths")
        for s in strengths: lines.append(f"- {s}")
        lines.append("")
        lines.append("## Areas to improve")
        for r in risks: lines.append(f"- {r}")
        lines.append("")
        notes = applicable_compliance(compute_tags())
        if notes:
            lines.append("## Likely compliance & standards")
            for n,l,note in notes:
                lines.append(f"- {n} — {l}: {note}")
            lines.append("")
        scores = st.session_state.get("detailed_scores", {})
        if scores:
            lines.append("## Section status")
            for sid in scores.keys():
                sec = [s for s in ALL_SECTIONS if s['id']==sid][0]
                emoji, label, _ = section_light(sec)
                lines.append(f"- {sid}: {emoji} {label}")
            lines.append("")
        lines.append("## Action plan")
        lines.append("### Quick wins")
        for x in (st.session_state.get('_quick_list_cache') or []): lines.append(f"- {x}")
        lines.append("### Foundations")
        for x in (st.session_state.get('_found_list_cache') or []): lines.append(f"- {x}")
        if st.session_state.get('_next_list_cache'):
            lines.append("### Next-level / compliance")
            for x in st.session_state['_next_list_cache']: lines.append(f"- {x}")
        return "\n".join(lines)

    def _sanitize_latin(text: str) -> str:
        # fpdf2 core fonts are latin-1; drop anything outside to avoid crashes (emojis etc.)
        return text.encode("latin-1", "ignore").decode("latin-1")

    def export_button():
        md = build_markdown_report()

        # Try fpdf2 if present
        try:
            from fpdf import FPDF  # fpdf2
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()

            def add_h1(t): pdf.set_font("Helvetica","B",16); pdf.multi_cell(0,8, _sanitize_latin(t)); pdf.ln(2)
            def add_h2(t): pdf.set_font("Helvetica","B",14); pdf.multi_cell(0,7, _sanitize_latin(t)); pdf.ln(1)
            def add_p(t, sz=12): pdf.set_font("Helvetica","",sz); pdf.multi_cell(0,6, _sanitize_latin(t))

            add_h1("SME Cybersecurity Self-Assessment")
            add_h2("Initial Summary & Action Plan"); pdf.ln(2)

            for line in md.splitlines():
                if   line.startswith("# "):   add_h1(line[2:])
                elif line.startswith("## "):  add_h2(line[3:])
                elif line.startswith("### "): pdf.set_font("Helvetica","B",12); pdf.multi_cell(0,6,_sanitize_latin(line[4:]))
                elif line.startswith("- "):   pdf.set_font("Helvetica","",12);  pdf.multi_cell(0,6,"- "+_sanitize_latin(line[2:]))
                elif line.strip()=="":        pdf.ln(1)
                else:                         add_p(line)

            out = pdf.output(dest="S")
            if isinstance(out, (bytes, bytearray)):
                pdf_bytes = bytes(out)
            else:
                pdf_bytes = out.encode("latin-1", "ignore")

            st.download_button("📄 Download summary + action plan (PDF)",
                               data=pdf_bytes, file_name="cyber-assessment.pdf",
                               mime="application/pdf")
            return
        except ImportError:
            pass
        except Exception as e:
            st.caption(f"PDF engine fallback (reason: {type(e).__name__})")

        # Fallback: Markdown (always available)
        st.download_button("⬇️ Download summary + action plan (Markdown)",
                           data=md.encode("utf-8"),
                           file_name="cyber-assessment.md",
                           mime="text/markdown")

    export_button()

    cA, cB = st.columns(2)
    with cA:
        if st.button("⬅ Back to Detailed"):
            go("Detailed"); st.rerun()
    with cB:
        if st.button("Start over"):
            for k,v in defaults.items(): st.session_state[k]=v
            go("Landing"); st.rerun()
