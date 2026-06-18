from dash import html,dcc
import dash
import dash_daq as daq
import dash_ag_grid as dag

def value_display(title,id,**kwargs):

    if 'className' in kwargs: 
        val_disp = html.Div(children=[
        html.Div(children=[
            html.Label(f'{title}:')
        ],style={'display':'flex',
                     'width': '50%',
                     'justifyContent': 'right',
                     "fontWeight": "bold",
                     "marginRight":"10px",
                     'alignItems':'center'}),
        html.Div(children=[
            html.Label(id=id,className=kwargs['className'])
        ],style={'display':'flex',
                     'width': '50%',
                     'justifyContent': 'left',
                     "marginRight":"10px",
                     'alignItems':'center'})
        ],className='divHorizontal')
    else:
        val_disp = html.Div(children=[
            html.Div(children=[
                html.Label(f'{title}:')
            ],style={'display':'flex',
                     'width': '50%',
                     'justifyContent': 'right',
                     "fontWeight": "bold",
                     "marginRight":"10px",
                     'alignItems':'center'}),
            html.Div(children=[
                html.Label(id=id)
            ],style={'display':'flex',
                     'width': '50%',
                     'justifyContent': 'left',
                     "marginRight":"10px",
                     'alignItems':'center'})
        ],className='divHorizontal')

    return val_disp

def table_row(title,value,**kwargs):

    if 'className' in kwargs: 
        val_disp = html.Div(children=[
        html.Div(children=[
            html.Label(f'{title}:')
        ],style={'width': '50%','textAlign': 'right',"fontWeight": "bold","marginRight":"10px",'alignItems':'center'}),
        html.Div(children=[
            html.Label(f'{value}',className=kwargs['className'])
        ],style={'width': '50%','textAlign': 'left'})
        ],className='divHorizontal')
    else:
        val_disp = html.Div(children=[
            html.Div(children=[
                html.Label(f'{title}:')
            ],style={'display':'flex',
                     'width': '50%',
                     'justifyContent': 'right',
                     "fontWeight": "bold",
                     "marginRight":"10px",
                     'alignItems':'center'}),
            html.Div(children=[
                html.Label(f'{value}')
            ],style={'width': '50%','textAlign': 'left','alignItems':'center'})
        ],className='datatable_row')

    return val_disp

def json_table(title,json_dict):
    title_div = html.Div(children=[
        html.Label(title,style={'fontWeight':'bold','fontStyle':'italic'})
    ],style={'marginTop':'10px'})
    div_children = []
    for k in json_dict.keys():
        # print(k)
        div_children.append(table_row(title=k,value=json_dict[k]))

    div = html.Div(children=[
        title_div,
        html.Div(children=div_children,className='datatable_box')],className='divCentered')
    
    return div

def multi_state_image_set(variable,target_value,image_1,image_2):
    if variable == target_value:
        img = image_1
    else:
        img = image_2
    
    return img

def numeric_input(title,id,min,max,**kwargs):
    if "placeholder" in kwargs:
        text = kwargs['placeholder']
    else:
        text = ''

    div = html.Div(children=[
        html.Div(html.Label(f'{title}:'),style={"display":"flex",'width': '50%','justify-content':'right',"fontWeight": "bold","marginRight":"10px","align-items":"center"}),
        html.Div(dcc.Input(id=id,type='number',placeholder=text,debounce=True,min=min,max=max),style={'width': '50%','textAlign': 'left'})
    ],style={'display':'flex','flexDirection':'row'})
    return div

def limit_switch_status(title,id):
    div = html.Div(children=[
        html.Div(children=[
            # html.Label(f'{title}:')
        ],style={"display":"flex",'width': '50%','justify-content':'right',"fontWeight": "bold","marginRight":"10px","align-items":"center"}),
        html.Div(children=[
            html.Label(title,style={'margin':'5px'}),
            daq.Indicator(id=id)
        ],style={'width': '50%',"display":"flex","justify-content":"right","align-items":"bottom"})        
    ],style={'display':'flex','flexDirection':'row'})

    return div

def two_tank_display(title1,title2,id1,id2,min,max,color1,color2):
    div = html.Div(children=[
        html.Div(children=[
            daq.Tank(label=title1,labelPosition='bottom',id=id1,min=min,max=max,showCurrentValue=True,units='mm',color=color1)
        ],style={'width': '50%',"display":"flex","justify-content":"right","align-items":"center","marginTop":"10px"}),
        html.Div(children=[
            daq.Tank(label=title2,labelPosition='bottom',id=id2,min=min,max=max,showCurrentValue=True,units='mm',color=color2)
        ],style={'width': '50%',"display":"flex","justify-content":"right","align-items":"center","marginTop":"10px"})
    ],style={'display':'flex','flexDirection':'row'})

    return div
    
def switch(title,id,initial_state):
    div = html.Div(children=[
        html.Div(children=[
            html.Label(f'{title}:')
        ],style={"display":"flex",'width': '50%','justify-content':'right',"fontWeight": "bold","marginRight":"10px","align-items":"center"}),
        html.Div(children=[
            daq.BooleanSwitch(id=id,on=bool(initial_state))
        ],style={'width': '50%','textAlign': 'left'})
    ],className='divHorizontal')

    return div

def LED_Img_Off_Green(bool_val):
    if bool_val:
        img = html.Img(src=dash.get_asset_url('Green_LED_On.png'),className='indicatorImage')        
    else:
        img = html.Img(src=dash.get_asset_url('LED_Off.png'),className='indicatorImage')
    return img

def LED_Img_Off_Red(bool_val):
    if bool_val:
        img = html.Img(src=dash.get_asset_url('Red_LED_On.png'),className='indicatorImage')        
    else:
        img = html.Img(src=dash.get_asset_url('LED_Off.png'),className='indicatorImage')
    return img

def LED_Img_Red_Green(bool_val):
    if bool_val:
        img = html.Img(src=dash.get_asset_url('Red_LED_On.png'),className='indicatorImage')        
    else:
        img = html.Img(src=dash.get_asset_url('Green_LED_On.png'),className='indicatorImage')
    return img
