# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Install cron
RUN apt-get update && apt-get install -y cron

# Set the working directory
WORKDIR /app

RUN mkdir /app/data

# Copy the Python script and shell script into the container
COPY watch.py .
COPY requirements.txt .

# Install the requests library
RUN pip install -r requirements.txt

# Add the cron job
RUN echo "*/5 * * * * /app/run_watch_file.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/watch_file

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/watch_file

# Apply the cron job
RUN crontab /etc/cron.d/watch_file

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the command on container startup
CMD cron && tail -f /var/log/cron.log
