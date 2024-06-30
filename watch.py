import requests
import os
from datetime import datetime
import argparse
from pathlib import Path

# URL of the file to watch
url = 'https://developer.trimet.org/schedule/gtfs.zip'

# Path to store the ETag and Last-Modified information
etag_file = 'data/etag.txt'
last_modified_file = 'data/last_modified.txt'

def convert_last_modified_to_datetime(last_modified_str):
    # Define the format of the Last-Modified date string
    date_format = '%a, %d %b %Y %H:%M:%S %Z'
    
    # Convert the Last-Modified string to a datetime object
    last_modified_datetime = datetime.strptime(last_modified_str, date_format)
    
    return last_modified_datetime

def get_server_file_info(url):
    response = requests.head(url)
    etag = response.headers.get('ETag')
    last_modified = response.headers.get('Last-Modified')
    return etag, last_modified

def get_local_file_info(etag_file, last_modified_file):
    etag = None
    last_modified = None
    if etag_file.exists():
        etag = etag_file.read_text().strip()
    if last_modified_file.exists():
        last_modified = last_modified_file.read_text().strip()
    return etag, last_modified

def save_local_file_info(etag, last_modified, etag_file, last_modified_file):
    if etag:
        etag_file.write_text(etag)
    if last_modified:
       last_modified_file.write_text(last_modified)

def download_file(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

def check_feed(url, etag_file, last_modified_file):
    server_etag, server_last_modified = get_server_file_info(url)
    local_etag, local_last_modified = get_local_file_info(etag_file, last_modified_file)

    if server_etag != local_etag or server_last_modified != local_last_modified:
        print('File has changed, downloading new version...')
        timestamp = convert_last_modified_to_datetime(server_last_modified).strftime('%Y%m%d_%H%M%S')
        filename = data_dir / f'{timestamp}.zip'  # Replace '.ext' with the correct file extension
        download_file(url, filename)
        save_local_file_info(server_etag, server_last_modified, etag_file, last_modified_file)
        print(f'File downloaded and saved as {filename}')
    else:
        print('File has not changed.')

def main():
    parser = argparse.ArgumentParser(description='Watch a file on a web server and download it if it changes.')
    parser.add_argument('--datadir', default="./data", help='The directory to store data files')
    args = parser.parse_args()

    data_dir = Path(args.datadir)

    etag_file = data_dir / 'etag.txt'
    last_modified_file = data_dir /'last_modified.txt'


if __name__ == '__main__':
    main()
