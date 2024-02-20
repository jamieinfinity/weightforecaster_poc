import os
import datetime
import random
from google.cloud import storage
from google.cloud import secretmanager


class MockRequest:
    def __init__(self, args=None, json_body=None):
        self.args = args or {}
        self.json = json_body or {}


def get_secret(secret_name):
    # Function to retrieve secrets based on the environment
    if os.environ.get('GCP_ENVIRONMENT') == 'true':
        # Access secret from GCP Secret Manager
        client = secretmanager.SecretManagerServiceClient()
        project_id = os.environ.get('GCP_PROJECT_ID')
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8")
    else:
        # Access secret from local environment variable
        from dotenv import load_dotenv
        load_dotenv('../../../.env')
        secret_value = os.environ.get(secret_name, 'VALUE_NOT_SET')
    return secret_value


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
        current_content = ''

    # Append the new line of data
    new_content = current_content + data_line

    # Upload the updated content back to the Cloud Storage file
    blob.upload_from_string(new_content)


def data_refresh(request):
    # Use try-except block to handle unexpected errors
    try:
        # Retrieve the Cloud Storage bucket name from Secret Manager
        bucket_name = get_secret('CLOUD_STORAGE_BUCKET')
        file_name = 'fitness_data.csv'

        data_line = generate_fake_data()
        append_to_storage(bucket_name, file_name, data_line)

        # For HTTP-triggered functions, return a response
        return f'Appended new data to {file_name} in bucket {bucket_name}'

    except Exception as e:
        print(f'Error: {e}')
        return f'Error: {e}', 500


def main():
    mock_request = MockRequest()
    res = data_refresh(mock_request)
    print(res)


if __name__ == '__main__':
    main()
