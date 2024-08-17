import requests
import streamlit as st
from PIL import Image       # Importing library PIL (Pillow) for image processing and displaying images
from io import BytesIO      # Importing library BytesIO for handling image data as a byte stream


# Function to generate a description of the image using the Hugging Face API
def generate_description(image_url):
    api_key = "Enter your api"  # Replaced these with my Hugging Face API key
    headers = {
        'Authorization': f'Bearer {api_key}'  # Set up the authorization header with the API key
    }
    payload = {
        'inputs': image_url                                                                         # Provided the image URL as input to the API
    }
    response = requests.post(
        'https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large',       # Used preprocess trained huggingface model
        headers=headers,
        json=payload  # Sent the request payload as JSON
    )

    # Checked the response status code
    if response.status_code == 200:
        result = response.json()  # Parsed the response JSON
        if isinstance(result, list) and len(result) > 0:
            description = result[0].get('generated_text', 'No description found')       # Extracted the description text
            return description
        else:
            return 'Unexpected response format'  # Handled unexpected response formats
    else:
        return f'Error in API request: {response.json()}'                  # Returned error message if the API request failed

# Function to analyze the emotion of the description by using the Hugging Face API
def analyze_emotion(description):
    api_key = "Enter your api"                  # Replaced with my Hugging Face API key
    headers = {
        'Authorization': f'Bearer {api_key}'                            # Set up the authorization header with the API key
    }
    payload = {
        'inputs': description  # Provided the description text as input to the API
    }
    response = requests.post(
        'https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english',  # Used preprocess trained huggingface sentiment model
        headers=headers,
        json=payload  # Sent the request payload as JSON
    )

    # Checked the response status code
    if response.status_code == 200:
        result = response.json()  # Parsed the response JSON
        if isinstance(result, list) and len(result) > 0:
            sentiment = result[0]  # Extracted sentiment data
            positive_score = next((item['score'] for item in sentiment if item['label'] == 'POSITIVE'), 0)  # Got positive score
            negative_score = next((item['score'] for item in sentiment if item['label'] == 'NEGATIVE'), 0)  # Got negative score

            # Defined thresholds for mapping emotions
            if positive_score > 0.6:
                return "happy"  # Returned "happy" if positive score was greater than 0.6
            elif negative_score > 0.5:
                return "sad"  # Returned "sad" if negative score was greater than 0.5 as mentioned in assignment description
            elif 0.5 <= positive_score <= 0.6:
                return "neutral"  # Returned "neutral" if positive score was between 0.5 and 0.6
            else:
                return "neutral"  # Defaulted to "neutral" if none of the conditions were met
        else:
            return 'Unexpected response format'  
    else:
        return f'Error in API request: {response.json()}'  # Returned error message if the API request failed

# creating Streamlit app for user friendly-experience
st.title("Analysing tone of Emotion by Image-Text Description")  # Set the title of the app
st.write("Enter the URL of an image to get its description and analyze the emotion based on the description.")

image_url = st.text_input("Image URL")  # Created a text input field for the image URL

if st.button("Analyze"):  # When the "Analyze" button was pressed
    if image_url:  # Checked if an image URL had been provided
        # Displayed the image
        try:
            response = requests.get(image_url)  # Fetched the image from the URL
            image = Image.open(BytesIO(response.content))  # Opened the image using PIL
            st.image(image, caption="Input Image", use_column_width=True)  # Displayed the image in the app
        except Exception as e:
            st.write(f"Error loading image: {e}")  # Handled errors if the image could not be loaded

        st.write("Generating description...")  # Informed the user that the description was being generated
        description = generate_description(image_url)  # Called the function to generate the description
        st.write(f"Description: {description}")  # Displayed the description

        if 'Error' not in description:  # Checked if no error occurred while generating the description
            st.write("Analyzing emotion...")  # by these piece of code informed the user that the emotion was being analyzed
            emotion = analyze_emotion(description)  # Called the function to analyze the emotion
            st.write(f"Emotion: {emotion}")  # Displayed the detected emotion
        else:
            st.write("Failed to generate description.")  # Informed the user if the description generation failed
    else:
        st.write("Please enter a valid image URL.")  # Prompted the user to enter a valid image URL if none was provided
