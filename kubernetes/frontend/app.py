from dash import dcc, html, Dash
from dash.dependencies import Input, Output
from configure import ConfigurationTab

app = Dash(__name__, suppress_callback_exceptions=True)
config_tab = ConfigurationTab(app)

app.layout = html.Div(
    [
        dcc.Tabs(
            id="tabs-example",
            value="tab-1",
            children=[
                dcc.Tab(label="Tab One", value="tab-1"),
                dcc.Tab(label="Tab Two", value="tab-2"),
                dcc.Tab(label="Tab Three", value="tab-3"),
            ],
        ),
        html.Div(id="tabs-content-example"),
    ]
)


@app.callback(
    Output("tabs-content-example", "children"), Input("tabs-example", "value")
)
def render_content(tab):
    if tab == "tab-1":
        return config_tab.get_layout()
    elif tab == "tab-2":
        return html.Div([html.H3("Content of Tab Two")])
    elif tab == "tab-3":
        return html.Div([html.H3("Content of Tab Three")])


if __name__ == "__main__":
    app.run_server(debug=True)
