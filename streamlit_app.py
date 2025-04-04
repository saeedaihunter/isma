import streamlit as st
import requests
import json


def call_api(text_list):
    """Call the API with the list of texts"""
    url = "https://test2-996798979251.us-central1.run.app"
    
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
st.write("Enter Units Of Meanings below (one per line) and submit to process")

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
