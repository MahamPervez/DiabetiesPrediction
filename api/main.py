import os
from flask import Flask, request, jsonify, render_template
import urllib.request
import json
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Replace with your Azure endpoint and key
url = os.getenv('AZURE_URL', 'http://4.157.218.232:80/api/v1/service/diabetiesclassfication/score')
api_key = os.getenv('AZURE_API_KEY', '5X7Ze1EKngl1OSGY0KOERNZ8NrjMbQMX')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    for field in ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']:
        if request.form[field] == '':
            return jsonify({"error": f"Field '{field}' cannot be empty."}), 400

    input_data = {
        "Pregnancies": int(request.form['Pregnancies']),
        "Glucose": int(request.form['Glucose']),
        "BloodPressure": int(request.form['BloodPressure']),
        "SkinThickness": int(request.form['SkinThickness']),
        "Insulin": int(request.form['Insulin']),
        "BMI": float(request.form['BMI']),
        "DiabetesPedigreeFunction": float(request.form['DiabetesPedigreeFunction']),
        "Age": int(request.form['Age']),
        "Outcome": 0
    }

    data = {
        "Inputs": {
            "web_service_input": [input_data]
        },
        "GlobalParameters": {}
    }

    body = json.dumps(data).encode('utf-8')
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + api_key}

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)
        result = response.read()
        logging.info("Response: %s", result)
        parsed_result = json.loads(result.decode('utf-8'))
        scored_labels = parsed_result['Results']['WebServiceOutput0'][0]['Scored Labels']

        if scored_labels == 1.0:
            message = "The person has diabetes."
        else:
            message = "The person does not have diabetes."

        return jsonify({"message": message})
    except urllib.error.HTTPError as error:
        logging.error("The request failed with status code: %s", error.code)
        logging.error(error.info())
        return jsonify({"error": error.read().decode()}), 500
    except urllib.error.URLError as error:
        logging.error("Failed to reach the server. Reason: %s", error.reason)
        return jsonify({"error": str(error.reason)}), 500

if __name__ == '__main__':
    app.run(debug=True)

