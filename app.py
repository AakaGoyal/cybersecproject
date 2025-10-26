import io
import csv
import streamlit as st
from typing import List, Tuple

# ─────────────────────────────────────────────────────────────
# Page setup & compact styles
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="SME Cybersecurity Self-Assessment", layout="wide")

st.markdown("""
<style>
/* Trim Streamlit's default header/padding to reduce vertical waste */
.stApp header { height: 0 !important; min-height: 0 !important; }
.block-container { padding-top: .6rem !important; max-width: 1180px; }

/* Tighter headings */
h1,h2,h3,h4 { margin: .15rem 0 .5rem !important; }
.section { margin-top: .35rem !important; }

/* Uniform gap between questions */
.qwrap { margin: .65rem 0 1.0rem !important; }

/* Readable hint color */
.hint { color:#46505a; font-size:.95rem; font-style:italic; margin:.25rem 0 .35rem; }

/* Chips / pills */
.pill {display:inline-block;border-radius:999px;padding:.18rem .55rem;border:1px solid #e5e7eb;font-size:.9rem;color:#374151;background:#fff}
.chip {display:inline-flex;align-items:center;gap:.35rem;border-radius:999px;padding:.18rem .6rem;border:1px solid #e5e7eb;margin-right:.35rem;font-weight:600}

/* Traffic lights */
.green{background:#e8f7ee;color:#0f5132;border-color:#cceedd}
.amber{background:#fff5d6;color:#8a6d00;border-color:#ffe7ad}
.red{background:#ffe5e5;color:#842029;border-color:#ffcccc}

/* Cards */
.card {border:1px solid #e6e8ec;border-radius:12px;padding:12px;background:#fff}
.sticky {position: sticky; top: 10px;}

/* Progress bar container spacing */
[data-testid="stProgress"] { margin:.35rem 0 .6rem; }
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
CRITICAL_SYSTEMS = ["ERP (Enterprise Resource Planning)", "Point of Sale (PoS)", "CRM (Customer Relationship Management)",
                    "EHR (Electronic Health Record)", "CMS (Content Management System)", "Other (type below)"]
WORK_ENVIRONMENTS = ["Local servers", "Cloud apps", "Hybrid"]
REMOTE_RATIO = ["Mostly on-site", "Hybrid", "Fully remote"]
DATA_TYPES = [
    "Customer personal data (PII)",
    "Employee/staff data",
    "Health/medical data",
    "Financial/transaction data",
]
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
    # Step 1
    person_name="", company_name="",
    sector_label=INDUSTRY_OPTIONS[0], sector_other="",
    years_in_business=YEARS_OPTIONS[0],
    employee_range=EMPLOYEE_RANGES[0],
    turnover_label=TURNOVER_OPTIONS[0],
    work_mode=None,  # no preselect
    business_region=REGION_OPTIONS[0],
    # Context
    critical_systems=[], critical_systems_other="",
    primary_work_env=WORK_ENVIRONMENTS[1],
    remote_ratio=REMOTE_RATIO[1],
    data_types=[],
    cross_border=CROSS_BORDER[0],
    certifications=["None"], certifications_other="",
    bp_card_payments=None,
    # Step 2 (Q1–Q9) — start with None so nothing is preselected
    bp_it_manager=None, bp_inventory=None, bp_byod=None, bp_sensitive=None,
    df_website=None, df_https=None, df_email=None, df_social=None, df_review=None,
    # Tier-2
    detailed_sections=[], detailed_scores={},
)
for k,v in defaults.items():
    st.session_state.setdefault(k,v)

# ─────────────────────────────────────────────────────────────
# Helper mappings & functions
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

def progress(step:int, total:int=3):
    st.progress(max(0, min(step, total))/total, text=f"Step {step} of {total}")

def go(page:str):
    st.session_state.page = page
    st.rerun()

def resolved_industry():
    if st.session_state.sector_label == "Other (type below)":
        return st.session_state.sector_other or "Other"
    return st.session_state.sector_label

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
        s=s.lower()
        if "erp" in s: tags.add("system:erp")
        if "pos" in s: tags.add("system:pos")
        if "crm" in s: tags.add("system:crm")
        if "ehr" in s: tags.add("system:ehr")
        if "cms" in s: tags.add("system:cms")
        if "other" in s: tags.add("system:other")
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

# Radio with NO default & NO placeholder
def radio_none(label, options:List[str], *, key:str, horizontal:bool=True, help:str|None=None):
    idx = options.index(st.session_state[key]) if st.session_state.get(key) in options else None
    return st.radio(label, options, index=idx, key=key, horizontal=horizontal, help=help)

# ─────────────────────────────────────────────────────────────
# Section registry (Tier-2 + Governance)
# ─────────────────────────────────────────────────────────────
def section(title_id, title, purpose, qlist): return {"id":title_id,"title":title,"purpose":purpose,"questions":qlist}

SECTION_3 = section("Access & Identity","🔐 Access & Identity Management",
    "Control of user access and authentication.", [
        {"id":"ai_pw","t":"Are strong passwords required for all accounts?","h":"Use at least 10–12 characters; a password manager helps."},
        {"id":"ai_mfa","t":"Is Multi-Factor Authentication (MFA) enabled for key accounts?","h":"Start with email, admin and finance; use an authenticator app."},
        {"id":"ai_admin","t":"Are admin rights limited to only those who need them?","h":"Grant temporarily and review quarterly."},
        {"id":"ai_shared","t":"Are shared accounts avoided or controlled?","h":"Prefer named accounts; if shared, rotate & log usage."},
        {"id":"ai_leavers","t":"Are old or unused accounts removed promptly?","h":"Disable the same day a person leaves; reclaim devices."},
    ])
SECTION_4 = section("Device & Data","💻 Device & Data Protection",
    "How well devices and company data are secured.", [
        {"id":"dd_lock","t":"Are all devices protected with a password or PIN?","h":"Turn on auto-lock ≤10 minutes."},
        {"id":"dd_fde","t":"Is full-disk encryption enabled on laptops and mobiles?","h":"BitLocker, FileVault, Android/iOS encryption."},
        {"id":"dd_edr","t":"Is reputable antivirus/EDR installed and active on all devices?","h":"E.g., Microsoft Defender, CrowdStrike."},
        {"id":"dd_backup","t":"Are important business files backed up regularly?","h":"Follow the 3–2–1 rule; automate it."},
        {"id":"dd_restore","t":"Are backups tested to ensure restore works?","h":"Try restoring quarterly; script if possible."},
        {"id":"dd_usb","t":"Are staff trained to handle suspicious files/USBs?","h":"Avoid unknown USBs; preview links."},
        {"id":"dd_wifi","t":"Are company devices separated from personal on Wi-Fi?","h":"Use separate SSIDs or VLANs."},
    ])
SECTION_5 = section("System & Software Updates","🧩 System & Software Updates",
    "Keeping systems patched and supported.", [
        {"id":"su_os_auto","t":"Are operating systems kept up to date automatically?","h":"Enable security patches."},
        {"id":"su_apps","t":"Are business applications updated regularly?","h":"Browsers, CRM, PoS, accounting, etc."},
        {"id":"su_unsupported","t":"Any devices running unsupported/outdated systems?","h":"Replace or isolate until replaced."},
        {"id":"su_review","t":"Is there a monthly process to review updates?","h":"Calendar/task list or MSP report."},
    ])
SECTION_6 = section("Incident Preparedness","🚨 Incident Preparedness",
    "Readiness to detect, respond, and recover.", [
        {"id":"ip_report","t":"Do employees know how to report incidents?","h":"Phishing mailbox, Slack/Teams #security, service desk."},
        {"id":"ip_plan","t":"Do you have a simple incident response plan?","h":"1-page checklist with roles & steps."},
        {"id":"ip_log","t":"Are incident details documented when they occur?","h":"Record what/when/who/impact."},
        {"id":"ip_contacts","t":"Are key contacts known for emergencies?","h":"Internal IT/MSP, cyber insurer, legal/DPO."},
        {"id":"ip_test","t":"Have you tested/simulated a cyber incident?","h":"30-minute tabletop twice a year."},
    ])
SECTION_7 = section("Vendor & Cloud","☁️ Vendor & Cloud Security",
    "Security of third-party tools, vendors, and online services.", [
        {"id":"vc_cloud","t":"Do you use cloud tools to store company data?","h":"M365, Google Workspace, Dropbox, sector SaaS."},
        {"id":"vc_mfa","t":"Are those cloud services protected with MFA & strong passwords?","h":"Enforce tenant-wide MFA; require for admins."},
        {"id":"vc_review","t":"Do you review how vendors protect your data?","h":"DPAs, security terms, certifications."},
        {"id":"vc_access","t":"Do you track which suppliers have access to systems/data?","h":"Maintain and review an access list."},
        {"id":"vc_notify","t":"If a vendor has a breach, will they notify you promptly?","h":"Ensure breach-notification clauses."},
    ])
SECTION_9 = section("Governance","🏛️ Governance",
    "Ownership, policies and assurance that tie everything together.", [
        {"id":"gv_owner","t":"Is there a named person responsible for cybersecurity?","h":"Small orgs: owner/manager; medium: delegate formally."},
        {"id":"gv_policy","t":"Do you have lightweight written policies?","h":"Acceptable use, passwords/MFA, incident, vendors, BYOD."},
        {"id":"gv_risk","t":"Do you review top cyber risks at least twice a year?","h":"List 5–10 risks, owners and due dates."},
        {"id":"gv_training","t":"Is security awareness tracked (onboarding + annual refresh)?","h":"Keep simple records; nudge non-completers."},
        {"id":"gv_audit","t":"Do you check compliance to policies and key controls?","h":"Simple checklist or MSP attestation."},
    ])

SECTION_8 = section("Awareness & Training","🧠 Awareness & Training",
    "Cybersecurity culture and user awareness.", [
        {"id":"at_training","t":"Have employees received cybersecurity awareness training?","h":"Short e-learning or live session."},
        {"id":"at_phish","t":"Do staff know how to identify phishing/scam emails?","h":"Links, sender, urgency, attachments."},
        {"id":"at_onboard","t":"Are new employees briefed at onboarding?","h":"Consistency from day one."},
        {"id":"at_reminders","t":"Do you share posters, reminders, or tips?","h":"Monthly internal post helps."},
        {"id":"at_lead","t":"Does management visibly support cybersecurity?","h":"Leaders mention it & ask for MFA completion."},
    ])

ALL_SECTIONS=[SECTION_3,SECTION_4,SECTION_5,SECTION_6,SECTION_7,SECTION_8,SECTION_9]
BASELINE_IDS={"Access & Identity","Device & Data","System & Software Updates","Awareness & Training","Governance"}

def render_section(sec):
    st.markdown(f"### {sec['title']}")
    st.caption(sec["purpose"])
    for q in sec["questions"]:
        st.markdown('<div class="qwrap">', unsafe_allow_html=True)
        radio_none(
            f"{q['t']}",
            ["🟢 Yes","🟡 Partially","🔴 No","🤔 Not sure"],
            key=q["id"],
            horizontal=True,
            help=q["h"]
        )
        st.markdown(f"<div class='hint'>Why it matters: {q['h']}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def section_score(sec):
    vals=[st.session_state.get(q["id"], None) for q in sec["questions"]]
    risk={"🟢 Yes":0,"🟡 Partially":1,"🤔 Not sure":1,"🔴 No":2}
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

def applicable_compliance(tags:set):
    hints=[]
    if any(t in tags for t in ["geo:eu","geo:uk"]) or "data:pii" in tags or "data:employee" in tags:
        hints.append(("GDPR","Regulation (EU/UK)","Likely applies if you process EU/UK personal data. Review DPAs and cross-border transfers."))
    if "payments:card" in tags or "system:pos" in tags or "data:financial" in tags:
        hints.append(("PCI DSS","Industry Standard","If you store/process/transmit card data. PSP-managed PoS may reduce scope."))
    if "data:health" in tags:
        hints.append(("HIPAA","US Regulation","Applies to US covered entities/business associates; treat as conditional if outside US."))
    hints.append(("ISO/IEC 27001","Standard","Clear maturity target and customer trust signal."))
    hints.append(("NIST CSF 2.0","Framework","Good structure for improvements even in SMEs."))
    return hints

# ─────────────────────────────────────────────────────────────
# LANDING
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Landing":
    progress(0)
    st.markdown("## 🛡️ SME Cybersecurity Self-Assessment")
    st.caption("Assess • Understand • Act — in under 15 minutes.")
    c1,c2 = st.columns(2)
    with c1:
        st.write("• Plain-language questions")
        st.write("• Traceable to NIST/ISO")
    with c2:
        st.write("• 10–15 minutes")
        st.write("• Safe demos of common scams")
    if st.button("Start ➜", type="primary"):
        go("Step 1")

# ─────────────────────────────────────────────────────────────
# STEP 1 — Business profile & Recommended context
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 1":
    progress(1)
    st.markdown("## 🧭 Tell us about the business")
    st.caption("Just the basics (~2 minutes).")

    snap, form = st.columns([1, 2], gap="large")
    with snap:
        st.markdown('<div class="sticky">', unsafe_allow_html=True)
        st.markdown("#### 📸 Snapshot")
        st.markdown(
            f"<div class='card'><b>Business:</b> {st.session_state.company_name or '—'}<br>"
            f"<b>Region:</b> {st.session_state.business_region}<br>"
            f"<b>Industry:</b> {resolved_industry()}<br>"
            f"<b>People:</b> {st.session_state.employee_range} · "
            f"<b>Years:</b> {st.session_state.years_in_business}<br>"
            f"<b>Turnover:</b> {st.session_state.turnover_label}<br>"
            f"<b>Work mode:</b> {st.session_state.work_mode or '—'}<br>"
            f"<b>Size (derived):</b> {org_size()}</div>",
            unsafe_allow_html=True
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
                                                           TURNOVER_OPTIONS, index=TURNOVER_OPTIONS.index(st.session_state.turnover_label))

        st.session_state.work_mode = radio_none("🧭 Work mode *", WORK_MODE, key="work_mode", horizontal=True)

        st.markdown("#### 🏗️ Operational context (recommended)")
        cA, cB = st.columns(2)
        with cA:
            st.session_state.critical_systems = st.multiselect("🧩 Critical systems in use", CRITICAL_SYSTEMS,
                                                               default=st.session_state.critical_systems)
            if "Other (type below)" in st.session_state.critical_systems:
                st.session_state.critical_systems_other = st.text_input("✍️ Specify other system",
                                                                        value=st.session_state.critical_systems_other)
            st.session_state.primary_work_env = st.radio("🏗️ Primary work environment",
                                                         WORK_ENVIRONMENTS, horizontal=True,
                                                         index=WORK_ENVIRONMENTS.index(st.session_state.primary_work_env))
            st.session_state.remote_ratio = st.radio("🏠 Remote work ratio", REMOTE_RATIO, horizontal=True,
                                                     index=REMOTE_RATIO.index(st.session_state.remote_ratio))
        with cB:
            st.session_state.data_types = st.multiselect("🔎 Types of personal data handled",
                                                         DATA_TYPES, default=st.session_state.data_types)
            st.session_state.cross_border = st.radio("🌐 Cross-border data flows", CROSS_BORDER, horizontal=True,
                                                     index=CROSS_BORDER.index(st.session_state.cross_border))
            st.session_state.certifications = st.multiselect("🔒 Certifications / schemes",
                                                             CERTIFICATION_OPTIONS, default=st.session_state.certifications)
            if "Other (type below)" in st.session_state.certifications:
                st.session_state.certifications_other = st.text_input("✍️ Specify other scheme",
                                                                      value=st.session_state.certifications_other)

        st.session_state.bp_card_payments = radio_none(
            "💳 Do you accept or process card payments (online or in-store)?",
            ["Yes","No","Not sure"], key="bp_card_payments", horizontal=True
        )

        missing=[]
        if not st.session_state.person_name.strip(): missing.append("name")
        if not st.session_state.company_name.strip(): missing.append("company")
        if st.session_state.sector_label == "Other (type below)" and not st.session_state.sector_other.strip():
            missing.append("industry")
        if st.session_state.work_mode is None: missing.append("work mode")

        cA, cB = st.columns([1,1])
        with cA:
            if st.button("⬅ Back"):
                go("Landing")
        with cB:
            if st.button("Continue ➜", type="primary", disabled=len(missing)>0):
                go("Step 2")

# ─────────────────────────────────────────────────────────────
# STEP 2 — Baseline quick checks (Q1–Q9)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 2":
    progress(2)
    st.markdown("## 🧪 Your current practices")
    st.caption("Answer the 9 quick checks. No trick questions.")

    snap, body, prev = st.columns([1, 1.65, 1], gap="large")
    with snap:
        st.markdown('<div class="sticky">', unsafe_allow_html=True)
        st.markdown("#### 📸 Snapshot")
        st.markdown(
            f"<div class='card'><b>Business:</b> {st.session_state.company_name}<br>"
            f"<b>Region:</b> {st.session_state.business_region}<br>"
            f"<b>Industry:</b> {resolved_industry()}<br>"
            f"<b>People:</b> {st.session_state.employee_range} · <b>Years:</b> {st.session_state.years_in_business}<br>"
            f"<b>Turnover:</b> {st.session_state.turnover_label} · <b>Size:</b> {org_size()}<br>"
            f"<b>Work mode:</b> {st.session_state.work_mode}</div>",
            unsafe_allow_html=True
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
            st.markdown('<div class="qwrap">', unsafe_allow_html=True)
            radio_none("Q1. 🧑‍💻 Who looks after your IT day-to-day?",
                ["Self-managed","Outsourced IT","Shared responsibility","Not sure"],
                key="bp_it_manager", horizontal=True,
                help="Laptops/phones, Wi-Fi, email, website/PoS, cloud apps, file storage/backup.")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="qwrap">', unsafe_allow_html=True)
            radio_none("Q2. 📋 Do you keep a simple list of company devices (laptops, phones, servers)?",
                ["🟢 Yes","🟡 Partially","🔴 No","🤔 Not sure"],
                key="bp_inventory", horizontal=True,
                help="An asset list helps find forgotten or unmanaged equipment.")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="qwrap">', unsafe_allow_html=True)
            radio_none("Q3. 📱 Do people use personal devices for work (BYOD)?",
                ["🟢 Yes","Sometimes","🔴 No","🤔 Not sure"], key="bp_byod", horizontal=True,
                help="E.g., reading work email on a personal phone or laptop.")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="qwrap">', unsafe_allow_html=True)
            radio_none("Q4. 🔐 Do you handle sensitive customer or financial data?",
                ["🟢 Yes","🔴 No","🤔 Not sure"], key="bp_sensitive", horizontal=True,
                help="Payment details, personal records, signed contracts.")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="qwrap">', unsafe_allow_html=True)
            radio_none("Q5. 🕸️ Do you have a public website?",
                ["Yes","No"], key="df_website", horizontal=True,
                help="Helps assess potential online entry points.")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="qwrap">', unsafe_allow_html=True)
            radio_none("Q6. 🔒 Is your website HTTPS (padlock in the browser)?",
                ["🟢 Yes","🟡 Partially","🔴 No","🤔 Not sure"], key="df_https", horizontal=True,
                help="HTTPS encrypts traffic and builds visitor trust.")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="qwrap">', unsafe_allow_html=True)
            radio_none("Q7. ✉️ Do you use business email addresses?",
                ["🟢 Yes","🟡 Partially","🔴 No"], key="df_email", horizontal=True,
                help="Personal email raises phishing risk. Custom domain + MFA are safer.")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="qwrap">', unsafe_allow_html=True)
            radio_none("Q8. 📣 Is your business active on social media?",
                ["Yes","No"], key="df_social", horizontal=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="qwrap">', unsafe_allow_html=True)
            radio_none("Q9. 🔎 Do you regularly check what’s public about the company or staff online?",
                ["Yes","Sometimes","No"], key="df_review", horizontal=True,
                help="E.g., staff lists, screenshots, leaked credentials.")
            st.markdown('</div>', unsafe_allow_html=True)

    with prev:
        st.write(""); st.write("")
        if st.button("⬅ Back to Step 1"):
            go("Step 1")
        required = ["bp_it_manager","bp_inventory","bp_byod","bp_sensitive","df_website","df_https","df_email","df_social","df_review"]
        missing = [k for k in required if st.session_state.get(k) is None]
        if st.button("Finish Initial Assessment ➜", type="primary", disabled=len(missing)>0):
            go("Step 3")

# ─────────────────────────────────────────────────────────────
# STEP 3 — Initial Summary
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 3":
    progress(3)
    st.markdown("## 📊 Initial Assessment Summary")
    over_txt, over_class, over_msg = overall_badge()
    st.markdown(f"<span class='pill {over_class}'>Overall digital dependency: <b>{over_txt}</b></span>", unsafe_allow_html=True)
    st.caption(over_msg)

    snap, glance = st.columns([1.05, 1.95], gap="large")
    with snap:
        st.markdown("### 📸 Snapshot")
        st.markdown(
            f"<div class='card'><b>Business:</b> {st.session_state.company_name}<br>"
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
        if st.session_state.bp_inventory not in ("🟢 Yes","🟡 Partially"): hints.append("📝 Add/finish your device list.")
        if st.session_state.df_website=='Yes' and st.session_state.df_https!='🟢 Yes': hints.append("🔒 Enable HTTPS for your website.")
        if st.session_state.bp_byod in ("🟢 Yes","Sometimes"): hints.append("📱 Set simple BYOD + MFA rules.")
        if hints: st.caption(" · ".join(hints))

    st.markdown("---")
    st.markdown("### 📚 Likely compliance & standards to consider")
    for name, level, note in applicable_compliance(compute_tags()):
        st.markdown(f"<div class='card' style='margin-bottom:.5rem'><b>{name}</b> <span class='pill amber' style='margin-left:.4rem'>{level}</span><div class='hint'>ℹ️ {note}</div></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        if st.button("⬅ Back"):
            go("Step 2")
    with c2:
        if st.button("Start over"):
            for k,v in defaults.items(): st.session_state[k]=v
            go("Landing")
    with c3:
        if st.button("Continue to detailed assessment ➜", type="primary"):
            st.session_state.detailed_sections = pick_active_sections(compute_tags())
            go("Detailed")

# ─────────────────────────────────────────────────────────────
# Detailed Assessment
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Detailed":
    st.markdown("## 🧩 Detailed Assessment")
    active_ids=set(st.session_state.get("detailed_sections", []))
    sections=[s for s in ALL_SECTIONS if s["id"] in active_ids] or [SECTION_3,SECTION_4,SECTION_5,SECTION_8,SECTION_9]
    tabs=st.tabs([s["title"] for s in sections])
    for tab, s in zip(tabs, sections):
        with tab: render_section(s)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅ Back to Summary"):
            go("Step 3")
    with c2:
        if st.button("Finish & see recommendations ➜", type="primary"):
            st.session_state["detailed_scores"]={s["id"]: section_score(s) for s in sections}
            go("Report")

# ─────────────────────────────────────────────────────────────
# Final Report + Exports
# ─────────────────────────────────────────────────────────────
def build_markdown_report()->str:
    sys,ppl,net = area_rag()
    lines=[]
    lines.append("# SME Cybersecurity Self-Assessment — Summary & Action Plan\n")
    lines.append("## Snapshot")
    lines.append(f"- Business: {st.session_state.company_name}")
    lines.append(f"- Region: {st.session_state.business_region}")
    lines.append(f"- Industry: {resolved_industry()}")
    lines.append(f"- People: {st.session_state.employee_range} | Years: {st.session_state.years_in_business}")
    lines.append(f"- Turnover: {st.session_state.turnover_label} | Work mode: {st.session_state.work_mode}")
    lines.append(f"- Derived size: {org_size()}\n")
    lines.append("## At-a-glance")
    lines.append(f"- Systems & devices: {sys[0]}")
    lines.append(f"- People & access: {ppl[0]}")
    lines.append(f"- Online exposure: {net[0]}\n")
    notes = applicable_compliance(compute_tags())
    if notes:
        lines.append("## Likely compliance & standards")
        for n,l,note in notes:
            lines.append(f"- {n} — {l}: {note}")
        lines.append("")
    scores = st.session_state.get("detailed_scores", {})
    if scores:
        lines.append("## Section status")
        lookup={s["id"]:s for s in ALL_SECTIONS}
        for sid, sc in scores.items():
            emoji, label, _ = section_light(lookup[sid])
            lines.append(f"- {sid}: {emoji} {label} (score {sc})")
        lines.append("")
    lines.append("## Action plan")
    for title, items in generate_actions().items():
        lines.append(f"### {title}")
        for i, x in enumerate(items, start=1): lines.append(f"{i}. {x}")
    return "\n".join(lines)

def generate_actions():
    tags=compute_tags()
    quick=[]; foundations=[]; nextlvl=[]
    if st.session_state.df_website=="Yes" and st.session_state.df_https!="🟢 Yes":
        quick.append("Enable HTTPS and force redirect (HTTP→HTTPS).")
    if st.session_state.df_email in ("🔴 No","🟡 Partially"):
        quick.append("Move to business email (M365/Google) and enforce MFA for all users.")
    if st.session_state.bp_inventory not in ("🟢 Yes","🟡 Partially"):
        quick.append("Create a simple **device inventory** and enable full-disk encryption.")
    if st.session_state.bp_byod in ("🟢 Yes","Sometimes"):
        foundations.append("Publish a **BYOD rule of 5**: screen lock, OS updates, disk encryption, MFA for email, approved apps.")
    foundations.append("Turn on **automatic OS & app updates**; remove unsupported systems.")
    foundations.append("Automate **backups** and **test a restore** quarterly.")
    if any(t in tags for t in ["infra:cloud","system:pos","geo:crossborder"]):
        nextlvl.append("Review **vendor contracts**: breach notification, data location/transfer, admin MFA.")
    if "payments:card" in tags or "system:pos" in tags:
        nextlvl.append("Confirm **PCI DSS** responsibilities with your PoS/PSP.")
    if any(t in tags for t in ["geo:eu","geo:uk"]):
        nextlvl.append("Document **GDPR basics**: Records of Processing, DPAs, contact for data requests.")
    return {
        "⚡ Quick wins (do these first)": quick or ["No urgent quick wins detected."],
        "🧱 Foundations to build this quarter": foundations,
        "🚀 Next-level / compliance alignment": nextlvl
    }

def export_csv_bytes()->bytes:
    buf=io.StringIO()
    w=csv.writer(buf)
    w.writerow(["Field","Value"])
    base = {
        "Business": st.session_state.company_name,
        "Region": st.session_state.business_region,
        "Industry": resolved_industry(),
        "People": st.session_state.employee_range,
        "Years": st.session_state.years_in_business,
        "Turnover": st.session_state.turnover_label,
        "Work mode": st.session_state.work_mode,
        "Derived size": org_size(),
    }
    for k,v in base.items(): w.writerow([k,v])
    w.writerow([])
    w.writerow(["Question","Answer"])
    for key in ["bp_it_manager","bp_inventory","bp_byod","bp_sensitive","df_website","df_https","df_email","df_social","df_review"]:
        w.writerow([key, st.session_state.get(key)])
    return buf.getvalue().encode("utf-8")

if st.session_state.page == "Report":
    st.markdown("## 🗺️ Recommendations & Section Scores")
    scores = st.session_state.get("detailed_scores", {})
    if scores:
        cols = st.columns(len(scores))
        lookup={s["id"]:s for s in ALL_SECTIONS}
        for (sid, sc), col in zip(scores.items(), cols):
            emoji, label, klass = section_light(lookup[sid])
            with col:
                st.markdown(f"<div class='card'><b>{sid}</b><div class='hint'>Status: <span class='pill {klass}'>{emoji} {label}</span> (score {sc})</div></div>", unsafe_allow_html=True)
    else:
        st.caption("No detailed scores yet. Complete the detailed assessment to see section scores.")

    st.markdown("---")
    st.markdown("### 🧭 Action plan")
    actions = generate_actions()
    for title, items in actions.items():
        st.markdown(f"**{title}**")
        st.markdown("\n".join([f"{i}. {x}" for i,x in enumerate(items, start=1)]))

    st.markdown("---")
    md = build_markdown_report()
    st.download_button("⬇️ Download report (Markdown)", data=md.encode("utf-8"),
                       file_name="cyber-assessment-report.md", mime="text/markdown")
    st.download_button("⬇️ Download snapshot (CSV)", data=export_csv_bytes(),
                       file_name="cyber-assessment-snapshot.csv", mime="text/csv")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅ Back to Detailed"):
            go("Detailed")
    with c2:
        if st.button("Start over"):
            for k,v in defaults.items(): st.session_state[k]=v
            go("Landing")
