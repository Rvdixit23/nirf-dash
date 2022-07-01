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
server = app.server


criteria_breakdown = dcc.Markdown(
            """
            ### Criteria Explained!
            ###### Teaching, Learning & Resources (TLR)
            - Student Strength including Doctoral Students(SS): 20 marks
            - Faculty-student ratio with emphasis on permanent faculty (FSR): 30
            marks
            - Combined metric for Faculty with PhD (or equivalent) and
            Experience (FQE): 20 marks
            - Financial Resources and their Utilisation (FRU): 30 marks
            ###### Research and Professional Practice (RP)
            - Combined metric for Publications (PU): 35 marks
            - Combined metric for Quality of Publications (QP): 40 marks
            - IPR and Patents: Published and Granted (IPR): 15 marks
            - Footprint of Projects and Professional Practice (FPPP): 10 marks
            ###### Graduation Outcomes (GO)
            - Combined metric for Placement and Higher Studies (GPH): 40 marks
            - Metric for University Examinations (GUE): 15 marks
            - Median Salary (GMS): 25 marks
            - Metric for Number of Ph.D. Students Graduated (GPHD): 20 marks
            ###### Outreach and Inclusivity (OI)
            - Percentage of Students from other States/Countries (Region Diversity
            RD): 30 marks
            - Percentage of Women (Women Diversity WD): 30 marks
            - Economically and Socially Challenged Students (ESCS): 20 marks
            - Facilities for Physically Challenged Students (PCS): 20 marks
            ###### Perception (PR)
            - Peer Perception: Employers & Academic Peer (PR): 100 marks
        """
        )

# -- Import and clean data (importing csv into pandas)
# df = pd.read_csv("IndianUniversityRankingFrom2017to2021.csv")
# df = df.pivot(index = ["Institute ID", "Name"], columns="Year", values="Rank")
# df = df.groupby(["Institute ID", "Name"])[["Rank"]].transform("Year")
# df.reset_index(inplace=True)
# print(df)

# ------------------------------------------------------------------------------
# App layout

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

reset_button = html.Button(
    "Reset", id="reset_values", n_clicks=0, className="setbutton"
)

app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Markdown(
                    """
                    ### **2021 Engineering NIRF Rankings, but YOU decide criteria weights**
                    #### **Please Note** ***To understand the scores and how they are computed, please refer to the NIRF website [here](https://www.nirfindia.org/nirfpdfcdn/2021/framework/Engineering.pdf).*** Metrics used for NIRF rankings are designed to be easily verifiable.
                    ###### For example, a high teacher to student ratio doesn't really mean the teachers are good. **Here are a list of metrics completely ignored by NIRF criteria which might matter to you.**
                    ###### Quality of teaching (different from qualification of teaching), Campus, Hostel, How good/safe the city is, Food, Fees and Cost of living, College activity clubs, Annual Fests, Peer Crowd.
                    ###### Watch my YouTube video to learn more about NIRF [here (Video not up yet)](https://www.youtube.com/channel/UCq5cUH_k3Y2u_rnUeF6zbDg/).
                """,
                ),
            ],
            id="intro_text",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [element for criteria in sliders for element in criteria],
                            id='sliders',
                        ),
                        html.Div(
                            college_table,
                            id="college_table"
                        ),
                    ],
                    id="slider_table_container",
                ),
                html.Div(reset_button),
            ],
        ),
        criteria_breakdown,
    ],
    # table and sliders below the text,
)


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
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
