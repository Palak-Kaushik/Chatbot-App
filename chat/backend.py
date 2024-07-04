from flask import Flask, request, jsonify
from transformers import T5Tokenizer, T5ForConditionalGeneration
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/chat": {"origins": "http://localhost:3000"}})

tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data['message']

    try:
        # Preprocess the input text
        input_text = user_message
        input_ids = tokenizer(input_text, return_tensors="pt").input_ids

        # Generate translations with longer maximum length
        outputs = model.generate(input_ids, max_length=100)

        # Decode the output tokens into human-readable text
        translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        ai_response = translated_text

    except Exception as e:
        # Handle any exceptions that occur during the translation
        ai_response = f"An error occurred: {str(e)}"

    return jsonify({"message": ai_response})

if __name__ == '__main__':
    app.run(debug=True)

