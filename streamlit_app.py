import streamlit as st
import requests
import json


def call_api(text_list):
    """Call the API with the list of texts"""
    url = "https://ismatalent-854321931145.europe-west1.run.app"
    
    # Prepare the payload
    payload = {
        "uom_list": text_list
    }
    
    # Set the headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Make the API call
    response = requests.post(url, headers=headers, json=payload)
    
    # Raise an exception for bad status codes
    response.raise_for_status()
    
    # Return the JSON response
    return response.json()


st.title("ISMA talent association test")
st.write("Enter Units of Meanings below (one per line) and click on submit to process")

# Create a text area for user input
text_input = st.text_area(
    "Enter texts (one per line):",
    height=300,
    placeholder="fearless\nhe is a great person\nattitude bienveillante\n..."
)

# Process the text input when the button is clicked
if st.button("Submit to API"):
    if text_input:
        # Split the input by newline and remove empty lines
        text_list = [text.strip() for text in text_input.split('\n') if text.strip()]
        
        if text_list:
            with st.spinner("Processing..."):
                try:
                    # Call the API
                    response = call_api(text_list)
                    
                    # Display the response
                    st.dataframe(response)
                    
                except Exception as e:
                    st.error(f"Error calling API: {str(e)}")
        else:
            st.warning("Please enter at least one text item")
    else:
        st.warning("Please enter text before submitting")

st.markdown("---")
st.subheader("Extract Units of Meaning with GPT")

# Input for full-text description
gpt_input = st.text_area(
    "Enter a description of a person or behavior:",
    placeholder="Layla is a highly motivated strategist and a great team leader..."
)

# Call GPT extraction API
if st.button("Extract with GPT"):
    if gpt_input:
        with st.spinner("Extracting..."):
            try:
                # Replace this URL with your ngrok/public FastAPI endpoint
                gpt_api_url = "https://ed86-34-125-230-117.ngrok-free.app/extract"

                gpt_payload = {
                    "text": gpt_input
                }

                gpt_response = requests.post(gpt_api_url, json=gpt_payload)
                gpt_response.raise_for_status()

                data = gpt_response.json()
                extracted = data.get("units_of_meaning", "No units found.")
                st.success("Units of meaning extracted:")
                st.text(extracted)

            except Exception as e:
                st.error(f"Error calling GPT extraction API: {str(e)}")
    else:
        st.warning("Please enter a description to extract from.")

