# isma_talent_analyzer.py  – 4-step wizard
import requests, pandas as pd, streamlit as st

# ───────── helpers ───────────────────────────────────────────────────────────
def rerun(): (getattr(st, "rerun", None) or st.experimental_rerun)()

def call_api(url, payload, err_msg):
    try:
        r = requests.post(url, json=payload, timeout=90)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"{err_msg}: {e}")
        st.stop()

# ───────── endpoints (private) ───────────────────────────────────────────────
API = st.secrets.get("isma_api", {
    "extract": "https://isma-extract-uom-854321931145.europe-west1.run.app",
    "analyze": "https://ismatalent-854321931145.europe-west1.run.app",
    "verbs":   "https://find-active-verbs-854321931145.europe-west1.run.app",
    "social":  "https://unique-social-contribution-writer-854321931145.europe-west1.run.app",
})

# ───────── UI SET-UP ─────────────────────────────────────────────────────────
st.set_page_config(page_title="ISMA Talent Analyzer", layout="wide")
st.title("✨ ISMA Talent Analyzer")

step = st.session_state.get("step", 1)

# ───────── STEP 1 : Extract Units of Meaning ────────────────────────────────
if step == 1:
    st.subheader("1️⃣  Extract Units of Meaning")

    SAMPLE = "Quentin est un explorateur d'idées permanent…"
    if st.button("Load sample letter"):
        st.session_state["letter"] = SAMPLE

    with st.form("extract_letter"):
        letter = st.text_area(
            "Paste the letter / description",
            value=st.session_state.get("letter", ""),
            height=180,
            placeholder="Layla is a highly motivated strategist…",
        )
        if st.form_submit_button("🚀 Extract UoMs") and letter.strip():
            with st.spinner("Extracting UoMs…"):
                data = call_api(API["extract"], {"text": letter}, "Cannot extract UoMs")
            st.session_state["uoms"] = [
                u.strip() for u in data.get("units_of_meaning", "")
                .replace("\n", ",").split(",") if u.strip()
            ]
            st.session_state["step"] = 2
            rerun()

# ───────── STEP 2 : Association Table (Super-Talents) ───────────────────────
if step == 2:
    st.subheader("2️⃣  Association Table of Super-Talents")

    # show extracted list for user context
    st.markdown("**Extracted UoMs:** " + ", ".join(st.session_state["uoms"]))

    if st.button("🔎 Analyze associations"):
        with st.spinner("Calling association service…"):
            res = call_api(API["analyze"],
                           {"uom_list": st.session_state["uoms"]},
                           "Cannot analyze UoMs")
        st.session_state["analysis"] = res
        st.success("Association table received")
        st.dataframe(res, use_container_width=True)

    col1, col2 = st.columns(2)
    if col1.button("⬅ Back"):
        st.session_state["step"] = 1
        rerun()
    if col2.button("➡ Proceed to action verbs"):
        st.session_state["step"] = 3
        rerun()

# ───────── STEP 3 : Find Inspiring Action Verbs ─────────────────────────────
if step == 3:
    st.subheader("3️⃣  Find Inspiring Action Verbs")

    default_text = "\n".join(st.session_state["uoms"])
    st.write("Edit the list below (one talent per line) or paste new ones:")
    txt = st.text_area("Talents for verb extraction", value=default_text, height=160)

    if st.button("⚡ Get verbs"):
        uoms = [ln.strip() for ln in txt.splitlines() if ln.strip()]
        if not uoms:
            st.warning("Enter at least one talent.")
            st.stop()

        with st.spinner("Fetching verbs…"):
            out = call_api(API["verbs"], {"uoms": uoms}, "Cannot fetch verbs")

        rows = [
            {"Use": True, "Talent": itm["uom"], "Verb": v.strip()}
            for itm in out.get("results", [])
            for v in itm["active_verbs"].split(",") if v.strip()
        ]
        st.session_state["verbs_df"] = pd.DataFrame(rows)
        st.success("Select the verbs you want to keep:")
        verbs_editor = st.data_editor(st.session_state["verbs_df"], use_container_width=True)
        st.session_state["verbs_kept"] = verbs_editor[verbs_editor["Use"]]["Verb"].astype(str).tolist()

    if st.session_state.get("verbs_kept"):
        if st.button("➡ Proceed to social contribution"):
            st.session_state["final_uoms"] = [ln.strip() for ln in txt.splitlines() if ln.strip()]
            st.session_state["step"] = 4
            rerun()

    if st.button("⬅ Back"):
        st.session_state["step"] = 2
        rerun()

# ───────── STEP 4 : Generate Unique Social Contribution ─────────────────────
if step == 4:
    st.subheader("4️⃣  Craft Unique Social Contribution (Over-Capacity)")

    # user may tweak ordering or wording one last time
    uom_text = ", ".join(st.session_state["final_uoms"])
    verb_text = ", ".join(st.session_state["verbs_kept"])

    uom_input  = st.text_input("Talents (comma-separated)", value=uom_text)
    verb_input = st.text_input("Action verbs (comma-separated)", value=verb_text)

    if st.button("🌟 Generate contribution"):
        talents = [t.strip() for t in uom_input.split(",") if t.strip()]
        verbs   = [v.strip() for v in verb_input.split(",") if v.strip()]
        if not talents or not verbs:
            st.warning("Need at least one talent and one verb.")
            st.stop()

        with st.spinner("Composing sentence…"):
            res = call_api(API["social"],
                           {"uoms": talents, "verbs": verbs},
                           "Cannot generate contribution")
        st.success("🎉 Unique Social Contribution")
        st.write(res.get("description", "No description returned."))

    if st.button("⬅ Back"):
        st.session_state["step"] = 3
        rerun()
