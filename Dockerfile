# Use the official Python image from the Docker Hub
FROM python:3.9-alpine

# Install cron
# RUN apt-get update && apt-get install -y cron

# Set the working directory
WORKDIR /app

RUN mkdir /app/data

# Copy the Python script and shell script into the container
COPY watch.py .
COPY requirements.txt .

# Install the requests library
RUN pip install -r requirements.txt

ARG CRON_SCHEDULE="* * * * *"
RUN echo "${CRON_SCHEDULE} python3 /app/watch.py" | crontab -

CMD ["crond", "-f", "2>&1"]