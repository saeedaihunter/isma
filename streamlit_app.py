# isma_talent_analyzer.py  – titles now match the doc’s wording
import requests, pandas as pd, streamlit as st

# ── utilities ────────────────────────────────────────────────────────────────
def rerun(): (getattr(st, "rerun", None) or st.experimental_rerun)()
def call_api(url, payload, err_msg):
    try:
        r = requests.post(url, json=payload, timeout=90)
        r.raise_for_status();  return r.json()
    except Exception as e:
        st.error(f"{err_msg}: {e}");  st.stop()

# ── endpoints (kept internal) ────────────────────────────────────────────────
API = st.secrets.get("isma_api", {
    "extract": "https://isma-extract-uom-854321931145.europe-west1.run.app",
    "analyze": "https://ismatalent-854321931145.europe-west1.run.app",
    "verbs":   "https://find-active-verbs-854321931145.europe-west1.run.app",
    "social":  "https://unique-social-contribution-writer-854321931145.europe-west1.run.app",
})

st.set_page_config(page_title="ISMA Talent Analyzer", layout="wide")
st.title("✨ ISMA Talent Analyzer")

step = st.session_state.get("step", 1)

# ── STEP 1 : Extract Units of Meaning ────────────────────────────────────────
if step == 1:
    st.subheader("1️⃣  Extract Units of Meaning")
    SAMPLE = "Quentin est un explorateur d'idées permanent…"
    if st.button("Load sample"): st.session_state["description"] = SAMPLE

    with st.form("extract"):
        desc = st.text_area("Paste description", value=st.session_state.get("description",""),
                            height=160, placeholder="Layla is a highly motivated strategist…")
        if st.form_submit_button("🚀 Extract UoMs") and desc.strip():
            with st.spinner("Extracting…"):
                data = call_api(API["extract"], {"text": desc}, "Cannot extract UoMs")
            st.session_state["uoms"] = [u.strip() for u in data.get("units_of_meaning","")
                                         .replace("\n",",").split(",") if u.strip()]
            st.session_state["step"] = 2 ; rerun()

# ── STEP 2 : Prioritise Super-Talents ────────────────────────────────────────
if step == 2:
    st.subheader("2️⃣  Prioritise Super-Talents")
    df = pd.DataFrame({"Talent": st.session_state["uoms"]})
    df = st.data_editor(df, reorderable=True, use_container_width=True, num_rows="dynamic")

    back, fwd = st.columns(2)
    if back.button("⬅ Back"): st.session_state["step"] = 1 ; rerun()

    if fwd.button("🔎 Analyze Super-Talents"):
        uoms = df["Talent"].dropna().astype(str).tolist()
        st.session_state["uoms"] = uoms
        with st.spinner("Analyzing…"):
            res = call_api(API["analyze"], {"uom_list": uoms}, "Cannot analyze")
        st.session_state["analysis"] = res
        st.success(f"{len(uoms)} super-talents analyzed")
        st.dataframe(res, use_container_width=True)
        st.session_state["step"] = 3 ; rerun()

# ── STEP 3 : Find Inspiring Action Verbs ─────────────────────────────────────
if step == 3:
    st.subheader("3️⃣  Find Inspiring Action Verbs")
    with st.form("verbs"):
        chosen = st.multiselect("Select super-talents", st.session_state["uoms"],
                                default=st.session_state["uoms"])
        if st.form_submit_button("⚡ Get verbs") and chosen:
            with st.spinner("Fetching verbs…"):
                out = call_api(API["verbs"], {"uoms": chosen}, "Cannot fetch verbs")

            rows = [{"Use": True, "Talent": itm["uom"], "Verb": v.strip()}
                    for itm in out.get("results", [])
                    for v in itm["active_verbs"].split(",") if v.strip()]
            st.session_state["verbs_df"] = pd.DataFrame(rows)
            st.session_state["step"] = 4 ; rerun()

# ── STEP 4 : Craft Unique Social Contribution (Over-Capacity) ────────────────
if step == 4:
    st.subheader("4️⃣  Craft Unique Social Contribution (Over-Capacity)")

    df_tal = pd.DataFrame({"Talent": st.session_state["uoms"]})
    df_ver = st.session_state.get("verbs_df", pd.DataFrame(columns=["Use","Talent","Verb"]))

    st.markdown("**Reorder super-talents (top = highest priority)**")
    df_tal = st.data_editor(df_tal, reorderable=True, use_container_width=True)

    st.markdown("**Select verbs to keep**")
    df_ver = st.data_editor(df_ver, use_container_width=True)

    back, gen = st.columns(2)
    if back.button("⬅ Back"): st.session_state["step"] = 3 ; rerun()

    if gen.button("🌟 Generate contribution"):
        talents = df_tal["Talent"].dropna().astype(str).tolist()
        verbs   = df_ver[df_ver["Use"]]["Verb"].astype(str).tolist()
        if not talents or not verbs:
            st.warning("Need at least one super-talent and one verb.")
        else:
            with st.spinner("Composing sentence…"):
                res = call_api(API["social"], {"uoms": talents, "verbs": verbs},
                               "Cannot generate contribution")
            st.success("🎉 Unique Social Contribution")
            st.write(res.get("description", "No description returned."))
