# app.py — Conversational UX: Landing → Initial 1 (required) → Initial 2 (Q1–Q9, friendly copy) → Summary
import streamlit as st

st.set_page_config(page_title="SME Cybersecurity Self-Assessment", layout="wide")

# -----------------------------
# Session defaults
# -----------------------------
defaults = {
    "page": "Landing",
    # pg 1.1 (required)
    "person_name": "",
    "company_name": "",
    "sector_label": "Select industry…",
    "sector_other": "",
    "years_in_business": "<1 year",
    "employee_range": "1–5",
    "turnover_label": "<€100k",
    "work_mode": "Local & in-person",
    # pg 1.2 answers
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
    score = 0
    score += 1 if st.session_state.df_website == "Yes" else 0
    score += 1 if st.session_state.df_email in ["Yes", "Partially"] else 0
    score += 1 if st.session_state.df_social == "Yes" else 0
    score += 1 if st.session_state.bp_sensitive == "Yes" else 0
    score += 1 if st.session_state.bp_byod in ["Yes", "Sometimes"] else 0
    if score <= 1:  return "Low", "🟢"
    if score <= 3:  return "Medium", "🟡"
    return "High", "🔴"

def summary_highlights_and_blindspots():
    hi, bs = [], []
    if st.session_state.df_https == "Yes":
        hi.append("Website uses HTTPS (encrypted traffic).")
    if st.session_state.bp_inventory in ["Yes", "Partially"]:
        hi.append("You keep a device list (even partial helps).")
    if st.session_state.df_email in ["Partially", "No"]:
        bs.append("Personal email in use — move to business email to cut phishing risk.")
    if st.session_state.bp_byod in ["Yes", "Sometimes"]:
        bs.append("BYOD needs clear rules, MFA and basic hardening.")
    if st.session_state.bp_sensitive == "Yes":
        bs.append("Sensitive data calls for regular backups and strong access control (MFA).")
    if not hi: hi.append("Solid starting point across core practices.")
    if not bs: bs.append("Keep improving: test incident response and tighten MFA hygiene.")
    return hi[:3], bs[:3]

def validate_initial1():
    errors = []
    if not st.session_state.person_name.strip(): errors.append("Your name is required.")
    if not st.session_state.company_name.strip(): errors.append("Business name is required.")
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

# Nicely formatted radio questions with Q-number + emoji + micro-hint
def ask_radio(qnum: int, emoji: str, prompt: str, hint: str, options: list, key: str, horizontal=True):
    st.markdown(f"**Q{qnum}. {emoji} {prompt}**")
    if hint:
        st.caption(hint)
    return st.radio(" ", options, key=key, horizontal=horizontal, label_visibility="collapsed")

# -----------------------------
# PAGES
# -----------------------------
if st.session_state.page == "Landing":
    st.title("🛡️ SME Cybersecurity Self-Assessment")
    st.subheader("Assess · Understand · Act — in under 15 minutes.")
    st.write(
        "Cyber threats powered by AI are getting more deceptive, but most SMEs don’t have time for heavyweight frameworks. "
        "This plain-language self-assessment helps you understand exposure and prioritise next steps, "
        "mapped to recognised standards (NIST CSF 2.0 & ISO 27001:2022)."
    )
    st.markdown("### What to expect")
    st.markdown(
        "- 30 concise questions across key security areas  \n"
        "- Traffic-light (RAG) results highlighting strengths and risks  \n"
        "- Personalised top actions aligned to established standards  \n"
        "- Runs locally — no data uploaded"
    )
    st.markdown("---")
    c1, c2, _ = st.columns([1,1,6])
    if c1.button("Start ➜", type="primary"):
        next_page("Initial 1")
    if c2.button("See sample results"):
        # Seed demo data → Summary
        st.session_state.person_name = "Demo User"
        st.session_state.company_name = "Demo"
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
        next_page("Summary")

elif st.session_state.page == "Initial 1":
    st.title("Step 1 of 3 – Tell us about the business")
    st.caption("Just the basics. This helps us tailor the next questions (≈ 2 minutes).")

    left, right = st.columns([1, 2], gap="large")
    with left:
        snapshot()

    with right:
        st.session_state.person_name = st.text_input("👤 Your name (required)", value=st.session_state.person_name)
        st.session_state.company_name = st.text_input("🏢 Business name (required)", value=st.session_state.company_name)

        st.session_state.sector_label = st.selectbox(
            "🏷️ Industry / core service (required)",
            INDUSTRY_OPTIONS,
            index=INDUSTRY_OPTIONS.index(st.session_state.sector_label)
            if st.session_state.sector_label in INDUSTRY_OPTIONS else 0,
        )
        if st.session_state.sector_label == "Other (type below)":
            st.session_state.sector_other = st.text_input(
                "✍️ Type your industry (required)",
                value=st.session_state.sector_other,
                placeholder="e.g., Architecture, Automotive services",
            )
        else:
            st.session_state.sector_other = ""

        st.session_state.years_in_business = st.selectbox(
            "📅 How long in business? (required)",
            YEARS_OPTIONS,
            index=YEARS_OPTIONS.index(st.session_state.years_in_business),
        )
        st.session_state.employee_range = st.selectbox(
            "👥 Number of people (incl. contractors) (required)",
            EMPLOYEE_RANGES,
            index=EMPLOYEE_RANGES.index(st.session_state.employee_range),
        )
        st.session_state.turnover_label = st.selectbox(
            "💶 Approx. annual turnover (required)",
            TURNOVER_OPTIONS,
            index=TURNOVER_OPTIONS.index(st.session_state.turnover_label)
            if st.session_state.turnover_label in TURNOVER_OPTIONS else 0,
        )
        st.session_state.work_mode = st.radio(
            "🧭 Work mode (required)",
            WORK_MODE, horizontal=True,
            index=WORK_MODE.index(st.session_state.work_mode),
        )

    st.markdown("---")
    valid, errs = validate_initial1()
    b1, b2 = st.columns(2)
    if b1.button("⬅ Back"):
        next_page("Landing")
    if b2.button("Continue ➜", type="primary", disabled=not valid):
        next_page("Initial 2")
    if not valid:
        for e in errs:
            st.caption(f"⚠️ {e}")

elif st.session_state.page == "Initial 2":
    st.title("Step 2 of 3 – Your Cyber Practices")
    st.caption("Quick checks. Plain language, no trick questions.")

    left, right = st.columns([1, 2], gap="large")
    with left:
        snapshot()

    with right:
        st.subheader("🧭 Section 1 — Business Profile")
        # Q1 — IT management with background explainer
        ask_radio(
            1, "🖥️",
            "Who looks after your **IT** day-to-day?",
            "_By IT we mean the stuff your business relies on: laptops/phones, Wi-Fi, email, website, point-of-sale, cloud apps (e.g., Google/Microsoft), file storage/backup. Who keeps these running and secure?_",
            ["Self-managed", "Outsourced IT", "Shared responsibility", "Not sure"],
            key="bp_it_manager",
            horizontal=False
        )
        # Q2 — Inventory
        ask_radio(
            2, "📋",
            "Do you keep a simple **list of company devices** (laptops, phones, servers)?",
            "_Helps find forgotten or unmanaged gear._",
            ["Yes", "Partially", "No", "Not sure"],
            key="bp_inventory"
        )
        # Q3 — BYOD
        ask_radio(
            3, "📱",
            "Do people use **personal devices** for work (BYOD)?",
            "_Example: staff reading work email on a personal phone or laptop._",
            ["Yes", "Sometimes", "No", "Not sure"],
            key="bp_byod"
        )
        # Q4 — Sensitive data
        ask_radio(
            4, "🔐",
            "Do you handle **sensitive customer or financial data**?",
            "_Examples: payment details, personal records, contracts._",
            ["Yes", "No", "Not sure"],
            key="bp_sensitive"
        )

        st.markdown("---")
        st.subheader("🌐 Section 2 — Digital Footprint")
        # Q5 — Website
        ask_radio(
            5, "🕸️",
            "Do you have a **public website**?",
            "_This helps us understand internet-facing entry points._",
            ["Yes", "No"],
            key="df_website"
        )
        # Q6 — HTTPS
        ask_radio(
            6, "🔒",
            "Is your website **HTTPS** (padlock in the browser)?",
            "_Encrypts traffic and builds trust with visitors._",
            ["Yes", "No", "Not sure"],
            key="df_https"
        )
        # Q7 — Business email
        ask_radio(
            7, "✉️",
            "Do you use **business email addresses** (e.g., info@yourcompany.com)?",
            "_Personal Gmail/Yahoo accounts increase phishing risk._",
            ["Yes", "Partially", "No"],
            key="df_email"
        )
        # Q8 — Social presence
        ask_radio(
            8, "📣",
            "Is your business **active on social media** (LinkedIn, Instagram, etc.)?",
            "_Helps gauge your brand’s visibility online._",
            ["Yes", "No"],
            key="df_social"
        )
        # Q9 — Open info check
        ask_radio(
            9, "🔎",
            "Do you regularly **check what’s public** about the company or staff online?",
            "_E.g., contact details, staff lists, screenshots that reveal systems._",
            ["Yes", "Sometimes", "No"],
            key="df_review"
        )

    st.markdown("---")
    c1, c2 = st.columns(2)
    if c1.button("⬅ Back"):
        next_page("Initial 1")
    if c2.button("Finish Initial Assessment ✅", type="primary"):
        next_page("Summary")

elif st.session_state.page == "Summary":
    # ---- compact CSS so everything fits above the fold ----
    st.markdown("""
    <style>
      .block-container {padding-top: 1.2rem; padding-bottom: 0.6rem; max-width: 1150px;}
      h1, h2, h3, h4 {margin: .2rem 0 .6rem;}
      .card {border:1px solid #e6e8ec; border-radius:12px; padding:10px 12px; background:#fff;}
      .badge {display:inline-flex; align-items:center; gap:.45rem; padding:.25rem .6rem;
              border-radius:999px; font-weight:600; background:#e3f7e8; color:#0f5132; border:1px solid #c8eed1;}
      .warn {background:#fff6db; color:#8a6d00; border-color:#fde9a9;}
      .danger {background:#ffe6e6; color:#842029; border-color:#ffcdcd;}
      .muted {color:#6b7280; font-size:.92rem;}
      ul {margin:.25rem 0 .25rem 1.1rem;} ul li{margin:.15rem 0;}
      .metric {border:1px solid #eceff3; border-radius:12px; padding:10px; text-align:center;}
      .metric h4{margin:.1rem 0 .25rem; font-size:1rem;}
      .metric .v{font-size:1.05rem; font-weight:700;}
      .cta-row {margin-top:.5rem;}
    </style>
    """, unsafe_allow_html=True)

    # ---- single source of truth for the profile block (avoids duplication) ----
    def render_snapshot_card():
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
        if inv == "yes":           return "🟢 Good", "Device list maintained."
        if inv == "partially":     return "🟡 Partial", "Finish your device list."
        if inv in {"no","not sure"}: return "🔴 At risk", "No inventory → hard to secure."
        return "⚪ Unknown", "—"

    def area_people_access():
        byod  = (st.session_state.bp_byod or "").lower()
        email = (st.session_state.df_email or "").lower()
        if byod == "no" and email == "yes":                 return "🟢 Safe", "Managed devices & business email."
        if email == "no":                                    return "🔴 At risk", "Personal email in use."
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

    # ---------- header + traffic light ----------
    level, emoji = digital_dependency_level()
    st.markdown("## ✅ Initial Assessment Summary")
    if level == "Low":
        st.markdown(f'<span class="badge">🟢 Overall digital dependency: <b>Low</b></span>', unsafe_allow_html=True)
        st.caption("Great job — strong digital hygiene and low exposure.")
    elif level == "Medium":
        st.markdown(f'<span class="badge warn">🟡 Overall digital dependency: <b>Medium</b></span>', unsafe_allow_html=True)
        st.caption("Balanced setup. A few quick wins will reduce risk fast.")
    else:
        st.markdown(f'<span class="badge danger">🔴 Overall digital dependency: <b>High</b></span>', unsafe_allow_html=True)
        st.caption("Higher exposure — prioritise quick actions to lower risk.")

    st.markdown("")

    # ---------- TOP ROW: Snapshot (left) · At-a-glance tiles (right) ----------
    c_left, c_right = st.columns([1.15, 1.85], gap="large")
    with c_left:
        st.markdown("#### Snapshot")
        render_snapshot_card()

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

    # ---------- MIDDLE ROW: Strengths vs Risks side-by-side ----------
    hi, bs = summary_highlights_and_blindspots()
    s_col, r_col = st.columns(2, gap="large")
    with s_col:
        st.markdown("#### ✅ Strengths")
        st.markdown('<div class="card"><ul>'+ "".join([f"<li>{x}</li>" for x in hi]) +'</ul></div>', unsafe_allow_html=True)
    with r_col:
        st.markdown("#### ⚠️ Areas to improve")
        st.markdown('<div class="card"><ul>'+ "".join([f"<li>{x}</li>" for x in bs]) +'</ul></div>', unsafe_allow_html=True)

    # ---------- Save space: put long details behind expanders ----------
    with st.expander("Business details"):
        # reuse the same renderer to avoid drift
        render_snapshot_card()
        st.caption("This is the same information as the snapshot above (no duplication).")

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
        st.info("Top-5 recommendations view coming next.")
