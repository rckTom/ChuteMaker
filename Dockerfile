# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Configure

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN apt update && apt install -y python3-dev \
                          gcc \
                          libc-dev \
                          libffi-dev \
                          libcairo2-dev

# Copy the source code into the container.
COPY . .

# Install python dependecys
RUN python -m pip install -r requirements.txt

# Expose the port that the application listens on.
EXPOSE 8000

# Switch to the non-privileged user to run the application.
USER appuser

# Run the application.
CMD ["uwsgi", "--http", "0.0.0.0:8000", "-w", "chutemaker_webapp:app"]