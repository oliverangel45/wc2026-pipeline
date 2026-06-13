import os
import json
import time
import logging
import requests
from dotenv import load_dotenv
from kafka import KafkaProducer

# Log and Load Env Variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "broker:29092")
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")
BASE_URL = "https://api.football-data.org/v4"
COMPETITION_CODE = "WC"
MATCHES_TOPIC = "wc.matches"
EVENTS_TOPIC = "wc.events"
POLL_INTERVAL = 60

def create_producer():
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=3
        )
        logger.info("Kafka producer created successfully")
        return producer
    except Exception as e:
        logger.error(f"Failed to create Kafka producer: {e}")
        raise

def fetch_matches():
    try:
        headers = {"x-Auth-Token": FOOTBALL_API_KEY}
        url = f"{BASE_URL}/competitions/{COMPETITION_CODE}/matches"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Fetched {len(data['matches'])} matches from football-data.org")
        return data['matches']
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching matches: {e}")
        return []
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error fetching matches: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching matches: {e}")
        return []

def fetch_events(match_id):
    try:
        headers = {"X-Auth-Token": FOOTBALL_API_KEY}
        url = f"{BASE_URL}/matches/{match_id}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        goals = data.get('goals', [])
        bookings = data.get('bookings', [])
        substitutions = data.get('substitutions', [])
        events = goals + bookings + substitutions
        logger.info(f"Fetched {len(events)} events for match {match_id}")
        return events
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching events for match {match_id}: {e}")
        return []
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error fetching events for match {match_id}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching events for match {match_id}: {e}")
        return []
    
def send_match(producer, match):
    try:
        message = {
            "match_id": match["id"],
            "home_team": match["homeTeam"]["name"],
            "away_team": match["awayTeam"]["name"],
            "home_score": match["score"]["fullTime"]["home"],
            "away_score": match["score"]["fullTime"]["away"],
            "status": match["status"],
            "matchday": match.get("matchday"),
            "stage": match["stage"],
            "utc_date": match["utcDate"],
            "last_updated": match["lastUpdated"]
        }
        producer.send(MATCHES_TOPIC, value=message)
        logger.info(f"Sent match {message['match_id']} to {MATCHES_TOPIC}")
    except Exception as e:
        logger.error(f"Failed to send match {match.get('id'): {e}}")
        
def send_events(producer, match_id, events):
    for event in events:
        try:
            message = {
                "event_id": f"{match_id}_{event.get('minute')}_{event.get('type')}_{event.get('player', {}).get('name')}",
                "match_id": match_id,
                "minute": event.get("minute"),
                "extra_time_minute": event.get("extraTime"),
                "event_type": event.get("type"),
                "event_detail": event.get("detail"),
                "team_id": event.get("team", {}).get("id"),
                "team_name": event.get("team", {}).get("name"),
                "player_name": event.get("player", {}).get("name"),
                "assist_name": event.get("assist", {}).get("name")
            }
            producer.send(EVENTS_TOPIC, value=message)
            logger.info(f"Sent event {message['event_id']} to {EVENTS_TOPIC}")
        except Exception as e:
            logger.error(f"Failed to send event for match {match_id}: {e}")

def main():
    logger.info("Starting matches/events producer")
    producer = create_producer()

    while True:
        try:
            matches = fetch_matches()

            for match in matches:
                send_match(producer, match)

                if match['status'] in ['IN_PLAY', 'PAUSED', 'FINISHED']:
                    events = fetch_events(match['id'])
                    send_events(producer, match['id'], events)

            producer.flush()
            logger.info(f"Poll complete. Sleeping for {POLL_INTERVAL} seconds")
            time.sleep(POLL_INTERVAL)

        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            logger.info(f"Sleeping for {POLL_INTERVAL} seconds before retrying")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()