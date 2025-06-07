import os
from flask import Flask, request, jsonify
import fitz 
from transformers import pipeline

app = Flask(__name__)

qa_pipeline = pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")

simplifier = pipeline("summarization", model="t5-base")

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/simplify', methods=['POST'])
def simplify_text():
    try:
        input_text = request.json.get('text')
        if not input_text:
            return jsonify({"error": "No text provided"}), 400

        max_input_length = 512 
        text_chunks = [input_text[i:i + max_input_length] for i in range(0, len(input_text), max_input_length)]

        detailed_summary = ""
        for chunk in text_chunks:
            summary = simplifier(
                chunk,
                min_length=100,  
                max_length=300,
                num_beams=6,  
                length_penalty=2.0,  
                no_repeat_ngram_size=2  
            )
            detailed_summary += summary[0]['summary_text'].strip() + "\n"

        return jsonify({'simplified_text': detailed_summary.strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        text = extract_text_from_pdf(file_path)
        return jsonify({"extracted_text": text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def extract_text_from_pdf(file_path):
    document = fitz.open(file_path)
    text = ""
    for page in document:
        text += page.get_text("text")
    return text

@app.route('/qa', methods=['POST'])
def answer_question():
    try:
        question = request.json.get('question')
        context = request.json.get('context')

        if not question or not context:
            return jsonify({"error": "Missing question or context"}), 400

        answer = qa_pipeline(question=question, context=context)

        return jsonify({'answer': answer['answer']})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
