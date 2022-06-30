import itertools
from typing import List
import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import (
    Dash,
    dcc,
    html,
    Input,
    Output,
    callback_context,
)  # pip install dash (version 2.0.0 or higher)


app = Dash(__name__)

# -- Import and clean data (importing csv into pandas)
# df = pd.read_csv("IndianUniversityRankingFrom2017to2021.csv")
# df = df.pivot(index = ["Institute ID", "Name"], columns="Year", values="Rank")
# df = df.groupby(["Institute ID", "Name"])[["Rank"]].transform("Year")
# df.reset_index(inplace=True)
# print(df)

# ------------------------------------------------------------------------------
# App layout
ranking_criteria = [
    "Teaching, Learning & Resources",
    "Research and Professional Practice",
    "Graduation Outcomes",
    "Outreach and Inclusivity",
    "Perception",
]

global old_values
old_values = [30, 30, 20, 10, 10]

sliders = [
    [
        html.H3(criteria + " Weight"),
        dcc.Slider(
            id=criteria,
            min=0,
            max=100,
            value=default_value,
            tooltip={"placement": "bottom", "always_visible": True},
        ),
        html.Br(),
    ]
    for criteria, default_value in zip(ranking_criteria, old_values)
]


app.layout = html.Div(
    [element for criteria in sliders for element in criteria]
    + [html.Button("Reset", id="reset_values", n_clicks=0)]
)


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [
        Output(component_id=criteria, component_property="value")
        for criteria in ranking_criteria
    ],
    [Input(component_id="reset_values", component_property="n_clicks")]
    + [
        Input(component_id=criteria, component_property="value")
        for criteria in ranking_criteria
    ],
    prevent_initial_call=True,
)
def ensure_sum(reset_id, *values):
    callback_trigger = callback_context
    global old_values
    trigger_id = callback_trigger.triggered[0]["prop_id"].split(".")[0]
    if trigger_id == "reset_values":
        print("here")
        return [30, 30, 20, 10, 10]
    results = [None for _ in values]
    for index, slider in enumerate(values):
        if slider != old_values[index]:
            total_left = 100 - slider
            old_val_before_change = old_values[index]
            results[index] = slider
    if any(results):
        for index, old_val in enumerate(old_values):
            if not results[index]:
                # print(f"({old_val}/(100 - {old_val_before_change}))*{total_left}")
                results[index] = (old_val / (100 - old_val_before_change)) * total_left
    old_values = [result for result in results]
    return results


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True)
