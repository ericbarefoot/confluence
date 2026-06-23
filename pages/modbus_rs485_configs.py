from dash import Dash, dcc, html, callback, Input, Output ,dash_table,ctx,State,ALL
import dash
import os
import json

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

baudrates = [9600,19200,38400,57600,115200]
bits = [8,7]
parity = ['N','E','O']
stop_bits = [0,1,2]

dash.register_page(__name__)

# time.sleep(1)

layout =html.Div(children= [
        html.H2("MODBUS over RS-485"),
        html.H3("Select Com Port"),
        html.Div(children = [
            dcc.Dropdown(options= ports,id={'type':'MODBUS over RS-485','index':'com port'},style={'width':200,'padding':5},persistence=True,value=ports[0]),
            dcc.Button('Refresh',id={'type':'MODBUS over RS-485','index':'com-port-refresh-button'})
        ],className='divHorizontal'),
        html.H3("Baudrate"),
        dcc.Dropdown(id={'type':'MODBUS over RS-485','index':'baudrate'},options=baudrates,value=9600,persistence=True),
        html.H3("Bits"),
        dcc.Dropdown(id={'type':'MODBUS over RS-485','index':'bits'},options=bits,value=8,persistence=True),
        html.H3("Parity"),
        dcc.Dropdown(id={'type':'MODBUS over RS-485','index':'parity'},options=parity,value='N',persistence=True),
        html.H3("Stop Bits"),
        dcc.Dropdown(id={'type':'MODBUS over RS-485','index':'stopbits'},options=stop_bits,value=1,persistence=True),
        html.H3("Server ID"),
        dcc.Input(id = {'type':'MODBUS over RS-485','index':'serverID'},type='number',debounce=True,value=1,min=1,persistence=True),
        html.Br(),
        dcc.Button("Write Changes",id = {'type':'MODBUS over RS-485','index':'write-modbusRS485-changes'})

    ],className='divBorder')

 
@callback(Input({'type':'MODBUS over RS-485','index':'write-modbusRS485-changes'},'n_clicks'),
          State({'type': 'MODBUS over RS-485', 'index': ALL},'id'),
          State({'type': 'MODBUS over RS-485', 'index': ALL}, 'value'))

def write_modbusRS485_changes(n,widget_ids,widget_values):
    # Load the existing config into a dict
    print(widget_values)
    try:
        with open('confluence_config.json', 'r') as file:
            settings_json = json.load(file)
    except:
        print('JSON File is empty or not found')
        settings_json = {}

    settings_json[widget_ids[0]['type']] = {}

    for i, obj in enumerate(widget_ids):
        if widget_values[i] != None:
            settings_json[obj['type']][obj['index']] = widget_values[i]

    with open("confluence_config.json", "w") as json_file:
        json.dump(settings_json, json_file)

