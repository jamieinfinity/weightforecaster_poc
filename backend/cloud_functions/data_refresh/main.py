import os
import datetime
import random
from google.cloud import storage


class MockRequest:
    def __init__(self, args=None, json_body=None):
        self.args = args or {}
        self.json = json_body or {}


def generate_fake_data():
    # Function to generate fake data
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    weight = random.uniform(170, 180)  # Random float between 170 and 180
    calories = random.uniform(1500, 3000)  # Random float between 1500 and 3500
    steps = random.uniform(5000, 15000)  # Random float between 5000 and 15000

    # Format as CSV line
    data_line = f'{date},{weight:.2f},{calories:.2f},{steps:.2f}\n'
    return data_line


def append_to_storage(bucket_name, file_name, data_line):
    # Function to append data to a file in Cloud Storage
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # Check if the file exists and download its contents
    if blob.exists():
        current_content = blob.download_as_text()
    else:
        current_content = 'date,weight,calories,steps\n'

    # Append the new line of data
    new_content = current_content + data_line

    # Upload the updated content back to the Cloud Storage file
    blob.upload_from_string(new_content)


def data_refresh(request):
    # Use try-except block to handle unexpected errors
    try:
        # Retrieve the Cloud Storage bucket name from Secret Manager
        bucket_name = os.environ.get('CLOUD_STORAGE_BUCKET')
        file_name = os.environ.get('FITNESS_DATA_FILE')

        if not bucket_name or not file_name:
            return ("Bucket or file name environment variables not set.", 500)

        data_line = generate_fake_data()
        append_to_storage(bucket_name, file_name, data_line)

        # For HTTP-triggered functions, return a response
        return f'Appended new data to {file_name} in bucket {bucket_name}'

    except Exception as e:
        return (str(e), 500)


def main():
    # NOTE: main is used for local testing only
    # load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv('../../../.env')
    # data_refresh function is triggered by an HTTP request
    mock_request = MockRequest()
    res = data_refresh(mock_request)
    print(res)


if __name__ == '__main__':
    main()
