import streamlit as st
import requests
import json

st.title("ISMA Talent Analyzer")
st.write("This tool lets you extract Units of Meaning (UOMs) from a natural language description and analyze them.")

# ----------------------------------------
# PART 1: EXTRACT UOMs FROM A TEXT BLOCK
# ----------------------------------------
st.subheader("Step 1: Describe a person or behavior")
gpt_input = st.text_area(
    "Write a natural language description:",
    placeholder="Layla is a highly motivated strategist and a great team leader..."
)

extracted_list = []

if st.button("Extract UOMs and Analyze"):
    if gpt_input:
        with st.spinner("Extracting Units of Meaning with GPT..."):
            try:
                gpt_api_url = "https://isma-extract-uom-854321931145.europe-west1.run.app"
                gpt_payload = {"text": gpt_input}
                gpt_response = requests.post(gpt_api_url, json=gpt_payload)
                gpt_response.raise_for_status()

                gpt_data = gpt_response.json()
                extracted_raw = gpt_data.get("units_of_meaning", "")
                extracted_list = [item.strip() for item in extracted_raw.replace("\n", ",").split(",") if item.strip()]

                if not extracted_list:
                    st.warning("No units of meaning were extracted.")
                else:
                    st.success("✅ Units of Meaning extracted:")
                    st.write(extracted_list)

                    with st.spinner("Analyzing UOMs via ISMA API..."):
                        isma_url = "https://ismatalent-854321931145.europe-west1.run.app"
                        isma_payload = {"uom_list": extracted_list}
                        isma_response = requests.post(isma_url, json=isma_payload)
                        isma_response.raise_for_status()

                        isma_data = isma_response.json()
                        if isma_data:
                            st.success("✅ Talent associations found:")
                            st.dataframe(isma_data)
                        else:
                            st.info("No associations were found for the extracted UOMs.")

            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")
    else:
        st.warning("Please enter a description first.")

# ----------------------------------------
#  PART 2: MANUAL ENTRY OF UOMs
# ----------------------------------------
st.markdown("---")
st.subheader("Manual Entry: Enter Units of Meaning directly")

text_input = st.text_area(
    "Enter Units of Meaning (one per line):",
    height=300,
    placeholder="fearless\nhe is a great person\nattitude bienveillante\n..."
)

manual_uom_list = []

if st.button("Submit Manual UOMs"):
    if text_input:
        manual_uom_list = [text.strip() for text in text_input.split('\n') if text.strip()]
        if manual_uom_list:
            with st.spinner("Processing UOMs..."):
                try:
                    response = requests.post(
                        "https://ismatalent-854321931145.europe-west1.run.app",
                        headers={"Content-Type": "application/json"},
                        json={"uom_list": manual_uom_list}
                    )
                    response.raise_for_status()
                    data = response.json()
                    st.success("✅ Results:")
                    st.dataframe(data)
                except Exception as e:
                    st.error(f"⚠️ Error calling ISMA API: {str(e)}")
        else:
            st.warning("Please enter at least one UOM.")
    else:
        st.warning("Please enter text before submitting.")

# ----------------------------------------
#  PART 3: GET ACTION VERBS FOR UOMs
# ----------------------------------------
st.markdown("---")
st.subheader("Find Action Verbs for UOMs")

# Combine both sources (manual or extracted) for user convenience
uoms_for_verbs = []

if extracted_list:
    uoms_for_verbs.extend(extracted_list)

if manual_uom_list:
    uoms_for_verbs.extend(manual_uom_list)

# Deduplicate
uoms_for_verbs = list(set(uoms_for_verbs))

default_uoms = "\n".join(uoms_for_verbs)

verb_input = st.text_area(
    "Enter UOMs for which to find action verbs (one per line):",
    value=default_uoms,
    height=200
)

if st.button("Get Action Verbs"):
    uom_lines = [u.strip() for u in verb_input.split('\n') if u.strip()]
    if not uom_lines:
        st.warning("Please enter at least one UOM.")
    else:
        with st.spinner("Calling GPT to find related verbs..."):
            try:
                verb_api_url = "https://find-active-verbs-854321931145.europe-west1.run.app"  
                payload = {"uoms": uom_lines}
                response = requests.post(verb_api_url, json=payload)
                response.raise_for_status()

                data = response.json()
                results = data.get("results", [])
                if results:
                    st.success("✅ Action verbs found:")
                    st.dataframe(results)
                else:
                    st.info("No action verbs were returned.")
            except Exception as e:
                st.error(f"⚠️ Error calling Active Verbs API: {str(e)}")
# ----------------------------------------
# PART 4: GENERATE SOCIAL CONTRIBUTION TEXT
# ----------------------------------------
st.markdown("---")
st.subheader("Generate Unique Social Contribution Description")

st.markdown("Provide a list of talents (UOMs) and active verbs. The AI will generate a description of the person’s social contribution.")

# Auto-fill UOMs and Verbs from previous steps if available
uoms_default = ", ".join(uoms_for_verbs) if uoms_for_verbs else ""
verbs_default = ""

# If you already have the results from Part 3 (action verbs), extract them here
if 'results' in locals():
    extracted_verbs = []
    for r in results:
        extracted_verbs.extend([v.strip() for v in r['active_verbs'].split(",")])
    verbs_default = ", ".join(sorted(set(extracted_verbs)))

talents_input = st.text_area("Talents (UOMs, comma-separated):", value=uoms_default, height=100)
verbs_input = st.text_area("Action Verbs (comma-separated):", value=verbs_default, height=100)

if st.button("Generate Contribution Text"):
    talents_list = [t.strip() for t in talents_input.split(",") if t.strip()]
    verbs_list = [v.strip() for v in verbs_input.split(",") if v.strip()]

    if not talents_list or not verbs_list:
        st.warning("Please provide both talents and action verbs.")
    else:
        with st.spinner("Generating social contribution text..."):
            try:
                contribution_api_url = "https://unique-social-contribution-writer-854321931145.europe-west1.run.app"  # 🔁 Replace this with your real URL
                payload = {"uoms": talents_list, "verbs": verbs_list}
                response = requests.post(contribution_api_url, json=payload)
                response.raise_for_status()

                data = response.json()
                description = data.get("description", "No description returned.")
                st.success("🌟 Unique Social Contribution Description:")
                st.write(description)

            except Exception as e:
                st.error(f"⚠️ Error calling Social Contribution API: {str(e)}")
