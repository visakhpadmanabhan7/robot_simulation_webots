import paho.mqtt.client as mqtt
import sqlite3
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database setup
def initialize_database():
    conn = sqlite3.connect('../ur5_data.db')
    cursor = conn.cursor()
    # Define the schema with joint angles and velocities
    cursor.execute('''DROP TABLE IF EXISTS joint_data''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS joint_data (
                        timestamp TEXT PRIMARY KEY,
                        shoulder_pan_joint_angle REAL,
                        shoulder_lift_joint_angle REAL,
                        elbow_joint_angle REAL,
                        wrist_1_joint_angle REAL,
                        wrist_2_joint_angle REAL,
                        wrist_3_joint_angle REAL,
                        shoulder_pan_joint_velocity REAL,
                        shoulder_lift_joint_velocity REAL,
                        elbow_joint_velocity REAL,
                        wrist_1_joint_velocity REAL,
                        wrist_2_joint_velocity REAL,
                        wrist_3_joint_velocity REAL
                    )''')
    conn.commit()
    conn.close()
    logging.info("Database initialized with updated schema.")

# Insert data into the database
def insert_joint_data(data):
    try:
        with sqlite3.connect('../ur5_data.db') as conn:
            cursor = conn.cursor()
            # Insert data into respective columns
            cursor.execute('''INSERT OR REPLACE INTO joint_data 
                              (timestamp, shoulder_pan_joint_angle, shoulder_lift_joint_angle, 
                               elbow_joint_angle, wrist_1_joint_angle, wrist_2_joint_angle, 
                               wrist_3_joint_angle, shoulder_pan_joint_velocity, 
                               shoulder_lift_joint_velocity, elbow_joint_velocity, 
                               wrist_1_joint_velocity, wrist_2_joint_velocity, 
                               wrist_3_joint_velocity)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (data['timestamp'],
                            data['joint_angles']['shoulder_pan_joint'],
                            data['joint_angles']['shoulder_lift_joint'],
                            data['joint_angles']['elbow_joint'],
                            data['joint_angles']['wrist_1_joint'],
                            data['joint_angles']['wrist_2_joint'],
                            data['joint_angles']['wrist_3_joint'],
                            data['joint_velocities']['shoulder_pan_joint'],
                            data['joint_velocities']['shoulder_lift_joint'],
                            data['joint_velocities']['elbow_joint'],
                            data['joint_velocities']['wrist_1_joint'],
                            data['joint_velocities']['wrist_2_joint'],
                            data['joint_velocities']['wrist_3_joint']))
            conn.commit()
            logging.info(f"Data inserted for timestamp {data['timestamp']}")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")

# Callback function for receiving joint data
def on_joint_data(client, userdata, message):
    try:
        # Decode the received message
        data = json.loads(message.payload.decode("utf-8"))
        logging.info(f"Received joint data: {data}")

        # Insert data into the database
        insert_joint_data(data)
    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding error: {e}")
    except Exception as e:
        logging.error(f"Error in on_joint_data: {e}")

# Set up the MQTT client and subscribe to the joint data topic
def setup_mqtt_client():
    client = mqtt.Client()
    client.message_callback_add("ur5/joint_data", on_joint_data)
    try:
        client.connect("localhost", 1883)  # Replace with actual IP if needed
        logging.info("Connected to MQTT broker.")
    except Exception as e:
        logging.error(f"Error connecting to MQTT broker: {e}")
        sys.exit(1)
    client.subscribe("ur5/joint_data")
    return client

if __name__ == "__main__":
    # Initialize database and MQTT client
    initialize_database()
    client = setup_mqtt_client()

    # Start processing MQTT messages
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        logging.info("Disconnecting from MQTT broker and exiting...")
        client.disconnect()
