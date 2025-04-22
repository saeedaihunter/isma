import streamlit as st
import requests
import json

st.title("ISMA Talent Analyzer")
st.write("This tool lets you extract Units of Meaning (UOMs) from a natural language description and analyze them.")

# ----------- INPUT SECTION -----------
st.subheader("Step 1: Describe a person or behavior")
gpt_input = st.text_area(
    "Write a natural language description:",
    placeholder="Layla is a highly motivated strategist and a great team leader..."
)

# ----------- CHAINED WORKFLOW BUTTON -----------
if st.button("Extract UOMs and Analyze"):
    if gpt_input:
        with st.spinner("Extracting Units of Meaning with GPT..."):
            try:
                # Step 1: Call GPT Extraction API
                gpt_api_url = "https://037b-34-70-50-221.ngrok-free.app/extract"  # ✅ replace if needed
                gpt_payload = {"text": gpt_input}
                gpt_response = requests.post(gpt_api_url, json=gpt_payload)
                gpt_response.raise_for_status()

                # Get extracted text
                gpt_data = gpt_response.json()
                extracted_raw = gpt_data.get("units_of_meaning", "")
                extracted_list = [
                    item.strip() for item in extracted_raw.replace("\n", ",").split(",") if item.strip()
                ]

                if not extracted_list:
                    st.warning("No units of meaning were extracted.")
                else:
                    st.success("✅ Units of Meaning extracted:")
                    st.write(extracted_list)

                    with st.spinner("Analyzing UOMs via ISMA API..."):
                        # Step 2: Call ISMA API with extracted UOMs
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

# ----------- MANUAL FALLBACK SECTION -----------
st.markdown("---")
st.subheader("Manual Entry: Enter Units of Meaning directly")

text_input = st.text_area(
    "Enter Units of Meaning (one per line):",
    height=300,
    placeholder="fearless\nhe is a great person\nattitude bienveillante\n..."
)

if st.button("Submit Manual UOMs"):
    if text_input:
        text_list = [text.strip() for text in text_input.split('\n') if text.strip()]
        if text_list:
            with st.spinner("Processing UOMs..."):
                try:
                    response = requests.post(
                        "https://ismatalent-854321931145.europe-west1.run.app",
                        headers={"Content-Type": "application/json"},
                        json={"uom_list": text_list}
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
