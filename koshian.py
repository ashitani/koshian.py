#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Koshian.py(こしあんパイ)

konashi2.0ファームに焼き変えたKoshianをPythonからArduino風に制御する
ライブラリです。

pygattlib: https://bitbucket.org/OscarAcena/pygattlib
に依存します。いまのところubuntu linux 14.04 でしか動作確認していません。

example:

from koshian import *

class myKoshian(Koshian):
    def setup(self):    
        self.pinMode(PIO5, OUTPUT)

    def loop(self):
        self.digitalWrite(PIO5, HIGH)
        delay(1000)
        self.digitalWrite(PIO5, LOW)
        delay(1000)

mac = "00:00:00:00:00:00"
k= myKoshian(mac)
k.run()

"""

KONASHI_VERSION="konashi2.0-f0127f"

from gattlib import GATTRequester, GATTResponse

import time

def find():	
    from gattlib import DiscoveryService

    service = DiscoveryService("hci0") 
    devices = service.discover(2)

    adrs=[]

    for address, name in devices.items():
        if name==KONASHI_VERSION:
            print "found "+ KONASHI_VERSION +", "+address
            adrs.append(address)

    if adrs==[]:
        print KONASHI_VERSION+" device not found"
        exit()

    return adrs[0]


def delay(ms):
    """
    msecオーダでウェイトします。
    """
    time.sleep(0.001*ms)  

# class variable settings..
OUTPUT=1
INPUT=0

HIGH=1
LOW=0

PIO0=0
PIO1=1
PIO2=2
PIO3=3
PIO4=4
PIO5=5
# PIO6,7 is fixed to be I2C on Konashi2.0

AIO0=0
AIO1=1
AIO2=2

ENABLE=1
DISABLE=0

HANDLE = {
"PIO_setting":0x1022,
"PIO_pullup":0x1024,
"PIO_output":0x1026,
"PIO_notification":0x1028,
"PWM_config":0x1032,
"PWM_parameter":0x1034,
"PWM_duty":0x1036,
"ANALOG_drive":0x1042,
"ANALOG_read_0":0x1044,
"ANALOG_read_1":0x1046,
"ANALOG_read_2":0x1048,
"I2C_config":0x1052,
"I2C_start_stop":0x1054,
"I2C_write":0x1056, 
"I2C_read_parameter":0x1058, 
"I2C_read":0x105a, 
"UART_config":0x1062, 
"UART_baud_rate":0x1064, 
"UART_tx":0x1066, 
"UART_rx_notification":0x1068, 
"hardware_reset":0x1072, 
"low_battery_notification":0x1074
}


class Servo:
    """
    ArduinoのServoライブラリもどき
    """
    def __init__(self, koshian):
        self.koshian = koshian
        self.pwmRange = [544,2400]
        self.servoPin = PIO1

    # -------------------------------------------
    #  Servo Functions 
    # -------------------------------------------

    def attach(self, pin, min=544, max=2400):
        self.servoPin=pin
        self.pwmRange = [min,max]
        self.koshian.setPWMmode(self.servoPin,ENABLE)
        self.koshian.writePWMperiod(self.servoPin,20000) # 20msec

    def write(self, angle):
        pwmMin=self.pwmRange[0]
        pwmMax=self.pwmRange[1]
        uS= int(pwmMin + float(angle)/180.0*(pwmMax-pwmMin))
        self.writeMicrosecond(uS)

    def writeMicrosecond(self,uS):
        self.koshian.writePWMduty(self.servoPin,uS)

    def detach(self):
        self.koshian.setPWMmode(self.servoPin,DISABLE)

class Wire:
    """
    ArduinoのWireライブラリもどき。デバッグ中。
    """
    def __init__(self, koshian):
        self.koshian = koshian
        self.I2Caddress = 0;

    # -------------------------------------------
    #  I2C Functions 　PIO6/7 is used
    # -------------------------------------------

    def begin(self,address):
        """
        To be debugged
        """
        self.I2Caddress = (address)
        self.koshian.I2C_config(1)

    def write(self,value):
        self.koshian.I2C_start_stop(1)
        self.koshian.I2C_write(self.I2Caddress,value)
        self.koshian.I2C_start_stop(0)

    def read(self,length):
        self.koshian.I2C_read_parameter(self.I2Caddress,length)
        return self.koshian.I2C_read()

class Serial:
    """
    ArduinoのWireクラスもどき。デバッグ中。
    """

    # -------------------------------------------
    #  UART Functions  TX/RX is used
    # -------------------------------------------
    def __init__(self, koshian):
        self.koshian = koshian

    def begin(self,speed):
        """
        speed: bps(2400/9600 is supported)
        """
        self.koshian.UART_baud_rate(speed)
        self.koshian.UART_config(ENABLE)

    def end(self):
        self.koshian.UART_config(DISABLE)

    def read(self):
        """
        read 1 byte strings
        """
        return self.koshian.UART_rx()

    def flush(self):
        """
        TBD
        """
        pass

    def println(self,data,format):
        """
        TBD
        """
        pass

    def write(self,val):        
        """
        data: max 18bytes strings
        """
        self.koshian.UART_tx(val)

class Koshian:
    """
    Koshian.pyの基本クラス
    """

    def __init__(self,mac=""):
        if mac=="":
            self.mac=find()
        else:
            self.mac=mac
        self.startup()

    def startup(self):
        self.connect()
        delay(500)

        self.pin=0
        self.pin_mode=0
        self.pwm_mode=0  

        #self.hardwareReset()

        # このシーケンスを経ると一発目の入力が正しく機能する（？）
        self.writePinMode(0xFF)
        self.writePIO(0xFF)
        self.writePinMode(0x00)

        self.I2C_read_length = 1

    # -------------------------------------------
    #  Digital I/O Functions 
    # -------------------------------------------
    def pinMode(self,pin,mode):
        """
        PIOを入出力指定します。
        pin: ピン番号。PIO0などのように指定します。
        mode: INPUT/OUTPUT で指定します。
        """
        self.setPWMmode(pin,DISABLE)

        r = self.readPinMode()
        if mode == OUTPUT:
            r|= (1<<pin)&0xFF
        else:
            r&= (~((1<<pin))&0xFF)
        self.writePinMode(r)
   
    def digitalWrite(self,pin,value):
        """
        PIOにデジタル出力します。
        pin: ピン番号。PIO0などのように指定します。
        value: HIGH/LOW で指定します。
        """
        self.setPWMmode(pin,DISABLE)

        if value == HIGH:
            self.pin|= (1<<pin)&0xFF
        else:
            self.pin&= (~((1<<pin))&0xFF)
        self.writePIO(self.pin)
   
    def digitalRead(self,pin):
        """
        PIOからデジタル入力します。
        pin: ピン番号。PIO0などのように指定します。
        戻り値は HIGH/LOW です。
        """
        if (self.pwm_mode & (1<<pin))!=0:
            self.setPWMmode(pin,DISABLE)

        dat = self.readPIO()
        mask = (1<<pin)&0xFF
        if (dat&mask)==0:
            return LOW
        else:
            return HIGH

    # -------------------------------------------
    #  Analog I/O Functions 
    # -------------------------------------------

    def analogRead(self,pin):
        """
        AIOからデジタル入力します。
        pin: ピン番号。AIO0などのように指定します。
        戻り値は mV単位です
        """
        return self.ANALOG_read(pin)

    def analogWrite(self,pin,value):
        """
        DACは未対応のようなので、PWMのみです。
        pin: PIO0,1,2のみ。
        value: 0-255
        value/255*VCC が出力されます。
        """
        self.setPWMmode(pin,ENABLE)
        self.writePWMperiod(pin,255*20)
        self.writePWMduty(pin,value*20)

    # -------------------------------------------
    #  Others
    # -------------------------------------------

    
    # -------------------------------------------
    #  PWM Functions 
    # -------------------------------------------
    def setPWMmode(self,pin,mode):
        """
        pin: PIO0,1,2を指定。
        mode: ENABLE/DISABLE
        """
        new_mode=self.pwm_mode
        if mode == ENABLE:
            new_mode|= (1<<pin)&0xFF
        else:
            new_mode&= (~((1<<pin))&0xFF)
        if new_mode!=self.pwm_mode:
            self.writePWMmode(new_mode)

    # -------------------------------------------
    #  konashi PIO functions
    # -------------------------------------------

    def writePinMode(self,value):
        """
        value
        bit0-5: PIO0-5
        0: INPUT
        1: OUTPUT
        """
        return self.write_command("PIO_setting",[value])

    def readPinMode(self):
        return self.read_command("PIO_setting")
 
    def writePIOpullup(self,value):
        """
        value
        bit0-5: PIO0-5
        0: DISABLE
        1: ENABLE
        """
        return self.write_command("PIO_pullup",[value])

    def readPIOpullup(self):
        return self.read_command("PIO_pullup")

    def writePIO(self,value):
        """
        value
        bit0-5: PIO0-5
        0: LOW
        1: HIGH
        """
        return self.write_command("PIO_output",[value])

    def readPIO(self):
        return self.read_command("PIO_notification")


    # -------------------------------------------
    #  konashi Analog IO functions
    # -------------------------------------------

    #def ANALOG_drive(self,pin):
    
    def ANALOG_read(self,pin):
        handle_string=""
        if pin==AIO0:
            handle_string = "ANALOG_read_0"
        elif pin==AIO1:
            handle_string = "ANALOG_read_1"
        elif pin==AIO2:
            handle_string = "ANALOG_read_2"

        dat=self.read_async_command(handle_string,length=2)

        adat= (dat[0]<<8) + dat[1]

        return adat

    # -------------------------------------------
    #  konashi UART functions
    # -------------------------------------------

    def UART_config(self,mode):
        """
        mode
        0: UART DISABLE
        1: UART ENABLE
        """
        self.write_command("UART_config",[mode])

    def UART_baud_rate(self,bit_rate):
        """
        bit_rate: bps(2400/9600 is supported)
        """
        dat=[0,0]
        bit_rate/=240
        dat[0] = (bit_rate&0xFF00)>>8
        dat[1] = (bit_rate&0x00FF)
        self.write_command("UART_baud_rate",dat)

    def UART_tx(self,data):
        """
        data: max 18bytes strings
        """
        dat=(map(lambda n:ord(n),data))
        self.write_command("UART_tx",dat)

    def UART_rx(self):
        """
        read 1 byte strings
        """
        return chr(self.read_command("UART_rx",dat)[0])

    # -------------------------------------------
    #  konashi I2C functions
    # -------------------------------------------

    def I2C_config(self,mode):
        """
        mode
        0: I2C DISABLE
        1: I2C ENABLE(100kHz)
        2: I2C ENABLE(400kHz)
        """
        self.write_command("I2C_config",[mode])

    def I2C_start_stop(self,mode):
        """
        mode
        0: STOP CONDITION
        1: START CONDITION
        2: REPEATED START CONDITION
        """
        self.write_command("I2C_start_stop",[mode])

    def I2C_write(self, slave_address, data):
        """
        slave_address: I2C slave address(8bit)
        data: data array (max 16 bytes)
        """
        dat = [0] *2
        dat[0] = len(data)+2
        dat[1] = (slave_address <<1)&0xfe
        if isinstance(data,list):
            dat+=data
        if isinstance(data,str):
            dat+=map(lambda n:ord(n), data)

        self.write_command("I2C_write",dat)

    def I2C_read_parameter(self,slave_address, length):
        """
        Send Read Request
        slave_address: I2C slave address(7bit)
        """
        self.I2C_read_length = length
        dat = [0] *2
        dat[0] = self.I2C_read_length
        dat[1] = (slave_address <<1)|0x01
        self.write_command("I2C_read_parameter",dat)

    def I2C_read(self):
        return self.read_async_command("I2C_read",length=self.I2C_read_length)
        
    # -------------------------------------------
    #  konashi PWM functions
    # -------------------------------------------

    def readPWMmode(self):
        return self.read_command("PWM_config")

    def writePWMmode(self,mode):
        self.mode=mode
        self.write_command("PWM_config",[self.mode])

    def writePWMperiod(self,pin,period):
        """
        period: 1000-20480[usec]
        """
        param=[pin,0,0,0,0]
        param[1] = (period & 0xFF000000)>>24
        param[2] = (period & 0x00FF0000)>>16
        param[3] = (period & 0x0000FF00)>>8
        param[4] = (period & 0x000000FF)
        self.write_command("PWM_parameter",param)

    def writePWMduty(self,pin,duty):
        param=[pin,0,0,0,0]
        param[1] = (duty & 0xFF000000)>>24
        param[2] = (duty & 0x00FF0000)>>16
        param[3] = (duty & 0x0000FF00)>>8
        param[4] = (duty & 0x000000FF)
        self.write_command("PWM_duty",param)

    # -------------------------------------------
    #  konashi other functions
    # -------------------------------------------
    def hardwareReset(self):
        self.write_command("hardware_reset",[0xff])


    # -------------------------------------------
    #  Bluetooth functions (depend on pygattlib)
    # -------------------------------------------
    def connect(self):
        self.req = GATTRequester(self.mac)

    def write_command(self, handle_id, parameter):
        """
        parameter: 配列
        """
        handle = HANDLE[handle_id]
        self.req.write_by_handle(handle, str(bytearray(parameter)))

    def read_async_command(self,handle_id,length=1):
        """
        1バイトリードのときはintで、
        2バイト以上リードするときは配列で返します。
        """
        response = GATTResponse()
        handle = HANDLE[handle_id]
        self.req.read_by_handle_async(handle, response)
        while not response.received():
            time.sleep(0.1)
        ans = response.received()[0]
        ans = map(lambda n:ord(n), ans)
        if length==1:
            return ans[0]
        else:
            return ans

    def read_command(self, handle_id, length=1):
        """
        同期リード。
        1バイトリードのときはintで、
        2バイト以上リードするときは配列で返します。
        """
        handle = HANDLE[handle_id]
        ans=self.req.read_by_handle(handle)[0]
        ans=map(lambda n:ord(n), ans)
        if length==1:
            return ans[0]
        else:
            return ans

    # -------------------------------------------
    #  Main Routine
    # -------------------------------------------

    def setup(self):
        pass

    def loop(self):
        pass

    def run(self):
        self.setup()
        while 1:
            self.loop()


if __name__ == '__main__':

    class myKoshian(Koshian):
        def setup(self):    
            # s = Servo(self)
            # s.attach(PIO1)
            # s.write(45)

            #self.analogWrite(PIO1,128)

            # self.pinMode(PIO0, INPUT)
            # self.pinMode(PIO1, INPUT)
            # self.pinMode(PIO2, INPUT)
            # self.pinMode(PIO3, INPUT)
            # self.pinMode(PIO4, INPUT)
            # self.pinMode(PIO5, INPUT)

            # self.pinMode(PIO1, OUTPUT)
            # self.pinMode(PIO2, OUTPUT)
            # self.pinMode(PIO5, OUTPUT)

            # self.digitalWrite(PIO1, HIGH)
            # self.digitalWrite(PIO2, HIGH)
            # self.digitalWrite(PIO5, HIGH)

            self.I2C_config(1)

        def loop(self):
            print "loop"
#             self.I2C_start_stop(1)
# #            self.I2C_write(4,"hello")
#             self.I2C_write(4,[1,2,3])
#             self.I2C_start_stop(0)
            self.I2C_read_parameter(4,1)
            print self.I2C_read()
            delay(100)

    k=myKoshian()
    k.run()



