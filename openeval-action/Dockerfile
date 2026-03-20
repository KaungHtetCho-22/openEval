FROM python:3.11-slim

WORKDIR /app

# Keep dependencies minimal: runtime + GitHub API calls.
RUN pip install --no-cache-dir openeval requests

COPY entrypoint.py /app/entrypoint.py

ENTRYPOINT ["python", "/app/entrypoint.py"]

