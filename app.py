import streamlit as st

# ─────────────────────────────────────────────────────────────
# Page setup & compact styles
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="SME Cybersecurity Self-Assessment", layout="wide")

st.markdown("""
<style>
  .block-container {max-width: 1180px;}
  h1,h2,h3,h4 {margin:.2rem 0 .6rem}
  .hint {color:#6b7280; font-size:.9rem; font-style:italic; margin:.15rem 0 .25rem}
  .pill {display:inline-block;border-radius:999px;padding:.18rem .55rem;border:1px solid #e5e7eb;font-size:.9rem;color:#374151;background:#fff}
  .chip {display:inline-flex;align-items:center;gap:.35rem;border-radius:999px;padding:.18rem .6rem;border:1px solid #e5e7eb;margin-right:.35rem;font-weight:600}
  .green{background:#e8f7ee;color:#0f5132;border-color:#cceedd}
  .amber{background:#fff5d6;color:#8a6d00;border-color:#ffe7ad}
  .red{background:#ffe5e5;color:#842029;border-color:#ffcccc}
  .card {border:1px solid #e6e8ec;border-radius:12px;padding:10px 12px;background:#fff}
  .sticky {position: sticky; top: 10px;}
  div[data-baseweb="radio"] > div {gap:.5rem;}
  .btnrow {margin-top:.4rem}
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
    "<€100k",
    "€100k–€200k","€200k–€300k","€300k–€400k","€400k–€500k",
    "€500k–€600k","€600k–€700k","€700k–€800k","€800k–€900k","€900k–€1M",
    "€1M–€2M","€2M–€5M","€5M–€10M",">€10M"
]

# New options for routing/context
REGION_OPTIONS = ["EU / EEA", "UK", "United States", "Other / Multi-region"]
CRITICAL_SYSTEMS = ["ERP", "PoS", "CRM", "EHR", "CMS", "Other (type below)"]
WORK_ENVIRONMENTS = ["Local servers", "Cloud apps", "Hybrid"]
REMOTE_RATIO = ["Mostly on-site", "Hybrid", "Fully remote"]
DATA_TYPES = ["Customer PII", "Employee data", "Health data", "Financial records"]
CROSS_BORDER = ["EU-only", "Includes Non-EU regions", "Unsure"]
CERTIFICATION_OPTIONS = [
    "None",
    "ISO/IEC 27001",
    "Cyber Essentials (UK)",
    "SOC 2",
    "GDPR compliance program",
    "PCI DSS (Payment Card Industry)",
    "HIPAA (US healthcare)",
    "NIS2 readiness",
    "Other (type below)"
]

# ─────────────────────────────────────────────────────────────
# State
# ─────────────────────────────────────────────────────────────
defaults = dict(
    page="Landing",
    # Step 1 — basics
    person_name="", company_name="",
    sector_label=INDUSTRY_OPTIONS[0], sector_other="",
    years_in_business=YEARS_OPTIONS[0],
    employee_range=EMPLOYEE_RANGES[0],
    turnover_label=TURNOVER_OPTIONS[0],
    work_mode=WORK_MODE[0],
    # Step 1 — new context
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
    # Step 2 — baseline answers (Q1–Q9)
    bp_it_manager="", bp_inventory="", bp_byod="", bp_sensitive="",
    df_website="", df_https="", df_email="", df_social="", df_review="",
    # Tier-2
    detailed_sections=[],
    detailed_scores={},
)
for k,v in defaults.items():
    st.session_state.setdefault(k,v)

# ─────────────────────────────────────────────────────────────
# Helper mappings & functions
# ─────────────────────────────────────────────────────────────
TURNOVER_TO_SIZE = {
    "<€100k":"Micro","€100k–€200k":"Micro","€200k–€300k":"Micro","€300k–€400k":"Micro",
    "€400k–€500k":"Micro","€500k–€600k":"Micro","€600k–€700k":"Micro","€700k–€800k":"Micro",
    "€800k–€900k":"Micro","€900k–€1M":"Micro","€1M–€2M":"Micro",
    "€2M–€5M":"Small","€5M–€10M":"Small",
    ">€10M":"Medium",
}
EMP_RANGE_TO_SIZE = {
    "1–5":"Micro","6–10":"Micro","10–25":"Small","26–50":"Small","51–100":"Medium","More than 100":"Medium"
}
INDUSTRY_TAGS = {
    "Retail & Hospitality": "retail",
    "Professional / Consulting / Legal / Accounting": "professional_services",
    "Manufacturing / Logistics": "manufacturing",
    "Creative / Marketing / IT Services": "it_services",
    "Health / Wellness / Education": "health_edu",
    "Public sector / Non-profit": "public_nonprofit",
    "Other (type below)": "other",
}

def resolved_industry():
    if st.session_state.sector_label == "Other (type below)":
        return st.session_state.sector_other or "Other"
    return st.session_state.sector_label

def org_size():
    a = TURNOVER_TO_SIZE.get(st.session_state.turnover_label, "Micro")
    b = EMP_RANGE_TO_SIZE.get(st.session_state.employee_range, a)
    order = {"Micro":0,"Small":1,"Medium":2}
    return a if order[a] >= order[b] else b

def industry_tag():
    label = resolved_industry()
    return INDUSTRY_TAGS.get(label, "other")

def region_tag():
    r = (st.session_state.get("business_region") or "").lower()
    if "eu" in r or "eea" in r: return "eu"
    if "uk" in r: return "uk"
    if "united states" in r or r == "us" or "america" in r: return "us"
    return "other"

def certification_tags():
    certs = st.session_state.get("certifications", []) or []
    tags = set()
    for c in certs:
        c_low = c.lower()
        if "iso" in c_low: tags.add("cert:iso27001")
        elif "cyber essentials" in c_low: tags.add("cert:ce")
        elif "soc 2" in c_low: tags.add("cert:soc2")
        elif "pci" in c_low: tags.add("cert:pci")
        elif "hipaa" in c_low: tags.add("cert:hipaa")
        elif "nis2" in c_low: tags.add("cert:nis2")
        elif "gdpr" in c_low: tags.add("cert:gdpr")
        elif "none" in c_low: tags.add("cert:none")
        elif "other" in c_low:
            tags.add("cert:other")
    return tags

def compute_tags():
    tags = set()
    # size, industry, region
    tags.add(f"size:{org_size()}")
    tags.add(f"industry:{industry_tag()}")
    tags.add(f"geo:{region_tag()}")
    # infra / work
    env = (st.session_state.get("primary_work_env") or "")
    if env == "Cloud apps": tags.add("infra:cloud")
    elif env == "Local servers": tags.add("infra:onprem")
    else: tags.add("infra:hybrid")
    rr = (st.session_state.get("remote_ratio") or "")
    if rr == "Fully remote": tags.add("work:remote")
    elif rr == "Hybrid": tags.add("work:hybrid")
    else: tags.add("work:onsite")
    # systems
    for s in st.session_state.get("critical_systems", []) or []:
        key = s.split()[0].lower()
        if key in {"erp","pos","crm","ehr","cms"}:
            tags.add(f"system:{key}")
        elif "other" in key:
            tags.add("system:other")
    # data types
    for d in st.session_state.get("data_types", []) or []:
        dl = d.lower()
        if "customer" in dl: tags.add("data:pii")
        if "employee" in dl: tags.add("data:employee")
        if "health" in dl: tags.add("data:health")
        if "financial" in dl: tags.add("data:financial")
    # cross-border
    cb = st.session_state.get("cross_border") or ""
    if cb == "EU-only": tags.add("geo:eu_only")
    elif cb == "Unsure": tags.add("geo:unsure")
    else: tags.add("geo:crossborder")
    # sensitivity & cards
    if (st.session_state.get("bp_sensitive") or "").lower() == "yes":
        tags.add("data:sensitive")
    if (st.session_state.get("bp_card_payments") or "").lower() == "yes":
        tags.add("payments:card")
    # certifications
    tags |= certification_tags()
    return tags

# Baseline RAG from Q1–Q9
def area_rag():
    inv = (st.session_state.bp_inventory or "").lower()
    if inv == "yes":    sys = ("🟢 Good","green")
    elif inv == "partially": sys=("🟡 Partial","amber")
    elif inv in {"no","not sure"}: sys=("🔴 At risk","red")
    else:               sys=("⚪ Unknown","")

    byod  = (st.session_state.bp_byod or "").lower()
    email = (st.session_state.df_email or "").lower()
    if byod=="no" and email=="yes": ppl=("🟢 Safe","green")
    elif email=="no":               ppl=("🔴 At risk","red")
    elif byod in {"yes","sometimes"} or email=="partially":
        ppl=("🟡 Mixed","amber")
    else:                           ppl=("⚪ Unknown","")

    web=(st.session_state.df_website or "").lower()
    https=(st.session_state.df_https or "").lower()
    if web=="yes" and https=="yes":  net=("🟢 Protected","green")
    elif web=="yes" and https=="no": net=("🔴 Exposed","red")
    elif web=="yes" and https=="not sure": net=("🟡 Check","amber")
    elif web=="no":                 net=("🟢 Low","green")
    else:                           net=("⚪ Unknown","")
    return sys, ppl, net

def overall_badge():
    sys,ppl,net = area_rag()
    score = sum({"green":0,"amber":1,"red":2}.get(x[1],1) for x in [sys,ppl,net])
    if score <= 1: return ("Low","green","Great job — strong digital hygiene.")
    if score <= 3: return ("Medium","amber","Balanced setup. A few quick wins will reduce risk fast.")
    return ("High","red","Higher exposure — prioritise quick actions to lower risk.")

def go(page):
    st.session_state.page = page
    st.rerun()

# ─────────────────────────────────────────────────────────────
# Section registry (Tier-2 sections 3–8)
# ─────────────────────────────────────────────────────────────
SECTION_3 = {
    "id":"Access & Identity",
    "title":"🔐 Access & Identity Management",
    "purpose":"Control of user access and authentication.",
    "questions":[
        {"id":"ai_pw","text":"Are strong passwords required for all accounts?","hint":"≥10–12 chars; mix letters/numbers/symbols."},
        {"id":"ai_mfa","text":"Is Multi-Factor Authentication (MFA) enabled for key accounts?","hint":"Password + extra step (app/token)."},
        {"id":"ai_admin","text":"Are admin rights limited to only those who need them?","hint":"Restrict & monitor privileged roles."},
        {"id":"ai_shared","text":"Are shared accounts avoided or controlled?","hint":"Avoid everyone using 'admin@'."},
        {"id":"ai_leavers","text":"Are old or unused accounts removed promptly?","hint":"Employees leaving; contractors end."},
    ]
}
SECTION_4 = {
    "id":"Device & Data",
    "title":"💻 Device & Data Protection",
    "purpose":"How well devices and company data are secured.",
    "questions":[
        {"id":"dd_lock","text":"Are all devices protected with a password or PIN?","hint":"Prevents access if lost/stolen."},
        {"id":"dd_fde","text":"Is full-disk encryption enabled on laptops and mobiles?","hint":"Keeps data safe if stolen."},
        {"id":"dd_edr","text":"Is reputable AV/EDR installed and active on all devices?","hint":"Defender, CrowdStrike, SentinelOne."},
        {"id":"dd_backup","text":"Are important business files backed up regularly?","hint":"Automated or cloud/offsite."},
        {"id":"dd_restore","text":"Are backups tested to ensure restore works?","hint":"Practice restore occasionally."},
        {"id":"dd_usb","text":"Are staff trained to handle suspicious files/USBs?","hint":"Unknown USBs, strange attachments."},
        {"id":"dd_wifi","text":"Are company devices separated from personal on Wi-Fi?","hint":"Guest vs corporate network."},
    ]
}
SECTION_5 = {
    "id":"System & Software Updates",
    "title":"🧩 System & Software Updates",
    "purpose":"Keeping systems patched and supported.",
    "questions":[
        {"id":"su_os_auto","text":"Are operating systems kept up to date automatically?","hint":"Enable security patches."},
        {"id":"su_apps","text":"Are business applications updated regularly?","hint":"Browsers, CRM, accounting, etc."},
        {"id":"su_unsupported","text":"Any devices running unsupported/outdated systems?","hint":"e.g., Win7, old Android."},
        {"id":"su_review","text":"Is there a monthly process/reminder to review updates?","hint":"Alerts or MSP checks."},
    ]
}
SECTION_6 = {
    "id":"Incident Preparedness",
    "title":"🚨 Incident Preparedness",
    "purpose":"Readiness to detect, respond, and recover.",
    "questions":[
        {"id":"ip_report","text":"Do employees know how to report incidents?","hint":"Phishing, data loss, suspicious activity."},
        {"id":"ip_plan","text":"Do you have a simple incident response plan?","hint":"Even a short checklist helps."},
        {"id":"ip_log","text":"Are incident details documented when they occur?","hint":"What happened, when, impact."},
        {"id":"ip_contacts","text":"Are key staff aware of emergency contacts?","hint":"Internal IT, MSP, specialist."},
        {"id":"ip_test","text":"Have you tested/simulated handling a cyber incident?","hint":"Quick tabletop exercise."},
    ]
}
SECTION_7 = {
    "id":"Vendor & Cloud",
    "title":"☁️ Vendor & Cloud Security",
    "purpose":"Security of third-party tools, vendors, and online services.",
    "questions":[
        {"id":"vc_cloud","text":"Do you use cloud tools to store company data?","hint":"M365, Google Drive, Dropbox."},
        {"id":"vc_mfa","text":"Are those cloud services protected with MFA & strong passwords?","hint":"Prevent unauthorised access."},
        {"id":"vc_review","text":"Do you review how vendors protect your data?","hint":"DPAs, security terms."},
        {"id":"vc_access","text":"Do you track which suppliers have access to systems/data?","hint":"Maintain an access list."},
        {"id":"vc_notify","text":"If a vendor suffers an incident, will you be informed promptly?","hint":"Breach notification clauses."},
    ]
}
SECTION_8 = {
    "id":"Awareness & Training",
    "title":"🧠 Awareness & Training",
    "purpose":"Cybersecurity culture and user awareness.",
    "questions":[
        {"id":"at_training","text":"Have employees received cybersecurity awareness training?","hint":"Short online sessions count."},
        {"id":"at_phish","text":"Do staff know how to identify phishing/scam emails?","hint":"Links, sender, errors."},
        {"id":"at_onboard","text":"Are new employees briefed on cybersecurity at onboarding?","hint":"Consistency from day one."},
        {"id":"at_reminders","text":"Do you share posters, reminders, or tips?","hint":"Newsletter or checklist."},
        {"id":"at_lead","text":"Does management regularly promote cybersecurity?","hint":"Leadership buy-in matters."},
    ]
}
ALL_SECTIONS = [SECTION_3, SECTION_4, SECTION_5, SECTION_6, SECTION_7, SECTION_8]
BASELINE_IDS = {"Access & Identity","Device & Data","System & Software Updates","Awareness & Training"}

def render_section(section):
    st.markdown(f"### {section['title']}")
    st.caption(section["purpose"])
    for q in section["questions"]:
        st.radio(
            q["text"],
            ["Yes","Partially","No","Not sure"],
            key=q["id"],
            horizontal=True,
            label_visibility="visible",
            help=q["hint"]
        )
    st.markdown("")

def section_score(section):
    vals = [st.session_state.get(q["id"], "") for q in section["questions"]]
    risk = {"Yes":0,"Partially":1,"Not sure":1,"No":2}
    score = sum(risk.get(v,1) for v in vals)
    return round(score/len(vals), 2) if vals else 0.0

def pick_active_sections(tags:set):
    active = set()
    active |= BASELINE_IDS  # always on
    if "size:Small" in tags or "size:Medium" in tags:
        active.add("Incident Preparedness")
    if any(t in tags for t in ["infra:cloud","system:pos","geo:crossborder"]):
        active.add("Vendor & Cloud")
    order = [s["id"] for s in ALL_SECTIONS]
    return [sid for sid in order if sid in active]

def applicable_compliance(tags:set):
    hints = []
    if any(t in tags for t in ["geo:eu","geo:uk"]) or "data:pii" in tags or "data:employee" in tags:
        hints.append(("GDPR","Regulation (EU/UK)","Likely applicable if you process EU/UK personal data. Review DPAs and cross-border transfers."))
    if "payments:card" in tags or "system:pos" in tags or "data:financial" in tags:
        hints.append(("PCI DSS","Industry Standard","If you store/process/transmit card data. PSP-managed PoS may reduce scope."))
    if "data:health" in tags:
        hints.append(("HIPAA","US Regulation","Applies to US covered entities/business associates. Treat as conditional if outside US."))
    if "cert:iso27001" in tags or org_size() in {"Small","Medium"}:
        hints.append(("ISO/IEC 27001","Standard","Useful maturity target and customer trust signal."))
    if "cert:nis2" in tags or industry_tag() in {"manufacturing","it_services","public_nonprofit"}:
        hints.append(("NIS2","EU Directive","Sector & size dependent; check local transposition and scoping."))
    return hints

# ─────────────────────────────────────────────────────────────
# LANDING
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Landing":
    st.markdown("### SME Cybersecurity Self-Assessment")
    st.markdown("**Assess · Understand · Act — in under 15 minutes.**")
    st.write(
        "A plain-language self-assessment that shows your exposure and the **top actions** to take next. "
        "Lightweight but traceable to recognised standards (NIST CSF 2.0; ISO/IEC 27001:2022)."
    )
    st.markdown("#### Why this works")
    left, right = st.columns(2)
    with left:
        st.write("• Plain-language questions")
        st.write("• Traceable to NIST/ISO")
    with right:
        st.write("• Lightweight, 10–15 minutes")
        st.write("• Safe demos of common scams")
    if st.button("Start ➜", type="primary"):
        go("Step 1")

# ─────────────────────────────────────────────────────────────
# STEP 1 — Business profile + Operational context
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 1":
    st.markdown("##### Step 1 of 3")
    st.markdown("## Tell us about the business")
    st.caption("Just the basics (~2 minutes).")

    snap, form = st.columns([1, 2], gap="large")

    with snap:
        st.markdown('<div class="sticky">', unsafe_allow_html=True)
        st.markdown("#### Snapshot")
        st.markdown(
            f'<div class="card">'
            f'<div><b>Business:</b> {st.session_state.company_name or "—"}</div>'
            f'<div><b>Region:</b> {st.session_state.business_region}</div>'
            f'<div><b>Industry:</b> {resolved_industry()}</div>'
            f'<div><b>People:</b> {st.session_state.employee_range} · '
            f'<b>Years:</b> {st.session_state.years_in_business}</div>'
            f'<div><b>Turnover:</b> {st.session_state.turnover_label}</div>'
            f'<div><b>Work mode:</b> {st.session_state.work_mode}</div>'
            f'<div><b>Size (derived):</b> {org_size()}</div>'
            f'</div>', unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with form:
        st.markdown("#### About you")
        st.session_state.person_name = st.text_input("👤 Your name *", value=st.session_state.person_name)

        st.markdown("#### About the business")
        st.session_state.company_name = st.text_input("🏢 Business name *", value=st.session_state.company_name)

        c1, c2 = st.columns(2)
        with c1:
            st.session_state.business_region = st.selectbox(
                "🌍 Business location / region *",
                REGION_OPTIONS,
                index=REGION_OPTIONS.index(st.session_state.business_region)
            )
            st.session_state.sector_label = st.selectbox("🏷️ Industry / service *",
                INDUSTRY_OPTIONS,
                index=INDUSTRY_OPTIONS.index(st.session_state.sector_label)
                if st.session_state.sector_label in INDUSTRY_OPTIONS else 0)
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
                TURNOVER_OPTIONS,
                index=TURNOVER_OPTIONS.index(st.session_state.turnover_label))
        st.session_state.work_mode = st.radio("🧭 Work mode *",
            WORK_MODE, horizontal=True, index=WORK_MODE.index(st.session_state.work_mode))

        st.markdown("#### Operational context (optional but recommended)")
        cA, cB = st.columns(2)
        with cA:
            st.session_state.critical_systems = st.multiselect(
                "🧩 Critical systems in use",
                CRITICAL_SYSTEMS,
                default=st.session_state.critical_systems
            )
            if "Other (type below)" in st.session_state.critical_systems:
                st.session_state.critical_systems_other = st.text_input(
                    "✍️ Specify other system",
                    value=st.session_state.critical_systems_other
                )
            st.session_state.primary_work_env = st.radio(
                "🏗️ Primary work environment",
                WORK_ENVIRONMENTS,
                horizontal=True,
                index=WORK_ENVIRONMENTS.index(st.session_state.primary_work_env)
            )
            st.session_state.remote_ratio = st.radio(
                "🏠 Remote work ratio",
                REMOTE_RATIO,
                horizontal=True,
                index=REMOTE_RATIO.index(st.session_state.remote_ratio)
            )
        with cB:
            st.session_state.data_types = st.multiselect(
                "🔎 Types of personal data handled",
                DATA_TYPES,
                default=st.session_state.data_types
            )
            st.session_state.cross_border = st.radio(
                "🌐 Cross-border data flows",
                CROSS_BORDER,
                horizontal=True,
                index=CROSS_BORDER.index(st.session_state.cross_border)
            )
            st.session_state.certifications = st.multiselect(
                "🔒 Certifications / schemes",
                CERTIFICATION_OPTIONS,
                default=st.session_state.certifications
            )
            if "Other (type below)" in st.session_state.certifications:
                st.session_state.certifications_other = st.text_input(
                    "✍️ Specify other scheme",
                    value=st.session_state.certifications_other
                )
        # PCI quick flag
        st.session_state.bp_card_payments = st.radio(
            "💳 Do you accept or process card payments (online or in-store)?",
            ["Yes","No","Not sure"],
            horizontal=True,
            index=(["Yes","No","Not sure"].index(st.session_state.bp_card_payments)
                   if st.session_state.bp_card_payments else 1)
        )

        # Required gate
        missing = []
        if not st.session_state.person_name.strip(): missing.append("name")
        if not st.session_state.company_name.strip(): missing.append("company")
        if st.session_state.sector_label == "Other (type below)" and not st.session_state.sector_other.strip():
            missing.append("industry")
        if not st.session_state.business_region: missing.append("region")

        st.markdown('<div class="btnrow">', unsafe_allow_html=True)
        cA, cB = st.columns([1,1])
        with cA:
            if st.button("⬅ Back"):
                go("Landing")
        with cB:
            disabled = len(missing) > 0
            if st.button("Continue ➜", type="primary", disabled=disabled):
                go("Step 2")
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# STEP 2 — Baseline quick checks (Q1–Q9)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 2":
    st.markdown("##### Step 2 of 3")
    st.markdown("## Your cyber practices")
    st.caption("Answer the 9 quick checks. No trick questions.")

    snap, body, prev = st.columns([1, 1.6, 1], gap="large")

    with snap:
        st.markdown('<div class="sticky">', unsafe_allow_html=True)
        st.markdown("#### Snapshot")
        st.markdown(
            f'<div class="card">'
            f'<div><b>Business:</b> {st.session_state.company_name}</div>'
            f'<div><b>Region:</b> {st.session_state.business_region}</div>'
            f'<div><b>Industry:</b> {resolved_industry()}</div>'
            f'<div><b>People:</b> {st.session_state.employee_range} · '
            f'<b>Years:</b> {st.session_state.years_in_business}</div>'
            f'<div><b>Turnover:</b> {st.session_state.turnover_label} · '
            f'<b>Size:</b> {org_size()}</div>'
            f'<div><b>Work mode:</b> {st.session_state.work_mode}</div>'
            f'</div>', unsafe_allow_html=True
        )
        sys,ppl,net = area_rag()
        st.markdown("#### At-a-glance")
        st.markdown(f'<span class="chip {sys[1]}">🖥️ Systems · {sys[0]}</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="chip {ppl[1]}">👥 People · {ppl[0]}</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="chip {net[1]}">🌐 Exposure · {net[0]}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with body:
        tab1, tab2 = st.tabs(["🧭 Business profile (Q1–Q4)", "🌐 Digital footprint (Q5–Q9)"])

        with tab1:
            st.markdown("**Q1. 🖥️ Who looks after your IT day-to-day?**")
            st.markdown('<div class="hint">We mean laptops/phones, Wi-Fi, email, website, point-of-sale, cloud apps, file storage/backup.</div>', unsafe_allow_html=True)
            st.radio(" ", ["Self-managed","Outsourced IT","Shared responsibility","Not sure"],
                     key="bp_it_manager", horizontal=True, label_visibility="collapsed")

            st.markdown("**Q2. 📋 Do you keep a simple list of company devices (laptops, phones, servers)?**")
            st.markdown('<div class="hint">Helps find forgotten or unmanaged gear.</div>', unsafe_allow_html=True)
            st.radio(" ", ["Yes","Partially","No","Not sure"], key="bp_inventory",
                     horizontal=True, label_visibility="collapsed")

            st.markdown("**Q3. 📱 Do people use personal devices for work (BYOD)?**")
            st.markdown('<div class="hint">Example: staff reading work email on a personal phone or laptop.</div>', unsafe_allow_html=True)
            st.radio(" ", ["Yes","Sometimes","No","Not sure"], key="bp_byod",
                     horizontal=True, label_visibility="collapsed")

            st.markdown("**Q4. 🔐 Do you handle sensitive customer or financial data?**")
            st.markdown('<div class="hint">E.g., payment details, personal records, contracts.</div>', unsafe_allow_html=True)
            st.radio(" ", ["Yes","No","Not sure"], key="bp_sensitive",
                     horizontal=True, label_visibility="collapsed")

        with tab2:
            st.markdown("**Q5. 🕸️ Do you have a public website?**")
            st.markdown('<div class="hint">Helps assess potential online entry points.</div>', unsafe_allow_html=True)
            st.radio(" ", ["Yes","No"], key="df_website", horizontal=True, label_visibility="collapsed")

            st.markdown("**Q6. 🔒 Is your website HTTPS (padlock in the browser)?**")
            st.markdown('<div class="hint">Encrypts traffic and builds trust with visitors.</div>', unsafe_allow_html=True)
            st.radio(" ", ["Yes","No","Not sure"], key="df_https", horizontal=True, label_visibility="collapsed")

            st.markdown("**Q7. ✉️ Do you use business email addresses (e.g., info@yourcompany.com)?**")
            st.markdown('<div class="hint">Personal Gmail/Yahoo accounts increase phishing risk.</div>', unsafe_allow_html=True)
            st.radio(" ", ["Yes","Partially","No"], key="df_email", horizontal=True, label_visibility="collapsed")

            st.markdown("**Q8. 📣 Is your business active on social media (LinkedIn, Instagram, etc.)?**")
            st.radio(" ", ["Yes","No"], key="df_social", horizontal=True, label_visibility="collapsed")

            st.markdown("**Q9. 🔎 Do you regularly check what’s public about the company or staff online?**")
            st.markdown('<div class="hint">E.g., contact details, staff lists, screenshots that reveal systems.</div>', unsafe_allow_html=True)
            st.radio(" ", ["Yes","Sometimes","No"], key="df_review", horizontal=True, label_visibility="collapsed")

    with prev:
        st.write(""); st.write("")
        if st.button("⬅ Back to Step 1"):
            go("Step 1")
        required = ["bp_it_manager","bp_inventory","bp_byod","bp_sensitive","df_website","df_https","df_email","df_social","df_review"]
        missing = [k for k in required if not st.session_state.get(k)]
        disabled = len(missing) > 0
        if st.button("Finish Initial Assessment ➜", type="primary", disabled=disabled):
            go("Step 3")

# ─────────────────────────────────────────────────────────────
# STEP 3 — Summary
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 3":
    st.markdown("## Initial Assessment Summary")

    over_txt, over_class, over_msg = overall_badge()
    st.markdown(
        f'<span class="pill {over_class}">Overall digital dependency: <b>{over_txt}</b></span>',
        unsafe_allow_html=True,
    )
    st.caption(over_msg)

    snap, glance = st.columns([1.1, 1.9], gap="large")
    with snap:
        st.markdown("### Snapshot")
        st.markdown(
            f'<div class="card">'
            f'<div><b>Business:</b> {st.session_state.company_name}</div>'
            f'<div><b>Region:</b> {st.session_state.business_region}</div>'
            f'<div><b>Industry:</b> {resolved_industry()}</div>'
            f'<div><b>People:</b> {st.session_state.employee_range} · '
            f'<b>Years:</b> {st.session_state.years_in_business} · '
            f'<b>Turnover:</b> {st.session_state.turnover_label}</div>'
            f'<div><b>Work mode:</b> {st.session_state.work_mode} · '
            f'<b>Size:</b> {org_size()}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with glance:
        st.markdown("### At-a-glance")
        sys, ppl, net = area_rag()
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown('<div class="card"><div style="font-weight:600;display:flex;gap:.4rem;align-items:center">🖥️ Systems & devices</div>'
                        f'<div style="margin-top:.35rem">{sys[0]}</div></div>', unsafe_allow_html=True)
        with g2:
            st.markdown('<div class="card"><div style="font-weight:600;display:flex;gap:.4rem;align-items:center">👥 People & access</div>'
                        f'<div style="margin-top:.35rem">{ppl[0]}</div></div>', unsafe_allow_html=True)
        with g3:
            st.markdown('<div class="card"><div style="font-weight:600;display:flex;gap:.4rem;align-items:center">🌐 Online exposure</div>'
                        f'<div style="margin-top:.35rem">{net[0]}</div></div>', unsafe_allow_html=True)

        hints = []
        if st.session_state.bp_inventory not in ("Yes", "Partially"):
            hints.append("📝 Finish your device list.")
        hints.append("👥 Add MFA & BYOD rules.")
        if st.session_state.df_website == "Yes":
            if st.session_state.df_https == "Yes":
                hints.append("🔒 Site uses HTTPS.")
            else:
                hints.append("🔒 Add HTTPS to your website.")
        st.caption(" · ".join(hints))

    st.markdown("---")

    colS, colR = st.columns(2, gap="large")
    with colS:
        st.markdown("### Strengths")
        strengths = []
        if st.session_state.df_https == "Yes":
            strengths.append("Website uses HTTPS (encrypted traffic).")
        if st.session_state.bp_inventory in ("Yes", "Partially"):
            strengths.append("You keep a device list (even partial helps).")
        if not strengths:
            strengths.append("Solid starting point across core practices.")
        st.markdown('<div class="card"><ul style="margin:.25rem 1rem">'+ "".join([f"<li>{x}</li>" for x in strengths]) + "</ul></div>", unsafe_allow_html=True)

    with colR:
        st.markdown("### Areas to improve")
        risks = []
        if st.session_state.df_email == "No":
            risks.append("Personal email in use — move to business email to cut phishing risk.")
        if st.session_state.bp_byod in ("Yes", "Sometimes"):
            risks.append("BYOD needs clear rules, MFA and basic hardening.")
        if st.session_state.bp_sensitive == "Yes":
            risks.append("Sensitive data calls for regular backups and strong access control (MFA).")
        if st.session_state.df_website == "Yes" and st.session_state.df_https != "Yes":
            risks.append("Add HTTPS to your website (padlock) to encrypt traffic and build trust.")
        if not risks:
            risks.append("Keep improving: test incident response and tighten MFA hygiene.")
        st.markdown('<div class="card"><ul style="margin:.25rem 1rem">'+ "".join([f"<li>{x}</li>" for x in risks]) + "</ul></div>", unsafe_allow_html=True)

    st.markdown("")
    with st.expander("Business details"):
        st.write({
            "Business": st.session_state.company_name,
            "Region": st.session_state.business_region,
            "Industry": resolved_industry(),
            "People (incl. contractors)": st.session_state.employee_range,
            "Years in business": st.session_state.years_in_business,
            "Turnover": st.session_state.turnover_label,
            "Work mode": st.session_state.work_mode,
            "Derived size": org_size(),
        })
    with st.expander("Operational context"):
        st.write({
            "Critical systems": st.session_state.critical_systems,
            "Primary environment": st.session_state.primary_work_env,
            "Remote ratio": st.session_state.remote_ratio,
            "Data types": st.session_state.data_types,
            "Cross-border flows": st.session_state.cross_border,
            "Certifications": st.session_state.certifications,
            "Card payments": st.session_state.bp_card_payments or "—",
        })
    with st.expander("See all baseline answers (Q1–Q9)"):
        st.write({
            "Q1 IT oversight": st.session_state.bp_it_manager or "—",
            "Q2 Device inventory": st.session_state.bp_inventory or "—",
            "Q3 BYOD": st.session_state.bp_byod or "—",
            "Q4 Sensitive data": st.session_state.bp_sensitive or "—",
            "Q5 Website": st.session_state.df_website or "—",
            "Q6 HTTPS": st.session_state.df_https or "—",
            "Q7 Business email": st.session_state.df_email or "—",
            "Q8 Social presence": st.session_state.df_social or "—",
            "Q9 Public info checks": st.session_state.df_review or "—",
        })

    st.markdown("---")
    st.markdown("### Likely compliance & standards to consider")
    tags = compute_tags()
    for name, level, note in applicable_compliance(tags):
        st.markdown(
            f'<div class="card" style="margin-bottom:.5rem">'
            f'<div style="font-weight:600">{name} <span class="pill amber" style="margin-left:.4rem">{level}</span></div>'
            f'<div style="font-size:.95rem;margin-top:.25rem">{note}</div>'
            f'</div>', unsafe_allow_html=True
        )

    st.markdown("")
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button("⬅ Back"):
            st.session_state.page = "Step 2"; st.rerun()
    with c2:
        if st.button("Start over"):
            for k, v in defaults.items():
                st.session_state[k] = v
            st.session_state.page = "Landing"; st.rerun()
    with c3:
        if st.button("Continue to detailed assessment ➜", type="primary"):
            st.session_state.detailed_sections = pick_active_sections(tags)
            st.session_state.page = "Detailed"; st.rerun()

# ─────────────────────────────────────────────────────────────
# TIER-2 — Detailed Assessment (adaptive)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Detailed":
    st.markdown("##### Step 3 of 3")
    st.markdown("## Detailed Assessment")

    active_ids = set(st.session_state.get("detailed_sections", []))
    sections_to_show = [s for s in ALL_SECTIONS if s["id"] in active_ids]

    if not sections_to_show:
        st.info("No additional sections selected. You can return to the summary.")
    else:
        tabs = st.tabs([s["title"] for s in sections_to_show])
        for tab, section in zip(tabs, sections_to_show):
            with tab:
                render_section(section)

    st.markdown("")
    c1, c2 = st.columns([1,2])
    with c1:
        if st.button("⬅ Back to Summary"):
            st.session_state.page = "Step 3"; st.rerun()
    with c2:
        if st.button("Finish & see recommendations ➜", type="primary"):
            scores = {s["id"]: section_score(s) for s in sections_to_show}
            st.session_state["detailed_scores"] = scores
            st.session_state.page = "Report"; st.rerun()

# ─────────────────────────────────────────────────────────────
# Final Report
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Report":
    st.markdown("## Recommendations & Section Scores")
    scores = st.session_state.get("detailed_scores", {})
    if scores:
        cols = st.columns(len(scores))
        for (sid, sc), col in zip(scores.items(), cols):
            level = "green" if sc < 0.5 else "amber" if sc < 1.2 else "red"
            label = "Low" if level=="green" else "Medium" if level=="amber" else "High"
            with col:
                st.markdown(
                    f'<div class="card"><div style="font-weight:600">{sid}</div>'
                    f'<div style="margin-top:.25rem"><span class="pill {level}">Risk: <b>{label}</b> (score {sc})</span></div></div>',
                    unsafe_allow_html=True
                )
    else:
        st.caption("No detailed scores yet. Complete the detailed assessment to see section scores.")

    st.markdown("---")
    st.markdown("### Top actions to consider")
    actions = []
    if (st.session_state.df_website == "Yes") and (st.session_state.df_https != "Yes"):
        actions.append("Enable HTTPS and force redirect from HTTP to HTTPS.")
    if st.session_state.df_email in ("No","Partially"):
        actions.append("Move all users to business email (e.g., M365/Google Workspace) and enforce MFA.")
    if st.session_state.bp_inventory not in ("Yes","Partially"):
        actions.append("Create a simple device inventory and enable full-disk encryption on laptops.")
    if (st.session_state.bp_byod in ("Yes","Sometimes")):
        actions.append("Define a BYOD policy: screen lock, OS updates, encryption, MFA for email/apps.")
    t = compute_tags()
    if any(x in t for x in ["infra:cloud","system:pos","geo:crossborder"]):
        actions.append("Review vendor/cloud contracts: breach notification, MFA on admin, and access logs.")
    if not actions:
        actions.append("Test incident response with a short tabletop exercise and tighten MFA hygiene.")
    st.markdown('<div class="card"><ul style="margin:.25rem 1rem">'+ "".join([f"<li>{x}</li>" for x in actions[:5]]) + "</ul></div>", unsafe_allow_html=True)

    st.markdown("")
    c1, c2 = st.columns([1,1])
    with c1:
        if st.button("⬅ Back to Detailed"):
            st.session_state.page = "Detailed"; st.rerun()
    with c2:
        if st.button("Start over"):
            for k, v in defaults.items(): st.session_state[k] = v
            st.session_state.page = "Landing"; st.rerun()
