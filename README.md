# confluence
A library of code to convert signals (analog, serial, modbus, etc.) to MQTT that can be integrated into the Sandpiper ecosystem. 

## Network Topology
```
                                                                                                         
                                                                                                         
  ┌──────────┐                                                    ┌───────────────────────────┐          
  │ Sensor 1 ┼─────────┐      ┌───────────────────┐               │       MQTT Broker         │          
  └──────────┘   RS485 └─────►│ Confluence Node   │     TCP       │                           │          
                              │                   ├◄─────────────►│   Raspberry Pi running    │          
  ┌──────────┐         ┌─────►│ (Raspberry Pi)    │               │    Eclipse Mosquitto      │          
  │ Sensor 2 ┼─────────┘      └───────────────────┘               └────▲───────────────▲──────┘          
  └──────────┘ Modbus RS485                                            │               │                 
                                                                       │TCP            │TCP              
                                                                   ┌───┘               └───┐             
                                                                   │                       │             
                                                            ┌──────▼───────┐   ┌───────────▼──────────┐  
                                                            │ User Device  │   │  Additional          │  
                                                            │  HMI / GUI   │   │  Control/Measurement │  
                                                            │              │   │  (PLC, etc)          │  
                                                            └──────────────┘   └──────────────────────┘  
                                                                                                         

```
