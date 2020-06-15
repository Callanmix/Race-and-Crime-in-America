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


## Dash components
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("About", href="#"))
    ],
    brand="Crime and Race",
    brand_href="#",
    color="success",
    dark=True,
)

jumbotron = dbc.Jumbotron(
    [
        html.H1("Crime", className="display-3"),
        html.P(children=[
            "This data is a combination of US Government records collected on 6/9/2020."
            "The data comes from API calls to the ", 
            html.A('Crime Data Explorer', href='https://crime-data-explorer.fr.cloud.gov/', target="_blank"),
            " and the ",
            html.A('US Census Bureau', href='https://data.census.gov/cedsci/profile?q=United%20States&g=0100000US&tid=ACSDP1Y2018.DP05', target="_blank"),
            ". The creation script is available on github."
        
        ],
            className="lead"
        ),
        html.P('These two graphs show total crimes commited by race and the percent of those'
               ' crimes by total population of that race. You can change the type of crime below.',
               className="lead"),
        html.Hr(className="my-2"),
        html.Div(style={'textAlign': 'center'}, children=[
            dcc.Dropdown(
                    id='crime_choice',
                    options=[{'label': i + ' ', 'value': i} for i in data['Crime'].unique()],
                    value='Aggravated Assault'
                )
        ]),
        html.Br(), html.Br(), html.Br(), html.Br()
    ]
)


def make_plotly_total_sums():
    df = grouped_data.merge(
        data[['Year', 'Code', 'Race', 'Population_Totals']],
        on=['Year', 'Code', 'Race']
    ).drop_duplicates(
    ).groupby(
        ['Year', 'Race']
    ).sum(
    ).reset_index()
    
    fig = px.line(x = df['Year'],
                  y = df['Count'] / df['Population_Totals'],
                  color = df['Race'],
                  labels = {'x':'Year', 'y':'Total Incidents / Total Population'},
                  template='simple_white')
    fig.update_layout(
        legend=dict(
            x=0,
            y=1.2,
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color="black"
            ),
            bgcolor="LightSteelBlue",
            bordercolor="Black",
            borderwidth=2
        ),
        font = dict(
            color='white'
        ),
        paper_bgcolor='rgba(42,161,152,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        legend_title_text='Race'
    )
    return fig

app = dash.Dash(__name__,
            external_stylesheets=[dbc.themes.SOLAR])
server = app.server
app.title = 'Race and Crime in America'

app.layout = dbc.Container([
    ## Navbar and Header
    navbar,
    html.Br(),
    html.Div(style={'textAlign': 'center'}, children=[
        html.H1([
            html.Strong('Crime Rates By State and Race')
        ])
    ]),
    html.Hr(style={'border': '2px solid white'}),
    html.Br(),
    
    ## First two Graphs and jumbotron
    dbc.Row([
        
        dbc.Col(jumbotron, md=4),
        
        dbc.Col([
            
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.H3('Sum of Incidents'),
                        dcc.Graph(id='sum_indcident'),
                        html.Br()
                    ],style={'textAlign': 'center'}),
                md=12),
            ]),

            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.H3('Average of Incident %'),
                        dcc.Graph(id='avg_%')
                    ],style={'textAlign': 'center'}),
                md=12)
            ])
            
        ], md=8)
        
    ], align="center"),
    html.Br(), html.Br(),

    ## Total crimes % by race
    dbc.Row([
        dbc.Col(
                html.Div([
                    html.H3('% of Race by All Crimes'),
                    dcc.Graph(id='total_crime', figure=make_plotly_total_sums())
                ],style={'textAlign': 'center'})
        )  
        ]),
    
    ## US map of Crimes
     dbc.Row([
          dbc.Col(
              
            html.Div(style={'textAlign': 'center'}, children=[
                dcc.Dropdown(
                        id='race',
                        options=[{'label': i + ' ', 'value': i} for i in np.append(['All'], data['Race'].unique())],
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
    
    ## Footer with Citation
    html.Br(),
    html.Br(),
    html.Footer('United States Department of Health and Human Services (US DHHS), Centers for Disease Control and Prevention (CDC),'
                'National Center for Health Statistics (NCHS), Bridged-Race Population Estimates, United States July 1st resident '
                'population by state, county, age, sex, bridged-race, and Hispanic origin. Compiled from 1990-1999 bridged-race intercensal '
                'population estimates (released by NCHS on 7/26/2004); revised bridged-race 2000-2009 intercensal population estimates (released by NCHS on 10/26/2012);'
                ' and bridged-race Vintage 2018 (2010-2018) postcensal population estimates (released by NCHS on 6/25/2019). Available on CDC WONDER Online Database.'
                ' Accessed at http://wonder.cdc.gov/bridged-race-v2018.html on Jun 9, 2020 5:27:20 PM')
    
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
    fig.update_layout(
        font = dict(
            color='white'
        ),
        paper_bgcolor='rgba(42,161,152,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend_title_text='Race'
    )
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
                 color=df['Race'],
                 template='simple_white')
    fig.update_layout(
        legend=dict(
            x=0,
            y=1.2,
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color="black"
            ),
            bgcolor="LightSteelBlue",
            bordercolor="Black",
            borderwidth=2
        ),
        font = dict(
            color='white'
        ),
        paper_bgcolor='rgba(42,161,152,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        legend_title_text='Race'
    )
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
                 color=df['Race'],
                 template='simple_white')
    fig.update_layout(
        legend=dict(
            x=0,
            y=1.2,
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color="black"
            ),
            bgcolor="LightSteelBlue",
            bordercolor="Black",
            borderwidth=2
        ),
        font = dict(
            color='white'
        ),
        paper_bgcolor='rgba(42,161,152,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        legend_title_text='Race'
    )
    return fig

if __name__ == '__main__':
    app.run_server(use_reloader = False)