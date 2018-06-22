// author: Yu-Lun Chiang      //
// date  : 2018.06.14         //
// goal  : Embedding system   //

#include <XBee.h>
#include "DHT.h"

/////XBee_SETUP/////
XBee xbee = XBee();
XBeeAddress64 remoteAddress = XBeeAddress64(0x00000000, 0x0000ffff);
int packetIndex = 0;

/////(airTemp/airHumidity)DHT22_SETUP/////
#define DHTPIN 9
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);
double airTemp = 0.0;
double airHumidity = 0.0;
int airTempShift = 0;
int airHumidityShift = 0;

/////(airIllumination)PhotoResistance/////
#define PRPIN A1
int airIllumination = 0;

/////(soilTemp)LM35_SETUP/////
#define LM35PIN A0
double soilTemp = 0.0;
int soilTempShift = 0;

/////(soilHumidity)SEN0193/////
#define SEN0193PIN A4
int soilHumidity = 0;

/////(soilConductivity)EC10_SETUP/////
#define EC10PIN A2
int soilCond = 0;

/////(soilPH)SEN161_SETUP/////
#define SEN161PIN A3
double soilPH = 0.0;
int soilPHShift = 0;


void setup(){
  Serial.begin(9600);
  xbee.begin(Serial);
  dht.begin();
}

void loop(){
  
  air_DHT22();
  air_PR();  
  soil_LM35();
  soil_SEN0193();
  soil_EC10();
  soil_SEN161();
  
  // packetIndex //
  packetIndex++;
  if(packetIndex > 65535) packetIndex = 1;

  XBeeSendPacket();
  delay(2000);
}

void air_DHT22(){
  airTemp = dht.readTemperature();
  airTempShift = airTemp*100;
  airHumidity = dht.readHumidity();
  airHumidityShift = airHumidity*100;

}

void air_PR(){
  airIllumination = analogRead(PRPIN);
}

void soil_LM35(){
  soilTemp = analogRead(LM35PIN)*(500.0/1023.0);
  soilTempShift = soilTemp*100;
}

void soil_EC10(){
  soilCond = analogRead(EC10PIN)*(5.0/1023.0)*2500;
}

void soil_SEN0193(){
  soilHumidity = analogRead(SEN0193PIN);
}

void soil_SEN161(){
  soilPH = analogRead(SEN161PIN)*(14.0/1023.0);
  soilPHShift = soilPH*100;
}

// XBeeSendPacket_Public_Function //
void XBeeSendPacket(){
   uint8_t text[] = {packetIndex>>8, packetIndex,\
   airTempShift>>8, airTempShift,\
   airIllumination>>8, airIllumination,\ 
   airHumidityShift>>8, airHumidityShift,\
   soilTempShift>>8, soilTempShift,\ 
   soilHumidity>>8, soilHumidity,\
   soilCond>>8, soilCond,\
   soilPHShift>>8, soilPHShift};

  ZBTxRequest zbTx = ZBTxRequest(remoteAddress,text, sizeof(text));
  zbTx.setAddress16(0xfffe);
  xbee.send(zbTx);  
}