from dash import dcc, html, dependencies
from dash.dependencies import Input, Output, State


class ConfigurationTab:
    def __init__(self, app):
        self.app = app
        self.config = dict()
        self.repair_facility_layout = html.Div(children=[])
        self.layout = html.Div(
            [
                dcc.Input(id="input-text", type="text", placeholder="Enter text here"),
                html.Button("Submit", id="submit-button", n_clicks=0),
                html.Div(id="output-div", children="Hello World"),
                self.get_repair_facility_layout(id=1),
            ]
        )
        self.register_callbacks()

    def register_callbacks(self):
        @self.app.callback(
            Output("output-div", "children"),
            [Input("submit-button", "n_clicks")],
            [State("input-text", "value")],
        )
        def update_output(n_clicks, value):
            if n_clicks > 0:
                return f"You have entered: {value}"
            return ""

    def get_layout(self):
        return self.layout
    

    def get_repair_facility_layout(self, entity):
        self.repair_facility_layout.children = self.recursion(entity)

    def recursion(self, entity):
        for child in self.config.get(entity, []):
            self.repair_facility_layout.children.append(
                html.Details(
                    [
                        html.Summary(f"{entity} {child["id"]}"),
                        html.Div(self.get_repair_facility_layout()),
                    ]
                )
            )
        return layout
            

        layout = html.Details(
            [
                html.Summary(f"Repair Facility {id}"),
                html.Div(
                    [
                        html.Details(
                            [
                                html.Summary("Workspace"),
                                html.Div(
                                    html.Details([html.Summary("Worker"), html.Div()])
                                ),
                            ]
                        ),
                    ]
                ),
            ]
        )
        return layout

    def add_repair_facility(self):
        self.facilities.append(self.get_repair_facility_layout())
        # self.layout.children.append(self.facilities[-1])
