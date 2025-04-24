import streamlit as st
import requests

st.set_page_config(page_title="ISMA Talent Analyzer", layout="wide")
st.title("✨ ISMA Talent Analyzer")
st.write("This tool helps you extract Units of Meaning (UOMs), analyze them, find matching action verbs, and generate a unique social contribution.")

# Initialize session state variables
st.session_state.setdefault('extracted_list', [])
st.session_state.setdefault('manual_uom_list', [])
st.session_state.setdefault('analysis_results', [])
st.session_state.setdefault('verb_results', [])

# --------- PART 1: EXTRACT FROM DESCRIPTION ---------
st.header("1. Extract Talents from a Description")
with st.expander("▶ Step 1: Enter Description", expanded=True):
    gpt_input = st.text_area("Describe a person or behavior:", placeholder="Layla is a highly motivated strategist and a great team leader...")
    if st.button("Extract UOMs"):
        if gpt_input:
            with st.spinner("Extracting Units of Meaning with GPT..."):
                try:
                    response = requests.post("https://isma-extract-uom-854321931145.europe-west1.run.app", json={"text": gpt_input})
                    response.raise_for_status()
                    uoms = response.json().get("units_of_meaning", "")
                    st.session_state.extracted_list = [u.strip() for u in uoms.replace("\n", ",").split(",") if u.strip()]
                    st.success("✅ Extracted UOMs:")
                    st.write(st.session_state.extracted_list)
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")
        else:
            st.warning("Please enter a description first.")

# --------- PART 2: ANALYZE UOMS ---------
st.header("2. Analyze Extracted or Manual Talents")
with st.expander("▶ Step 2: Review/Edit Talents and Analyze", expanded=True):
    combined_uoms = st.session_state.extracted_list + st.session_state.manual_uom_list
    default_uom_text = "\n".join(combined_uoms)
    manual_input = st.text_area("Edit or add talents (one per line):", value=default_uom_text, height=200)

    if st.button("Analyze Talents"):
        uom_list = [line.strip() for line in manual_input.split("\n") if line.strip()]
        st.session_state.manual_uom_list = uom_list
        with st.spinner("Analyzing talents..."):
            try:
                response = requests.post("https://ismatalent-854321931145.europe-west1.run.app", json={"uom_list": uom_list})
                response.raise_for_status()
                st.session_state.analysis_results = response.json()
                st.success("✅ Analysis Results:")
                st.dataframe(st.session_state.analysis_results)
            except Exception as e:
                st.error(f"⚠️ Error calling ISMA API: {e}")

# --------- PART 3: FIND ACTION VERBS ---------
st.header("3. Discover Action Verbs for Talents")
with st.expander("▶ Step 3: Get Action Verbs", expanded=True):
    all_uoms = st.session_state.manual_uom_list
    uom_input = "\n".join(all_uoms)
    verb_input_area = st.text_area("Talents for verb extraction (one per line):", value=uom_input, height=150)

    if st.button("Find Action Verbs"):
        uoms = [u.strip() for u in verb_input_area.split("\n") if u.strip()]
        if uoms:
            with st.spinner("Finding action verbs..."):
                try:
                    response = requests.post("https://find-active-verbs-854321931145.europe-west1.run.app", json={"uoms": uoms})
                    response.raise_for_status()
                    st.session_state.verb_results = response.json().get("results", [])
                    st.success("✅ Found Action Verbs:")
                    st.dataframe(st.session_state.verb_results)
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")
        else:
            st.warning("Enter at least one UOM.")

# --------- PART 4: SOCIAL CONTRIBUTION ---------
st.header("4. Generate Unique Social Contribution")
with st.expander("▶ Step 4: Generate Description", expanded=True):
    talents = ", ".join(st.session_state.manual_uom_list)
    verbs = ", ".join({v.strip() for r in st.session_state.verb_results for v in r.get('active_verbs', '').split(',') if v.strip()})

    talents_input = st.text_area("Talents (comma-separated):", value=talents)
    verbs_input = st.text_area("Action Verbs (comma-separated):", value=verbs)

    if st.button("Generate Contribution Text"):
        talents_list = [t.strip() for t in talents_input.split(",") if t.strip()]
        verbs_list = [v.strip() for v in verbs_input.split(",") if v.strip()]

        if not talents_list or not verbs_list:
            st.warning("Please provide both talents and verbs.")
        else:
            with st.spinner("Generating contribution text..."):
                try:
                    response = requests.post("https://unique-social-contribution-writer-854321931145.europe-west1.run.app", json={"uoms": talents_list, "verbs": verbs_list})
                    response.raise_for_status()
                    description = response.json().get("description", "No description returned.")
                    st.success("🌟 Unique Social Contribution:")
                    st.write(description)
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")
