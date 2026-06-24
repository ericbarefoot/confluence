from dash import Dash, dcc, html, callback, Input, Output ,dash_table,ctx,State,ALL
import dash
import os
import json
import SAFL_Dash_Toolbox as safl

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

try:
    with open('confluence_config.json', 'r') as file:
        settings_json = json.load(file)
except:
    print('JSON File is empty or not found')
    settings_json = {}

dash.register_page(__name__,path='/')

if 'MODBUS over RS-485' in settings_json.keys():
    if 'publish' in settings_json['MODBUS over RS-485'].keys():
        publish_table = safl.json_table(title="Registers to Publish",json_dict=settings_json['MODBUS over RS-485']['publish'])

layout = html.Div(children=[
    html.Div(children= [
        html.H2("MODBUS over RS-485"),
        html.H3("Select Com Port"),
        html.Div(children = [
            dcc.Dropdown(options= ports,id={'interface':'MODBUS over RS-485','settings':'comms','index':'com port'},style={'width':200,'padding':5},persistence=True,value=ports[0]),
            dcc.Button('Refresh',id={'interface':'MODBUS over RS-485','index':'com-port-refresh-button'})
        ],className='divHorizontal'),
        html.H3("Baudrate"),
        dcc.Dropdown(id={'interface':'MODBUS over RS-485','settings':'comms','index':'baudrate'},options=baudrates,value=9600,persistence=True),
        html.H3("Bits"),
        dcc.Dropdown(id={'interface':'MODBUS over RS-485','settings':'comms','index':'bits'},options=bits,value=8,persistence=True),
        html.H3("Parity"),
        dcc.Dropdown(id={'interface':'MODBUS over RS-485','settings':'comms','index':'parity'},options=parity,value='N',persistence=True),
        html.H3("Stop Bits"),
        dcc.Dropdown(id={'interface':'MODBUS over RS-485','settings':'comms','index':'stopbits'},options=stop_bits,value=1,persistence=True),
        html.H3("Server ID"),
        dcc.Input(id = {'interface':'MODBUS over RS-485','settings':'comms','index':'serverID'},type='number',debounce=True,value=1,min=1,persistence=True),
        html.Br(),
        dcc.Button("Write Changes",id = {'interface':'MODBUS over RS-485','settings':'comms','index':'write-modbusRS485-changes'})

    ],className='divBorder'),
    html.Div(children=[
        html.H2("Publish"),
        html.Div(id="Registers to Publish",children=publish_table),
        html.H3("Add a Register to the Publication List"),
        dcc.Input(id = {'interface':'MODBUS over RS-485','settings':'publish','index':'new_publish_topic'},debounce=True,type='text'),
        dcc.Input(id={'interface':'MODBUS over RS-485','settings':'publish','index':'new_publish_reg'},debounce=True,type='number'),
        dcc.Button("Add Publication",id={'interface':'MODBUS over RS-485','settings':'publish','index':'add_new_publication'})
    ],className='divBorder')
])

 

# Update the Comms portion of the Modbus RS-485 configuration
@callback(Input({'interface':'MODBUS over RS-485','settings':'comms','index':'write-modbusRS485-changes'},'n_clicks'),
          State({'interface': 'MODBUS over RS-485','settings':'comms', 'index': ALL},'id'),
          State({'interface': 'MODBUS over RS-485','settings':'comms', 'index': ALL}, 'value'))

def write_modbusRS485_changes(n,widget_ids,widget_values):
    # Load the existing config into a dict
    print(widget_values)
    try:
        with open('confluence_config.json', 'r') as file:
            settings_json = json.load(file)
    except:
        print('JSON File is empty or not found')
        settings_json = {}
        settings_json[widget_ids[0]['interface']] = {}

    settings_json[widget_ids[0]['interface']][widget_ids[0]['settings']] = {}

    for i, obj in enumerate(widget_ids):
        if widget_values[i] != None:
            settings_json[obj['interface']][obj['settings']][obj['index']] = widget_values[i]

    with open("confluence_config.json", "w") as json_file:
        json.dump(settings_json, json_file,indent=4)

@callback(Output("Registers to Publish",'children'),
          Input({'interface':'MODBUS over RS-485','settings':'publish','index':'add_new_publication'},'n_clicks'),
          State({'interface': 'MODBUS over RS-485','settings':'publish', 'index': ALL},'value'),
          prevent_initial_call=True)

def Update_Publication_List(n,widget_values):
    settings_json['MODBUS over RS-485']['publish'][widget_values[0]] = widget_values[1]

    with open("confluence_config.json", "w") as json_file:
        json.dump(settings_json, json_file,indent=4)

    if 'MODBUS over RS-485' in settings_json.keys():
        if 'publish' in settings_json['MODBUS over RS-485'].keys():
            publish_table = safl.json_table(title="Registers to Publish",json_dict=settings_json['MODBUS over RS-485']['publish'])

    return publish_table