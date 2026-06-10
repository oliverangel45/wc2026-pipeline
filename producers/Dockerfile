FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY producers/ ./producers/

ENV PRODUCER_TYPE=matches_events

CMD ["sh", "-c" "python producers/${PRODUCER_TYPE}_producer.py"]