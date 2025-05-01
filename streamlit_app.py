# isma_talent_analyzer.py
import json
import textwrap
import requests
import pandas as pd
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG ─ change endpoints in .streamlit/secrets.toml or override here
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_ENDPOINTS = {
    "extract": "https://isma-extract-uom-854321931145.europe-west1.run.app",
    "analyze": "https://ismatalent-854321931145.europe-west1.run.app",
    "verbs":   "https://find-active-verbs-854321931145.europe-west1.run.app",
    "social":  "https://unique-social-contribution-writer-854321931145.europe-west1.run.app",
}
ENDPOINTS = st.secrets.get("isma_api", DEFAULT_ENDPOINTS)

# ──────────────────────────────────────────────────────────────────────────────
# PAGE SET-UP
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="ISMA Talent Analyzer", layout="wide")
st.title("✨ ISMA Talent Analyzer")

st.sidebar.header("⚙️ Settings")
for k in DEFAULT_ENDPOINTS:
    ENDPOINTS[k] = st.sidebar.text_input(f"{k.capitalize()} endpoint", ENDPOINTS[k])

# keep wizard state
step = st.session_state.get("step", 1)

# handy helper
def call_api(url: str, payload: dict, err_msg: str):
    try:
        r = requests.post(url, json=payload, timeout=40)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        st.error(f"{err_msg}: {exc}")
        st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# STEP 1 – EXTRACT UOMs
# ──────────────────────────────────────────────────────────────────────────────
if step == 1:
    st.subheader("1️⃣  Describe the person or behaviour")

    SAMPLE = textwrap.dedent("""
        Quentin est un explorateur d'idées permanent. Il relie l'improbable et entraîne son équipe …
    """).strip()

    if st.button("Load sample"):
        st.session_state["description"] = SAMPLE

    with st.form("extract_form", clear_on_submit=False):
        description = st.text_area(
            "Paste or type a description", 
            value=st.session_state.get("description", ""), 
            height=180, placeholder="Layla is a highly motivated strategist…"
        )
        submitted = st.form_submit_button("🚀 Extract talents")

    if submitted and description.strip():
        with st.spinner("Calling GPT to extract talents…"):
            data = call_api(
                ENDPOINTS["extract"],
                {"text": description},
                "Cannot extract talents"
            )
        uoms = [u.strip() for u in data.get("units_of_meaning", "").replace("\n", ",").split(",") if u.strip()]
        st.session_state["uoms"] = uoms or []
        st.session_state["step"] = 2
        st.experimental_rerun()

# ──────────────────────────────────────────────────────────────────────────────
# STEP 2 – REVIEW & ANALYZE UOMs
# ──────────────────────────────────────────────────────────────────────────────
if step == 2:
    st.subheader("2️⃣  Review / prioritise talents")
    st.info("Drag rows to reorder – top = highest priority")

    # initial DataFrame
    df_uom = pd.DataFrame({"Talent": st.session_state.get("uoms", [])})
    edited_df = st.data_editor(df_uom, num_rows="dynamic", use_container_width=True, reorderable=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ Back"):
            st.session_state["step"] = 1
            st.experimental_rerun()

    with col2:
        if st.button("🔎 Analyze talents"):
            uom_list = edited_df["Talent"].dropna().astype(str).tolist()
            st.session_state["uoms"] = uom_list
            with st.spinner("Analyzing talents…"):
                analysis = call_api(
                    ENDPOINTS["analyze"],
                    {"uom_list": uom_list},
                    "Cannot analyze talents"
                )
            st.session_state["analysis"] = analysis
            st.success(f"Analyzed {len(uom_list)} talents")
            st.dataframe(analysis, use_container_width=True)
            st.session_state["step"] = 3

    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# STEP 3 – FIND ACTION VERBS
# ──────────────────────────────────────────────────────────────────────────────
if step == 3:
    st.subheader("3️⃣  Get inspiring action verbs")

    with st.form("verb_form"):
        st.write("Select the talents for which you want verbs:")
        selected_uoms = st.multiselect(
            "Talents", st.session_state.get("uoms", []), 
            default=st.session_state.get("uoms", [])
        )
        verb_sub = st.form_submit_button("⚡ Find verbs")

    if verb_sub and selected_uoms:
        with st.spinner("Fetching verbs…"):
            verb_json = call_api(
                ENDPOINTS["verbs"],
                {"uoms": selected_uoms},
                "Cannot find verbs"
            )

        # flatten into a DataFrame with a choose checkbox
        rows = []
        for item in verb_json.get("results", []):
            talent = item["uom"]
            verbs = [v.strip() for v in item["active_verbs"].split(",") if v.strip()]
            rows.extend({"Use": True, "Talent": talent, "Verb": v} for v in verbs)

        df_verbs = pd.DataFrame(rows)
        edited_verbs = st.data_editor(df_verbs, use_container_width=True)

        # store only checked verbs
        chosen = edited_verbs[edited_verbs["Use"]]["Verb"].unique().tolist()
        st.session_state["verbs"] = chosen

        if st.button("➡ Next: craft contribution"):
            st.session_state["step"] = 4
            st.experimental_rerun()

    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# STEP 4 – GENERATE UNIQUE SOCIAL CONTRIBUTION
# ──────────────────────────────────────────────────────────────────────────────
if step == 4:
    st.subheader("4️⃣  Generate unique social contribution")

    st.write("Reorder talents if needed (importance top-down) and uncheck verbs you don’t like.")

    # talents reorder
    df_tal = pd.DataFrame({"Talent": st.session_state["uoms"]})
    df_tal = st.data_editor(df_tal, reorderable=True, use_container_width=True, num_rows="dynamic")

    # verbs selector
    df_ver = pd.DataFrame({"Use": True, "Verb": st.session_state.get("verbs", [])})
    df_ver = st.data_editor(df_ver, use_container_width=True)

    if st.button("🌟 Generate contribution"):
        final_talents = df_tal["Talent"].dropna().astype(str).tolist()
        final_verbs   = df_ver[df_ver["Use"]]["Verb"].astype(str).tolist()

        if not final_talents or not final_verbs:
            st.warning("Need at least one talent and one verb.")
            st.stop()

        with st.spinner("Composing sentence…"):
            result = call_api(
                ENDPOINTS["social"],
                {"uoms": final_talents, "verbs": final_verbs},
                "Cannot generate contribution"
            )

        sentence = result.get("description", "No description returned.")
        st.success("🎉 Your unique social contribution")
        st.write(sentence)

        # offer download
        payload = {
            "talents": final_talents,
            "verbs": final_verbs,
            "contribution": sentence,
        }
        st.download_button(
            "💾 Download JSON",
            data=json.dumps(payload, indent=2, ensure_ascii=False),
            file_name="isma_profile.json",
            mime="application/json",
        )

    if st.button("↩ Back"):
        st.session_state["step"] = 3
        st.experimental_rerun()
