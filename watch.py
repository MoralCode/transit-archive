import requests
import os
from datetime import datetime

# URL of the file to watch
url = 'https://developer.trimet.org/schedule/gtfs.zip'

# Path to store the ETag and Last-Modified information
etag_file = 'etag.txt'
last_modified_file = 'last_modified.txt'

def get_server_file_info(url):
    response = requests.head(url)
    etag = response.headers.get('ETag')
    last_modified = response.headers.get('Last-Modified')
    return etag, last_modified

def get_local_file_info():
    etag = None
    last_modified = None
    if os.path.exists(etag_file):
        with open(etag_file, 'r') as f:
            etag = f.read().strip()
    if os.path.exists(last_modified_file):
        with open(last_modified_file, 'r') as f:
            last_modified = f.read().strip()
    return etag, last_modified

def save_local_file_info(etag, last_modified):
    if etag:
        with open(etag_file, 'w') as f:
            f.write(etag)
    if last_modified:
        with open(last_modified_file, 'w') as f:
            f.write(last_modified)

def download_file(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

def main():
    server_etag, server_last_modified = get_server_file_info(url)
    local_etag, local_last_modified = get_local_file_info()

    if server_etag != local_etag or server_last_modified != local_last_modified:
        print('File has changed, downloading new version...')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'file_{timestamp}.ext'  # Replace '.ext' with the correct file extension
        download_file(url, filename)
        save_local_file_info(server_etag, server_last_modified)
        print(f'File downloaded and saved as {filename}')
    else:
        print('File has not changed.')

if __name__ == '__main__':
    main()
