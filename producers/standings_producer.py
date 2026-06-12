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
STANDINGS_TOPIC = "wc.standings"
POLL_INTERVAL = 300 # Updates standings every 5 mins to manage API calls

def create_producer():
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
            acks='all'
            retries=3
        )
        logger.info("Kafka producer created successfully")
        return producer
    except Exception as e:
        logger.error(f"Failed to create Kafka producer: {e}")
        raise

def fetch_standings():
    try:
        headers = {"x-Auth-Token": FOOTBALL_API_KEY}
        url = f"{BASE_URL}/competitions/{COMPETITION_CODE}/standings"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        standings = []
        for group in data.get('standings', []):
            group_name = group.get('group', 'UNKNOWN')
            for team_standing in group.get('table', []):
                standings.append({
                    'group_name': group_name,
                    'team_standing': team_standing
                })
        logger.info(f"Fetched standings for {len(standings)} teams")
        return standings
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching matches: {e}")
        return []
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error fetching matches: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching matches: {e}")
        return []

def send_standing(producer, group_name, team_standing):
    try:
        message = {
            "team_id": team_standing["team"]["id"],
            "team_name": team_standing["team"]["name"],
            "group_name": group_name,
            "position": team_standing["position"],
            "played_games": team_standing["playedGames"],
            "won": team_standing["won"],
            "draw": team_standing["draw"],
            "lost": team_standing["lost"],
            "points": team_standing["points"],
            "goals_for": team_standing["goalsFor"],
            "goals_against": team_standing["goalsAgainst"],
            "goal_diff": team_standing["goalDifference"],
            "raw_payload": team_standing
        }
        producer.send(STANDINGS_TOPIC, value=message)
        logger.info(f"Sent standing for {message['team_name']} in {group_name} to {STANDINGS_TOPIC}")
    except Excepttion as e:
        logger.error(f"Failed to send standing for team {team_standing.get('team', {}).get('name')}: {e}")
    
def main():
    logger.info("Starting standings producer")
    producer = create_producer()
    
    while True:
        try:
            standings = fetch_standings()
            
            for standing in standings:
                send_standing(
                    producer,
                    standing['group_name'],
                    standing['team_standing']
                )
            producer.flush()
            logger.info(f"Poll complete. Sleeping for {POLL_INTERVAL} seconds")
            time.sleep(POLL_INTERVAL)
            
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            logger.info(f"Sleeping for {POLL_INTERVAL} seconds before retrying")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()