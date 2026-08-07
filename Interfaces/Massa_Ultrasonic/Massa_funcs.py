import serial
import struct
import time
import numpy as np
import datetime

class massa():
    def __init__(self,comm_port,ids,names,offset_array):
        self.ids = ids # array of massa id numbers
        self.names = names
        self.offsets = offset_array
        self.comm_errors = [0]*len(self.ids)
        # self.stop_signal = stop_signal

        try:
            self.comm = serial.Serial(comm_port,baudrate=19200,timeout=0.2,bytesize=8,parity='N',stopbits=1)
        except Exception as e:
            print(f'Unable to open Massa Com Port: {comm_port}')
            print(e)

    def poll_status(self):

        self.massa_id_array = []
        self.error_array    = []
        self.dist_mm_array  = []
        self.target_array   = []
        self.strength_array = []
        self.massa_temperature_array = []
        self.water_depth_array = []


        for i in range(len(self.ids)):
            # print(f'Polling Massa with ID: {self.ids[i]}')
            # Format the message to request the status from the Massa
            message=[170, int(self.ids[i]), 3, 0, 0, (170+int(self.ids[i])+3+0+0) % 256]
            b=bytes(message)

            # Send the message and read the response
            try:
                # print(i)
                self.comm.write(b)
                # self.comm.flush()
                res=self.comm.read(6)
                
                if len(res) < 6:
                    self.comm_errors[i] += 1

                #print(f'Massa Response:{len(res)}')
                # Parse the response
                massa_id=res[0]  # Massa ID number

                dist_data=bytearray([res[2], res[3]])  # Massa Distance in two Bytes
                dist_int=struct.unpack(
                    '<H', dist_data)  # Conver the distance to an unsigned int\
                dist=dist_int[0]/128  # Convert from unsigned int to distance in inches
                dist_mm=dist*25.4  # Convert from inches to mm
                # print(f'Distance Measurement for Massa with ID={self.ids[i]} :{dist_mm:.2f} cm')

                # Internal temperature of the Massa
                massa_temperature=res[4]*0.48876-50

                # Parse Diagnostics
                diag='{0:08b}'.format(res[1])
                err=diag[7]
                error_key={'0': 'OK', '1': 'Error'}
                error=error_key[err]

                target_detected=diag[4]
                target_detected_key={'0': 'No', '1': 'Yes'}
                target=target_detected_key[target_detected]

                strength_binary=diag[0:4]
                strength_key={'0000': '0%', '0001': '25%',
                    '0010': '50%', '0011': '75%', '0100': '100%'}
                strength = strength_key[strength_binary]

                # Validate Massa Measurements
                if target_detected == '0':
                    dist_mm = float('nan')

                # Compute the depth of the water:
                self.water_depth_array.append(round(self.offsets[i]-dist_mm,2))
                

                ## Add measurements to arrays                
                self.massa_id_array.append(massa_id)
                self.error_array.append(error)
                self.dist_mm_array.append(round(dist_mm,2))
                self.target_array.append(target)
                self.strength_array.append(strength)
                self.massa_temperature_array.append(round(massa_temperature,1))
                
                
                time.sleep(0.05)
            
            except Exception as e:
                #raise(e)
                print(f'Massa Read Error: {e}')
                self.massa_id_array =           [float('nan')]*len(self.ids)
                self.error_array    =           [float('nan')]*len(self.ids)
                self.dist_mm_array  =           [float('nan')]*len(self.ids)
                self.target_array   =           [float('nan')]*len(self.ids)
                self.strength_array =           [float('nan')]*len(self.ids)
                self.massa_temperature_array =  [float('nan')]*len(self.ids)
                self.water_depth_array =        [float('nan')]*len(self.ids)

            self.status = {"timestamp":datetime.datetime.now().isoformat(timespec='milliseconds'),
                      "device names":self.names,
                      "massa IDs":self.massa_id_array,
                      "errors": self.error_array,
                      "dist_mm": self.dist_mm_array,
                      "signal_strength":self.strength_array,
                      "target acquired":self.target_array,
                      "massa temperature":self.massa_temperature_array,
                      "offsets":self.offsets,
                      "water_depth":self.water_depth_array
                      }
            # return status
            
    def update_offset(self,massa_id,new_offset):
        ids = np.array(self.ids)
        idx = np.where(ids==massa_id)[0].item()

        self.offsets[idx] = new_offset          



if __name__ == '__main__':
    # import time
    
    massas = massa('COM3',ids=[1],offset_array=[0])

    try:
        while True:
                    
            massas.poll_status()

            print(f'Massa Distance Array: {massas.dist_mm_array}')
            print(f'Massa Signal Strengths: {massas.strength_array}')

            # print(f'Distance: {massa_1.dist_mm[0]} cm')
            # print(f'Target Detected: {massa_1.target[0]}')
            # print(f'Massa Temperature: {massa_1.massa_temperature[0]} degC')
            # print(f'Signal Strength: {massa_1.strength[0]}\n\n')

            time.sleep(0.5)
    except KeyboardInterrupt:
        print('Stopping')
