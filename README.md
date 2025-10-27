# 🛡️ SME Cybersecurity Self-Assessment

A lightweight, privacy-safe web app that helps **small and medium-sized enterprises (SMEs)** assess their cybersecurity maturity — including **AI-driven social-engineering risks** — through quick questions, guided simulations, and clear next steps.

---

## 🚀 Live Demo
**▶️ Streamlit Cloud:** [Launch the app here](https://share.streamlit.io/aakagoyal/cybersecproject/main/app.py)

---

## 🧩 Features
- 🧭 5-step guided assessment flow (Business Basics → Operational Context → Baseline → Detailed → Report)
- 🧩 7 assessment domains  
  *(Governance, Access & Identity, Device & Data, System & Software Updates, Incident Preparedness, Vendor & Cloud, Awareness & AI Risk)*
- 🎯 Real-time traffic-light scoring (0-100) with visual dashboard
- 💡 Inline hints & “Why it matters” guidance under each question
- 🧪 Interactive **Simulations** — practise spotting phishing & AI-based deception
- 🔒 Privacy-first design (no data stored, local session only)
- 📄 Export results as CSV and Markdown summaries

---

## 🧱 Tech Stack
- [Streamlit](https://streamlit.io/) (Python 3.11)
- Built-in CSS for responsive layout (no external chart libs)
- Deterministic local scoring (no backend or DB)
- Exports via standard Python libraries (`csv`, `io`, `datetime`)

---

## 🧭 How to Run Locally
```bash
# Clone the repo
git clone https://github.com/AakaGoyal/cybersecproject.git
cd cybersecproject

# (Optional) create venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install requirements
pip install -r requirements.txt

# Run the app
streamlit run app.py
