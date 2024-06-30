# Watch File Downloader

This project consists of a Python script that monitors a file on a web server and downloads it if it has been updated. The script checks the ETag and Last-Modified headers to determine if the file has changed. The setup uses Docker to run the script on a schedule using cron.


## Prerequisites

Docker or a reasonably modern version of python3 are needed to run this code 

## Getting Started

1. **Clone the repository**

    ```sh
    git clone https://github.com/yourusername/watch-file-downloader.git
    cd watch-file-downloader
    ```
1. create a directory to store data in, such as `mkdir data`
1. inside this data directory, create a file called `feeds.csv` with the following content:
	```csv
	dirname,feed_url
	NAME,URL
	```
	replace NAME with a directory name you want to use for this feed and URL with the url to the GTFS feed (a .zip file) that you want to start archiving. The file can contain many entries if you want to monitor many feeds.

2. **Build the Docker image**

    ```sh
    docker build -t watch-file-image .
    ```

3. **Run the Docker container**

    ```sh
    docker run -d --name watch-file-container -v /path/to/data/directory:/app/data watch-file-image
    ```

The Docker container will now run the Python script every 5 minutes to check for updates to the specified feeds. If any of the feeds have changed, they will be downloaded to the data directory and saved with a timestamped filename.

## Customization

- **URL to watch**: Update the `url` variable in `watch_file.py` with the URL of the file you want to monitor.
- **Check interval**: Modify the cron expression in the Dockerfile (`*/5 * * * *`) to change how often the script checks for updates. For example, `*/10 * * * *` will check every 10 minutes.
- **File extension**: Update the file extension in the `download_file` function in `watch_file.py` to match the type of file you are downloading.

## Logs

Logs from the cron job are stored in `/var/log/cron.log` inside the container. You can view the logs by running:

```sh
docker logs watch-file-container
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.