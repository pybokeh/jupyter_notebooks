import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

df = pd.read_excel(
    "https://github.com/chris1610/pbpython/blob/master/data/salesfunnel.xlsx?raw=True"
)
mgr_options = df["Manager"].unique()

app = dash.Dash()

app.layout = html.Div([
    html.H2("Sales Funnel Report"),
    html.Div(
        [
            dcc.Dropdown(
                id="Manager",
                options=[{
                    'label': i,
                    'value': i
                } for i in mgr_options],
                value='All Managers'),
        ],
        style={'width': '25%',
               'display': 'inline-block'}),
    dcc.Graph(id='funnel-graph'),
])


@app.callback(
    dash.dependencies.Output('funnel-graph', 'figure'),
    [dash.dependencies.Input('Manager', 'value')])
def update_graph(Manager):
    if Manager == "All Managers":
        df_plot = df.copy()
    else:
        df_plot = df[df['Manager'] == Manager]

    pv = pd.pivot_table(
        df_plot,
        index=['Name'],
        columns=["Status"],
        values=['Quantity'],
        aggfunc=sum,
        fill_value=0)

    trace1 = go.Bar(x=pv.index, y=pv[('Quantity', 'declined')], name='Declined')
    trace2 = go.Bar(x=pv.index, y=pv[('Quantity', 'pending')], name='Pending')
    trace3 = go.Bar(x=pv.index, y=pv[('Quantity', 'presented')], name='Presented')
    trace4 = go.Bar(x=pv.index, y=pv[('Quantity', 'won')], name='Won')

    return {
        'data': [trace1, trace2, trace3, trace4],
        'layout':
        go.Layout(
            title='Customer Order Status for {}'.format(Manager),
            barmode='stack')
    }


if __name__ == '__main__':
    app.run_server(debug=True)
