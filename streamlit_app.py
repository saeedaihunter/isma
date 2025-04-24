import streamlit as st
import requests

st.set_page_config(page_title="ISMA Talent Analyzer", layout="wide")

st.title("✨ ISMA Talent Analyzer")
st.write("This tool helps you extract Units of Meaning (UOMs) from natural language descriptions and explore their deeper meanings.")

# Persistent session state
if 'extracted_list' not in st.session_state:
    st.session_state.extracted_list = []
if 'manual_uom_list' not in st.session_state:
    st.session_state.manual_uom_list = []
if 'results' not in st.session_state:
    st.session_state.results = []

# --------- PART 1: EXTRACT FROM DESCRIPTION ---------
st.header("1. Extract Talents from a Description")
with st.expander("▶ Step 1: Enter Description", expanded=True):
    gpt_input = st.text_area("Describe a person or behavior:", placeholder="Layla is a highly motivated strategist and a great team leader...")
    if st.button("Extract UOMs"):
        if gpt_input:
            with st.spinner("Extracting Units of Meaning with GPT..."):
                try:
                    gpt_api_url = "https://isma-extract-uom-854321931145.europe-west1.run.app"
                    gpt_payload = {"text": gpt_input}
                    gpt_response = requests.post(gpt_api_url, json=gpt_payload)
                    gpt_response.raise_for_status()

                    gpt_data = gpt_response.json()
                    extracted_raw = gpt_data.get("units_of_meaning", "")
                    st.session_state.extracted_list = [item.strip() for item in extracted_raw.replace("\n", ",").split(",") if item.strip()]

                    if not st.session_state.extracted_list:
                        st.warning("No Units of Meaning were extracted.")
                    else:
                        st.success("✅ Units of Meaning extracted:")
                        st.write(st.session_state.extracted_list)
                except Exception as e:
                    st.error(f"⚠️ Error: {str(e)}")
        else:
            st.warning("Please enter a description first.")

# --------- PART 2: MANUAL ENTRY ---------
st.header("2. Manual Entry of Talents")
with st.expander("▶ Step 2: Enter Talents Manually", expanded=False):
    text_input = st.text_area("Enter one UOM per line:", value="\n".join(st.session_state.manual_uom_list), height=200)
    if st.button("Analyze Manual UOMs"):
        manual_uoms = [text.strip() for text in text_input.split('\n') if text.strip()]
        if manual_uoms:
            st.session_state.manual_uom_list = manual_uoms
            with st.spinner("Analyzing talents with ISMA API..."):
                try:
                    response = requests.post(
                        "https://ismatalent-854321931145.europe-west1.run.app",
                        headers={"Content-Type": "application/json"},
                        json={"uom_list": manual_uoms}
                    )
                    response.raise_for_status()
                    st.session_state.results = response.json()
                    st.success("✅ Analysis Results:")
                    st.dataframe(st.session_state.results)
                except Exception as e:
                    st.error(f"⚠️ Error calling ISMA API: {str(e)}")
        else:
            st.warning("Please enter at least one UOM.")

# --------- PART 3: ACTION VERBS ---------
st.header("3. Discover Action Verbs for Talents")
with st.expander("▶ Step 3: Find Action Verbs", expanded=False):
    combined_uoms = list(set(st.session_state.extracted_list + st.session_state.manual_uom_list))
    default_uoms = "\n".join(combined_uoms)
    verb_input = st.text_area("List of UOMs (one per line):", value=default_uoms, height=150)
    if st.button("Get Action Verbs"):
        uom_lines = [u.strip() for u in verb_input.split('\n') if u.strip()]
        if not uom_lines:
            st.warning("Please enter at least one UOM.")
        else:
            with st.spinner("Finding action verbs via GPT..."):
                try:
                    verb_api_url = "https://find-active-verbs-854321931145.europe-west1.run.app"
                    payload = {"uoms": uom_lines}
                    response = requests.post(verb_api_url, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    st.session_state.results = data.get("results", [])
                    if st.session_state.results:
                        st.success("✅ Action Verbs Found:")
                        st.dataframe(st.session_state.results)
                    else:
                        st.info("No action verbs were returned.")
                except Exception as e:
                    st.error(f"⚠️ Error calling Action Verbs API: {str(e)}")

# --------- PART 4: SOCIAL CONTRIBUTION ---------
st.header("4. Generate Social Contribution Text")
with st.expander("▶ Step 4: Generate Contribution", expanded=False):
    uoms_default = ", ".join(combined_uoms)
    verbs_default = ""
    if st.session_state.results:
        extracted_verbs = []
        for r in st.session_state.results:
            extracted_verbs.extend([v.strip() for v in r.get('active_verbs', '').split(",")])
        verbs_default = ", ".join(sorted(set(extracted_verbs)))

    talents_input = st.text_area("Talents (comma-separated):", value=uoms_default, height=100)
    verbs_input = st.text_area("Action Verbs (comma-separated):", value=verbs_default, height=100)

    if st.button("Generate Social Contribution"):
        talents_list = [t.strip() for t in talents_input.split(",") if t.strip()]
        verbs_list = [v.strip() for v in verbs_input.split(",") if v.strip()]

        if not talents_list or not verbs_list:
            st.warning("Please provide both talents and action verbs.")
        else:
            with st.spinner("Generating description..."):
                try:
                    contribution_api_url = "https://unique-social-contribution-writer-854321931145.europe-west1.run.app"
                    payload = {"uoms": talents_list, "verbs": verbs_list}
                    response = requests.post(contribution_api_url, json=payload)
                    response.raise_for_status()

                    data = response.json()
                    description = data.get("description", "No description returned.")
                    st.success("🌟 Unique Social Contribution:")
                    st.write(description)
                except Exception as e:
                    st.error(f"⚠️ Error calling Contribution API: {str(e)}")
