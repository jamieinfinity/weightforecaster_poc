import os
import json
from google.cloud import storage


class MockRequest:
    def __init__(self, args=None, json_body=None):
        self.args = args or {}
        self.json = json_body or {}
        self.method = 'GET'


def fetch_fitness_data(request):
    # Set CORS headers
    cors_origin = os.environ.get('CORS_ORIGIN')
    if not cors_origin:
        return json.dumps({"error": "CORS_ORIGIN environment variable not set."}), 500

    headers = {
        'Access-Control-Allow-Origin': cors_origin,
    }
    # Handling the preflight request
    if request.method == 'OPTIONS':
        # Add necessary preflight headers here
        headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        headers['Access-Control-Allow-Headers'] = 'Content-Type'
        headers['Access-Control-Max-Age'] = '3600'
        return ('', 204, headers)

    try:
        # Implement the logic to fetch and return data
        bucket_name = os.getenv('CLOUD_STORAGE_BUCKET')
        file_name = os.getenv('FITNESS_DATA_FILE')

        if not bucket_name or not file_name:
            return json.dumps({"error": "Bucket or file name environment variables not set."}), 500

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        data = blob.download_as_text()

        # Convert CSV to JSON (assuming CSV has columns "date,weight,calories,steps")
        lines = data.strip().split('\n')
        cols = lines[0].split(',')
        json_data = [dict(zip(cols, line.split(','))) for line in lines[1:]]

        return (json.dumps(json_data), 200, headers)
    except Exception as e:
        return (json.dumps({"error": str(e)}), 500, headers)


def main():
    from dotenv import load_dotenv
    load_dotenv('../../../.env')
    mock_request = MockRequest()
    res = fetch_fitness_data(mock_request)
    print(res)


if __name__ == '__main__':
    main()
