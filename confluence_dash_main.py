import os
import json
from dash import Dash, dcc, html, callback, Input, Output ,dash_table,ctx,State,ALL
import dash
import dash_auth
import json
import credentials as creds

# check if a confluence_config.json file exists.  If not, make a blank one. 
if not os.path.isfile('confluence_config.json'):
    with open('confluence_config.json','w') as fid:
        json.dump([],fid)

credentials = creds.credentials
token       = creds.token

app = Dash(name=__name__,use_pages=True)
auth = dash_auth.BasicAuth(app,credentials)
app.server.secret_key = token


available_interfaces = ["None",'MODBUS over RS-485','Massa RS-485']


app.layout = html.Div(children=[
    html.H1("Confluence Configurator",style={'textAlign':'center'}),
    html.H2("Select Which Interface to Use for this Confluence"),
    dcc.RadioItems(id='Interface-selector',options=available_interfaces,value='None',persistence='True'),
    html.Br(),
    html.Div(children=[
        html.H3('Select an Interface to Configure',style={'textAlign':'center'}),
        html.Div(children=[
            html.Div(
                dcc.Link(
                    dcc.Button(f"{page['name']}",className='button') ,href=page["relative_path"]
                    )
            ) for page in dash.page_registry.values()
        ],className='divHorizontal'),
        dash.page_container])
])

@app.callback(
    # Targets the 'disabled' property of ALL components matching this type
    Output({'type': ALL, 'index': ALL}, 'disabled'),
    Input('Interface-selector', 'value'),
    # We bring in the IDs as State just to know how many elements we need to return a value for
    State({'type': ALL, 'index': ALL}, 'id')
)
def toggle_all_widgets(interface_selected, total_widgets):
    # make a dict of states: 
    states = []
    for i in total_widgets:
        if i['type'] == interface_selected:
            states.append(False)
        else:
            states.append(True)

    return states

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8050,debug=True)