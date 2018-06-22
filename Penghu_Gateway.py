#coding:utf-8
import serial
import time
import threading
import MySQLdb
import os

ser = serial.Serial(port = '/dev/ttyUSB0', baudrate = 9600)

def ReceiveData():
   global DecRFData
   while True:
       try:
           print 'Receiving data ... '
           packet_FirstData = ser.read()
           RowData = ''
           Check_value = 0
           if  packet_FirstData == '\x7E' :
               packetLength = int((ser.read() + ser.read()).encode('hex'),16)
               for i in range(0,packetLength):
                   Remain_packet= ser.read()                    
                   RowData += Remain_packet                
                   Check_value += int(Remain_packet.encode('hex'),16)
               CheckSum = ser.read()
               if (0xFF - (Check_value & 0xFF)) == int(CheckSum.encode('hex'),16):
                   HexRowData = RowData.encode('hex')
                   FrameType =  HexRowData[0:2]
                   Address64 = HexRowData[12:18]
                   Address16 = HexRowData[18:22]
                   ReceOption = HexRowData[22:24]
                   HexRFData = HexRowData[24:len(HexRowData)]
                   DecRFData = HexToDec(Address64, HexRFData)
                   return DecRFData
               else:
                   DecRFData = ['0','0','0','0','0','0','0','0','0']
                   print 'decode failed'
                   return DecRFData
       except IOError as e:
           print e
           

def HexToDec(Address64,HexRFData):
    nodeID = Address64
    packetIndex = int(HexRFData[0:4],16)
    airTemp = int(HexRFData[4:8],16)/100.0
    airIllumination = int(HexRFData[8:12],16)
    airHumidity = int(HexRFData[12:16],16)/100.0
    soilTemp = int(HexRFData[16:20],16)/100.0
    soilHumidity = int(HexRFData[20:24],16)
    soilConductivity = int(HexRFData[24:28],16)
    soilPH = int(HexRFData[28:32],16)/100.0

    return [nodeID, packetIndex, airTemp, airIllumination, airHumidity, soilTemp, soilHumidity, soilConductivity, soilPH]

def ToBackEnd(receivetime,data): 
    try:
        db = MySQLdb.connect(host="140.112.xxx.xxx", user="username", passwd="password", db="database", port=port)
        cursor = db.cursor()
        sql = "INSERT INTO PengHu(Time, nodeID, packetIndex, airTemp, airIllumination, airHumidity, soilTemp, soilHumidity, soilConductivity, soilPH) VALUES ('%s' ,'%s' ,'%s' ,'%s','%s','%s','%s' ,'%s' ,'%s' ,'%s')" %\
              (receivetime, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8])
        cursor.execute(sql)
        db.commit()
        print 'Insert data successful...'
        return True
    except:
        print 'Fail to insert data...'
        return False
    db.close()

def CheckConnect():
    try:
        response = urllib2.urlopen('http://140.112.94.126',timeout = 4)
        print 'Network connect successful...'
        LogData('Network connect successful...','Status.txt')
        time.sleep(1)
        return True
    except:
        print 'Network connect fail... '
        LogData('Network connect fail... ','Status.txt')
        time.sleep(1)
        return False

def LogData(day,receivetime,DecRFData,filename):
    if os.path.exists('//home//pi//Documents//Penghu_Gateway//'+day):
        files = file('//home//pi//Documents//Penghu_Gateway//'+day+'//'+filename,'a')
        files.write(receivetime+' '+DecRFData+'\r\n')
        files.close()
    else:
        os.mkdir('//home//pi//Documents//Penghu_Gateway//'+day)
        files = file('//home//pi//Documents//Penghu_Gateway//'+day+'//'+filename,'a')
        files.write(receivetime+' '+DecRFData+'\r\n')        
    files.close()

if __name__ == '__main__':
    while True:
        
        try:
            day = time.strftime('%Y-%m-%d',time.localtime(time.time()))
            receivetime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            DecRFData = ReceiveData()
            # ToBackEnd(receivetime, DecRFData)
            # LogData(day, receivetime, DecRFData,'logdata')
            # global DecData
            # DecData = [0,0]
            print "airTemp:" + str(DecRFData[2])
            if DecRFData[2] > 25:
                ser.write('\x7E\x00\x10\x17\x01\x00\x13\xA2\x00\x41\x50\x94\xE5\xFF\xFE\x02\x44\x30\x05\xB0')
            else:
                ser.write('\x7E\x00\x10\x17\x01\x00\x13\xA2\x00\x41\x50\x94\xE5\xFF\xFE\x02\x44\x30\x04\xB1')
                
                   
        except Exception as e:
            #print e
            print 'Sensor node is still working....' 
        

