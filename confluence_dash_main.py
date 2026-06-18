import os
import json
from dash import Dash, dcc, html, callback, Input, Output ,dash_table,ctx,State
import dash
import dash_auth
import credentials as creds

credentials = creds.credentials
token       = creds.token

app = Dash(name=__name__)#,use_pages=True)
auth = dash_auth.BasicAuth(app,credentials)
app.server.secret_key = token

# List Available Serial Ports
# Look for Linux ports:
stream = os.popen('python -m serial.tools.list_ports "USB"')
output = stream.read()
ports = output.splitlines()

# if we didnt' find any linux ports, try looking for Windows Ports:
if len(ports)<1:
    stream = os.popen('python -m serial.tools.list_ports "COM"')
    output = stream.read()
    ports = output.splitlines()

if len(ports)>=1:
    # clean up the strings in ports array
    for i,p in enumerate(ports):
        ports[i] = p.strip()

if len(ports)<1:
    #we didn't find any ports!
    ports = ['No Available Com Ports']

app.layout = html.Div(children=[
    html.H1("Confluence Configurator",style={'textAlign':'center'}),
    html.Div(children= [
        html.H2("Select Com Port"),
        html.Div(children = [
            dcc.Dropdown(options= ports,id='com-port-selector',style={'width':200,'padding':5}),
            dcc.Button('Refresh',id='com-port-refresh-button')
        ],className='divHorizontal')
    ],className='divBorder')
])


# @callback(Output('com-port-selector','options'))

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8050,debug=True)