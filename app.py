# Q&A Chatbot
#from langchain.llms import OpenAI

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
import fitz  # PyMuPDF
import streamlit as st
import os
import io
import pathlib
import textwrap
from PIL import Image

Image.MAX_IMAGE_PIXELS = 356277618  # Adjust this value as needed


import google.generativeai as genai


os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## Function to load OpenAI model and get respones

def get_gemini_response(input,image,prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input,image[0],prompt])
    return response.text
    
# Function to convert PDF to image
def convert_pdf_to_image(pdf_bytes):
    images = []
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        image_bytes = page.get_pixmap().tobytes()
        image = Image.open(io.BytesIO(image_bytes))
        images.append(image)
    st.image(image, caption="Uploaded PDF.", use_column_width=True)
    return images

# Function to extract images from PDF file
def extract_images_from_pdf(uploaded_file):
    images = []
    if uploaded_file is not None:
        pdf_bytes = uploaded_file.getvalue()
        pdf_document = fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")

        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)
            image_bytes = page.get_pixmap().tobytes()
            image = Image.open(io.BytesIO(image_bytes))
            images.append(image)

    return images

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        if file_extension in ["jpg", "jpeg", "png"]:
            # For image files, return the image directly
            bytes_data = uploaded_file.getvalue()
            image_parts = [
                {
                    "mime_type": uploaded_file.type,
                    "data": bytes_data
                }
            ]
            return image_parts
        elif file_extension == "pdf":
            # For PDF files, convert each page to an image and return as a list
            images = []

            # Get the bytes data of the uploaded PDF file
            pdf_bytes = uploaded_file.getvalue()

            # Open PDF file using PyMuPDF
            pdf_document = fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")

            for page_number in range(len(pdf_document)):
                # Get image bytes for each page
                page = pdf_document.load_page(page_number)
                image_bytes = page.get_pixmap().tobytes()
                
                # Convert bytes to PIL Image
                image = Image.open(io.BytesIO(image_bytes))
                
                # Convert Image to bytes
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format="JPEG")
                img_byte_arr = img_byte_arr.getvalue()

                images.append({
                    "mime_type": "image/jpeg",
                    "data": img_byte_arr
                })

            return images
        else:
            raise ValueError("Unsupported file format.")
    else:
        raise FileNotFoundError("No file uploaded")


##initialize our streamlit app

st.set_page_config(page_title="Gemini Image Demo")

st.header("Gemini Application")
input=st.text_input("Input Prompt: ",key="input")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png","pdf"])
image=""   

if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        if file_extension in ["jpg", "jpeg", "png"]:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image.", use_column_width=True)
        elif file_extension == "pdf":
            images = extract_images_from_pdf(uploaded_file)

            if images:
                st.write(f"Number of images extracted: {len(images)}")

                # Display each extracted image
                for i, image in enumerate(images):
                    st.subheader(f"Image {i + 1}")
                    st.image(image, caption=f"Page {i + 1}")
        else:
            raise ValueError("Unsupported file format.")
else:
    raise FileNotFoundError("No file uploaded")

submit=st.button("Tell me about the image")

input_prompt = """
               You are an expert in understanding invoices.
               You will receive input images as invoices &
               you will have to answer questions based on the input image
               """

## If ask button is clicked

if submit:
    image_data = input_image_setup(uploaded_file)
    response=get_gemini_response(input_prompt,image_data,input)
    st.subheader("The Response is")
    st.write(response)