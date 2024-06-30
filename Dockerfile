# Use the official Python image from the Docker Hub
FROM python:3.9-alpine

# Set the working directory
WORKDIR /app

RUN mkdir /app/data

COPY requirements.txt .

# Install the requests library
RUN pip install -r requirements.txt

COPY watch.py .

ARG CRON_SCHEDULE="* * * * *"
RUN echo "${CRON_SCHEDULE} python3 /app/watch.py https://developer.trimet.org/schedule/gtfs.zip /app/data" | crontab -
	
CMD ["crond", "-f", "2>&1"]