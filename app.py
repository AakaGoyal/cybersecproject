import streamlit as st

# ─────────────────────────────────────────────────────────────
# Page setup & styles (added safer top padding)
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="SME Cybersecurity Self-Assessment", layout="wide")

st.markdown("""
<style>
  .block-container {max-width: 1160px; padding-top: 2.25rem !important;}
  .main > div:first-child {padding-top: 2.25rem !important;}
  h1,h2,h3,h4 {margin:.2rem 0 .5rem}
  .lead {color:#4b5563; margin:.25rem 0 .75rem}
  .hint {color:#6b7280; font-size:.95rem; margin:.15rem 0 .55rem}
  .pill {display:inline-block;border-radius:999px;padding:.18rem .55rem;border:1px solid #e5e7eb;font-size:.9rem;color:#374151;background:#fff}
  .chip {display:inline-flex;align-items:center;gap:.35rem;border-radius:999px;padding:.18rem .6rem;border:1px solid #e5e7eb;margin-right:.35rem;font-weight:600}
  .green{background:#e8f7ee;color:#0f5132;border-color:#cceedd}
  .amber{background:#fff5d6;color:#8a6d00;border-color:#ffe7ad}
  .red{background:#ffe5e5;color:#842029;border-color:#ffcccc}
  .card {border:1px solid #e6e8ec;border-radius:12px;padding:12px;background:#fff}
  .sticky {position: sticky; top: 12px;}
  div[data-baseweb="radio"] > div {gap:.5rem;}
  .btnrow {margin-top:.4rem}
  .tight {margin-top:.25rem}
  .kicker {font-size:.95rem;color:#6b7280;margin-bottom:.35rem}
  .tag {font-size:.75rem;border-radius:8px;padding:.08rem .4rem;border:1px solid #e5e7eb;margin-left:.25rem}
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
DATA_TYPES = ["Customer personal data (PII)", "Employee/staff data", "Health/medical data", "Financial/transaction data"]
CROSS_BORDER = ["EU-only", "Includes Non-EU regions", "Unsure"]
CERTIFICATION_OPTIONS = [
    "None","ISO/IEC 27001","Cyber Essentials (UK)","SOC 2",
    "GDPR compliance program","PCI DSS (Payment Cards)","HIPAA (US healthcare)",
    "NIS2 readiness","Other (type below)"
]

DATA_TYPE_HELP = {
    "Customer personal data (PII)": "Names, emails, phone numbers, addresses, IDs, online identifiers.",
    "Employee/staff data": "HR info like contracts, payroll, performance, IDs, contact details.",
    "Health/medical data": "Any health info or patient records (diagnosis, treatment, insurance).",
    "Financial/transaction data": "Invoices, bank details, card tokens, PoS records, refunds."
}

SECTION_INTRO = {
    "Access & Identity":
        "🔑 **What this covers:** who can access what, and how safely (passwords, MFA, admin rights, removing ex-staff).  \n🧭 **Why it matters:** most breaches start with weak or reused passwords.",
    "Device & Data":
        "💻 **What this covers:** laptops/phones protection, disk encryption, antivirus/EDR, backups and restores.  \n🧭 **Why it matters:** lost or stolen devices shouldn’t expose your data.",
    "System & Software Updates":
        "🧩 **What this covers:** OS & app updates, and avoiding unsupported systems.  \n🧭 **Why it matters:** patches close known holes attackers scan for.",
    "Incident Preparedness":
        "🚨 **What this covers:** reporting, a simple response plan, key contacts, and quick practice.  \n🧭 **Why it matters:** clear steps limit damage and downtime.",
    "Vendor & Cloud":
        "☁️ **What this covers:** MFA on cloud tools, contracts, who has access, and breach notification.  \n🧭 **Why it matters:** third-parties are part of your security.",
    "Awareness & Training":
        "🧠 **What this covers:** basic training, phishing know-how, onboarding, reminders, leadership support.  \n🧭 **Why it matters:** people stop the majority of attacks.",
}

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
    # Operating context (in Step 2)
    critical_systems=[], critical_systems_other="",
    primary_work_env=WORK_ENVIRONMENTS[1],
    remote_ratio=REMOTE_RATIO[1],
    data_types=[], cross_border=CROSS_BORDER[0],
    certifications=["None"], certifications_other="",
    bp_card_payments="",
    # Baseline answers (Q1–Q9)
    bp_it_manager="", bp_inventory="", bp_byod="", bp_sensitive="",
    df_website="", df_https="", df_email="", df_social="", df_review="",
    # Tier 2
    detailed_sections=[], detailed_scores={},
)
for k,v in defaults.items():
    st.session_state.setdefault(k,v)

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
TURNOVER_TO_SIZE = {**{k:"Micro" for k in TURNOVER_OPTIONS[:11]}, **{"€2M–€5M":"Small","€5M–€10M":"Small",">€10M":"Medium"}}
EMP_RANGE_TO_SIZE = {"1–5":"Micro","6–10":"Micro","10–25":"Small","26–50":"Small","51–100":"Medium","More than 100":"Medium"}
INDUSTRY_TAGS = {
    "Retail & Hospitality":"retail","Professional / Consulting / Legal / Accounting":"professional_services",
    "Manufacturing / Logistics":"manufacturing","Creative / Marketing / IT Services":"it_services",
    "Health / Wellness / Education":"health_edu","Public sector / Non-profit":"public_nonprofit",
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
        c=c.lower()
        if "iso" in c: tags.add("cert:iso27001")
        elif "cyber essentials" in c: tags.add("cert:ce")
        elif "soc 2" in c: tags.add("cert:soc2")
        elif "pci" in c: tags.add("cert:pci")
        elif "hipaa" in c: tags.add("cert:hipaa")
        elif "nis2" in c: tags.add("cert:nis2")
        elif "gdpr" in c: tags.add("cert:gdpr")
        elif "none" in c: tags.add("cert:none")
        elif "other" in c: tags.add("cert:other")
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

def go(page): st.session_state.page=page; st.rerun()

# ─────────────────────────────────────────────────────────────
# Sections (Tier-2)
# ─────────────────────────────────────────────────────────────
def section(title_id, qlist):
    return {"id":title_id, "title":title_id, "questions":qlist}

SECTION_3 = section("Access & Identity", [
    {"id":"ai_pw","t":"Are strong passwords required for all accounts?","h":"Use at least 10–12 characters and avoid reuse."},
    {"id":"ai_mfa","t":"Is Multi-Factor Authentication (MFA) enabled for key accounts?","h":"Password + second step (app/token)."},
    {"id":"ai_admin","t":"Are admin rights limited to only those who need them?","h":"Restrict and monitor privileged roles."},
    {"id":"ai_shared","t":"Are shared accounts avoided or controlled?","h":"Avoid generic 'admin@' logins; use named accounts."},
    {"id":"ai_leavers","t":"Are old or unused accounts removed promptly?","h":"Remove access for leavers and contractors quickly."},
])
SECTION_4 = section("Device & Data", [
    {"id":"dd_lock","t":"Are all laptops/phones protected with a password or PIN?","h":"Prevents access if lost or stolen."},
    {"id":"dd_fde","t":"Is full-disk encryption enabled on laptops and mobiles?","h":"Keeps data safe even if a device is stolen."},
    {"id":"dd_edr","t":"Is reputable antivirus/EDR installed and active on all devices?","h":"Examples: Microsoft Defender, CrowdStrike."},
    {"id":"dd_backup","t":"Are important business files backed up regularly?","h":"Use automated cloud or offsite backups."},
    {"id":"dd_restore","t":"Are backups tested so you know restore works?","h":"Practice restoring occasionally."},
    {"id":"dd_usb","t":"Are staff trained to handle suspicious files/USBs?","h":"Don’t plug unknown USBs; be wary of attachments."},
    {"id":"dd_wifi","t":"Are company devices separated from personal ones on Wi-Fi?","h":"Use guest and corporate networks."},
])
SECTION_5 = section("System & Software Updates", [
    {"id":"su_os_auto","t":"Are operating systems kept up to date automatically?","h":"Enable automatic security patches."},
    {"id":"su_apps","t":"Are business apps updated regularly?","h":"Browsers, CRM, accounting, PoS, etc."},
    {"id":"su_unsupported","t":"Any devices running unsupported/outdated systems?","h":"E.g., Windows 7, old Android versions."},
    {"id":"su_review","t":"Do you have a monthly reminder/process to review updates?","h":"Automatic alerts or MSP checks are fine."},
])
SECTION_6 = section("Incident Preparedness", [
    {"id":"ip_report","t":"Do employees know how to report incidents or suspicious activity?","h":"E.g., phishing emails, data loss."},
    {"id":"ip_plan","t":"Do you have a simple incident response plan?","h":"Even a 1-page checklist helps."},
    {"id":"ip_log","t":"Are incident details recorded when they occur?","h":"What happened, when, and the impact."},
    {"id":"ip_contacts","t":"Are key contacts known for emergencies?","h":"Internal IT, MSP, or external specialist."},
    {"id":"ip_test","t":"Have you tested or simulated a cyber incident?","h":"A 30-min tabletop builds confidence."},
])
SECTION_7 = section("Vendor & Cloud", [
    {"id":"vc_cloud","t":"Do you use cloud tools to store company data?","h":"M365, Google Workspace, Dropbox, industry SaaS."},
    {"id":"vc_mfa","t":"Are cloud accounts protected with MFA and strong passwords?","h":"Turn on MFA for all admin and user accounts."},
    {"id":"vc_review","t":"Do you review how vendors protect your data?","h":"Check DPAs, security terms and certifications."},
    {"id":"vc_access","t":"Do you track which suppliers have access to systems/data?","h":"Maintain a current access list."},
    {"id":"vc_notify","t":"Will vendors notify you promptly if they have a breach?","h":"Ensure contracts have breach-notification clauses."},
])
SECTION_8 = section("Awareness & Training", [
    {"id":"at_training","t":"Have employees received any cybersecurity training?","h":"Even short online sessions count."},
    {"id":"at_phish","t":"Do staff know how to spot phishing or scam emails?","h":"Check links, sender, tone and spelling."},
    {"id":"at_onboard","t":"Are new employees briefed during onboarding?","h":"Consistency from day one."},
    {"id":"at_reminders","t":"Do you share posters, reminders, or tips?","h":"Monthly nudges keep awareness fresh."},
    {"id":"at_lead","t":"Does management actively promote cybersecurity?","h":"Leadership buy-in builds culture."},
])
ALL_SECTIONS=[SECTION_3,SECTION_4,SECTION_5,SECTION_6,SECTION_7,SECTION_8]
BASELINE_IDS={"Access & Identity","Device & Data","System & Software Updates","Awareness & Training"}

def render_section(sec):
    st.markdown(f"### {sec['id']}")
    st.markdown(f"<div class='hint'>{SECTION_INTRO.get(sec['id'],'')}</div>", unsafe_allow_html=True)
    for q in sec["questions"]:
        st.radio(q["t"], ["Yes","Partially","No","Not sure"], key=q["id"], horizontal=True)
        st.markdown(f"<div class='hint'>💡 {q['h']}</div>", unsafe_allow_html=True)
    st.markdown("")

def section_score(sec):
    vals=[st.session_state.get(q["id"],"") for q in sec["questions"]]
    risk={"Yes":0,"Partially":1,"Not sure":1,"No":2}
    return round(sum(risk.get(v,1) for v in vals)/len(vals),2) if vals else 0.0

def section_light(sec):
    """Return (emoji,label,class) traffic light from section score."""
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

def applicable_compliance(tags:set):
    hints=[]
    if any(t in tags for t in ["geo:eu","geo:uk"]) or "data:pii" in tags or "data:employee" in tags:
        hints.append(("GDPR","Regulation (EU/UK)","Likely applies if you process EU/UK personal data. Review DPAs and cross-border transfers."))
    if "payments:card" in tags or "system:pos" in tags or "data:financial" in tags:
        hints.append(("PCI DSS","Industry Standard","If you store/process/transmit card data. PSP-managed PoS may reduce scope."))
    if "data:health" in tags:
        hints.append(("HIPAA","US Regulation","Applies to US covered entities/business associates; treat as conditional otherwise."))
    hints.append(("ISO/IEC 27001","Standard","A clear maturity target and customer trust signal."))
    return hints

# ─────────────────────────────────────────────────────────────
# LANDING
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Landing":
    st.markdown("# 🛡️ SME Cybersecurity Self-Assessment")
    st.markdown("<div class='lead'>Assess · Understand · Act — in under 15 minutes.</div>", unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.write("• 🗣️ Plain-language questions")
        st.write("• 📚 Traceable to NIST/ISO")
    with right:
        st.write("• ⏱️ 10–15 minutes")
        st.write("• 🧪 Safe demos of common scams")
    if st.button("Start ➜", type="primary"): go("Step 1")

# ─────────────────────────────────────────────────────────────
# STEP 1 — Business basics
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 1":
    st.markdown("##### Step 1 of 4")
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
        cA, cB = st.columns([1,1])
        with cA:
            if st.button("⬅ Back"): go("Landing")
        with cB:
            st.button("Continue ➜", type="primary", disabled=len(missing)>0, on_click=lambda: go("Step 2"))
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# STEP 2 — Quick checks + Operating context (optional)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 2":
    st.markdown("##### Step 2 of 4")
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
            st.markdown("Use plain answers — we’ll guide you next.")
            st.radio("**Q1. Who looks after your IT day-to-day?**", ["Self-managed","Outsourced IT","Shared responsibility","Not sure"], key="bp_it_manager", horizontal=True)
            st.markdown("<div class='hint'>Includes laptops/phones, Wi-Fi, email, website, cloud apps, file storage/backup.</div>", unsafe_allow_html=True)

            st.radio("**Q2. Do you keep a simple list of company devices (laptops, phones, servers)?**",
                     ["Yes","Partially","No","Not sure"], key="bp_inventory", horizontal=True)
            st.markdown("<div class='hint'>An asset list helps find forgotten or unmanaged gear.</div>", unsafe_allow_html=True)

            st.radio("**Q3. Do people use personal devices for work (BYOD)?**", ["Yes","Sometimes","No","Not sure"], key="bp_byod", horizontal=True)
            st.markdown("<div class='hint'>E.g., reading work email on a personal phone or laptop.</div>", unsafe_allow_html=True)

            st.radio("**Q4. Do you handle sensitive customer or financial data?**", ["Yes","No","Not sure"], key="bp_sensitive", horizontal=True)
            st.markdown("<div class='hint'>Payment details, personal records, contracts.</div>", unsafe_allow_html=True)

        with tab2:
            st.radio("**Q5. Do you have a public website?**", ["Yes","No"], key="df_website", horizontal=True)
            st.markdown("<div class='hint'>Helps assess potential online entry points.</div>", unsafe_allow_html=True)

            st.radio("**Q6. Is your website HTTPS (padlock in the browser)?**", ["Yes","No","Not sure"], key="df_https", horizontal=True)
            st.markdown("<div class='hint'>HTTPS encrypts traffic and builds visitor trust.</div>", unsafe_allow_html=True)

            st.radio("**Q7. Do you use business email addresses (e.g., info@yourcompany.com)?**", ["Yes","Partially","No"], key="df_email", horizontal=True)
            st.markdown("<div class='hint'>Personal Gmail/Yahoo accounts increase phishing risk.</div>", unsafe_allow_html=True)

            st.radio("**Q8. Is your business active on social media (LinkedIn, Instagram, etc.)?**", ["Yes","No"], key="df_social", horizontal=True)

            st.radio("**Q9. Do you regularly check what’s public about the company or staff online?**", ["Yes","Sometimes","No"], key="df_review", horizontal=True)
            st.markdown("<div class='hint'>Contact details, staff lists, or screenshots can reveal systems.</div>", unsafe_allow_html=True)

        with tab3:
            st.markdown("These details help tailor your results. Skip if unsure — you can add later.")
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
                    st.markdown("<div class='hint'><b>What these mean:</b><br>" + "<br>".join([f"• <b>{d}</b>: {DATA_TYPE_HELP[d]}" for d in st.session_state.data_types]) + "</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='hint'>Choose any that apply — we’ll tailor compliance notes accordingly.</div>", unsafe_allow_html=True)
                st.radio("🌐 Cross-border data flows", CROSS_BORDER, key="cross_border", horizontal=True, index=CROSS_BORDER.index(st.session_state.cross_border))
                st.multiselect("🔒 Certifications / schemes", CERTIFICATION_OPTIONS, key="certifications", default=st.session_state.certifications)
                if "Other (type below)" in st.session_state.certifications:
                    st.text_input("✍️ Specify other scheme", key="certifications_other", value=st.session_state.certifications_other)
                st.radio("💳 Do you accept or process card payments (online or in-store)?", ["Yes","No","Not sure"], key="bp_card_payments",
                         horizontal=True, index=(["Yes","No","Not sure"].index(st.session_state.bp_card_payments) if st.session_state.bp_card_payments else 1))

    with prev:
        st.write(""); st.write("")
        if st.button("⬅ Back to Step 1"): go("Step 1")
        required = ["bp_it_manager","bp_inventory","bp_byod","bp_sensitive","df_website","df_https","df_email","df_social","df_review"]
        missing = [k for k in required if not st.session_state.get(k)]
        st.button("Continue ➜", type="primary", disabled=len(missing)>0, on_click=lambda: go("Step 3"))

# ─────────────────────────────────────────────────────────────
# STEP 3 — Summary
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 3":
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
        if st.button("⬅ Back"): go("Step 2")
    with c2:
        if st.button("Start over"):
            for k,v in defaults.items(): st.session_state[k]=v
            go("Landing")
    with c3:
        if st.button("Continue to detailed assessment ➜", type="primary"):
            st.session_state.detailed_sections = pick_active_sections(compute_tags())
            go("Detailed")

# ─────────────────────────────────────────────────────────────
# STEP 4 — Detailed
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Detailed":
    st.markdown("##### Step 4 of 4")
    st.markdown("## 🧩 Detailed Assessment")

    active_ids=set(st.session_state.get("detailed_sections", []))
    sections=[s for s in ALL_SECTIONS if s["id"] in active_ids] or [SECTION_3,SECTION_4,SECTION_5,SECTION_8]
    tabs=st.tabs([("🔐 " if s["id"]=='Access & Identity' else "💻 " if s['id']=='Device & Data' else "🧩 " if s['id']=='System & Software Updates' else "🚨 " if s['id']=='Incident Preparedness' else "☁️ " if s['id']=='Vendor & Cloud' else "🧠 ")+s["id"] for s in sections])
    for tab, s in zip(tabs, sections):
        with tab: render_section(s)

    c1,c2 = st.columns([1,2])
    with c1:
        if st.button("⬅ Back to Summary"): go("Step 3")
    with c2:
        if st.button("Finish & see action plan ➜", type="primary"):
            st.session_state["detailed_scores"]={s["id"]: section_score(s) for s in sections}
            go("Report")

# ─────────────────────────────────────────────────────────────
# REPORT — Action Plan (traffic lights, no numbers)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Report":
    st.markdown("## 🗺️ Action Plan & Section Status")

    # Section traffic lights (no numeric scores shown)
    detailed_scores = st.session_state.get("detailed_scores", {})
    if detailed_scores:
        cols = st.columns(len(detailed_scores))
        lookup = {s["id"]: s for s in ALL_SECTIONS}
        for (sid, _), col in zip(detailed_scores.items(), cols):
            emoji, label, klass = section_light(lookup[sid])
            with col:
                st.markdown(
                    f"<div class='card'><b>{sid}</b>"
                    f"<div class='hint'>Status: <span class='pill {klass}'>{emoji} {label}</span></div></div>",
                    unsafe_allow_html=True
                )
    else:
        st.caption("No detailed sections answered yet. Complete the detailed assessment to see section status.")

    # Build plan
    tags = compute_tags()
    quick, foundations, nextlvl = [], [], []

    if st.session_state.df_website=="Yes" and st.session_state.df_https!="Yes":
        quick.append("🔒 Enable HTTPS and force redirect (HTTP→HTTPS). <span class='tag'>High impact</span> <span class='tag'>Low effort</span>")
    if st.session_state.df_email in ("No","Partially"):
        quick.append("📧 Move to business email (M365/Google) and **enforce MFA** for all users. <span class='tag'>High</span> <span class='tag'>Low</span>")
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

    c1,c2 = st.columns([1,1])
    with c1:
        if st.button("⬅ Back to Detailed"): go("Detailed")
    with c2:
        if st.button("Start over"):
            for k,v in defaults.items(): st.session_state[k]=v
            go("Landing")
