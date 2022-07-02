import pandas as pd
import numpy as np
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import (
    Dash,
    dash_table,
    dcc,
    html,
    Input,
    Output,
    callback_context,
)  # pip install dash (version 2.0.0 or higher)


app = Dash(__name__)
server = app.server

# ------------------------------------------------------------------------------
# App components

# Criteria breakdown
with open("docs/criteria.md", "r") as criteriaFile:
    criteria_breakdown = dcc.Markdown(criteriaFile.read())

# Introduction text
with open("docs/intro.md", "r") as introFile:
    intro = dcc.Markdown(introFile.read())

# Usage Instructions
with open("docs/usage.md", "r") as usageFile:
    usage = dcc.Markdown(usageFile.read())

# College Tables
college_df = pd.read_csv("sample_data.csv")
college_df = college_df.drop(["Institute Id"], axis=1)
college_table = dash_table.DataTable(
    id="college_rankings_with_custom_weight",
    data=college_df.to_dict("records"),
    columns=[{"name": i, "id": i} for i in college_df.columns],
    editable=True,
    filter_action="native",
    sort_action="custom",
    sort_mode="single",
    sort_by=[{"column_id": "Score", "direction": "desc"}],
    column_selectable="single",
    # row_selectable="multi",
    # row_deletable=True,
    selected_columns=[],
    selected_rows=[],
    page_action="native",
    page_current=0,
    page_size=10,
    style_cell={
        "overflow": "hidden",
        "textOverflow": "ellipsis",
        "maxWidth": "8%",
        "width": "0.1%",
        "white-space": "nowrap",
    },
    style_filter={
        "maxWidth": "2%",
    },
)

ranking_criteria = [
    "Teaching, Learning & Resources",
    "Research and Professional Practice",
    "Graduation Outcomes",
    "Outreach and Inclusivity",
    "Perception",
]

global old_values
old_values = [90, 90, 60, 30, 30]

sliders = [
    [
        html.H4(criteria),
        dcc.Slider(
            id=criteria,
            min=0,
            max=100,
            value=default_value,
            tooltip={"placement": "bottom", "always_visible": True},
        ),
    ]
    for criteria, default_value in zip(ranking_criteria, old_values)
]

tagged_sliders = [element for criteria in sliders for element in criteria]

reset_button = html.Button(
    "Reset", id="reset_values", n_clicks=0, className="setbutton"
)

toggle_iits_button = html.Button(
    "Toggle IITs", id="toggle_iits", n_clicks=0, className="setbutton"
)

toggle_nits_button = html.Button(
    "Toggle NITs", id="toggle_nits", n_clicks=0, className="setbutton"
)

# ------------------------------------------------------------------------------
# App layout

app.layout = html.Div(
    [
        html.Div(
            [
                usage,
            ],
            id="intro_text",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            tagged_sliders,
                            id='sliders',
                        ),
                        html.Div(
                            college_table,
                            id="college_table"
                        ),
                    ],
                    id="slider_table_container",
                ),
                html.Div([reset_button]),
            ],
            id="ranking_dash"
        ),
        intro,
        criteria_breakdown,
    ],
    # table and sliders below the text,
)


# ------------------------------------------------------------------------------
# Interactive functionality
@app.callback(
    [
        Output(component_id=criteria, component_property="value")
        for criteria in ranking_criteria
    ],
    [Input(component_id="reset_values", component_property="n_clicks")],
    prevent_initial_call=True,
)
def ensure_sum(reset_id):
    callback_trigger = callback_context
    global old_values
    trigger_id = callback_trigger.triggered[0]["prop_id"].split(".")[0]
    if trigger_id == "reset_values":
        old_values = [90, 90, 60, 30, 30]
        return [90, 90, 60, 30, 30]


@app.callback(
    Output(
        component_id="college_rankings_with_custom_weight", component_property="data"
    ),
    [
        Input(
            component_id="college_rankings_with_custom_weight",
            component_property="sort_by",
        ),
    ]
    + [
        Input(component_id=criteria, component_property="value")
        for criteria in ranking_criteria
    ],
    prevent_initial_call=True,
)
def weight_tables(sort_by, *weights):
    criteria_short = ["TLR", "RPC", "GO", "OI", "Perception"]
    total = sum(weights)
    new_df = college_df
    new_df["Score"] = 0
    for criteria, weight in zip(criteria_short, weights):
        new_df["Score"] += (weight / total) * new_df[criteria]
    new_df["Score"].round(2)
    new_df.sort_values(by="Score", ascending=False, inplace=True)
    new_df["Rank"] = np.arange(len(new_df)) + 1
    # print(new_df.head())
    return new_df.to_dict("records")


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True)
