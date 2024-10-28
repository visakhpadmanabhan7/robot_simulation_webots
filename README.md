[Architecture Diagram](module_diagram.pdf)

1. To simulate the robot : Webots application and used ur5 robotic arm and used the controller publish_angle.py.
2. The joint and velocity data are pushed to MQTT broker.
3. The data is received by the subscriber and the data is stored in the SQLite database. (main.py and ur5_data.db)
4. The data is visualised using dash application in realtime with the flexibility to check different values. (vis.py)
5. Analysis of data and prediction is performed in modelling.ipynb.