# app.py  — Clean build (Landing → pg1.1 → pg1.2)
import streamlit as st

st.set_page_config(page_title="SME Cybersecurity Self-Assessment", layout="wide")

# ---------------------------------------------------
# Session defaults
# ---------------------------------------------------
defaults = {
    "page": "Landing",
    # pg1.1 fields
    "person_name": "",
    "company_name": "",
    "sector_label": "",
    "years_in_business": "<1 year",
    "employee_range": "1–5",
    "turnover_label": "<€100k",
    "work_mode": "Local & in-person",
    # pg1.2 answers
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

EMPLOYEE_RANGES = ["1–5", "6–10", "10–25", "26–50", "51–100", "More than 100"]
TURNOVER_OPTIONS = ["<€100k"] + [f"€{i}00k" for i in range(1, 100)] + ["€10M–<€50M", "€50M+"]
YEARS_OPTIONS = ["<1 year", "1–3 years", "4–10 years", "10+ years"]
WORK_MODE = ["Local & in-person", "Online / remote", "A mix of both"]

# ---------------------------------------------------
# Helpers
# ---------------------------------------------------
def snapshot():
    """Left snapshot shown across pages."""
    st.subheader("Snapshot")
    st.markdown(
        f"**Business:** {st.session_state.company_name or '—'}  \n"
        f"**Industry:** {st.session_state.sector_label or '—'}  \n"
        f"**People:** {st.session_state.employee_range or '—'}  •  "
        f"**Years:** {st.session_state.years_in_business or '—'}  •  "
        f"**Turnover:** {st.session_state.turnover_label or '—'}  \n"
        f"**Work mode:** {st.session_state.work_mode or '—'}"
    )
    st.markdown("---")

def next_page(page_name: str):
    st.session_state.page = page_name
    st.rerun()

# ---------------------------------------------------
# PAGE: Landing
# ---------------------------------------------------
if st.session_state.page == "Landing":
    st.title("🛡️ SME Cybersecurity Self-Assessment")
    st.subheader("Assess. Understand. Act — in under 15 minutes.")
    st.write(
        "Cyber threats powered by AI are getting smarter, "
        "but most small businesses don’t have time for complex frameworks.  "
        "This guided assessment helps you discover your exposure and prioritise practical next steps — "
        "in plain language, mapped to recognised standards (NIST CSF 2.0 & ISO 27001 : 2022)."
    )
    st.markdown("### What to expect")
    st.markdown(
        "- 30 concise questions across key security areas  \n"
        "- Quick traffic-light (RAG) results  \n"
        "- Action plan aligned with international standards  \n"
        "- Runs locally — no data uploaded"
    )
    st.markdown("---")
    if st.button("Start ➜", type="primary"):
        next_page("Initial 1")

# ---------------------------------------------------
# PAGE: Initial Assessment pg 1.1
# ---------------------------------------------------
elif st.session_state.page == "Initial 1":
    st.title("Step 1 of 2 – Business Profile")
    st.caption("Tell us a bit about your business (≈ 2 minutes).")

    left, right = st.columns([1, 2], gap="large")
    with left:
        snapshot()

    with right:
        st.session_state.person_name = st.text_input(
            "Your name (required)", value=st.session_state.person_name
        )
        st.session_state.company_name = st.text_input(
            "Business name (required)", value=st.session_state.company_name
        )
        st.session_state.sector_label = st.text_input(
            "Industry / core service (e.g., retail, consulting)",
            value=st.session_state.sector_label,
        )
        st.session_state.years_in_business = st.selectbox(
            "How long in business?",
            YEARS_OPTIONS,
            index=YEARS_OPTIONS.index(st.session_state.years_in_business),
        )
        st.session_state.employee_range = st.selectbox(
            "Number of people (incl. contractors)",
            EMPLOYEE_RANGES,
            index=EMPLOYEE_RANGES.index(st.session_state.employee_range),
        )
        st.session_state.turnover_label = st.selectbox(
            "Approx. annual turnover", TURNOVER_OPTIONS,
            index=TURNOVER_OPTIONS.index(st.session_state.turnover_label)
            if st.session_state.turnover_label in TURNOVER_OPTIONS else 0,
        )
        st.session_state.work_mode = st.radio(
            "Work mode", WORK_MODE,
            horizontal=True,
            index=WORK_MODE.index(st.session_state.work_mode),
        )

    st.markdown("---")
    c1, c2 = st.columns(2)
    if c1.button("⬅ Back"):
        next_page("Landing")
    if c2.button("Continue to Cyber Questions ➜", type="primary",
                 disabled=not (st.session_state.person_name.strip() and st.session_state.company_name.strip())):
        next_page("Initial 2")

# ---------------------------------------------------
# PAGE: Initial Assessment pg 1.2
# ---------------------------------------------------
elif st.session_state.page == "Initial 2":
    st.title("Step 2 of 2 – Your Cyber Practices")

    left, right = st.columns([1, 2], gap="large")
    with left:
        snapshot()

    with right:
        st.subheader("Section 1 — Business Profile")
        st.radio(
            "Who manages your IT systems?\n*(Self-managed, outsourced, or shared responsibility.)*",
            ["Self-managed", "Outsourced IT", "Shared responsibility", "Not sure"],
            key="bp_it_manager",
            horizontal=False,
        )
        st.radio(
            "Do you maintain an inventory of company devices (laptops, phones, servers)?\n*(Helps identify unmanaged or forgotten assets.)*",
            ["Yes", "Partially", "No", "Not sure"],
            key="bp_inventory",
            horizontal=True,
        )
        st.radio(
            "Do employees use personal devices (BYOD) for work?\n*(Example: using private laptops or phones for business email.)*",
            ["Yes", "Sometimes", "No", "Not sure"],
            key="bp_byod",
            horizontal=True,
        )
        st.radio(
            "Do you handle sensitive customer or financial data?\n*(Examples: payment details, personal records, contracts.)*",
            ["Yes", "No", "Not sure"],
            key="bp_sensitive",
            horizontal=True,
        )

        st.markdown("---")
        st.subheader("Section 2 — Digital Footprint")
        st.radio(
            "Does your business have a public website?\n*(Helps assess potential online entry points.)*",
            ["Yes", "No"],
            key="df_website",
            horizontal=True,
        )
        st.radio(
            "Is your website protected with HTTPS (padlock symbol)?\n*(Encrypts traffic and builds trust.)*",
            ["Yes", "No", "Not sure"],
            key="df_https",
            horizontal=True,
        )
        st.radio(
            "Do you use business email addresses (e.g., info@yourcompany.com)?\n*(Personal Gmail/Yahoo accounts increase phishing risk.)*",
            ["Yes", "Partially", "No"],
            key="df_email",
            horizontal=True,
        )
        st.radio(
            "Is your business active on social-media platforms (e.g., LinkedIn, Instagram)?\n*(Helps gauge your brand’s visibility online.)*",
            ["Yes", "No"],
            key="df_social",
            horizontal=True,
        )
        st.radio(
            "Do you regularly review what company or staff information is public online?\n*(E.g., contact details, staff names, screenshots showing systems.)*",
            ["Yes", "Sometimes", "No"],
            key="df_review",
            horizontal=True,
        )

    st.markdown("---")
    c1, c2 = st.columns(2)
    if c1.button("⬅ Back to Profile"):
        next_page("Initial 1")
    if c2.button("Finish Initial Assessment ✅", type="primary"):
        st.success("Great! Assessment captured. Next: generate your summary page (to be implemented).")
