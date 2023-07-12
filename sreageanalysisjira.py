#!/usr/bin/env python3
import argparse
import logging
import numpy as np
import pandas as pd
import plotly.express as px
import dash

from age_query_builder.age_query_builder import TR1_DEFECTS, FTC_DEFECTS, ALL_DEFECTS
from age_query_builder.age_query_builder import TR1_FIXED_QUERY, TR1_CLOSED_QUERY
from age_query_builder.age_query_builder import FTC_FIXED_QUERY, TR1_CLOSED_QUERY
from age_query_builder.age_query_builder import CLOSED, FIXED
from age_query_builder.age_query_builder import get_query
from config import JIRA_API_TOKEN
from config import JIRAURL
from config import VERSION
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
from defect_info.defect_info import get_defects_filtered

from jira import JIRA
from jira_talker.jira_talker import JIRA_TALKER


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

jra = JIRA_TALKER()

app = dash.Dash(
    __name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"]
)
server = app.server  # required for gunicorn
app.title = "SRE Age Analysis - JIRA version"
PORT = 8154
DEFAULT_HIST_BUCKET_SIZE = 14

def bucketize(defects, bsize=DEFAULT_HIST_BUCKET_SIZE, field="priority"):
    hours_per_day = 24
    ages = {}
    ages_lists = {}
    counts = {}
    for d in defects:
        val = getattr(d, field, None)
        assert val is not None
        try:
            counts[val] += 1
            ages[val] += d.Age
            ages_lists[val].append(int(d.Age / hours_per_day))
        except KeyError:
            counts[val] = 1
            ages[val] = d.Age
            ages_lists[val] = [int(d.Age / hours_per_day)]
    # at this point I have
    # counts = a count of cases per priority, and
    # ages =  an overall sum of ages (in hours) per priority, and
    # ages_lists = a list of ages in days
    assert len(defects) == sum([counts[k] for k in counts.keys()])
    for k in counts.keys():
        ages[k] = int(ages[k] / (hours_per_day * counts[k]))
    ages_hists = {}
    for k in counts.keys():
        bucket_values = list(range(0, int(((max(ages_lists[k]) / bsize) + 1) * bsize), bsize))
        ages_hists[k] = np.histogram(ages_lists[k], bins=bucket_values)
    hist_sum = 0
    for k in counts.keys():
        hist_sum += sum(ages_hists[k][0])
    assert len(defects) == hist_sum, "len(defects) is {} != hist_sum of {}".format(len(defects), hist_sum)
    return ages, ages_hists


def save_and_return_df(thing, keys, bsize, filename):
    toto = {}
    for k in keys:
        try:
            toto[k] = list(thing[k][0])
        except KeyError:
            toto[k] = [0]
    maxlength = 0
    for k in keys:
        if len(toto[k]) > maxlength:
            maxlength = len(toto[k])
    for k in keys:
        if len(toto[k]) < maxlength:
            toto[k] = toto[k] + [0] * (maxlength - len(toto[k]))
    blabels = [(x + 1) * bsize for x in range(maxlength)]
    toto["days"] = blabels
    df = pd.DataFrame(toto)
    cols = ["days"] + keys
    df = df[cols]
    df.to_csv(filename)
    return df

def build_page():
    minslider=4
    maxslider=28
    slider_spacer = 64
    slider_marks = {}
    for mk in range(minslider, maxslider, 2):
        slider_marks[mk] = str(mk)
    return html.Div(children=[
        html.H1("Age of open defects tagged with sentry-gse, sentry-tr1."),
        html.Div(children=[
            html.Table([
                html.Tr([
                    html.Td("Parameters to adjust"),
                    html.Td("<" + "-" * slider_spacer + " Slider " + "-" * slider_spacer + ">"),
                    html.Td("Value ({} ... {} days)".format(minslider, maxslider))
                ]),
                html.Tr([
                    html.Td("Bucket Size"),
                    html.Td(
                        dcc.Slider(
                            id='bucketsize-slider',
                            min=minslider,
                            max=maxslider,
                            marks=slider_marks,
                            value=DEFAULT_HIST_BUCKET_SIZE
                       )
                    ),
                    html.Td(html.Label(id='bucket-size-value', children="{}".format(DEFAULT_HIST_BUCKET_SIZE)))
                ]),
                html.Tr([ 
                    html.Td("sentry-X"),
                    html.Td(
                        dcc.Dropdown(
                            id='sentry-choice-dropdown',
                            options=[
                                {'label': 'TR1', 'value': TR1_DEFECTS},
                                {'label': 'FTCSales', 'value': FTC_DEFECTS},
                                {'label': 'All', 'value': ALL_DEFECTS}
                            ],
                            value=ALL_DEFECTS
                        )
                    ),
                    html.Td(html.Label(id='sentry-defects-value', children=ALL_DEFECTS))
                ]),
                html.Tr([
                    html.Td("Non-Fixed or Non-Closed"),
                    html.Td(
                        dcc.Dropdown(
                            id='fixed-dropdown',
                            options=[
                                {'label': 'NonClosed', 'value': CLOSED},
                                {'label': 'NonFixed', 'value': FIXED}
                            ],
                            value=FIXED
                        )
                    ),
                    html.Td(html.Label(id='fixed-closed-value', children=FIXED))
                ]),
            ]),
        ]),
        dcc.Loading(id='Loading1', type='default', children=[
            html.Div(children=[
                html.Table([
                    html.Tr([
                        html.Td(
                            dcc.Graph(id='age-graph',
                                      style={'width': '800px', 'display': 'inline-block'})
                        ),
                    ]),
                    html.Tr([
                        html.Td(
                            dcc.Dropdown(
                                id='priority-dropdown',
                                options=[
                                    {'label': 'Low', 'value': 'Low'},
                                    {'label': 'Medium', 'value': 'Medium'},
                                    {'label': 'High', 'value': 'High'},
                                    {'label': 'Critical', 'value': 'Critical'},
                                ],
                                value=['Low', 'Medium', 'High', 'Critical'],
                                multi=True
                            )
                        )
                    ]),
                    html.Tr([
                        html.Td(
                            dcc.Graph(id='age-projects',
                                      style={'width': '800px', 'display': 'inline-block'})
                        ),
                    ]),
                    html.Tr([
                        html.Td(
                            dcc.Graph(id='age-status',
                                      style={'width': '800px', 'display': 'inline-block'})
                        ),
                    ])
                ])
            ])
        ])
    ])


app.layout = build_page()

def get_per_project_data(defects, priority):
    db = {}
    for d in defects:
        if d.priority in priority:
            proj = d.Project
            if db.get(proj) is None:
                db[proj] = 1
            else:
                db[proj] += 1
    sorted_keys = sorted(db.keys())
    return pd.DataFrame({
        'names': sorted_keys,
        'count': [db[x] for x in sorted_keys]
    })


def get_per_state_data(defects, priority):
    db = {}
    for d in defects:
        if d.priority in priority:
            state = d.State
            if db.get(state) is None:
                db[state] = 1
            else:
                db[state] += 1
    sorted_keys = sorted(db.keys())
    return pd.DataFrame({
        'names': sorted_keys,
        'count': [db[x] for x in sorted_keys]
    })



@app.callback(
    [Output(component_id='age-graph', component_property='figure'),
     Output(component_id='age-projects', component_property='figure'),
     Output(component_id='age-status', component_property='figure'),
     Output(component_id='bucket-size-value', component_property='children'),
     Output(component_id='fixed-closed-value', component_property='children'),
     Output(component_id='sentry-defects-value', component_property='children')],
    [Input(component_id='bucketsize-slider', component_property='value'),
     Input(component_id='fixed-dropdown', component_property='value'),
     Input(component_id='sentry-choice-dropdown', component_property='value'),
     Input(component_id='priority-dropdown', component_property='value')]
)
def update(bucketsize, which, sentry_choice, priority):
    if which == FIXED:
        if sentry_choice == TR1_DEFECTS:
            graph_title = "Age of unfixed {} TR1 defects. Total = {}."
        if sentry_choice == FTC_DEFECTS:
            graph_title = "Age of unfixed {} FTCSales defects. Total = {}."
        if sentry_choice == ALL_DEFECTS:
            graph_title = "Age of unfixed {} defects. Total = {}."
    else:
        if sentry_choice == TR1_DEFECTS:
            graph_title = "Age of non-closed {} TR1 defects. Total = {}."
        if sentry_choice == FTC_DEFECTS:
            graph_title = "Age of non-closed {} FTCSales defects. Total = {}."
        if sentry_choice == ALL_DEFECTS:
            graph_title = "Age of non-closed {} defects. Total = {}."
    priority_in_order = ['Critical', 'High', 'Medium', 'Low']
    # 
    query = get_query(which, sentry_choice)
    defects = get_defects_filtered(jra, query)
    defect_buckets, histogram = bucketize(defects, bsize=bucketsize)
    df = save_and_return_df(histogram, priority_in_order, bsize=bucketsize, filename="defects.csv")
    # generate the figures
    fig = px.line(df, x="days", y=priority_in_order, title=graph_title.format("defects", len(defects))).update_traces(mode="lines+markers")
    # project pies
    projdf = get_per_project_data(defects, priority)
    projpie = px.pie(projdf, values="count", names="names")
    statedf = get_per_state_data(defects, priority)
    statepie = px.pie(statedf, values="count", names="names")
    return fig, projpie, statepie, bucketsize, which, sentry_choice


def main():
    print(f"Version {VERSION}")
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", dest="debug", action="store_true", help="Set debug mode")
    parser.add_argument("-p", dest="port", default=PORT, help="Set port to listen on.")
    args = parser.parse_args()
    if args.debug:
        logger.warning("Debug mode")
        app.run_server(debug=True, port=args.port)
    else:
        app.run_server(host="0.0.0.0", port=args.port)



if __name__ == "__main__":
    main()
