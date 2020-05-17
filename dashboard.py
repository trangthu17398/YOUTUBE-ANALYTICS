import pandas as pd     #(version 1.0.0)
import plotly           #(version 4.5.4) pip install plotly==4.5.4
import plotly.express as px
import datetime 
from datetime import date
import dash             #(version 1.9.1) pip install dash==1.9.1
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

#---------------------------------------------------------------
#Taken from https://www.ecdc.europa.eu/en/geographical-distribution-2019-ncov-cases
df = pd.read_csv("Schannel1.csv")
available_year = df['Year'].unique()
available_month=df['publishedAt_month'].unique()
dff = df.groupby('Year', as_index=False)[['videoView','videoLike','videoDislike','videoComment']].sum()
dff['Videos']= df.groupby('Year', as_index=False).count()['videoTitle']
#---------------------------------------------------------------
app.layout = html.Div([
    html.Div([
        dash_table.DataTable(
            id='datatable_id',
            data=dff.to_dict('records'),
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": False} for i in dff.columns
            ],
            editable=False,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            row_selectable="multi",
            row_deletable=False,
            selected_rows=[],
            page_action="native",
            page_current= 0,
            page_size= 6,
            # page_action='none',
            # style_cell={
            # 'whiteSpace': 'normal'
            # },
            # fixed_rows={ 'headers': True, 'data': 0 },
            # virtualization=False,
            style_cell_conditional=[
                {'if': {'column_id': 'Year'},
                 'width': '10%', 'textAlign': 'left'},
                {'if': {'column_id': 'Videos'},
                 'width': '18%', 'textAlign': 'left'},
                {'if': {'column_id': 'videoView'},
                 'width': '18%', 'textAlign': 'left'},
                {'if': {'column_id': 'VideoLike'},
                 'width': '18%', 'textAlign': 'left'},
                {'if': {'column_id': 'VideoDislike'},
                 'width': '18%', 'textAlign': 'left'},
                {'if': {'column_id': 'VideoComment'},
                 'width': '18%', 'textAlign': 'left'},
            ],
        ),
    ],className='row'),

    html.Div([
        html.Div([
            'Bar chart',
            dcc.Dropdown(id='bardropdown',
                options=[{'label': 'Videos', 'value': 'Videos'},
                        {'label': 'View', 'value': 'videoView'},
                        {'label': 'Like', 'value': 'videoLike'},
                        {'label': 'Dislike', 'value': 'videoDislike'},
                        {'label': 'Comment', 'value': 'videoComment'}
                ],
                value='Videos',
                multi=False,
                clearable=False
            ),
        ],className='six columns'),

        html.Div([
        'Pie chart',
        dcc.Dropdown(id='piedropdown',
            options=[{'label': 'Videos', 'value': 'Videos'},
                    {'label': 'View', 'value': 'videoView'},
                    {'label': 'Like', 'value': 'videoLike'},
                    {'label': 'Dislike', 'value': 'videoDislike'},
                    {'label': 'Comment', 'value': 'videoComment'}
            ],
            value='videoComment',
            multi=False,
            clearable=False
        ),
        ],className='six columns'),

    ],className='row'),

    html.Div([
        html.Div([
            dcc.Graph(id='barchart'),
        ],className='six columns'),

        html.Div([
            dcc.Graph(id='piechart'),
        ],className='six columns'),

    ],className='row'),

    html.Div([
        dcc.Graph(
            id='top-graph'
        ),
        'Indicator_year',
        dcc.Dropdown(
            id='top-graph-indicator',
            options=[
                {'label': 'View', 'value': 'videoView'},
                {'label': 'Like', 'value': 'videoLike'},
                {'label': 'Dislike', 'value': 'videoDislike'},
                {'label': 'Comment', 'value': 'videoComment'}
            ],
            value='videoLike'
        ),
        'Year',
        dcc.Dropdown(
            id='top-graph-year',
            options=[
                {'label': year, 'value': year} for year in available_year
            ],
            value=available_year[0]
        )]),

    html.Div([
        dcc.Graph(
            id='top-graph1'
        ),
        'Indicator_month',
        dcc.Dropdown(
            id='top-graph-indicator1',
            options=[
                {'label': 'View', 'value': 'videoView'},
                {'label': 'Like', 'value': 'videoLike'},
                {'label': 'Dislike', 'value': 'videoDislike'},
                {'label': 'Comment', 'value': 'videoComment'}
            ],
            value='videoLike'
        ),
        'Month_Year',
        dcc.Dropdown(
            id='top-graph-month',
            options=[
                {'label': month, 'value': month}
                for month in available_month
            ],
            value=available_month[0]
        )])

])

#------------------------------------------------------------------
@app.callback(
    [Output('piechart', 'figure'),
     Output('barchart', 'figure')],
    [Input('datatable_id', 'selected_rows'),
     Input('piedropdown', 'value'),
     Input('bardropdown', 'value')])
def update_data(chosen_rows,piedropval,bardropval):
    if len(chosen_rows)==0:
        # df_filterd = dff[dff['Year'].isin([2020,2019,2018,2017,2016])]
        df_filterd = dff
    else:
        print(chosen_rows)
        df_filterd = dff[dff.index.isin(chosen_rows)]

    pie_chart=px.pie(
            data_frame=df_filterd,
            names='Year',
            values=piedropval,
            hole=.3,
            labels={'Year':'Year'}
            )
    df_bar = dff

    bar_chart = px.bar(
            data_frame=df_filterd,
            x='Year',
            y=bardropval)

    return (pie_chart,bar_chart)

@app.callback(
    Output('top-graph', 'figure'),
    [Input('top-graph-indicator', 'value'),
     Input('top-graph-year', 'value')]
)
def update_store_data(indicator, year):
    dff = df[df['Year'] == year].sort_values(indicator,ascending=True).tail(5)
    bar_chart = px.bar(
            data_frame=dff,
            y=dff['videoTitle'],
            x=dff[indicator],
            orientation='h',
            text='Month_str',
            title='%s - TOP 5 VIDEO CÓ LƯỢT %s CAO NHẤT NĂM %s'%(df['channelTitle'][0],indicator,year)
            )
    return bar_chart

@app.callback(
    Output('top-graph1', 'figure'),
    [Input('top-graph-indicator1', 'value'),
     Input('top-graph-month', 'value')]
)
def update_store_data1(indicator, month):
    dff1 = df[df['publishedAt_month'] == month].sort_values(indicator,ascending=True).tail(5)
    bar_chart1 = px.bar(
            data_frame=dff1,
            y=dff1['videoTitle'],
            x=dff1[indicator],
            orientation='h',
            text='DayofWeek',
            title='%s - TOP 5 VIDEO CÓ LƯỢT %s CAO NHẤT THÁNG %s'%(df['channelTitle'][0],indicator,month)
            )
    return bar_chart1

#------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)