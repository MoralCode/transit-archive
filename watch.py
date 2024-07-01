import requests
import os
from datetime import datetime
import argparse
from pathlib import Path
import csv
import zipfile
import io

# Filenames to store the ETag and Last-Modified information. these are used within each feeds sub-datadir 
ETAG_FILENAME = 'etag.txt'
LASTMODIFIED_FILENAME = 'last_modified.txt'
ARCHIVED_FEEDS_FILENAME = "archived_feeds.txt"

def convert_last_modified_to_datetime(last_modified_str):
    # Define the format of the Last-Modified date string
    date_format = '%a, %d %b %Y %H:%M:%S %Z'
    
    # Convert the Last-Modified string to a datetime object
    last_modified_datetime = datetime.strptime(last_modified_str, date_format)
    
    return last_modified_datetime

def get_server_file_info(url):
    response = requests.head(url)
    if response.status_code >= 300 and response.status_code < 400:
        print(f"Detected a redirect from configured urls {url} to {response.headers.get('Location')}")
        print(f"Please update your config to avoid this in future. Working around it")
        response = requests.head(url, allow_redirects=True)

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


def save_feed_archive_info(archived_feeds_file,feed_start_date, feed_end_date, feed_version, hosting_path, fallback_value=None, notes=None):
    needs_header = not archived_feeds_file.exists()

    feed_start_date = feed_start_date or fallback_value or ""
    feed_end_date = feed_end_date or fallback_value or ""
    feed_version = feed_version or fallback_value or ""


    with archived_feeds_file.open("a") as aff:
        fieldnames = ["feed_start_date","feed_end_date","feed_version","archive_url","archive_note"]
        # https://docs.python.org/3/library/csv.html#csv.unix_dialect
        writer = csv.DictWriter(aff, fieldnames=fieldnames, dialect='unix')
        if needs_header:
            writer.writeheader()

        writer.writerow({
            "feed_start_date": feed_start_date,
            "feed_end_date": feed_end_date,
            "feed_version": feed_version,
            "archive_url": str(hosting_path),
            "archive_note": notes.replace('"',"'") if notes is not None else ""
        })

def download_file(url, filename):
    response = requests.get(url, allow_redirects=True)
    with open(filename, 'wb') as f:
        f.write(response.content)

def check_feed(url,data_dir, domain):
    if not data_dir.exists():
        data_dir.mkdir()

    etag_file = data_dir / ETAG_FILENAME
    last_modified_file = data_dir / LASTMODIFIED_FILENAME
    archived_feeds_file = data_dir / ARCHIVED_FEEDS_FILENAME

    server_etag, server_last_modified = get_server_file_info(url)
    local_etag, local_last_modified = get_local_file_info(etag_file, last_modified_file)

    if server_etag != local_etag or server_last_modified != local_last_modified:
        print(f'Feed {data_dir.name} has changed, downloading new version...')
        if server_last_modified is not None:
            timestamp = convert_last_modified_to_datetime(server_last_modified).strftime('%Y%m%d_%H%M%S')
        else:
            timestamp = server_etag
        filename = data_dir / f'{timestamp}.zip'  # Replace '.ext' with the correct file extension
        download_file(url, filename)
        #download_file(url, filename)
        save_local_file_info(server_etag, server_last_modified, etag_file, last_modified_file)

        hosting_path = domain / filename

        with zipfile.ZipFile(filename) as gtfs_contents:

            fillin_value = convert_last_modified_to_datetime(server_last_modified).strftime('%Y%m%d_%H%M%S') if server_last_modified is not None else timestamp
            notes = None

            # this may not exist....
            try:
                feedinfo = gtfs_contents.read('feed_info.txt')
            except KeyError as e:
                
                if hasattr(e, 'message'):
                    e_msg = e.message
                else:
                    e_msg = e

                e_msg = str(e_msg).replace('"', '')

                msg = f"File archive could not be accurately updated with information from the feed: {e_msg}"
                print(msg)

                save_feed_archive_info(
                    archived_feeds_file,
                    None,
                    None,
                    None,
                    hosting_path,
                    fallback_value=fillin_value,
                    notes=f"{msg}. Filling in missing values with '{fillin_value}'")
                return
                
            string_data = feedinfo.decode('utf-8')
            # Use StringIO to create a file-like object
            feedFile = io.StringIO(string_data)
            reader = csv.DictReader(feedFile)
            info = list(reader)[0]

            # these may not exist either....

            feed_start_date = info.get("feed_start_date")
            feed_end_date = info.get("feed_end_date")
            feed_version = info.get("feed_version")

            notes = ""
            notes += "feed_start_date," if feed_start_date is None else ""
            notes += "feed_end_date," if feed_end_date is None else ""
            notes += "feed_version," if feed_version is None else ""
            notes = "did not exist in the source feed. Filling in missing values with the modification date"


        save_feed_archive_info(archived_feeds_file, feed_start_date, feed_end_date, feed_version, hosting_path, fallback_value=fillin_value, notes=notes)

        print(f'File downloaded and saved as {filename}')
    else:
        print(f'Feed {data_dir.name} has not changed.')

def main():
    parser = argparse.ArgumentParser(description='Watch a file on a web server and download it if it changes.')
    parser.add_argument('--datadir', default="./data", help='The directory to store data files')
    parser.add_argument('--domain', default="", help='The domain used for accessing the data files. This is written to the archive file every time a feed is updated.')
    args = parser.parse_args()

    data_dir = Path(args.datadir)

    feeds_file = data_dir / 'feeds.csv'

    with feeds_file.open('r') as feedfile:
        reader = csv.DictReader(feedfile)
        for row in reader:
            check_feed(row["feed_url"], data_dir / row["dirname"], args.domain)


if __name__ == '__main__':
    main()
