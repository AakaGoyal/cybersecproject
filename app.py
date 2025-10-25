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
if st.session_state.page == "Landing":
    st.title("🛡️ SME Cybersecurity Self-Assessment")
    st.subheader("Assess · Understand · Act — in under 15 minutes.")
    st.write(
        "Cyber threats powered by AI are getting more deceptive, "
        "but most SMEs don’t have time for heavyweight frameworks. "
        "This plain-language self-assessment helps you understand exposure and prioritise next steps, "
        "mapped to recognised standards (NIST CSF 2.0 & ISO 27001:2022)."
    )
    st.markdown("### What to expect")
    st.markdown(
        "- 30 concise questions across key security areas  \n"
        "- Traffic-light (RAG) results highlighting strengths and risks  \n"
        "- Action plan aligned to established standards  \n"
        "- Runs locally — no data uploaded"
    )
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
