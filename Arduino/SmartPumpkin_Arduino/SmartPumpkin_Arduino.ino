#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"

#define TRIG 2
#define ECHO 3
#define LIMT_INF 45
#define LIMT_SUP 120

#define CH 0x53
#define SLLEPCYCLE 6
//for nrf24 debug
/*
int serial_putc( char c, FILE * ) 
{
  Serial.write( c );
  return c;
} 

//for nrf24 debug
void printf_begin(void)
{
  fdevopen( &serial_putc, 0 );
}
*/
//nRF24 set the pin 9 to CE and 10 to CSN/SS
// Cables are:
//     SS       -> 10
//     MOSI     -> 11
//     MISO     -> 12
//     SCK      -> 13

RF24 radio(9,10);
char SendPayload[31] ="1";


//we only need a write pipe, but am planning to use it later
const uint64_t pipes[2] = { 0xF0F0F0F0E1LL,0xF0F0F0F0D2LL };
// here we can send up to 30 chars

void setupRF24(){
  radio.begin();
  radio.setChannel(CH);
  radio.setAutoAck(1);
  radio.enableDynamicAck();
  radio.setRetries(15,15);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_250KBPS);
  radio.setCRCLength(RF24_CRC_8);
  radio.setPayloadSize(32);
  
  radio.openReadingPipe(1,pipes[0]);
  radio.openWritingPipe(pipes[1]);
  radio.printDetails(); //for Debugging
  radio.powerDown();
  delay(5);
}

void setup() {
  // Serial.begin(9600);
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  //radio
  setupRF24();
}

void sendData(){
  radio.powerUp();
  delay(50);
   bool ok = radio.write(&SendPayload,strlen(SendPayload));
  delay(50);
  radio.powerDown();
}

long mesureDistance(){
  long duration, distance;
  digitalWrite(TRIG, LOW);  // Added this line
  delayMicroseconds(2); // Added this line
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10); // Added this line
  digitalWrite(TRIG, LOW);
  duration = pulseIn(ECHO, HIGH);
  distance = (duration/2) / 29.1;
  return distance;
}

void loop() {
  long distance = mesureDistance();
  /*if (distance >= 200 || distance <= 0){
    Serial.println("Out of range");
  }
  else {
    Serial.print(distance);
    Serial.println(" cm");
  }*/
  if (distance >= LIMT_INF && distance <= LIMT_SUP){
    sendData();
    for(int i=0;i<SLLEPCYCLE ;i++){
      delay(30000);
    }
  }else{
    delay(1000);
  }
}
