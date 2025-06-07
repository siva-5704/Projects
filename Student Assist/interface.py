import streamlit as st
import requests
from io import BytesIO

def simplify_text(input_text):
    if not input_text:
        st.warning("Please enter some text to simplify!")
        return None

    try:
        response = requests.post('http://127.0.0.1:5000/simplify', json={"text": input_text})

        if response.status_code == 200:
            simplified_text = response.json().get('simplified_text', '')
            return simplified_text
        else:
            st.error("There was an error with the simplification request.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        return None

def ask_question(question, context):
    if not question:
        st.warning("Please enter a question!")
        return None

    try:
        response = requests.post('http://127.0.0.1:5000/qa', json={"question": question, "context": context})

        if response.status_code == 200:
            answer = response.json().get('answer', 'No answer found')
            return answer
        else:
            st.error("There was an error with the Q&A request.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        return None

def upload_pdf():
    file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if file:
        files = {'file': file.getvalue()}
        try:
            response = requests.post("http://127.0.0.1:5000/upload_pdf", files=files)

            if response.status_code == 200:
                extracted_text = response.json().get("extracted_text", "")
                st.session_state.extracted_text = extracted_text
                st.subheader("Extracted Text:")
                st.write(extracted_text)
            else:
                st.error("Error extracting text from the PDF.")
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred while uploading the PDF: {e}")

st.title("Student Assist")

option = st.radio("Choose input method:", ["Text Input", "Upload PDF"])

if option == "Text Input":
    input_text = st.text_area("Enter Text to Simplify:", height=200)

    if st.button("Simplify Text"):
        simplified_text = simplify_text(input_text)
        if simplified_text:
            st.session_state.simplified_content = simplified_text              

    if 'simplified_content' in st.session_state:
        st.subheader("Simplified Text:")
        st.write(st.session_state.simplified_content)  

        question = st.text_area("Ask a Question:", height=100)

        if st.button("Get Answer"):
            answer = ask_question(question, st.session_state.simplified_content)
            if answer:
                st.subheader("Answer:")
                st.write(answer)

else:
    upload_pdf()

    if 'extracted_text' in st.session_state:
        question = st.text_area("Ask a Question:", height=100)

        if st.button("Get Answer"):
            answer = ask_question(question, st.session_state.extracted_text)
            if answer:
                st.subheader("Answer:")
                st.write(answer)
