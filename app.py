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
  /* compact radios */
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
    work_mode=WORK_MODE[0],
    # Step 2 — answers (Q1–Q9)
    bp_it_manager="", bp_inventory="", bp_byod="", bp_sensitive="",
    df_website="", df_https="", df_email="", df_social="", df_review="",
)
for k,v in defaults.items():
    st.session_state.setdefault(k,v)

def resolved_industry():
    if st.session_state.sector_label == "Other (type below)":
        return st.session_state.sector_other or "Other"
    return st.session_state.sector_label

# At-a-glance (RAG)
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

# ─────────────────────────────────────────────────────────────
# Navigation helpers
# ─────────────────────────────────────────────────────────────
def go(page): 
    st.session_state.page = page
    st.rerun()

# ─────────────────────────────────────────────────────────────
# LANDING (single screen)
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
# STEP 1 — Business profile (no scroll)
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
            f'<div><b>Industry:</b> {resolved_industry()}</div>'
            f'<div><b>People:</b> {st.session_state.employee_range} · '
            f'<b>Years:</b> {st.session_state.years_in_business}</div>'
            f'<div><b>Turnover:</b> {st.session_state.turnover_label}</div>'
            f'<div><b>Work mode:</b> {st.session_state.work_mode}</div>'
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

        # Required gate
        missing = []
        if not st.session_state.person_name.strip(): missing.append("name")
        if not st.session_state.company_name.strip(): missing.append("company")
        if st.session_state.sector_label == "Other (type below)" and not st.session_state.sector_other.strip():
            missing.append("industry")

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
# STEP 2 — Practices in TABS (no scroll)
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
            f'<div><b>Industry:</b> {resolved_industry()}</div>'
            f'<div><b>People:</b> {st.session_state.employee_range} · '
            f'<b>Years:</b> {st.session_state.years_in_business}</div>'
            f'<div><b>Turnover:</b> {st.session_state.turnover_label}</div>'
            f'<div><b>Work mode:</b> {st.session_state.work_mode}</div>'
            f'</div>', unsafe_allow_html=True
        )
        # Mini “live” glances
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
        st.write("")  # spacer to align buttons
        st.write("")
        if st.button("⬅ Back to Step 1"):
            go("Step 1")
        # validation for Q1–Q9
        required = ["bp_it_manager","bp_inventory","bp_byod","bp_sensitive","df_website","df_https","df_email","df_social","df_review"]
        missing = [k for k in required if not st.session_state.get(k)]
        disabled = len(missing) > 0
        if st.button("Finish Initial Assessment ➜", type="primary", disabled=disabled):
            go("Step 3")

# ─────────────────────────────────────────────────────────────
# STEP 3 — Summary (one screen)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "Step 3":
    st.markdown("##### Step 3 of 3")
    st.markdown("## Initial Assessment Summary")

    over_txt, over_class, over_msg = overall_badge()
    st.markdown(f'<span class="chip {over_class}">Overall digital dependency: <b>{over_txt}</b></span>', unsafe_allow_html=True)
    st.caption(over_msg)

    a, b = st.columns([1.1, 2])
    with a:
        st.markdown("#### Snapshot")
        st.markdown(
            f'<div class="card">'
            f'<div><b>Business:</b> {st.session_state.company_name}</div>'
            f'<div><b>Industry:</b> {resolved_industry()}</div>'
            f'<div><b>People:</b> {st.session_state.employee_range} · '
            f'<b>Years:</b> {st.session_state.years_in_business} · '
            f'<b>Turnover:</b> {st.session_state.turnover_label}</div>'
            f'<div><b>Work mode:</b> {st.session_state.work_mode}</div>'
            f'</div>', unsafe_allow_html=True
        )
    with b:
        st.markdown("#### At-a-glance")
        sys,ppl,net = area_rag()
        st.markdown(f'<span class="chip {sys[1]}">🖥️ Systems & devices · {sys[0]}</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="chip {ppl[1]}">👥 People & access · {ppl[0]}</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="chip {net[1]}">🌐 Online exposure · {net[0]}</span>', unsafe_allow_html=True)

    # Keep on one screen: details behind two small expanders
    st.markdown("---")
    colS, colR = st.columns(2)
    with colS:
        with st.expander("✅ Strengths"):
            strengths = []
            if st.session_state.df_https == "Yes":
                strengths.append("Website uses HTTPS (encrypted traffic).")
            if st.session_state.bp_inventory in ("Yes","Partially"):
                strengths.append("You keep a device list (even partial helps).")
            if not strengths:
                strengths.append("Solid starting point across core practices.")
            st.markdown("<ul>"+ "".join([f"<li>{x}</li>" for x in strengths]) +"</ul>", unsafe_allow_html=True)
    with colR:
        with st.expander("⚠️ Areas to improve", expanded=True):
            risks = []
            if st.session_state.df_email == "No":
                risks.append("Personal email in use — move to business email to cut phishing risk.")
            if st.session_state.bp_byod in ("Yes","Sometimes"):
                risks.append("BYOD needs clear rules, MFA and basic hardening.")
            if st.session_state.bp_sensitive == "Yes":
                risks.append("Sensitive data calls for regular backups and strong access control (MFA).")
            if st.session_state.df_website == "Yes" and st.session_state.df_https != "Yes":
                risks.append("Add HTTPS to your website (padlock) to encrypt traffic and build trust.")
            if not risks:
                risks.append("Keep improving: test incident response and tighten MFA hygiene.")
            st.markdown("<ul>"+ "".join([f"<li>{x}</li>" for x in risks]) +"</ul>", unsafe_allow_html=True)

    c1,c2,c3 = st.columns([1,1,2])
    with c1:
        if st.button("⬅ Back to Step 2"):
            go("Step 2")
    with c2:
        if st.button("Start over"):
            for k,v in defaults.items(): st.session_state[k]=v
            go("Landing")
    with c3:
        st.write("")  # placeholder for future actions
