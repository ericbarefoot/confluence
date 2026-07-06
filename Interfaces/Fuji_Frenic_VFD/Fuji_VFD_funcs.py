import time
from tkinter import E
import minimalmodbus
import json

class VFD():
    def __init__(self,comm_port,server_id,baudrate,bytesize,parity,stopbits,timeout):
        try: 
            self.comm = minimalmodbus.Instrument(comm_port, server_id, baudrate,bytesize,parity,stopbits, debug=False) 
            self.comm.serial.timeout = timeout   # seconds
            self.comm.mode = minimalmodbus.MODE_RTU   # rtu or ascii mode
            self.comm_status  = 'VFD Com Port Found: '+comm_port
        except Exception as e:
            print(e)
            self.comm_status = 'VFD Com Port Not Found: '+comm_port
            self.comm = ''

        self.comm_errors = 0
        self.analog_input = [float('nan'),float('nan')]

        self.alarm_codes = {0: 'No Alarm',
              1: 'OverCurrent During Acceleration',
              2: 'OverCurrent During Deceleration',
              3: 'OverCurrent During Constant Speed Operation',
              5: 'Ground Fault',
              6: 'OverVoltage During Acceleration',
              7: 'OverVoltage During Decceleration',
              8: 'OverVoltage During Constant Speed Operation or Stopping',
              10: 'Undervoltage',
              11: 'Input Phase Loss',
              14: 'Fuse Blown',
              16: 'Charing Circuit Fault',
              17: 'Heat Sink Overheat',
              18: 'External Alarm (E-Stop)',
              19: 'Internal Air Overheat',
              20: 'Motor Protection (PTC/NTC Thermistor)',
              22: 'Breaking Resistor Overheat',
              23: 'Motor OverLoad',
              24: 'Motor Overload, Motor 2',
              25: 'Inverter Overload',
              27: 'OverSpeed Protection',
              28: 'PG Disconnection',
              29: 'NTC Disconnection Error',
              31: 'Memory Error',
              32: 'Keypad Communications Error',
              33: 'CPU error',
              34: 'Option Communications Error',
              35: 'Option Error',
              36: 'Run Operation Error',
              37: 'Tuning Error',
              38: 'RS-485 Communications Error',
              44: 'Motor Over Load (Motor 3)',
              45: 'Motor OverLoad (motor 4)',
              46: 'Output Phaseloss',
              47: 'Folling Error: Excessive Speed Deviation',
              51: 'Data Save Error on insufficient voltage',
              53: 'RS-485 communications error (Option/Communications port2)',
              54: 'Hardware Error',
              57: 'EN Circuit Error',
              58: 'PID Feedback Disconnection Detected',
              59: 'DB Transistor Trounle',
              100: 'DC fan lock detected',
              101: 'Motor Overload Warning',
              102: 'Cooling Fin Overheat Warning',
              103: 'Life Warning',
              104: 'Command Loss',
              105: 'PID warning ouput',
              106: 'Low Torque Detected',
              108: 'Machine Life (accumulated operation hours)',
              109: 'Machine Life (Number of starting times)',
              254: 'Simulated Error'}


    def poll_state(self):
        try: 
            state_message_word = format(self.comm.read_register(2062,0,3),'016b')
            motor_alarm = int(state_message_word[4])
            motor_fwd =   int(state_message_word[15])
            motor_rev =   int(state_message_word[14])
            motor_acel =  int(state_message_word[6])
            motor_decel=  int(state_message_word[5])

            # print(state_message_word)

            if int(motor_alarm) >0: 
                alarm_code = self.comm.read_register(2064,0,3)
                # print('Alarm on '+motor_names[motor_comm_obj.address]+' VFD: '+alarm_codes[int(alarm_code)])
            else:
                alarm_code = 0

            if motor_alarm >0 and alarm_code ==18:
                self.e_stop =1
            else:
                self.e_stop=0

            if motor_fwd:
                self.state_message = 'motor On - Forward'
            elif motor_rev:
                self.state_message = 'motor On - Reverse'
            elif motor_acel:
                self.state_message = 'motor Acceleration'
            elif motor_decel:
                self.state_message = 'motor Decelerating'
            elif motor_alarm:
                self.state_message = self.alarm_codes[int(alarm_code)]
            else:
                self.state_message = 'motor Stopped'

            

        except Exception as e:
            print(e)
            self.comm_errors = self.comm_errors + 1
            self.e_stop = 0
            self.state_message = 'Error getting status'


    def poll_setpoint(self):
        try:
            self.setpoint = self.comm.read_register(2053,2,3)
        except Exception as e:
            print(e)
            self.comm_errors = self.comm_errors + 1
            self.setpoint = float('nan')

    def send_setpoint(self,setpoint):
        try:
            self.comm.write_register(1797,value=float(setpoint),number_of_decimals=2)
        except Exception as e:
            # print(e)
            self.comm_errors = self.comm_errors + 1

    def start_motor(self):
        start_command = int(b'0000000000000001',2)
        try:
            self.comm.write_register(1798,start_command,0)
        except Exception as e:
            self.comm_errors = self.comm_errors + 1
            print(e)

    def stop_motor(self):
        stop_command = int(b'0000000000000000',2)
        try:
            self.comm.write_register(1798,stop_command,0)
        except Exception as e:
            print(e)
            self.comm_errors = self.comm_errors + 1

    def clear_faults(self):
        # self.comm.write_bit(2,1,functioncode=5)
        try:
            command = int(b'1000000000000000',2)
            self.comm.write_register(1798,command,0)
            time.sleep(0.1)
            command = int(b'0000000000000000',2)
            self.comm.write_register(1798,command,0)
        except Exception as e:
            print(e)
        # self.comm.write_bit(2,1,functioncode=5)
   
    def poll_status(self):
        self.poll_state()
        self.poll_setpoint()

        self.status = {
            "com errors":self.comm_errors,
            "state":self.state_message,
            "freq setpoint":self.setpoint
        }


if __name__ == '__main__':
    fuji_vfd = VFD('COM17',1)

    setpoint = float(input('Enter Freq Setpoint: '))

    fuji_vfd.send_setpoint(setpoint)

    input('Press Enter to Start Motor')
    fuji_vfd.start_motor()

    try:
        while True:
            fuji_vfd.poll_status()
            print(f'Status: {fuji_vfd.state_message}')
            print(f'Setpoint: {fuji_vfd.setpoint}')
            time.sleep(1)
            # jets_s.clear_faults()
            # time.sleep(0.5)
    except KeyboardInterrupt:
        print('Stopping')
        fuji_vfd.stop_motor()
