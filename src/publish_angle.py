import paho.mqtt.client as mqtt
import math
import json
import time
from datetime import datetime
from controller import Robot

# Initialize the Webots robot and timestep
robot = Robot()
timestep = int(robot.getBasicTimeStep())

# MQTT Client for publishing data
mqtt_client = mqtt.Client("ur5_data_publisher")
mqtt_client.connect("localhost", 1883)

# Define UR5 joints
joint_names = ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint",
               "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"]
joints = [robot.getDevice(name) for name in joint_names]

# Sine wave parameters for movement
frequency = 0.5
amplitude = math.pi / 4

# Initialize variables for calculating velocity
previous_angles = {name: 0.0 for name in joint_names}
previous_time = robot.getTime()

start_time = robot.getTime()
while robot.step(timestep) != -1:
    # Get the current time and calculate elapsed time
    current_time = robot.getTime()
    elapsed_time = current_time - start_time
    dt = current_time - previous_time

    # Calculate joint angles using sine wave
    joint_data = {
        name: amplitude * math.sin(2 * math.pi * frequency * elapsed_time + i * math.pi / 6)
        for i, name in enumerate(joint_names)
    }

    # Set joint positions in Webots
    for i, joint in enumerate(joints):
        joint.setPosition(joint_data[joint_names[i]])

    # Calculate joint velocities (angle change over time)
    joint_velocities = {
        name: (joint_data[name] - previous_angles[name]) / dt if dt > 0 else 0.0
        for name in joint_names
    }

    # Update previous angles and time for the next iteration
    previous_angles = joint_data.copy()
    previous_time = current_time

    # Package data into JSON format
    data = {
        "timestamp": datetime.now().isoformat(),
        "joint_angles": joint_data,
        "joint_velocities": joint_velocities,

    }

    # Publish data to MQTT
    mqtt_client.publish("ur5/joint_data", json.dumps(data))

    # Debug print
    print(data)

    # Wait to match the simulation timestep
    time.sleep(timestep / 100.0)
