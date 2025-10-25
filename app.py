import streamlit as st

# ------------------------------------------------------------
# App shell & global style
# ------------------------------------------------------------
st.set_page_config(page_title="SME Cybersecurity Self-Assessment", layout="wide")

st.markdown("""
<style>
  .block-container {max-width: 1100px;}
  h1, h2, h3, h4 {margin:.2rem 0 .6rem}
  .micro {color:#6b7280; font-size:.92rem; margin-top:-.4rem}
  .hint {color:#6b7280; font-size:.9rem; font-style:italic; margin:.15rem 0 .3rem}
  .snap {border:1px solid #eceff3; border-radius:12px; padding:8px 12px; background:#fff}
  .pill {display:inline-block; border-radius:999px; padding:.2rem .6rem; border:1px solid #e5e7eb; font-size:.9rem; color:#374151;}
  .metric {border:1px solid #eceff3; border-radius:12px; padding:10px; text-align:center;}
  .metric h4{margin:.1rem 0 .25rem; font-size:1rem;}
  .metric .v{font-size:1.05rem; font-weight:700;}
  .badge {display:inline-flex; align-items:center; gap:.45rem; padding:.25rem .6rem;
          border-radius:999px; font-weight:600; background:#e3f7e8; color:#0f5132; border:1px solid #c8eed1;}
  .warn {background:#fff6db; color:#8a6d00; border-color:#fde9a9;}
  .danger {background:#ffe6e6; color:#842029; border-color:#ffcdcd;}
  .muted {color:#6b7280; font-size:.92rem;}
  .card {border:1px solid #e6e8ec; border-radius:12px; padding:10px 12px; background:#fff;}
  .cta-row {margin-top:.5rem;}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# Options & helpers
# ------------------------------------------------------------
EMPLOYEE_RANGES = ["1–5", "6–10", "10–25", "26–50", "51–100", "More than 100"]
YEARS_OPTIONS   = ["<1 year", "1–3 years", "3–5 years", "5–10 years", "10+ years"]

INDUSTRY_OPTIONS = [
    "Retail & Hospitality",
    "Professional / Consulting / Legal / Accounting",
    "Manufacturing / Logistics",
    "Creative / Marketing / IT Services",
    "Health / Wellness / Education",
    "Public sector / Non-profit",
    "Other (type below)",
]

WORK_MODE = ["Local & in-person", "Online / remote", "A mix of both"]

TURNOVER_OPTIONS = [
    "<€100k",
    "€100k–€200k", "€200k–€300k", "€300k–€400k", "€400k–€500k",
    "€500k–€600k", "€600k–€700k", "€700k–€800k", "€800k–€900k", "€900k–€1M",
    "€1M–€2M", "€2M–€5M", "€5M–€10M", ">€10M"
]

# Session defaults
defaults = {
    "page": "Landing",
    # Step 1
    "person_name": "",
    "company_name": "",
    "sector_label": INDUSTRY_OPTIONS[0],
    "sector_other": "",
    "years_in_business": YEARS_OPTIONS[0],
    "employee_range": EMPLOYEE_RANGES[0],
    "turnover_label": TURNOVER_OPTIONS[0],
    "work_mode": WORK_MODE[0],
    # Step 2 – answers (keys are owned by widgets on Step 2)
    "bp_it_manager": "",
    "bp_inventory": "",
    "bp_byod": "",
    "bp_sensitive": "",
    "df_website": "",
    "df_https": "",
    "df_email": "",
    "df_social": "",
    "df_review": "",
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

def next_page(name: str):
    st.session_state.page = name
    st.rerun()

def resolved_industry() -> str:
    if st.session_state.sector_label == "Other (type below)":
        return st.session_state.sector_other or "Other"
    return st.session_state.sector_label

def ui_progress(step:int, total:int=3, text:str=""):
    cols = st.columns([1,5,1])
    with cols[1]:
        st.markdown(f'<span class="pill">Step {step} of {total}</span>  {text}', unsafe_allow_html=True)

def profile_snapshot(compact:bool=True):
    if compact:
        st.markdown(
            f'<div class="snap">'
            f'<b>Business:</b> {st.session_state.company_name or "—"}  ·  '
            f'<b>Industry:</b> {resolved_industry()}'
            f'</div>', unsafe_allow_html=True)
    else:
        st.subheader("Snapshot")
        st.markdown(
            f"**Business:** {st.session_state.company_name or '—'}  \n"
            f"**Industry:** {resolved_industry()}  \n"
            f"**People:** {st.session_state.employee_range or '—'} • "
            f"**Years:** {st.session_state.years_in_business or '—'} • "
            f"**Turnover:** {st.session_state.turnover_label or '—'}  \n"
            f"**Work mode:** {st.session_state.work_mode or '—'}"
        )

def validate_initial1():
    errs = []
    if not st.session_state.person_name.strip(): errs.append("Please enter your name.")
    if not st.session_state.company_name.strip(): errs.append("Please enter the business name.")
    if st.session_state.sector_label == "Other (type below)" and not st.session_state.sector_other.strip():
        errs.append("Please type your industry.")
    if not st.session_state.years_in_business: errs.append("Select how long you’ve been in business.")
    if not st.session_state.employee_range: errs.append("Select the number of people.")
    if not st.session_state.turnover_label: errs.append("Select annual turnover.")
    if not st.session_state.work_mode: errs.append("Select work mode.")
    return (len(errs) == 0), errs

def section1_complete():
    return all(st.session_state.get(k) for k in ["bp_it_manager","bp_inventory","bp_byod","bp_sensitive"])

def section2_complete():
    return all(st.session_state.get(k) for k in ["df_website","df_https","df_email","df_social","df_review"])

def digital_dependency_level():
    score = 0
    if st.session_state.df_website == "Yes":
        score += 1
        if st.session_state.df_https == "No":
            score += 1
    if st.session_state.df_email == "No":
        score += 2
    elif st.session_state.df_email == "Partially":
        score += 1
    if st.session_state.bp_byod in ("Yes", "Sometimes"):
        score += 1
    if st.session_state.bp_sensitive == "Yes":
        score += 1
    if score <= 1:
        return ("Low", "🟢")
    if score <= 3:
        return ("Medium", "🟡")
    return ("High", "🔴")

def summary_highlights_and_blindspots():
    hi, bs = [], []
    if st.session_state.df_https == "Yes":
        hi.append("Website uses HTTPS (encrypted traffic).")
    if st.session_state.bp_inventory in ("Yes", "Partially"):
        hi.append("You keep a device list (even partial helps).")
    if st.session_state.df_email == "No":
        bs.append("Personal email in use — move to business email to cut phishing risk.")
    if st.session_state.bp_byod in ("Yes", "Sometimes"):
        bs.append("BYOD needs clear rules, MFA and basic hardening.")
    if st.session_state.bp_sensitive == "Yes":
        bs.append("Sensitive data calls for regular backups and strong access control (MFA).")
    if st.session_state.df_website == "Yes" and st.session_state.df_https != "Yes":
        bs.append("Add HTTPS to your website (padlock) to encrypt traffic and build trust.")
    return hi or ["Solid starting point across core practices."], bs or ["Keep improving: test incident response and tighten MFA hygiene."]

# ------------------------------------------------------------
# PAGES
# ------------------------------------------------------------

# Landing
if st.session_state.page == "Landing":
    st.title("SME Cybersecurity Self-Assessment")
    st.subheader("Assess · Understand · Act — in under 15 minutes.")
    st.caption("Plain-language questions that show your exposure and the top actions to take next. No sign-up; answers stay on this device.")

    cta1, cta2 = st.columns([1,1])
    if cta1.button("Start ➜", type="primary"):
        next_page("Initial 1")
    if cta2.button("See sample results"):
        next_page("Summary")

    st.markdown("---")
    st.markdown("#### What to expect")
    st.markdown("- 9 quick checks covering essential security practices  \n"
                "- Traffic-light results with strengths and risks  \n"
                "- Action plan aligned to recognised standards (NIST CSF / ISO/IEC 27001)  \n"
                "- Runs locally — no data uploaded")

# Step 1 — Business
elif st.session_state.page == "Initial 1":
    ui_progress(1, 3, "· Tell us about the business")
    st.title("Step 1 of 3 – Tell us about the business")
    st.caption("Just the basics. This helps us tailor the next questions in under 2 minutes.")

    left, right = st.columns([1, 2], gap="large")
    with left:
        profile_snapshot(compact=False)

    with right:
        st.markdown("#### About you")
        st.session_state.person_name = st.text_input("👤 Your name *", value=st.session_state.person_name)
        st.markdown('<div class="micro">All fields marked * are required.</div>', unsafe_allow_html=True)

        st.markdown("#### About the business")
        st.session_state.company_name = st.text_input("🏢 Business name *", value=st.session_state.company_name)

        st.session_state.sector_label = st.selectbox(
            "🏷️ Industry / core service *",
            INDUSTRY_OPTIONS,
            index=INDUSTRY_OPTIONS.index(st.session_state.sector_label)
            if st.session_state.sector_label in INDUSTRY_OPTIONS else 0,
            help="Pick the closest match. Choose 'Other' to type it."
        )
        if st.session_state.sector_label == "Other (type below)":
            st.session_state.sector_other = st.text_input("✍️ Type your industry *",
                value=st.session_state.sector_other, placeholder="e.g., Architecture, Automotive services")
        else:
            st.session_state.sector_other = ""

        colsA = st.columns(2)
        with colsA[0]:
            st.session_state.years_in_business = st.selectbox("📅 How long in business? *",
                YEARS_OPTIONS, index=YEARS_OPTIONS.index(st.session_state.years_in_business))
        with colsA[1]:
            st.session_state.employee_range = st.selectbox("👥 People (incl. contractors) *",
                EMPLOYEE_RANGES, index=EMPLOYEE_RANGES.index(st.session_state.employee_range))

        st.session_state.turnover_label = st.selectbox("💶 Approx. annual turnover *",
            TURNOVER_OPTIONS,
            index=TURNOVER_OPTIONS.index(st.session_state.turnover_label)
            if st.session_state.turnover_label in TURNOVER_OPTIONS else 0)
        st.markdown('<div class="hint">Use your best estimate — rough ranges are fine.</div>', unsafe_allow_html=True)

        st.markdown("#### How you operate")
        st.session_state.work_mode = st.radio("🧭 Work mode *", WORK_MODE, horizontal=True,
            index=WORK_MODE.index(st.session_state.work_mode))

    st.markdown("---")
    valid, errs = validate_initial1()
    c1, c2 = st.columns([1,1])
    if c1.button("⬅ Back"):
        next_page("Landing")
    if c2.button("Continue ➜", type="primary", disabled=not valid):
        next_page("Initial 2")
    if not valid:
        for e in errs:
            st.caption(f"⚠️ {e}")

# Step 2 — Cyber practices
elif st.session_state.page == "Initial 2":
    ui_progress(2, 3, "· Your cyber practices")
    st.title("Step 2 of 3 – Your Cyber Practices")
    st.caption("Almost there — just a few short questions about how you use tech. No trick questions.")

    st.markdown("#### Snapshot")
    profile_snapshot(compact=True)
    st.markdown("---")

    s1_open = not section1_complete()
    with st.expander("🧭 Section 1 — Business profile (4 questions)" + (" ✓" if not s1_open else ""), expanded=s1_open):
        st.markdown("**Q1. 🖥️ Who looks after your IT day-to-day?**")
        st.caption("_By IT we mean the stuff your business relies on: laptops/phones, Wi-Fi, email, website, point-of-sale, cloud apps (Google/Microsoft), file storage/backup. Who keeps these running and secure?_")
        st.radio(" ", ["Self-managed", "Outsourced IT", "Shared responsibility", "Not sure"],
                 key="bp_it_manager", label_visibility="collapsed")

        st.markdown("**Q2. 📋 Do you keep a simple list of company devices (laptops, phones, servers)?**")
        st.caption("_Helps find forgotten or unmanaged gear._")
        st.radio(" ", ["Yes", "Partially", "No", "Not sure"],
                 key="bp_inventory", label_visibility="collapsed")

        st.markdown("**Q3. 📱 Do people use personal devices for work (BYOD)?**")
        st.caption("_Example: staff reading work email on a personal phone or laptop._")
        st.radio(" ", ["Yes", "Sometimes", "No", "Not sure"],
                 key="bp_byod", label_visibility="collapsed")

        st.markdown("**Q4. 🔐 Do you handle sensitive customer or financial data?**")
        st.caption("_Examples: payment details, personal records, contracts._")
        st.radio(" ", ["Yes", "No", "Not sure"],
                 key="bp_sensitive", label_visibility="collapsed")

    s2_open = not section2_complete()
    with st.expander("🌐 Section 2 — Digital footprint (5 questions)" + (" ✓" if not s2_open else ""), expanded=s2_open):
        st.markdown("**Q5. 🕸️ Do you have a public website?**")
        st.caption("_Helps assess potential online entry points._")
        st.radio(" ", ["Yes", "No"], key="df_website", label_visibility="collapsed")

        st.markdown("**Q6. 🔒 Is your website HTTPS (padlock in the browser)?**")
        st.caption("_Encrypts traffic and builds trust with visitors._")
        st.radio(" ", ["Yes", "No", "Not sure"], key="df_https", label_visibility="collapsed")

        st.markdown("**Q7. ✉️ Do you use business email addresses (e.g., info@yourcompany.com)?**")
        st.caption("_Personal Gmail/Yahoo accounts increase phishing risk._")
        st.radio(" ", ["Yes", "Partially", "No"], key="df_email", label_visibility="collapsed")

        st.markdown("**Q8. 📣 Is your business active on social media (LinkedIn, Instagram, etc.)?**")
        st.caption("_Helps gauge your brand’s visibility online._")
        st.radio(" ", ["Yes", "No"], key="df_social", label_visibility="collapsed")

        st.markdown("**Q9. 🔎 Do you regularly check what’s public about the company or staff online?**")
        st.caption("_E.g., contact details, staff lists, screenshots that reveal systems._")
        st.radio(" ", ["Yes", "Sometimes", "No"], key="df_review", label_visibility="collapsed")

    st.markdown("---")
    b1, b2 = st.columns([1,1])
    if b1.button("⬅ Back"):
        next_page("Initial 1")
    if b2.button("Finish Initial Assessment ✅", type="primary"):
        next_page("Summary")

# Summary
elif st.session_state.page == "Summary":
    st.markdown("## ✅ Initial Assessment Summary")

    level, emoji = digital_dependency_level()
    if level == "Low":
        st.markdown(f'<span class="badge">🟢 Overall digital dependency: <b>{level}</b></span>', unsafe_allow_html=True)
        st.caption("Great job — strong digital hygiene and low exposure.")
    elif level == "Medium":
        st.markdown(f'<span class="badge warn">🟡 Overall digital dependency: <b>{level}</b></span>', unsafe_allow_html=True)
        st.caption("Balanced setup. A few quick wins will reduce risk fast.")
    else:
        st.markdown(f'<span class="badge danger">🔴 Overall digital dependency: <b>{level}</b></span>', unsafe_allow_html=True)
        st.caption("Higher exposure — prioritise quick actions to lower risk.")

    c_left, c_right = st.columns([1.15, 1.85], gap="large")
    with c_left:
        st.markdown("#### Snapshot")
        st.markdown(
            f'<div class="card">'
            f'<div><b>Business:</b> {st.session_state.company_name or "—"}</div>'
            f'<div><b>Industry:</b> {resolved_industry()}</div>'
            f'<div><b>People:</b> {st.session_state.employee_range or "—"} · '
            f'<b>Years:</b> {st.session_state.years_in_business or "—"} · '
            f'<b>Turnover:</b> {st.session_state.turnover_label or "—"}</div>'
            f'<div><b>Work mode:</b> {st.session_state.work_mode or "—"}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    def area_systems_devices():
        inv = (st.session_state.bp_inventory or "").lower()
        if inv == "yes":          return "🟢 Good", "Finish your device list."
        if inv == "partially":    return "🟡 Partial", "Complete your device list."
        if inv in {"no","not sure"}: return "🔴 At risk", "No inventory → hard to secure."
        return "⚪ Unknown", "—"

    def area_people_access():
        byod  = (st.session_state.bp_byod or "").lower()
        email = (st.session_state.df_email or "").lower()
        if byod == "no" and email == "yes":         return "🟢 Safe", "Managed devices & business email."
        if email == "no":                            return "🔴 At risk", "Personal email in use."
        if byod in {"yes","sometimes"} or email=="partially": return "🟡 Mixed", "Add MFA & BYOD rules."
        return "⚪ Unknown", "—"

    def area_online_exposure():
        web   = (st.session_state.df_website or "").lower()
        https = (st.session_state.df_https or "").lower()
        if web == "yes" and https == "yes":  return "🟢 Protected", "Site uses HTTPS."
        if web == "yes" and https == "no":   return "🔴 Exposed", "Add HTTPS (encrypt traffic)."
        if web == "yes" and https == "not sure": return "🟡 Check", "Verify HTTPS (padlock)."
        if web == "no":                      return "🟢 Low", "No public site."
        return "⚪ Unknown", "—"

    with c_right:
        st.markdown("#### At-a-glance")
        a1, a2, a3 = st.columns(3)
        s_txt, s_hint = area_systems_devices()
        p_txt, p_hint = area_people_access()
        o_txt, o_hint = area_online_exposure()
        a1.markdown(f'<div class="metric"><h4>🖥️ Systems & devices</h4><div class="v">{s_txt}</div></div>', unsafe_allow_html=True)
        a2.markdown(f'<div class="metric"><h4>👥 People & access</h4><div class="v">{p_txt}</div></div>', unsafe_allow_html=True)
        a3.markdown(f'<div class="metric"><h4>🌐 Online exposure</h4><div class="v">{o_txt}</div></div>', unsafe_allow_html=True)
        st.caption(f"🖥️ {s_hint} · 👥 {p_hint} · 🌐 {o_hint}")

    st.markdown("---")
    st.markdown("#### Strengths & Risks")
    hi, bs = summary_highlights_and_blindspots()
    s_col, r_col = st.columns(2, gap="large")
    with s_col:
        st.markdown("##### ✅ Strengths")
        st.markdown('<div class="card"><ul>'+ "".join([f"<li>{x}</li>" for x in hi]) +'</ul></div>', unsafe_allow_html=True)
    with r_col:
        st.markdown("##### ⚠️ Areas to improve")
        st.markdown('<div class="card"><ul>'+ "".join([f"<li>{x}</li>" for x in bs]) +'</ul></div>', unsafe_allow_html=True)

    with st.expander("Business details"):
        profile_snapshot(compact=False)
        st.caption("This matches the snapshot above (single source of truth).")

    with st.expander("See all answers (Q1–Q9)"):
        st.markdown(
            f"- **Q1 IT oversight:** {st.session_state.bp_it_manager or '—'}  \n"
            f"- **Q2 Device inventory:** {st.session_state.bp_inventory or '—'}  \n"
            f"- **Q3 BYOD:** {st.session_state.bp_byod or '—'}  \n"
            f"- **Q4 Sensitive data:** {st.session_state.bp_sensitive or '—'}  \n"
            f"- **Q5 Website:** {st.session_state.df_website or '—'}  \n"
            f"- **Q6 HTTPS:** {st.session_state.df_https or '—'}  \n"
            f"- **Q7 Business email:** {st.session_state.df_email or '—'}  \n"
            f"- **Q8 Social presence:** {st.session_state.df_social or '—'}  \n"
            f"- **Q9 Public info checks:** {st.session_state.df_review or '—'}"
        )

    st.markdown('<div class="cta-row"></div>', unsafe_allow_html=True)
    b1, b2, b3 = st.columns([1,1,2])
    if b1.button("⬅ Back"):
        next_page("Initial 2")
    if b2.button("Start over"):
        for k, v in defaults.items(): st.session_state[k] = v
        next_page("Landing")
    if b3.button("See my top 5 recommendations ➜", type="primary"):
        st.info("Top-5 recommendations will be generated in the next phase of the build.")
