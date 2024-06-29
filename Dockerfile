# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Install cron
RUN apt-get update && apt-get install -y cron

# Set the working directory
WORKDIR /app

# Copy the Python script and shell script into the container
COPY watch_file.py .
COPY run_watch_file.sh .

# Make the shell script executable
RUN chmod +x run_watch_file.sh

# Install the requests library
RUN pip install requests

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
