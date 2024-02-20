import os
from google.cloud import storage
from flask import Flask, request, jsonify
from flask_cors import CORS


class MockRequest:
    def __init__(self, args=None, json_body=None):
        self.args = args or {}
        self.json = json_body or {}


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/fetch_fitness_data', methods=['GET', 'POST', 'OPTIONS'])
def fetch_fitness_data(request):
    # Preflight request for CORS
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type header
        # and caches preflight response for an hour
        headers = {
            'Access-Control-Allow-Origin': '*',  # replace with your app domain in production
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Max-Age': '3600',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
        return ('', 204, headers)

    # Actual request
    try:
        # Retrieve bucket name and file name from environment variables
        bucket_name = os.environ.get('CLOUD_STORAGE_BUCKET')
        file_name = os.environ.get('FITNESS_DATA_FILE')

        if not bucket_name or not file_name:
            return jsonify({"error": "Bucket or file name environment variables not set."}), 500

        # Instantiates a client
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        data = blob.download_as_text()

        # Convert CSV to JSON
        lines = data.strip().split('\n')
        headers = lines[0].split(',')
        json_data = [dict(zip(headers, line.split(','))) for line in lines[1:]]

        # Include Access-Control-Allow-Origin header in the response
        headers = {'Access-Control-Allow-Origin': '*'}
        return jsonify(json_data), 200, headers

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def main():
    from dotenv import load_dotenv
    load_dotenv('../../../.env')


if __name__ == '__main__':
    main()
    app.run(debug=True, port=8080)
