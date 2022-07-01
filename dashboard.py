from functools import reduce
import itertools
from typing import List
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

# -- Import and clean data (importing csv into pandas)
# df = pd.read_csv("IndianUniversityRankingFrom2017to2021.csv")
# df = df.pivot(index = ["Institute ID", "Name"], columns="Year", values="Rank")
# df = df.groupby(["Institute ID", "Name"])[["Rank"]].transform("Year")
# df.reset_index(inplace=True)
# print(df)

# ------------------------------------------------------------------------------
# App layout

college_df = pd.read_csv("sample_data.csv")
college_df = college_df.drop(
    ["Institute Id", "TLR", "RPC", "GO", "OI", "Perception"], axis=1
)
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
old_values = [30, 30, 20, 10, 10]

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

reset_button = html.Button(
    "Reset", id="reset_values", n_clicks=0, className="setbutton"
)

app.layout = html.Div(
    [
        html.Div(
            dcc.Markdown(
                """
                    ### **2021 Engineering NIRF Rankings, but YOU decide criteria weights**
                    #### **Please Note** *To understand the scores and how they are computed, please refer to the NIRF website [here](https://www.nirfindia.org/nirfpdfcdn/2021/framework/Engineering.pdf).* Metrics used for NIRF rankings are designed to be easily verifiable.
                    ###### For example, a high teacher to student ratio doesn't really mean the teachers are good. **Here are a list of metrics completely ignored by NIRF criteria which might matter to you.**
                    ###### Quality of teaching (different from qualification of teaching), Campus, Hostel, How good/safe the city is, Food, Fees and Cost of living, College activity clubs, Annual Fests, Peer Crowd.
                    ###### Watch my YouTube video to learn more about NIRF [here (Video not up yet)](https://www.youtube.com/channel/UCq5cUH_k3Y2u_rnUeF6zbDg/).
                """,
            ),
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [element for criteria in sliders for element in criteria],
                            style={"width": "40%"},
                        ),
                        html.Div(
                            college_table,
                            style={
                                "width": "60%",
                                "display": "flex",
                                "align-items": "center",
                                "justify-content": "center",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "flex-direction": "row",
                        "align-content": "center",
                    },
                ),
                html.Div(reset_button),
            ],
        ),
    ],
    # table and sliders below the text
    style={"display": "flex", "flex-direction": "column"},
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
        old_values = [30, 30, 20, 10, 10]
        return [30, 30, 20, 10, 10]
    results = [None for _ in values]
    for index, slider in enumerate(values):
        if slider != old_values[index]:
            total_left = 100 - slider
            old_val_before_change = old_values[index]
            results[index] = slider
    if old_val_before_change == 100:
        results = [total_left / 4 if not res else 100 - total_left for res in results]
    if filter(lambda x: x is not None, results):
        for index, old_val in enumerate(old_values):
            if results[index] == None:
                # print(f"({old_val}/(100 - {old_val_before_change}))*{total_left}")
                results[index] = (old_val / (100 - old_val_before_change)) * total_left
    old_values = [result for result in results]
    return results


@app.callback(
    Output(
        component_id="college_rankings_with_custom_weight", component_property="data"
    ),
    [
        Input(
            component_id="college_rankings_with_custom_weight",
            component_property="sort_by",
        )
    ]
    + [
        Input(component_id=criteria, component_property="value")
        for criteria in ranking_criteria
    ],
    prevent_initial_call=True,
)
def weight_tables(sort_by, *weights):
    criteria_short = ["TLR", "RPC", "GO", "OI", "Perception"]
    new_df = college_df
    new_df["Score"] = 0
    for criteria, weight in zip(criteria_short, weights):
        new_df["Score"] += (weight / 100) * new_df[criteria]
    new_df["Score"].round(2)
    new_df.sort_values(by="Score", ascending=False, inplace=True)
    new_df["Rank"] = np.arange(len(new_df)) + 1
    print(new_df.head())
    return new_df.to_dict("records")


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True)
