import os
import json
import logging
from dotenv import load_dotenv
from kafka import KafkaConsumer
import snowflake.connector

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Kafka Constants
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "broker:29092")
KAFKA_GROUP_ID = "wc2026-consumer-group"

# Snowflake Constants
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_RAW_SCHEMA")
SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_CONSUMER_ROLE")

# Topics
MATCHES_TOPIC = "wc.matches"
STANDINGS_TOPIC = "wc.standings"
EVENTS_TOPIC = "wc.events"

TOPICS = [MATCHES_TOPIC, STANDINGS_TOPIC, EVENTS_TOPIC]

def create_snowflake_connection():
    try:
        conn = snowflake.connector.connect(
            account=SNOWFLAKE_ACCOUNT,
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            warehouse=SNOWFLAKE_WAREHOUSE,
            database=SNOWFLAKE_DATABASE,
            schema=SNOWFLAKE_SCHEMA,
            role=SNOWFLAKE_ROLE
        )
        logger.info("Snowflake connection established successfully.")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to Snowflake: {e}")
        raise

# Insert data into RAW matches table
def insert_match(cursor, message):
    try:
        sql = """
            INSERT INTO MATCHES (
                MATCH_ID, HOME_TEAM, AWAY_TEAM,
                HOME_SCORE, AWAY_SCORE, STATUS,
                MATCHDAY, STAGE, UTC_DATE,
                LAST_UPDATED, RAW_PAYLOAD
            ) VALUES (
                %(match_id)s, %(home_team)s, %(away_team)s,
                %(home_score)s, %(away_score)s, %(status)s,
                %(matchday)s, %(stage)s, %(utc_date)s,
                %(last_updated)s, PARSE_JSON(%(raw_payload)s)                
            )
        """
        message['raw_payload'] = json.dumps(message)
        cursor.execute(sql, message)
        logger.info(f"Inserted match {message['match_id']} into MATCHES")
    except Exception as e:
        logger.error(f"Failed to inset {message.get('match_id')}: {e}")
        raise

# Insert data into RAW standings table
def insert_standing(cursor, message):
    try:
        sql = """
            INSERT INTO STANDINGS (
                TEAM_ID, TEAM_NAME, GROUP_NAME,
                POSITION, PLAYED_GAMES, WON,
                DRAW, LOST, POINTS,
                GOALS_FOR, GOALS_AGAINST, GOAL_DIFF,
                RAW_PAYLOAD
            ) VALUES (
                %(team_id)s, %(team_name)s, %(group_name)s,
                %(position)s, %(played_games)s, %(won)s,
                %(draw)s, %(lost)s, %(points)s,
                %(goals_for)s, %(goals_against)s, %(goal_diff)s,
                PARSE_JSON(%(raw_payload)s)
            )
        """
        message['raw_payload'] = json.dumps(message)
        cursor.execute(sql, message)
        logger.info(f"Inserted standing for {message['team_name']} into STANDINGS")
    except Exception as e:
        logger.error(f"Failed to insert standing for {message.get('team_name')}: {e}")
        raise


# Insert data into RAW events table
def insert_event(cursor, message):
    try:
        sql = """
            INSERT INTO EVENTS (
                EVENT_ID, MATCH_ID, MINUTE,
                EXTRA_TIME_MINUTE, EVENT_TYPE, EVENT_DETAIL,
                TEAM_ID, TEAM_NAME, PLAYER_NAME,
                ASSIST_NAME, RAW_PAYLOAD
            ) VALUES (
                %(event_id)s, %(match_id)s, %(minute)s,
                %(extra_time_minute)s, %(event_type)s, %(event_detail)s,
                %(team_id)s, %(team_name)s, %(player_name)s,
                %(assist_name)s, PARSE_JSON(%(raw_payload)s)
            )
        """
        message['raw_payload'] = json.dumps(message)
        cursor.execute(sql, message)
        logger.info(f"Inserted event {message['event_id']} into EVENTS")
    except Exception as e:
        logger.error(f"Failed to insert event {message.get('event_id')}: {e}")
        raise

def create_consumer():
    try:
        consumer = KafkaConsumer(
            *TOPICS,
            bootstap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id=KAFKA_GROUP_ID,
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )
        logger.info(f"Kafka consumer subscribed to topics: {TOPICS}")
        return consumer
    except Exception as e:
        logger.error(f"Failed to create Kafka consumer: {e}")
        raise

def main():
    logger.info("Starting consumer...")
    
    conn = create_snowflake_connection()
    cursor = conn.cursor()
    consumer = create_consumer()
    
    try:
        for message in consumer:
            topic = message.topic
            value = message.value
            
            try:
                if topic == MATCHES_TOPIC:
                    insert_match(cursor, value)
                elif topic == STANDINGS_TOPIC:
                    insert_standing(cursor, value)
                elif topic == EVENTS_TOPIC:
                    insert_event(cursor, value)
                else:
                    logger.warning(f"Received message from unkown topic: {topic}")
                    continue
                
                conn.commit()
                consumer.commit() # Commits Kafka offset AFTER row inserted to table
                logger.info(f"Commited offset for {topic} topic")
            
            except Exception as e:
                logger.error(f"Failed to process message from {topic}: {e}")
                conn.rollback() # Cancels Snowflake transaction
        
    except Exception as e:
        logger.error(f"Consumer loop failed: {e}")
        raise
    finally:
        logger.info("Closing consumer and Snowflake connection")
        cursor.close()
        conn.close()
        consumer.close()
        
if __name__ == "__main__":
    main()