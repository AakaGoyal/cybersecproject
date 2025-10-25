# app.py — Landing → Initial 1 (required) → Initial 2 → Summary (implemented)
import streamlit as st

st.set_page_config(page_title="SME Cybersecurity Self-Assessment", layout="wide")

# -----------------------------
# Session defaults
# -----------------------------
defaults = {
    "page": "Landing",
    # pg 1.1 fields (Business Profile)
    "person_name": "",
    "company_name": "",
    "sector_label": "Select industry…",   # dropdown default (forces selection)
    "sector_other": "",
    "years_in_business": "<1 year",
    "employee_range": "1–5",
    "turnover_label": "<€100k",
    "work_mode": "Local & in-person",
    # pg 1.2 answers
    "bp_it_manager": "Self-managed",
    "bp_inventory": "Yes",
    "bp_byod": "Yes",
    "bp_sensitive": "Yes",
    "df_website": "Yes",
    "df_https": "Yes",
    "df_email": "Yes",
    "df_social": "Yes",
    "df_review": "Yes",
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# -----------------------------
# Option lists
# -----------------------------
INDUSTRY_OPTIONS = [
    "Select industry…",
    "Retail & Hospitality",
    "Professional / Consulting / Legal / Accounting",
    "Manufacturing / Logistics",
    "Creative / Marketing / IT Services",
    "Health / Wellness / Education",
    "Digital / SaaS",
    "Public sector / Non-profit",
    "Other (type below)",
]
YEARS_OPTIONS = ["<1 year", "1–3 years", "4–10 years", "10+ years"]
EMPLOYEE_RANGES = ["1–5", "6–10", "10–25", "26–50", "51–100", "More than 100"]
WORK_MODE = ["Local & in-person", "Online / remote", "A mix of both"]

def build_turnover_options():
    opts = ["<€100k"]
    for v in range(100_000, 10_000_000, 100_000):  # €100k … €9.9M
        label = f"€{v/1_000_000:.1f}M" if v >= 1_000_000 else f"€{v//1000}k"
        opts.append(label)
    opts += ["€10.0M–<€50.0M", "€50.0M+"]
    return opts
TURNOVER_OPTIONS = build_turnover_options()

# -----------------------------
# Helpers
# -----------------------------
def resolved_industry() -> str:
    lbl = st.session_state.sector_label
    if lbl == "Other (type below)":
        return st.session_state.sector_other.strip() or "—"
    if lbl == "Select industry…":
        return "—"
    return lbl

def snapshot():
    st.subheader("Snapshot")
    st.markdown(
        f"**Business:** {st.session_state.company_name or '—'}  \n"
        f"**Industry:** {resolved_industry()}  \n"
        f"**People:** {st.session_state.employee_range or '—'}  •  "
        f"**Years:** {st.session_state.years_in_business or '—'}  •  "
        f"**Turnover:** {st.session_state.turnover_label or '—'}  \n"
        f"**Work mode:** {st.session_state.work_mode or '—'}"
    )
    st.markdown("---")

def next_page(name: str):
    st.session_state.page = name
    st.rerun()

def digital_dependency_level():
    """
    Heuristic 0–5 → Low/Medium/High.
    Signals: website/email/social, sensitive data, BYOD.
    """
    score = 0
    score += 1 if st.session_state.df_website == "Yes" else 0
    score += 1 if st.session_state.df_email in ["Yes", "Partially"] else 0
    score += 1 if st.session_state.df_social == "Yes" else 0
    score += 1 if st.session_state.bp_sensitive == "Yes" else 0
    score += 1 if st.session_state.bp_byod in ["Yes", "Sometimes"] else 0
    if score <= 1:
        return "Low", "🟢"
    if score <= 3:
        return "Medium", "🟡"
    return "High", "🔴"

def summary_highlights_and_blindspots():
    """Generate 2–3 highlights and blind spots from answers."""
    hi, bs = [], []
    if st.session_state.df_https == "Yes":
        hi.append("Website uses HTTPS, which encrypts traffic and builds trust.")
    if st.session_state.bp_inventory in ["Yes", "Partially"]:
        hi.append("You keep an inventory of company devices.")

    if st.session_state.df_email in ["Partially", "No"]:
        bs.append("Personal email for work increases phishing risk — move to business email.")
    if st.session_state.bp_byod in ["Yes", "Sometimes"]:
        bs.append("Personal devices (BYOD) need clear rules, MFA, and basic hardening.")
    if st.session_state.bp_sensitive == "Yes":
        bs.append("Handling customer/financial data requires backups and access control (MFA).")
    if not hi:
        hi.append("Good starting point across core practices.")
    if not bs:
        bs.append("Keep improving: review incident response steps and password/MFA hygiene.")
    return hi[:3], bs[:3]

# ---- strict validation for Initial 1
def validate_initial1():
    errors = []
    if not st.session_state.person_name.strip():
        errors.append("Your name is required.")
    if not st.session_state.company_name.strip():
        errors.append("Business name is required.")
    if st.session_state.sector_label == "Select industry…":
        errors.append("Please select an industry.")
    elif st.session_state.sector_label == "Other (type below)" and not st.session_state.sector_other.strip():
        errors.append("Please type your industry.")
    if st.session_state.years_in_business not in YEARS_OPTIONS:
        errors.append("Please select how long in business.")
    if st.session_state.employee_range not in EMPLOYEE_RANGES:
        errors.append("Please select number of people.")
    if st.session_state.turnover_label not in TURNOVER_OPTIONS:
        errors.append("Please select approximate annual turnover.")
    if st.session_state.work_mode not in WORK_MODE:
        errors.append("Please choose a work mode.")
    return (len(errors) == 0, errors)

# -----------------------------
# PAGES
# -----------------------------
# ===== Landing (professional hero with preview, trust cues, dual CTAs) =====
if st.session_state.page == "Landing":
    # light CSS for spacing/typography without heavy theming
    st.markdown("""
    <style>
      .container {max-width: 1100px; margin: 0 auto;}
      .hero h1 {font-size: 2.2rem; line-height: 1.15; margin: 0 0 .5rem;}
      .sub {font-size: 1.15rem; color: #444; margin-bottom: .75rem;}
      .muted {color:#666;}
      .lock {display:inline-flex; align-items:center; gap:.4rem; font-size:.95rem; color:#375; background:#EAF6EE; padding:.35rem .55rem; border-radius:8px;}
      .grid {display:grid; grid-template-columns: repeat(4,minmax(0,1fr)); gap:12px; margin-top:18px;}
      .card {background: #fff; border:1px solid #eee; border-radius:14px; padding:12px 14px;}
      .preview {background:#fff; border:1px solid #eee; border-radius:16px; padding:16px;}
      .badge {display:inline-flex; align-items:center; gap:.4rem; padding:.2rem .5rem; border-radius:999px; font-size:.9rem;}
      .badge.low{background:#E9F7EF} .badge.med{background:#FFF8E1} .badge.high{background:#FFEBEE}
      .section-title {font-weight:700; font-size:1.25rem; margin:24px 0 8px;}
      @media (max-width: 980px){
        .grid {grid-template-columns: 1fr 1fr;}
      }
    </style>
    """, unsafe_allow_html=True)

    # HERO
    hero_left, hero_right = st.columns([7,5], gap="large")
    with hero_left:
        st.markdown('<div class="hero">', unsafe_allow_html=True)
        st.markdown("### 🛡️ SME Cybersecurity Self-Assessment", unsafe_allow_html=True)
        st.markdown('<h1 class="h1">Assess · Understand · Act — in under 15 minutes.</h1>', unsafe_allow_html=True)
        st.markdown(
            '<p class="sub">A plain-language self-assessment that shows your exposure and the <strong>top actions to take next</strong>. '
            'Lightweight but <em>traceable</em> to recognised standards (NIST CSF 2.0, ISO 27001:2022).</p>',
            unsafe_allow_html=True
        )

        cta1, cta2 = st.columns([1,1])
        with cta1:
            if st.button("Start self-assessment ➜", type="primary", use_container_width=True):
                st.session_state.page = "Initial 1"; st.rerun()
        with cta2:
            if st.button("See sample results", use_container_width=True):
                # seed demo data and jump to Summary
                st.session_state.person_name = "Demo User"
                st.session_state.company_name = "Sample Co."
                st.session_state.sector_label = "Retail & Hospitality"
                st.session_state.years_in_business = "1–3 years"
                st.session_state.employee_range = "10–25"
                st.session_state.turnover_label = "€500k"
                st.session_state.work_mode = "A mix of both"
                st.session_state.bp_it_manager = "Shared responsibility"
                st.session_state.bp_inventory = "Partially"
                st.session_state.bp_byod = "Sometimes"
                st.session_state.bp_sensitive = "Yes"
                st.session_state.df_website = "Yes"
                st.session_state.df_https = "No"
                st.session_state.df_email = "Partially"
                st.session_state.df_social = "Yes"
                st.session_state.df_review = "Sometimes"
                st.session_state.page = "Summary"; st.rerun()

        st.markdown('<div class="lock">🔒 No sign-up. Answers stay on this device.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Why this works</div>', unsafe_allow_html=True)
        st.markdown('<div class="grid">', unsafe_allow_html=True)
        st.markdown('<div class="card">✅ Plain-language questions</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">📎 Traceable to NIST/ISO</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">⚡ Lightweight, 10–15 minutes</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">🧪 Safe demos of common scams</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with hero_right:
        st.markdown('<div class="preview">', unsafe_allow_html=True)
        st.caption("Preview of your summary")
        st.markdown('<span class="badge med">🟡 Overall: Medium dependency</span>', unsafe_allow_html=True)
        st.write("**Highlights**")
        st.write("• Website uses HTTPS\n\n• Device list exists (partial)")
        st.write("**Potential blind spots**")
        st.write("• Personal email in use → move to business email\n• BYOD needs MFA + clear rules")
        st.markdown('<div class="muted">Mapped to: NIST CSF PR.AC, PR.DS · ISO 27001 A.5, A.8</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # HOW IT WORKS
    st.markdown('<div class="section-title">How it works</div>', unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    s1.info("**1. Answer**\nShort questions about your setup and online presence.")
    s2.info("**2. See results**\nClear traffic-light summary with context.")
    s3.info("**3. Act**\nTop-5 actions aligned to recognised control families.")

    st.markdown("---")
    if st.button("Start ➜", type="primary"):
        next_page("Initial 1")

elif st.session_state.page == "Initial 1":
    st.title("Step 1 of 3 – Business Profile")
    st.caption("Tell us a bit about your business (≈ 2 minutes).")

    left, right = st.columns([1, 2], gap="large")
    with left:
        snapshot()

    with right:
        st.session_state.person_name = st.text_input("Your name (required)", value=st.session_state.person_name)
        st.session_state.company_name = st.text_input("Business name (required)", value=st.session_state.company_name)

        st.session_state.sector_label = st.selectbox(
            "Industry / core service (required)",
            INDUSTRY_OPTIONS,
            index=INDUSTRY_OPTIONS.index(st.session_state.sector_label)
            if st.session_state.sector_label in INDUSTRY_OPTIONS else 0,
        )
        if st.session_state.sector_label == "Other (type below)":
            st.session_state.sector_other = st.text_input(
                "Type your industry (required)",
                value=st.session_state.sector_other,
                placeholder="e.g., Architecture, Automotive services",
            )
        else:
            st.session_state.sector_other = ""

        st.session_state.years_in_business = st.selectbox(
            "How long in business? (required)",
            YEARS_OPTIONS,
            index=YEARS_OPTIONS.index(st.session_state.years_in_business),
        )
        st.session_state.employee_range = st.selectbox(
            "Number of people (incl. contractors) (required)",
            EMPLOYEE_RANGES,
            index=EMPLOYEE_RANGES.index(st.session_state.employee_range),
        )
        st.session_state.turnover_label = st.selectbox(
            "Approx. annual turnover (required)",
            TURNOVER_OPTIONS,
            index=TURNOVER_OPTIONS.index(st.session_state.turnover_label)
            if st.session_state.turnover_label in TURNOVER_OPTIONS else 0,
        )
        st.session_state.work_mode = st.radio(
            "Work mode (required)",
            WORK_MODE, horizontal=True,
            index=WORK_MODE.index(st.session_state.work_mode),
        )

    st.markdown("---")
    valid, errs = validate_initial1()
    c1, c2 = st.columns(2)
    if c1.button("⬅ Back"):
        next_page("Landing")
    if c2.button("Continue to Cyber Questions ➜", type="primary", disabled=not valid):
        next_page("Initial 2")
    if not valid:
        for e in errs:
            st.caption(f"⚠️ {e}")

elif st.session_state.page == "Initial 2":
    st.title("Step 2 of 3 – Your Cyber Practices")

    left, right = st.columns([1, 2], gap="large")
    with left:
        snapshot()

    with right:
        st.subheader("Section 1 — Business Profile")
        st.radio(
            "Who manages your IT systems?  \n*(Self-managed, outsourced, or shared responsibility.)*",
            ["Self-managed", "Outsourced IT", "Shared responsibility", "Not sure"],
            key="bp_it_manager",
        )
        st.radio(
            "Do you maintain an inventory of company devices (laptops, phones, servers)?  \n*(Helps identify unmanaged or forgotten assets.)*",
            ["Yes", "Partially", "No", "Not sure"], key="bp_inventory", horizontal=True
        )
        st.radio(
            "Do employees use personal devices (BYOD) for work?  \n*(Example: using private laptops or phones for business email.)*",
            ["Yes", "Sometimes", "No", "Not sure"], key="bp_byod", horizontal=True
        )
        st.radio(
            "Do you handle sensitive customer or financial data?  \n*(Examples: payment details, personal records, contracts.)*",
            ["Yes", "No", "Not sure"], key="bp_sensitive", horizontal=True
        )

        st.markdown("---")
        st.subheader("Section 2 — Digital Footprint")
        st.radio(
            "Does your business have a public website?  \n*(Helps assess potential online entry points.)*",
            ["Yes", "No"], key="df_website", horizontal=True
        )
        st.radio(
            "Is your website protected with HTTPS (padlock symbol)?  \n*(Encrypts traffic and builds trust.)*",
            ["Yes", "No", "Not sure"], key="df_https", horizontal=True
        )
        st.radio(
            "Do you use business email addresses (e.g., info@yourcompany.com)?  \n*(Personal Gmail/Yahoo accounts increase phishing risk.)*",
            ["Yes", "Partially", "No"], key="df_email", horizontal=True
        )
        st.radio(
            "Is your business active on social-media platforms (e.g., LinkedIn, Instagram)?  \n*(Helps gauge brand visibility online.)*",
            ["Yes", "No"], key="df_social", horizontal=True
        )
        st.radio(
            "Do you regularly review what company or staff information is public online?  \n*(E.g., contact details, staff names, screenshots showing systems.)*",
            ["Yes", "Sometimes", "No"], key="df_review", horizontal=True
        )

    st.markdown("---")
    c1, c2 = st.columns(2)
    if c1.button("⬅ Back to Profile"):
        next_page("Initial 1")
    if c2.button("Finish Initial Assessment ✅", type="primary"):
        next_page("Summary")  # ← now navigates to Summary

elif st.session_state.page == "Summary":
    st.title("✅ Initial Assessment Summary")

    left, right = st.columns([1, 2], gap="large")
    with left:
        snapshot()

    with right:
        # Traffic-light banner
        level, emoji = digital_dependency_level()
        st.markdown(f"**Overall digital dependency:** {emoji} **{level}**")
        st.caption("Derived from online exposure, data handling, and device practices.")

        st.markdown("---")
        st.subheader("Business Profile")
        st.markdown(
            f"- **Assessed by:** {st.session_state.person_name}  \n"
            f"- **Business:** {st.session_state.company_name}  \n"
 # app.py — Landing → Initial 1 (required) → Initial 2 → Summary (implemented)
import streamlit as st

st.set_page_config(page_title="SME Cybersecurity Self-Assessment", layout="wide")

# -----------------------------
# Session defaults
# -----------------------------
defaults = {
    "page": "Landing",
    # pg 1.1 fields (Business Profile)
    "person_name": "",
    "company_name": "",
    "sector_label": "Select industry…",   # dropdown default (forces selection)
    "sector_other": "",
    "years_in_business": "<1 year",
    "employee_range": "1–5",
    "turnover_label": "<€100k",
    "work_mode": "Local & in-person",
    # pg 1.2 answers
    "bp_it_manager": "Self-managed",
    "bp_inventory": "Yes",
    "bp_byod": "Yes",
    "bp_sensitive": "Yes",
    "df_website": "Yes",
    "df_https": "Yes",
    "df_email": "Yes",
    "df_social": "Yes",
    "df_review": "Yes",
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# -----------------------------
# Option lists
# -----------------------------
INDUSTRY_OPTIONS = [
    "Select industry…",
    "Retail & Hospitality",
    "Professional / Consulting / Legal / Accounting",
    "Manufacturing / Logistics",
    "Creative / Marketing / IT Services",
    "Health / Wellness / Education",
    "Digital / SaaS",
    "Public sector / Non-profit",
    "Other (type below)",
]
YEARS_OPTIONS = ["<1 year", "1–3 years", "4–10 years", "10+ years"]
EMPLOYEE_RANGES = ["1–5", "6–10", "10–25", "26–50", "51–100", "More than 100"]
WORK_MODE = ["Local & in-person", "Online / remote", "A mix of both"]

def build_turnover_options():
    opts = ["<€100k"]
    for v in range(100_000, 10_000_000, 100_000):  # €100k … €9.9M
        label = f"€{v/1_000_000:.1f}M" if v >= 1_000_000 else f"€{v//1000}k"
        opts.append(label)
    opts += ["€10.0M–<€50.0M", "€50.0M+"]
    return opts
TURNOVER_OPTIONS = build_turnover_options()

# -----------------------------
# Helpers
# -----------------------------
def resolved_industry() -> str:
    lbl = st.session_state.sector_label
    if lbl == "Other (type below)":
        return st.session_state.sector_other.strip() or "—"
    if lbl == "Select industry…":
        return "—"
    return lbl

def snapshot():
    st.subheader("Snapshot")
    st.markdown(
        f"**Business:** {st.session_state.company_name or '—'}  \n"
        f"**Industry:** {resolved_industry()}  \n"
        f"**People:** {st.session_state.employee_range or '—'}  •  "
        f"**Years:** {st.session_state.years_in_business or '—'}  •  "
        f"**Turnover:** {st.session_state.turnover_label or '—'}  \n"
        f"**Work mode:** {st.session_state.work_mode or '—'}"
    )
    st.markdown("---")

def next_page(name: str):
    st.session_state.page = name
    st.rerun()

def digital_dependency_level():
    """
    Heuristic 0–5 → Low/Medium/High.
    Signals: website/email/social, sensitive data, BYOD.
    """
    score = 0
    score += 1 if st.session_state.df_website == "Yes" else 0
    score += 1 if st.session_state.df_email in ["Yes", "Partially"] else 0
    score += 1 if st.session_state.df_social == "Yes" else 0
    score += 1 if st.session_state.bp_sensitive == "Yes" else 0
    score += 1 if st.session_state.bp_byod in ["Yes", "Sometimes"] else 0
    if score <= 1:
        return "Low", "🟢"
    if score <= 3:
        return "Medium", "🟡"
    return "High", "🔴"

def summary_highlights_and_blindspots():
    """Generate 2–3 highlights and blind spots from answers."""
    hi, bs = [], []
    if st.session_state.df_https == "Yes":
        hi.append("Website uses HTTPS, which encrypts traffic and builds trust.")
    if st.session_state.bp_inventory in ["Yes", "Partially"]:
        hi.append("You keep an inventory of company devices.")

    if st.session_state.df_email in ["Partially", "No"]:
        bs.append("Personal email for work increases phishing risk — move to business email.")
    if st.session_state.bp_byod in ["Yes", "Sometimes"]:
        bs.append("Personal devices (BYOD) need clear rules, MFA, and basic hardening.")
    if st.session_state.bp_sensitive == "Yes":
        bs.append("Handling customer/financial data requires backups and access control (MFA).")
    if not hi:
        hi.append("Good starting point across core practices.")
    if not bs:
        bs.append("Keep improving: review incident response steps and password/MFA hygiene.")
    return hi[:3], bs[:3]

# ---- strict validation for Initial 1
def validate_initial1():
    errors = []
    if not st.session_state.person_name.strip():
        errors.append("Your name is required.")
    if not st.session_state.company_name.strip():
        errors.append("Business name is required.")
    if st.session_state.sector_label == "Select industry…":
        errors.append("Please select an industry.")
    elif st.session_state.sector_label == "Other (type below)" and not st.session_state.sector_other.strip():
        errors.append("Please type your industry.")
    if st.session_state.years_in_business not in YEARS_OPTIONS:
        errors.append("Please select how long in business.")
    if st.session_state.employee_range not in EMPLOYEE_RANGES:
        errors.append("Please select number of people.")
    if st.session_state.turnover_label not in TURNOVER_OPTIONS:
        errors.append("Please select approximate annual turnover.")
    if st.session_state.work_mode not in WORK_MODE:
        errors.append("Please choose a work mode.")
    return (len(errors) == 0, errors)

# -----------------------------
# PAGES
# -----------------------------
# ===== Landing (professional hero with preview, trust cues, dual CTAs) =====
if st.session_state.page == "Landing":
    # light CSS for spacing/typography without heavy theming
    st.markdown("""
    <style>
      .container {max-width: 1100px; margin: 0 auto;}
      .hero h1 {font-size: 2.2rem; line-height: 1.15; margin: 0 0 .5rem;}
      .sub {font-size: 1.15rem; color: #444; margin-bottom: .75rem;}
      .muted {color:#666;}
      .lock {display:inline-flex; align-items:center; gap:.4rem; font-size:.95rem; color:#375; background:#EAF6EE; padding:.35rem .55rem; border-radius:8px;}
      .grid {display:grid; grid-template-columns: repeat(4,minmax(0,1fr)); gap:12px; margin-top:18px;}
      .card {background: #fff; border:1px solid #eee; border-radius:14px; padding:12px 14px;}
      .preview {background:#fff; border:1px solid #eee; border-radius:16px; padding:16px;}
      .badge {display:inline-flex; align-items:center; gap:.4rem; padding:.2rem .5rem; border-radius:999px; font-size:.9rem;}
      .badge.low{background:#E9F7EF} .badge.med{background:#FFF8E1} .badge.high{background:#FFEBEE}
      .section-title {font-weight:700; font-size:1.25rem; margin:24px 0 8px;}
      @media (max-width: 980px){
        .grid {grid-template-columns: 1fr 1fr;}
      }
    </style>
    """, unsafe_allow_html=True)

    # HERO
    hero_left, hero_right = st.columns([7,5], gap="large")
    with hero_left:
        st.markdown('<div class="hero">', unsafe_allow_html=True)
        st.markdown("### 🛡️ SME Cybersecurity Self-Assessment", unsafe_allow_html=True)
        st.markdown('<h1 class="h1">Assess · Understand · Act — in under 15 minutes.</h1>', unsafe_allow_html=True)
        st.markdown(
            '<p class="sub">A plain-language self-assessment that shows your exposure and the <strong>top actions to take next</strong>. '
            'Lightweight but <em>traceable</em> to recognised standards (NIST CSF 2.0, ISO 27001:2022).</p>',
            unsafe_allow_html=True
        )

        cta1, cta2 = st.columns([1,1])
        with cta1:
            if st.button("Start self-assessment ➜", type="primary", use_container_width=True):
                st.session_state.page = "Initial 1"; st.rerun()
        with cta2:
            if st.button("See sample results", use_container_width=True):
                # seed demo data and jump to Summary
                st.session_state.person_name = "Demo User"
                st.session_state.company_name = "Sample Co."
                st.session_state.sector_label = "Retail & Hospitality"
                st.session_state.years_in_business = "1–3 years"
                st.session_state.employee_range = "10–25"
                st.session_state.turnover_label = "€500k"
                st.session_state.work_mode = "A mix of both"
                st.session_state.bp_it_manager = "Shared responsibility"
                st.session_state.bp_inventory = "Partially"
                st.session_state.bp_byod = "Sometimes"
                st.session_state.bp_sensitive = "Yes"
                st.session_state.df_website = "Yes"
                st.session_state.df_https = "No"
                st.session_state.df_email = "Partially"
                st.session_state.df_social = "Yes"
                st.session_state.df_review = "Sometimes"
                st.session_state.page = "Summary"; st.rerun()

        st.markdown('<div class="lock">🔒 No sign-up. Answers stay on this device.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Why this works</div>', unsafe_allow_html=True)
        st.markdown('<div class="grid">', unsafe_allow_html=True)
        st.markdown('<div class="card">✅ Plain-language questions</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">📎 Traceable to NIST/ISO</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">⚡ Lightweight, 10–15 minutes</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">🧪 Safe demos of common scams</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with hero_right:
        st.markdown('<div class="preview">', unsafe_allow_html=True)
        st.caption("Preview of your summary")
        st.markdown('<span class="badge med">🟡 Overall: Medium dependency</span>', unsafe_allow_html=True)
        st.write("**Highlights**")
        st.write("• Website uses HTTPS\n\n• Device list exists (partial)")
        st.write("**Potential blind spots**")
        st.write("• Personal email in use → move to business email\n• BYOD needs MFA + clear rules")
        st.markdown('<div class="muted">Mapped to: NIST CSF PR.AC, PR.DS · ISO 27001 A.5, A.8</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # HOW IT WORKS
    st.markdown('<div class="section-title">How it works</div>', unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    s1.info("**1. Answer**\nShort questions about your setup and online presence.")
    s2.info("**2. See results**\nClear traffic-light summary with context.")
    s3.info("**3. Act**\nTop-5 actions aligned to recognised control families.")

    st.markdown("---")
    if st.button("Start ➜", type="primary"):
        next_page("Initial 1")

elif st.session_state.page == "Initial 1":
    st.title("Step 1 of 3 – Business Profile")
    st.caption("Tell us a bit about your business (≈ 2 minutes).")

    left, right = st.columns([1, 2], gap="large")
    with left:
        snapshot()

    with right:
        st.session_state.person_name = st.text_input("Your name (required)", value=st.session_state.person_name)
        st.session_state.company_name = st.text_input("Business name (required)", value=st.session_state.company_name)

        st.session_state.sector_label = st.selectbox(
            "Industry / core service (required)",
            INDUSTRY_OPTIONS,
            index=INDUSTRY_OPTIONS.index(st.session_state.sector_label)
            if st.session_state.sector_label in INDUSTRY_OPTIONS else 0,
        )
        if st.session_state.sector_label == "Other (type below)":
            st.session_state.sector_other = st.text_input(
                "Type your industry (required)",
                value=st.session_state.sector_other,
                placeholder="e.g., Architecture, Automotive services",
            )
        else:
            st.session_state.sector_other = ""

        st.session_state.years_in_business = st.selectbox(
            "How long in business? (required)",
            YEARS_OPTIONS,
            index=YEARS_OPTIONS.index(st.session_state.years_in_business),
        )
        st.session_state.employee_range = st.selectbox(
            "Number of people (incl. contractors) (required)",
            EMPLOYEE_RANGES,
            index=EMPLOYEE_RANGES.index(st.session_state.employee_range),
        )
        st.session_state.turnover_label = st.selectbox(
            "Approx. annual turnover (required)",
            TURNOVER_OPTIONS,
            index=TURNOVER_OPTIONS.index(st.session_state.turnover_label)
            if st.session_state.turnover_label in TURNOVER_OPTIONS else 0,
        )
        st.session_state.work_mode = st.radio(
            "Work mode (required)",
            WORK_MODE, horizontal=True,
            index=WORK_MODE.index(st.session_state.work_mode),
        )

    st.markdown("---")
    valid, errs = validate_initial1()
    c1, c2 = st.columns(2)
    if c1.button("⬅ Back"):
        next_page("Landing")
    if c2.button("Continue to Cyber Questions ➜", type="primary", disabled=not valid):
        next_page("Initial 2")
    if not valid:
        for e in errs:
            st.caption(f"⚠️ {e}")

elif st.session_state.page == "Initial 2":
    st.title("Step 2 of 3 – Your Cyber Practices")

    left, right = st.columns([1, 2], gap="large")
    with left:
        snapshot()

    with right:
        st.subheader("Section 1 — Business Profile")
        st.radio(
            "Who manages your IT systems?  \n*(Self-managed, outsourced, or shared responsibility.)*",
            ["Self-managed", "Outsourced IT", "Shared responsibility", "Not sure"],
            key="bp_it_manager",
        )
        st.radio(
            "Do you maintain an inventory of company devices (laptops, phones, servers)?  \n*(Helps identify unmanaged or forgotten assets.)*",
            ["Yes", "Partially", "No", "Not sure"], key="bp_inventory", horizontal=True
        )
        st.radio(
            "Do employees use personal devices (BYOD) for work?  \n*(Example: using private laptops or phones for business email.)*",
            ["Yes", "Sometimes", "No", "Not sure"], key="bp_byod", horizontal=True
        )
        st.radio(
            "Do you handle sensitive customer or financial data?  \n*(Examples: payment details, personal records, contracts.)*",
            ["Yes", "No", "Not sure"], key="bp_sensitive", horizontal=True
        )

        st.markdown("---")
        st.subheader("Section 2 — Digital Footprint")
        st.radio(
            "Does your business have a public website?  \n*(Helps assess potential online entry points.)*",
            ["Yes", "No"], key="df_website", horizontal=True
        )
        st.radio(
            "Is your website protected with HTTPS (padlock symbol)?  \n*(Encrypts traffic and builds trust.)*",
            ["Yes", "No", "Not sure"], key="df_https", horizontal=True
        )
        st.radio(
            "Do you use business email addresses (e.g., info@yourcompany.com)?  \n*(Personal Gmail/Yahoo accounts increase phishing risk.)*",
            ["Yes", "Partially", "No"], key="df_email", horizontal=True
        )
        st.radio(
            "Is your business active on social-media platforms (e.g., LinkedIn, Instagram)?  \n*(Helps gauge brand visibility online.)*",
            ["Yes", "No"], key="df_social", horizontal=True
        )
        st.radio(
            "Do you regularly review what company or staff information is public online?  \n*(E.g., contact details, staff names, screenshots showing systems.)*",
            ["Yes", "Sometimes", "No"], key="df_review", horizontal=True
        )

    st.markdown("---")
    c1, c2 = st.columns(2)
    if c1.button("⬅ Back to Profile"):
        next_page("Initial 1")
    if c2.button("Finish Initial Assessment ✅", type="primary"):
        next_page("Summary")  # ← now navigates to Summary

elif st.session_state.page == "Summary":
    st.title("✅ Initial Assessment Summary")

    left, right = st.columns([1, 2], gap="large")
    with left:
        snapshot()

    with right:
        # Traffic-light banner
        level, emoji = digital_dependency_level()
        st.markdown(f"**Overall digital dependency:** {emoji} **{level}**")
        st.caption("Derived from online exposure, data handling, and device practices.")

        st.markdown("---")
        st.subheader("Business Profile")
        st.markdown(
            f"- **Assessed by:** {st.session_state.person_name}  \n"
            f"- **Business:** {st.session_state.company_name}  \n"
            f"- **Industry:** {resolved_industry()}  \n"
            f"- **Years in business:** {st.session_state.years_in_business}  \n"
            f"- **People:** {st.session_state.employee_range}  \n"
            f"- **Turnover:** {st.session_state.turnover_label}  \n"
            f"- **Work mode:** {st.session_state.work_mode}"
        )

        st.markdown("---")
        st.subheader("Your Cyber Practices")
        st.markdown(
            f"- **IT management:** {st.session_state.bp_it_manager}  \n"
            f"- **Device inventory:** {st.session_state.bp_inventory}  \n"
            f"- **BYOD:** {st.session_state.bp_byod}  \n"
            f"- **Sensitive data:** {st.session_state.bp_sensitive}  \n"
            f"- **Website:** {st.session_state.df_website}  \n"
            f"- **HTTPS:** {st.session_state.df_https}  \n"
            f"- **Business email:** {st.session_state.df_email}  \n"
            f"- **Social media:** {st.session_state.df_social}  \n"
            f"- **Public info reviews:** {st.session_state.df_review}"
        )

        st.markdown("---")
        st.subheader("Highlights")
        hi, bs = summary_highlights_and_blindspots()
        for item in hi:
            st.write(f"• {item}")

        st.subheader("Potential blind spots")
        for item in bs:
            st.write(f"• {item}")

    st.markdown("---")
    c1, c2, c3 = st.columns([1, 1, 2])
    if c1.button("⬅ Back to Questions"):
        next_page("Initial 2")
    if c2.button("Start Over"):
        for k, v in defaults.items():
            st.session_state[k] = v
        next_page("Landing")
    if c3.button("Continue to Detailed Questionnaire ➜", type="primary"):
        st.info("Detailed questionnaire coming in the next phase.")
           f"- **Industry:** {resolved_industry()}  \n"
            f"- **Years in business:** {st.session_state.years_in_business}  \n"
            f"- **People:** {st.session_state.employee_range}  \n"
            f"- **Turnover:** {st.session_state.turnover_label}  \n"
            f"- **Work mode:** {st.session_state.work_mode}"
        )

        st.markdown("---")
        st.subheader("Your Cyber Practices")
        st.markdown(
            f"- **IT management:** {st.session_state.bp_it_manager}  \n"
            f"- **Device inventory:** {st.session_state.bp_inventory}  \n"
            f"- **BYOD:** {st.session_state.bp_byod}  \n"
            f"- **Sensitive data:** {st.session_state.bp_sensitive}  \n"
            f"- **Website:** {st.session_state.df_website}  \n"
            f"- **HTTPS:** {st.session_state.df_https}  \n"
            f"- **Business email:** {st.session_state.df_email}  \n"
            f"- **Social media:** {st.session_state.df_social}  \n"
            f"- **Public info reviews:** {st.session_state.df_review}"
        )

        st.markdown("---")
        st.subheader("Highlights")
        hi, bs = summary_highlights_and_blindspots()
        for item in hi:
            st.write(f"• {item}")

        st.subheader("Potential blind spots")
        for item in bs:
            st.write(f"• {item}")

    st.markdown("---")
    c1, c2, c3 = st.columns([1, 1, 2])
    if c1.button("⬅ Back to Questions"):
        next_page("Initial 2")
    if c2.button("Start Over"):
        for k, v in defaults.items():
            st.session_state[k] = v
        next_page("Landing")
    if c3.button("Continue to Detailed Questionnaire ➜", type="primary"):
        st.info("Detailed questionnaire coming in the next phase.")
