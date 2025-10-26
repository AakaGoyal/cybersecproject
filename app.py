import streamlit as st
from typing import List, Dict, Tuple

# ─────────────────────────────────────────────────────────────
# Page setup & global styles
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="SME Cybersecurity Self-Assessment", layout="wide")

st.markdown("""
<style>
  /* Layout + spacing */
  .block-container {max-width: 1160px; padding-top: .6rem !important;}
  h1,h2,h3,h4 {margin:.2rem 0 .6rem}
  [data-testid="stMarkdownContainer"] ul{margin:.25rem 0 .25rem 1.25rem}
  [data-testid="stMarkdownContainer"] ol{margin:.25rem 0 .25rem 1.25rem}

  /* Cards / chips / pills */
  .card {border:1px solid #e6e8ec;border-radius:12px;padding:12px;background:#fff}
  .chip {display:inline-flex;align-items:center;gap:.35rem;border-radius:999px;padding:.18rem .6rem;border:1px solid #e5e7eb;margin-right:.35rem;font-weight:600}
  .pill {display:inline-block;border-radius:999px;padding:.18rem .55rem;border:1px solid #e5e7eb;font-size:.9rem;color:#374151;background:#fff}

  .green{background:#e8f7ee;color:#0f5132;border-color:#cceedd}
  .amber{background:#fff5d6;color:#8a6d00;border-color:#ffe7ad}
  .red{background:#ffe5e5;color:#842029;border-color:#ffcccc}

  /* Help / explanation – darker & larger for readability */
  .hint{margin:.35rem 0 .85rem; font-size:1.02rem; color:#374151; font-style:italic; line-height:1.35}

  /* Uniform spacing for every Q-block */
  .qwrap{margin:.45rem 0 1.05rem;}
  .qtitle{margin-bottom:.25rem; font-weight:600}

  /* Sticky sidebar snapshot */
  .sticky{position:sticky; top:10px;}

  /* RADIO → traffic-light pills (hide BaseWeb dot, style rows) */
  .stRadio [data-baseweb="radio"] svg{display:none !important;}
  .stRadio [role="radiogroup"]{gap:.5rem !important; display:flex; flex-wrap:wrap}
  .stRadio [role="radiogroup"] > div{
    border:1px solid #e5e7eb; border-radius:999px; padding:.22rem .65rem;
    display:inline-flex; align-items:center; gap:.35rem; background:#fff;
    transition:background .12s ease, border-color .12s ease;
  }
  .stRadio [role="radiogroup"] > div:hover{ background:#f9fafb }
  .stRadio [role="radiogroup"] > div[aria-checked="true"]{ font-weight:600 }

  /* Selected color per option order: 1 Yes, 2 Partially, 3 No, 4 Not sure */
  .stRadio [role="radiogroup"] > div:nth-child(1)[aria-checked="true"]{ background:#e8f7ee; border-color:#cceedd; color:#0f5132; }
  .stRadio [role="radiogroup"] > div:nth-child(2)[aria-checked="true"]{ background:#fff5d6; border-color:#ffe7ad; color:#8a6d00; }
  .stRadio [role="radiogroup"] > div:nth-child(3)[aria-checked="true"]{ background:#ffe5e5; border-color:#ffcccc; color:#842029; }
  .stRadio [role="radiogroup"] > div:nth-child(4)[aria-checked="true"]{ background:#eef2f7; border-color:#e2e8f0; color:#334155; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Options & constants
# ─────────────────────────────────────────────────────────────
EMPLOYEE_RANGES = ["1–5","6–10","10–25","26–50","51–100","More than 100"]
YEARS_OPTIONS   = ["<1 year","1–3 years","3–5 years","5–10 years","10+ years"]
WORK_MODE       = ["Local & in-person","Online / remote","A mix of both"]
INDUSTRY_OPTIONS = [
    "Retail & Hospitality","Professional / Consulting / Legal / Accounting","Manufacturing / Logistics",
    "Creative / Marketing / IT Services","Health / Wellness / Education","Public sector / Non-profit",
    "Other (type below)",
]
TURNOVER_OPTIONS = [
    "<€100k","€100k–€200k","€200k–€300k","€300k–€400k","€400k–€500k",
    "€500k–€600k","€600k–€700k","€700k–€800k","€800k–€900k","€900k–€1M",
    "€1M–€2M","€2M–€5M","€5M–€10M",">€10M",
]
REGION_OPTIONS = ["EU / EEA","UK","United States","Other / Multi-region"]

# Full names (acronyms only in parentheses)
CRITICAL_SYSTEMS = [
    "Enterprise Resource Planning (ERP)",
    "Point of Sale (POS)",
    "Customer Relationship Management (CRM)",
    "Electronic Health Record (EHR)",
    "Content Management System (CMS)",
    "Other (type below)"
]
WORK_ENVIRONMENTS = ["Local servers","Cloud apps","Hybrid"]
REMOTE_RATIO = ["Mostly on-site","Hybrid","Fully remote"]
DATA_TYPES = ["Customer personal data (PII)","Employee/staff data","Health/medical data","Financial/transaction data"]
CROSS_BORDER = ["EU-only","Includes Non-EU regions","Unsure"]
CERTIFICATION_OPTIONS = [
    "None","ISO/IEC 27001","Cyber Essentials (UK)","SOC 2","GDPR compliance program",
    "PCI DSS (Payment Cards)","HIPAA (US healthcare)","NIS2 readiness","Other (type below)"
]

# Traffic-light choices
TRAFFIC_LABELS = ["🟢 Yes","🟡 Partially","🔴 No","🤔 Not sure"]
LABEL_TO_PLAIN = {"🟢 Yes":"Yes","🟡 Partially":"Partially","🔴 No":"No","🤔 Not sure":"Not sure"}
PLAIN_TO_LABEL = {v:k for k,v in LABEL_TO_PLAIN.items()}

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
    business_region=REGION_OPTIONS[0],
    # Step 2 — quick checks
    bp_it_manager="", bp_inventory="", bp_byod="", bp_sensitive="",
    df_website="", df_https="", df_email="", df_social="", df_review="",
    # Step 3 — context
    critical_systems=[], critical_systems_other="",
    primary_work_env=WORK_ENVIRONMENTS[1],
    remote_ratio=REMOTE_RATIO[1],
    data_types=[], cross_border=CROSS_BORDER[0],
    certifications=["None"], certifications_other="",
    bp_card_payments="",
    # Detailed
    detailed_sections=[], detailed_scores={}
)
for k,v in defaults.items():
    st.session_state.setdefault(k,v)

# ─────────────────────────────────────────────────────────────
# Helper fns (size/industry/region, tags, RAG, progress, radios)
# ─────────────────────────────────────────────────────────────
TURNOVER_TO_SIZE = {**{k:"Micro" for k in TURNOVER_OPTIONS[:11]}, **{"€2M–€5M":"Small","€5M–€10M":"Small",">€10M":"Medium"}}
EMP_RANGE_TO_SIZE = {"1–5":"Micro","6–10":"Micro","10–25":"Small","26–50":"Small","51–100":"Medium","More than 100":"Medium"}
INDUSTRY_TAGS = {
    "Retail & Hospitality":"retail","Professional / Consulting / Legal / Accounting":"professional_services",
    "Manufacturing / Logistics":"manufacturing","Creative / Marketing / IT Services":"it_services",
    "Health / Wellness / Education":"health_edu","Public sector / Non-profit":"public_nonprofit","Other (type below)":"other"
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
        if   "iso" in cl: tags.add("cert:iso27001")
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
    # systems — detect acronyms inside parentheses
    for s in st.session_state.critical_systems or []:
        sl=s.lower()
        if "(erp)" in sl: tags.add("system:erp")
        elif "(pos)" in sl: tags.add("system:pos")
        elif "(crm)" in sl: tags.add("system:crm")
        elif "(ehr)" in sl: tags.add("system:ehr")
        elif "(cms)" in sl: tags.add("system:cms")
        elif "other" in sl: tags.add("system:other")
    # data types
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
    sys=("🟢 Good","green") if inv=="yes" else ("🟡 Partial","amber") if inv in {"partially"} else ("🔴 At risk","red") if inv in {"no","not sure"} else ("⚪ Unknown","")
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

def progress(step:int, total:int, label:str=""):
    pct=max(0,min(step,total))/total
    st.progress(pct, text=label or f"Step {step} of {total}")

# Traffic-light radio storing plain values
def radio_traffic(prompt:str, key:str, *, horizontal=True):
    cur_plain = st.session_state.get(key, "")
    index = TRAFFIC_LABELS.index(PLAIN_TO_LABEL[cur_plain]) if cur_plain in PLAIN_TO_LABEL else 0
    picked = st.radio(prompt, TRAFFIC_LABELS, index=index, horizontal=horizontal, key=f"pretty__{key}", label_visibility="visible")
    st.session_state[key] = LABEL_TO_PLAIN[picked]

# ─────────────────────────────────────────────────────────────
# Detailed sections (incl. Governance) — richer “why we ask”
# ─────────────────────────────────────────────────────────────
def section(title_id, title, purpose, qlist):
    return {"id":title_id, "title":title, "purpose":purpose, "questions":qlist}

SECTION_3 = section("Access & Identity","🔐 Access & Identity Management",
    "Control of user access and authentication. We ask these to see how easily an attacker could reuse a password or escalate access.",
    [
        {"id":"ai_pw","t":"🔑 Are strong passwords required for all accounts?","h":"Why: Weak/reused passwords cause most breaches. Aim for 10–12+ chars and a manager for everyone."},
        {"id":"ai_mfa","t":"🛡️ Is Multi-Factor Authentication (MFA) enabled for key accounts?","h":"Why: MFA blocks most credential theft. Start with email, admin and finance."},
        {"id":"ai_admin","t":"🧰 Are admin rights limited to only those who need them?","h":"Why: Admin = ‘keys to the kingdom’. Grant temporarily; review quarterly; monitor sign-ins."},
        {"id":"ai_shared","t":"👥 Are shared accounts avoided or controlled?","h":"Why: Shared = no accountability. Prefer named accounts; if shared, rotate & log usage."},
        {"id":"ai_leavers","t":"🚪 Are old or unused accounts removed promptly?","h":"Why: Dormant accounts are easy targets. Disable on the day someone leaves."},
    ])

SECTION_4 = section("Device & Data","💻 Device & Data Protection",
    "We check how well devices and company data are protected in case of loss, theft or malware.",
    [
        {"id":"dd_lock","t":"🔒 Are all devices protected with a password or PIN?","h":"Why: Stops casual access if a device is lost; enable auto-lock (≤10 minutes)."},
        {"id":"dd_fde","t":"💽 Is full-disk encryption enabled on laptops and mobiles?","h":"Why: Encryption protects data at rest. BitLocker / FileVault / built-in mobile."},
        {"id":"dd_edr","t":"🧿 Is reputable antivirus/EDR installed and active on all devices?","h":"Why: Detects and contains malware. Defender, CrowdStrike, SentinelOne etc."},
        {"id":"dd_backup","t":"📦 Are important business files backed up regularly?","h":"Why: Ransomware and accidents happen. Use 3-2-1 rule; include cloud data."},
        {"id":"dd_restore","t":"🧪 Are backups tested so you know restore works?","h":"Why: Untested backups fail. Restore one file/VM at least quarterly."},
        {"id":"dd_usb","t":"🧰 Are staff trained to handle suspicious files/USBs?","h":"Why: Common infection path. Block unknown USBs; preview links before clicking."},
        {"id":"dd_wifi","t":"📶 Are company devices separated from personal ones on Wi-Fi?","h":"Why: Segmentation reduces spread. Use Guest vs Corporate SSIDs."},
    ])

SECTION_5 = section("System & Software Updates","🧩 System & Software Updates",
    "Unpatched systems are easy to scan and exploit. This checks how quickly you close known holes.",
    [
        {"id":"su_os_auto","t":"♻️ Are operating systems kept up to date automatically?","h":"Why: Removes known bugs fast. Enforce via MDM/RMM if possible."},
        {"id":"su_apps","t":"🧩 Are business applications updated regularly?","h":"Why: Browsers and productivity apps are frequent targets; use auto-update channels."},
        {"id":"su_unsupported","t":"⛔ Any devices running unsupported/outdated systems?","h":"Why: No patches = high risk. Replace/upgrade or isolate until replaced."},
        {"id":"su_review","t":"🗓️ Do you have a monthly reminder to review updates?","h":"Why: Habits win. Add a recurring task or use MSP reports."},
    ])

SECTION_6 = section("Incident Preparedness","🚨 Incident Preparedness",
    "Breaches are chaotic. A few simple practices reduce damage and downtime.",
    [
        {"id":"ip_report","t":"📣 Do employees know how to report incidents or suspicious activity?","h":"Why: Early reporting saves time. Create a phishing mailbox or Slack channel."},
        {"id":"ip_plan","t":"📝 Do you have a simple incident response plan?","h":"Why: Clear steps in a crisis. 1-page checklist: who to call, what to collect, who to notify."},
        {"id":"ip_log","t":"🧾 Are incident details recorded when they occur?","h":"Why: Good records speed recovery and insurance/legal responses."},
        {"id":"ip_contacts","t":"📇 Are key contacts known for emergencies?","h":"Why: No scrambling. Internal IT, MSP, cyber insurer, legal, data-protection contact."},
        {"id":"ip_test","t":"🎯 Have you tested or simulated a cyber incident?","h":"Why: Table-tops reveal gaps; run two 30-minute sessions a year."},
    ])

SECTION_7 = section("Vendor & Cloud","☁️ Vendor & Cloud Security",
    "Suppliers and SaaS are part of your security. These questions check how you manage that shared risk.",
    [
        {"id":"vc_cloud","t":"☁️ Do you use cloud tools to store company data?","h":"Why: Identity security (MFA) is critical; list your key SaaS and data locations."},
        {"id":"vc_mfa","t":"🔐 Are cloud accounts protected with MFA and strong passwords?","h":"Why: Stops account takeovers; enforce tenant-wide MFA."},
        {"id":"vc_review","t":"🔎 Do you review how vendors protect your data?","h":"Why: Contracts/DPA, ISO 27001/SOC 2, and breach terms matter."},
        {"id":"vc_access","t":"📜 Do you track which suppliers have access to systems/data?","h":"Why: Clear joiners/leavers for vendors; remove unused integrations."},
        {"id":"vc_notify","t":"🚨 Will vendors notify you promptly if they have a breach?","h":"Why: You need time to respond to your customers and regulators."},
    ])

SECTION_8 = section("Awareness & Training","🧠 Awareness & Training",
    "People block most attacks when they know what to look for. These items measure that culture.",
    [
        {"id":"at_training","t":"🎓 Have employees received any cybersecurity training?","h":"Why: Even 30 minutes helps. Track completion."},
        {"id":"at_phish","t":"🐟 Do staff know how to spot phishing/scam emails?","h":"Why: Most incidents start with email. Teach link/URL checks and reporting."},
        {"id":"at_onboard","t":"🧭 Are new employees briefed during onboarding?","h":"Why: Consistency from day one. Include password manager + MFA."},
        {"id":"at_reminders","t":"📢 Do you share posters, reminders, or tips?","h":"Why: Small nudges keep vigilance high."},
        {"id":"at_lead","t":"🤝 Does management actively promote cybersecurity?","h":"Why: Leadership attention drives completion rates."},
    ])

SECTION_9 = section("Governance","🏛️ Governance",
    "Policies, roles, risk and measurement — the glue that keeps improvements in place.",
    [
        {"id":"gov_policies","t":"📘 Do you have basic written policies (Acceptable Use, Bring-Your-Own-Device, Backup, Incident, Vendor)?","h":"Why: Short, findable policies guide day-to-day decisions."},
        {"id":"gov_roles","t":"🧩 Are security responsibilities clear (who approves access, who reviews logs, who owns backups)?","h":"Why: No gaps or overlap; a simple RACI works."},
        {"id":"gov_risk","t":"📊 Do you keep a simple risk/issue log with owners and due dates?","h":"Why: Makes priorities visible; review monthly."},
        {"id":"gov_reviews","t":"🗓️ Are routine reviews scheduled (access recertification, patch status, restore test)?","h":"Why: Cadence turns good intentions into results."},
        {"id":"gov_metrics","t":"📈 Do you track 3–5 metrics (MFA coverage, patch age, backup success, training completion)?","h":"Why: Trends show progress to leadership and customers."},
    ])

ALL_SECTIONS = [SECTION_3, SECTION_4, SECTION_5, SECTION_6, SECTION_7, SECTION_8, SECTION_9]
BASELINE_IDS = {"Access & Identity","Device & Data","System & Software Updates","Awareness & Training"}  # Governance added in detailed

def render_section(sec: Dict):
    st.markdown(f"### {sec['title']}")
    st.caption(sec["purpose"])
    for q in sec["questions"]:
        st.markdown(f"<div class='qwrap'><div class='qtitle'>{q['t']}</div>", unsafe_allow_html=True)
        radio_traffic(" ", key=q["id"])
        st.markdown(f"<div class='hint'>💡 {q['h']}</div></div>", unsafe_allow_html=True)

def section_score(sec: Dict) -> float:
    vals=[st.session_state.get(q["id"],"") for q in sec["questions"]]
    risk={"Yes":0,"Partially":1,"Not sure":1,"No":2}
    return round(sum(risk.get(v,1) for v in vals)/len(vals),2) if vals else 0.0

def pick_active_sections(tags:set):
    active=set(BASELINE_IDS)
    if "size:Small" in tags or "size:Medium" in tags: active.add("Incident Preparedness")
    if any(t in tags for t in ["infra:cloud","system:pos","geo:crossborder"]): active.add("Vendor & Cloud")
    active.add("Governance")
    order=[s["id"] for s in ALL_SECTIONS]
    return [sid for sid in order if sid in active]

# ─────────────────────────────────────────────────────────────
# LANDING
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Landing":
    progress(0, 6, "Welcome")
    st.markdown("## 🛡️ SME Cybersecurity Self-Assessment")
    st.caption("Assess · Understand · Act — in under 15 minutes.")
    c1, c2 = st.columns(2)
    with c1:
        st.write("• 🗣️ Plain-language questions")
        st.write("• 📚 Traceable to NIST/ISO")
    with c2:
        st.write("• ⏱️ 10–15 minutes")
        st.write("• 🧪 Practical, safe examples")
    if st.button("Start ➜", type="primary"):
        go("Step 1")

# ─────────────────────────────────────────────────────────────
# STEP 1 — Business basics
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 1":
    progress(1, 6, "Step 1 of 6 — Business basics")
    st.markdown("## 🧭 Tell us about the business")
    st.caption("Just the basics — the detailed bits come later.")

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
        if st.session_state.sector_label == "Other (type below)" and not st.session_state.sector_other.strip(): missing.append("industry")

        cA, cB = st.columns(2)
        with cA:
            if st.button("⬅ Back"):
                go("Landing")
        with cB:
            if st.button("Continue ➜", type="primary", disabled=len(missing)>0):
                go("Step 2")

# ─────────────────────────────────────────────────────────────
# STEP 2 — Quick checks (Q1–Q9)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 2":
    progress(2, 6, "Step 2 of 6 — Quick checks")
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
            st.markdown("<div class='qwrap'><div class='qtitle'>Q1. 🧑‍💻 Who looks after your IT day-to-day?</div>", unsafe_allow_html=True)
            st.markdown("<div class='hint'>We mean laptops/phones, Wi-Fi, email, website, point-of-sale, cloud apps, file storage/backup. Why: ownership clarifies who drives fixes.</div>", unsafe_allow_html=True)
            st.radio(" ", ["Self-managed","Outsourced IT","Shared responsibility","Not sure"],
                     key="bp_it_manager", horizontal=True, label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='qwrap'><div class='qtitle'>Q2. 📁 Do you keep a simple list of company devices (laptops, phones, servers)?</div>", unsafe_allow_html=True)
            st.markdown("<div class='hint'>Why: an asset list reveals forgotten or unmanaged gear and speeds incident response.</div>", unsafe_allow_html=True)
            radio_traffic(" ", key="bp_inventory")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='qwrap'><div class='qtitle'>Q3. 📱 Do people use personal devices for work (BYOD)?</div>", unsafe_allow_html=True)
            st.markdown("<div class='hint'>Why: personal devices can be less protected — set minimum rules (screen lock, updates, encryption, MFA for work apps).</div>", unsafe_allow_html=True)
            st.radio(" ", ["Yes","Sometimes","No","Not sure"], key="bp_byod", horizontal=True, label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='qwrap'><div class='qtitle'>Q4. 🔐 Do you handle sensitive customer or financial data?</div>", unsafe_allow_html=True)
            st.markdown("<div class='hint'>Why: higher protection and backup/testing are needed; may trigger GDPR/PCI/HIPAA duties.</div>", unsafe_allow_html=True)
            st.radio(" ", ["Yes","No","Not sure"], key="bp_sensitive", horizontal=True, label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
            st.markdown("<div class='qwrap'><div class='qtitle'>Q5. 🕸️ Do you have a public website?</div>", unsafe_allow_html=True)
            st.radio(" ", ["Yes","No"], key="df_website", horizontal=True, label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='qwrap'><div class='qtitle'>Q6. 🔒 Is your website HTTPS (padlock in the browser)?</div>", unsafe_allow_html=True)
            radio_traffic(" ", key="df_https")
            st.markdown("<div class='hint'>Why: HTTPS encrypts traffic and builds visitor trust; search engines expect it.</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='qwrap'><div class='qtitle'>Q7. ✉️ Do you use business email addresses?</div>", unsafe_allow_html=True)
            radio_traffic(" ", key="df_email")
            st.markdown("<div class='hint'>Why: personal email raises phishing and takeover risk; custom domains plus MFA are safer.</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='qwrap'><div class='qtitle'>Q8. 📣 Is your business active on social media?</div>", unsafe_allow_html=True)
            st.radio(" ", ["Yes","No"], key="df_social", horizontal=True, label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='qwrap'><div class='qtitle'>Q9. 🔎 Do you regularly check what’s public about the company or staff online?</div>", unsafe_allow_html=True)
            st.radio(" ", ["Yes","Sometimes","No"], key="df_review", horizontal=True, label_visibility="collapsed")
            st.markdown("<div class='hint'>Why: oversharing reveals systems and targets (emails, screenshots, staff lists).</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with prev:
        st.write(""); st.write("")
        if st.button("⬅ Back to Step 1"):
            go("Step 1")
        required = ["bp_it_manager","bp_inventory","bp_byod","bp_sensitive","df_website","df_https","df_email","df_social","df_review"]
        missing = [k for k in required if not st.session_state.get(k)]
        if st.button("Continue ➜", type="primary", disabled=len(missing)>0):
            go("Step 3")

# ─────────────────────────────────────────────────────────────
# STEP 3 — Operational context (recommended)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 3":
    progress(3, 6, "Step 3 of 6 — Operational context (recommended)")
    st.markdown("## 🏗️ Operational context (recommended)")
    st.caption("These details tailor the advice and compliance notes.")

    cA, cB = st.columns(2)
    with cA:
        st.multiselect("🧩 Critical systems in use", CRITICAL_SYSTEMS, key="critical_systems", default=st.session_state.critical_systems)
        st.markdown("<div class='hint'>What this is: the business apps you rely on (for example: Enterprise Resource Planning, Point of Sale, Customer Relationship Management, Electronic Health Record, Content Management System).<br>Why it matters: attackers target the systems that keep you trading; naming them lets us tailor actions and vendor checks.<br><i>Examples: ERP (SAP Business One, Odoo), POS (Square, Lightspeed), CRM (HubSpot), EHR (Epic), CMS (WordPress).</i></div>", unsafe_allow_html=True)
        if "Other (type below)" in st.session_state.critical_systems:
            st.text_input("✍️ Specify other system", key="critical_systems_other", value=st.session_state.critical_systems_other)

        st.radio("🏗️ Primary work environment", WORK_ENVIRONMENTS, key="primary_work_env", horizontal=True, index=WORK_ENVIRONMENTS.index(st.session_state.primary_work_env))
        st.markdown("<div class='hint'>What this is: where your files and apps mainly live.<br>Why it matters: local servers need device/network controls; cloud needs strong identity (MFA, admin hygiene).</div>", unsafe_allow_html=True)

        st.radio("🏠 Remote work ratio", REMOTE_RATIO, key="remote_ratio", horizontal=True, index=REMOTE_RATIO.index(st.session_state.remote_ratio))
        st.markdown("<div class='hint'>What this is: how often people work away from the office.<br>Why it matters: more remote work → more focus on MFA, device encryption and phishing awareness.</div>", unsafe_allow_html=True)

    with cB:
        st.multiselect("🔎 Types of personal data handled", DATA_TYPES, key="data_types", default=st.session_state.data_types)
        st.markdown("<div class='hint'>What this is: the kinds of personal or sensitive information you hold (customers, staff, health, payments).<br>Why it matters: different data → different obligations (e.g., GDPR, HIPAA, PCI) and higher protection needs.</div>", unsafe_allow_html=True)

        st.radio("🌐 Cross-border data flows", CROSS_BORDER, key="cross_border", horizontal=True, index=CROSS_BORDER.index(st.session_state.cross_border))
        st.markdown("<div class='hint'>What this is: whether personal data leaves the EU/UK.<br>Why it matters: transfers outside the EU/UK need extra contract terms and checks with vendors.</div>", unsafe_allow_html=True)

        st.multiselect("🔒 Certifications / schemes", CERTIFICATION_OPTIONS, key="certifications", default=st.session_state.certifications)
        st.markdown("<div class='hint'>What this is: security standards you follow or are aiming for.<br>Why it matters: aligns the plan with audits or customer expectations.</div>", unsafe_allow_html=True)
        if "Other (type below)" in st.session_state.certifications:
            st.text_input("✍️ Specify other scheme", key="certifications_other", value=st.session_state.certifications_other)

        st.radio("💳 Do you accept or process card payments (online or in-store)?", ["Yes","No","Not sure"], key="bp_card_payments",
                 horizontal=True, index=(["Yes","No","Not sure"].index(st.session_state.bp_card_payments) if st.session_state.bp_card_payments else 1))
        st.markdown("<div class='hint'>What this is: whether you take card data.<br>Why it matters: PCI DSS may apply; if your point-of-sale or payment service provider handles most of it, your scope is lighter but you still have duties.</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅ Back to Step 2"):
            go("Step 2")
    with c2:
        if st.button("Continue ➜", type="primary"):
            go("Step 4")

# ─────────────────────────────────────────────────────────────
# STEP 4 — Initial Summary
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 4":
    progress(4, 6, "Step 4 of 6 — Initial Summary")
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
        if st.session_state.bp_inventory not in ("Yes","Partially"): hints.append("📝 Add/finish your device list.")
        if st.session_state.df_website=='Yes' and st.session_state.df_https!='Yes': hints.append("🔒 Enable HTTPS for your website.")
        if st.session_state.bp_byod in ("Yes","Sometimes"): hints.append("📱 Set simple BYOD + MFA rules.")
        if hints: st.caption(" · ".join(hints))

    c1,c2,c3 = st.columns([1,1,2])
    with c1:
        if st.button("⬅ Back"):
            go("Step 3")
    with c2:
        if st.button("Start over"):
            for k,v in defaults.items(): st.session_state[k]=v
            go("Landing")
    with c3:
        if st.button("Continue to detailed assessment ➜", type="primary"):
            st.session_state.detailed_sections = pick_active_sections(compute_tags())
            go("Detailed")

# ─────────────────────────────────────────────────────────────
# STEP 5 — Detailed Assessment
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Detailed":
    progress(5, 6, "Step 5 of 6 — Detailed assessment")
    st.markdown("## 🧩 Detailed Assessment")
    active_ids=set(st.session_state.get("detailed_sections", []))
    sections=[s for s in ALL_SECTIONS if s["id"] in active_ids] or [SECTION_3,SECTION_4,SECTION_5,SECTION_8,SECTION_9]
    tabs=st.tabs([s["title"] for s in sections])
    for tab, s in zip(tabs, sections):
        with tab: render_section(s)

    cA, cB = st.columns(2)
    with cA:
        if st.button("⬅ Back to Summary"):
            go("Step 4")
    with cB:
        if st.button("Finish & see recommendations ➜", type="primary"):
            st.session_state["detailed_scores"]={s["id"]: section_score(s) for s in sections}
            go("Report")

# ─────────────────────────────────────────────────────────────
# STEP 6 — Report / Action Plan (numbered lists)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Report":
    progress(6, 6, "Step 6 of 6 — Action plan")
    st.markdown("## 🗺️ Action Plan & Section Status")

    scores = st.session_state.get("detailed_scores", {})
    if scores:
        cols = st.columns(len(scores))
        for (sid, sc), col in zip(scores.items(), cols):
            level = "green" if sc < 0.5 else "amber" if sc < 1.2 else "red"
            label = "Low" if level=="green" else "Medium" if level=="amber" else "High"
            with col:
                st.markdown(
                    f"<div class='card'><b>{sid}</b>"
                    f"<div class='hint'>Status: <span class='pill {level}'>{'🟢' if level=='green' else '🟡' if level=='amber' else '🔴'} {label}</span> (score {sc})</div></div>",
                    unsafe_allow_html=True
                )
    else:
        st.caption("No detailed sections answered yet. Complete the detailed assessment to see section status.")

    # Tailored action plan (numbered)
    tags = compute_tags()
    quick: List[str] = []
    foundations: List[str] = []
    nextlvl: List[str] = []

    if st.session_state.df_website=="Yes" and st.session_state.df_https!="Yes":
        quick.append("Enable HTTPS and force redirect (HTTP → HTTPS).")
    if st.session_state.df_email in ("No","Partially"):
        quick.append("Move everyone to business email (Microsoft 365/Google Workspace) and enforce MFA.")
    if st.session_state.bp_inventory not in ("Yes","Partially"):
        quick.append("Create a simple device inventory and enable full-disk encryption on laptops.")

    if st.session_state.bp_byod in ("Yes","Sometimes"):
        foundations.append("Publish a BYOD ‘rule of five’: screen lock, OS updates, disk encryption, MFA for email, approved apps.")
    foundations.append("Turn on automatic OS & app updates; remove unsupported systems.")
    foundations.append("Automate backups and test a restore quarterly.")
    foundations.append("Finalize governance basics: policy set, clear responsibilities (RACI), risk log, monthly checks, 3–5 metrics.")

    if any(t in tags for t in ["infra:cloud","system:pos","geo:crossborder"]):
        nextlvl.append("Review vendor/cloud contracts: breach notification, data location/transfer, and admin MFA.")
    if "payments:card" in tags or "system:pos" in tags:
        nextlvl.append("Confirm PCI DSS responsibilities with your payment/point-of-sale provider.")
    if any(t in tags for t in ["geo:eu","geo:uk"]):
        nextlvl.append("Document GDPR basics: Records of Processing, Data Processing Agreements, and a contact for data requests.")

    st.markdown("### ⚡ Quick wins (do these first)")
    st.markdown("<div class='card'><ol>"+ "".join([f"<li>{x}</li>" for x in (quick or ['No urgent quick wins detected.'])]) +"</ol></div>", unsafe_allow_html=True)
    st.markdown("### 🧱 Foundations to build this quarter")
    st.markdown("<div class='card'><ol>"+ "".join([f"<li>{x}</li>" for x in foundations]) +"</ol></div>", unsafe_allow_html=True)
    st.markdown("### 🚀 Next-level / compliance alignment")
    st.markdown("<div class='card'><ol>"+ "".join([f"<li>{x}</li>" for x in nextlvl]) +"</ol></div>", unsafe_allow_html=True)

    cA, cB = st.columns(2)
    with cA:
        if st.button("⬅ Back to Detailed"):
            go("Detailed")
    with cB:
        if st.button("Start over"):
            for k,v in defaults.items(): st.session_state[k]=v
            go("Landing")
