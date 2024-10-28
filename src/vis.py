import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import sqlite3
import pandas as pd

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "UR5 Robot Joint Data Visualization"

# Define the list of joint names
joint_names = [
    'shoulder_pan_joint',
    'shoulder_lift_joint',
    'elbow_joint',
    'wrist_1_joint',
    'wrist_2_joint',
    'wrist_3_joint'
]

# Layout with dropdowns to select a joint and display angle or velocity graph
app.layout = html.Div([
    html.H1("UR5 Robot Joint Data Visualization", style={'text-align': 'center'}),

    # Dropdown for selecting joint
    html.Div([
        html.Label("Select Joint:"),
        dcc.Dropdown(
            id='joint-dropdown',
            options=[{'label': joint.replace('_', ' ').capitalize(), 'value': joint} for joint in joint_names],
            value='shoulder_pan_joint',  # Default selected joint
            clearable=False
        ),
    ], style={'width': '40%', 'margin': '0 auto'}),

    # Dropdown for selecting data type (Angle or Velocity)
    html.Div([
        html.Label("Select Data Type:"),
        dcc.Dropdown(
            id='data-type-dropdown',
            options=[
                {'label': 'Angle', 'value': 'angle'},
                {'label': 'Velocity', 'value': 'velocity'}
            ],
            value='angle',  # Default data type
            clearable=False
        ),
    ], style={'width': '40%', 'margin': '0 auto', 'margin-top': '20px'}),

    # Graph for the selected joint and data type
    html.Div([
        dcc.Graph(id='joint_graph')
    ]),

    # Interval component for refreshing the data
    dcc.Interval(id='interval-component', interval=1 * 1000, n_intervals=0)  # Refresh every 1 second
])


# Function to fetch the latest data for a specific joint and data type from SQLite database
def fetch_joint_data(joint_name, data_type):
    conn = sqlite3.connect('../ur5_data.db')

    # Select the appropriate column based on data type
    column_name = f"{joint_name}_{data_type}"
    query = f"SELECT timestamp, {column_name} AS value FROM joint_data ORDER BY timestamp DESC LIMIT 50"

    # Read query result into DataFrame
    df = pd.read_sql(query, conn)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    conn.close()
    return df


# Callback function to update the graph based on selected joint, data type, and refresh interval
@app.callback(
    Output('joint_graph', 'figure'),
    [Input('joint-dropdown', 'value'), Input('data-type-dropdown', 'value'), Input('interval-component', 'n_intervals')]
)
def update_graph(selected_joint, selected_data_type, n):
    # Fetch the data for the selected joint and data type (angle or velocity)
    df = fetch_joint_data(selected_joint, selected_data_type)

    # Create the line plot for the selected joint and data type
    trace = go.Scatter(x=df['timestamp'], y=df['value'], mode='lines+markers', name=selected_joint)

    # Set y-axis label and title based on data type
    y_axis_title = "Angle (radians)" if selected_data_type == 'angle' else "Velocity (rad/s)"
    title = f"{selected_joint.replace('_', ' ').capitalize()} {selected_data_type.capitalize()} Over Time"

    # Define the figure layout
    fig = {
        'data': [trace],
        'layout': go.Layout(
            title=title,
            xaxis={'title': 'Time'},
            yaxis={'title': y_axis_title},
            template="plotly_dark"
        )
    }

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
