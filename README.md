# GTFS archiver

This project consists of a Python script that monitors a file on a web server and downloads it if it has been updated. The script checks the ETag and Last-Modified headers to determine if the file has changed. The setup uses Docker to run the script on a schedule using cron.

This is intended for archiving GTFS (public transit data) feeds when the transit agency doesnt archive their own feed. 


## Prerequisites

Docker or a reasonably modern version of python3 are needed to run this code 

## Getting Started

1. Clone the repository
2. create a directory to store data in, such as `mkdir data`
3. inside this data directory, create a file called `feeds.csv` with the following content:
	```csv
	dirname,feed_url
	NAME,URL
	```
	replace NAME with a directory name you want to use for this feed and URL with the url to the GTFS feed (a .zip file) that you want to start archiving. The file can contain many entries if you want to monitor many feeds.

4. install the python dependencies with `pip install -r requirements.txt`
5. run the script: `python3 ./watch.py --datadir <path to datadir>` 

If any of the feeds have changed, they will be downloaded to the data directory and saved with a timestamped filename. An entry in a CSV file located at `<data directory from >/<feed name>/archive 

### Cron scheduling through docker

1. to run the script in production on a schedule, use docker to build and run the image

    ```sh
    docker build -t watch-file-image .
    docker run -d --name watch-file-container -v /path/to/data/directory:/app/data watch-file-image
    ```

The Docker container will now run the Python script every 5 minutes to check for updates to the specified feeds.

## Customization

- **Check interval**: Modify the cron expression in the Dockerfile (`*/5 * * * *`) to change how often the script checks for updates. For example, `*/10 * * * *` will check every 10 minutes.
- **Hosting path**: pass the `--domain` arg into the script (or modify the docker file to include this) if you want to publicly host your files. This will allow your domain to be included in the archive list files so that the links work. You will need to configure a web server to serve the files in the data directory separately.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.