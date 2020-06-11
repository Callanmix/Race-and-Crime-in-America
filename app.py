import pandas as pd
import numpy as np
# Dash
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly_express as px


data = pd.read_csv('combined_data.csv')
grouped_data = data[['Year', 'Code', 'Race', 'Count']].groupby(['Year', 'Code','Race']).sum()
grouped_data = grouped_data.reset_index()

def make_plotly_total_sums():
    df = grouped_data.merge(
        data[['Year', 'Code', 'Race', 'Population_Totals']],
        on=['Year', 'Code', 'Race']
    ).drop_duplicates(
    ).groupby(
        ['Year', 'Race']
    ).sum(
    ).reset_index()
    
    total_sums = px.line(x = df['Year'],
                        y = df['Count'] / df['Population_Totals'],
                        color = df['Race'],
                        labels = {'x':'Year', 'y':'Total Incidents / Total Population'})
    total_sums.update_layout(
        legend=dict(
            x=.8,
            y=1,
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color="black"
            ),
            bgcolor="LightSteelBlue",
            bordercolor="Black",
            borderwidth=2
        )
    )
    return total_sums

app = dash.Dash(__name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    
    html.Div(style={'textAlign': 'center'}, children=[
        html.H1('Crime Rates By State and Race')
    ]),
    
    html.Div(children=[html.Br()]),
    
    html.Div(style={'textAlign': 'center'}, children=[
        dcc.Dropdown(
                id='crime_choice',
                options=[{'label': i + ' ', 'value': i} for i in data['Crime'].unique()],
                value='Aggravated Assault'
            )
    ]),
    
    html.Div(children=[html.Br()]),
        
    dbc.Row([
            dbc.Col(
                html.Div([
                    html.H3('Sum of Incidents'),
                    dcc.Graph(id='sum_indcident')
                ],style={'textAlign': 'center'}),
            md=6),
            
            dbc.Col(
                html.Div([
                    html.H3('Average of Incident %'),
                    dcc.Graph(id='avg_%')
                ],style={'textAlign': 'center'}),
            md=6)
        ],
        align="center"
    ),
    
     dbc.Row([
          dbc.Col(
            html.Div(style={'textAlign': 'center'}, children=[
                dcc.Dropdown(
                        id='race',
                        options=[{'label': i + ' ', 'value': i} for i in np.append(data['Race'].unique(), 'All')],
                        value='All'
                    ),
                html.Div(children=[html.Br()]),
                
                dcc.Dropdown(
                        id='crime',
                        options=[{'label': i + ' ', 'value': i} for i in data['Crime'].unique()],
                        value='Aggravated Assault'
                    ),
                
                html.Div(children=[html.Br()]),
                
                dcc.RadioItems(
                        id='rates',
                        options=[{'label': 'Crime Rate by Racial Population  ', 'value': 'race_pop'},
                                {'label': 'Crime Rate by Total Population  ', 'value': 'total_pop'}],
                    value='Crime Rate by Total Population  '
                    )
            ]), md=5
          ),
            dbc.Col(
                html.Div([
                    html.H3('Crime as % of Population'),
                    dcc.Graph(id='us_map')
                ],style={'textAlign': 'center'}),
            md=7),
        ],
        align="center"
    ),
    
    dbc.Row(
        [
        dbc.Col(
                html.Div([
                    dcc.Graph(id='total_crime', figure=make_plotly_total_sums())
                ],style={'textAlign': 'center'}),
            md=12)  
        ])
    
],fluid=True)




@app.callback(
    Output('us_map', 'figure'),
    [Input('crime', 'value'),
    Input('race', 'value'),
    Input('rates', 'value')])
def update_graph(crime, race, rates):
    if race == 'All':
        df = data[(data['Crime'] == crime)]
        fig = px.choropleth(df, locations="Code", color = df['Count']/df['Population'],
                                locationmode="USA-states", scope="usa",
                                animation_frame='Year')
    else:
        df = data[(data['Crime'] == crime) & (data['Race'] == race)]
        if rates == 'race_pop':
            fig = px.choropleth(df, locations="Code", color = df['Count']/df['Population_Totals'],
                                locationmode="USA-states", scope="usa",
                                animation_frame='Year')
        else:
            fig = px.choropleth(df, locations="Code", color = df['Count']/df['Population'],
                                locationmode="USA-states", scope="usa",
                                animation_frame='Year')
    return fig

@app.callback(
    Output('sum_indcident', 'figure'),
    [Input('crime_choice', 'value')])
def update_graph(crime_choice):
    df = data[data['Crime'] == crime_choice][['Year','Crime','Count','Population_Totals','Race']].groupby(
            ['Year','Crime','Race']
        ).sum().reset_index()
    fig = px.line(x = df['Year'],
                  y = df['Count'],
                  labels = {'x':'Year', 'y':'Sum of Total Incidents by Race'},
                 color=df['Race'])
    fig.update_layout(legend_orientation="h")
    return fig

@app.callback(
    Output('avg_%', 'figure'),
    [Input('crime_choice', 'value')])
def update_graph(crime_choice):
    df = data[data['Crime'] == crime_choice][['Year','Crime','Count','Population_Totals','Race']].groupby(
            ['Year','Crime','Race']
        ).sum().reset_index()
    fig = px.line(x = df['Year'],
                  y = df['Count'] / df['Population_Totals'],
                  labels = {'x':'Year', 'y':'Average % of Crime Per Population'},
                 color=df['Race'])
    fig.update_layout(legend_orientation="h")
    return fig

if __name__ == '__main__':
    app.run_server(debug = True, use_reloader = False)