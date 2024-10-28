[Architecture Diagram](module_diagram.pdf)

Packages used : requirements.txt

1. To simulate the robot : Webots application (https://cyberbotics.com/doc/reference/introduction) and used ur5 robotic arm and used the controller publish_angle.py.
2. The joint and velocity data payload is published to MQTT broker.
3. The payload is received by the subscriber (mqtt_subscriber) and the data is stored in the SQLite database. (ur5_data.db)
4. The data is visualised using dash application in realtime with the flexibility to check different values. (vis.py) (http://127.0.0.1:8050/)
5. Analysis of data and prediction is performed in modelling.ipynb.