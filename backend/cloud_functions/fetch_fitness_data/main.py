import os
import json
from google.cloud import storage


class MockRequest:
    def __init__(self, args=None, json_body=None):
        self.args = args or {}
        self.json = json_body or {}


def fetch_fitness_data(request):
    try:
        # Retrieve bucket name and file name from environment variables
        bucket_name = os.environ.get('CLOUD_STORAGE_BUCKET')
        file_name = os.environ.get('FITNESS_DATA_FILE')

        if not bucket_name or not file_name:
            return ("Bucket or file name environment variables not set.", 500)

        # Instantiates a client
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        data = blob.download_as_text()

        # Convert CSV to JSON (assuming CSV has headers "date,weight,calories,steps")
        lines = data.strip().split('\n')
        headers = lines[0].split(',')
        json_data = [dict(zip(headers, line.split(','))) for line in lines[1:]]

        # Return JSON response
        return (json.dumps(json_data), 200, {'Content-Type': 'application/json'})

    except Exception as e:
        return (str(e), 500)


def main():
    # NOTE: main is used for local testing only
    # load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv('../../../.env')
    # data_refresh function is triggered by an HTTP request
    mock_request = MockRequest()
    res = fetch_fitness_data(mock_request)
    print(res)


if __name__ == '__main__':
    main()
