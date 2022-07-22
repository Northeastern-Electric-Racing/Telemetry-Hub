#define MAX_MESSAGE_SIZE 100
#define START_TOKEN 's'
#define MESSAGE "CONNECT"

typedef struct data {
  uint32_t seconds : 31;      // 10-digit integer second times since epoch
  uint16_t milliseconds : 10; // 0-999
  uint16_t id : 11;           // 0x000-0x7FF
  uint8_t len : 4;            // 0-8 
  uint8_t data[8];            // 8 bytes of data
} data_t;

typedef struct control {
  uint8_t source : 1; // 0 from the car, 1 from offboard
  uint8_t id : 8;     // identifies purpose of the message (support 256 distinct ids)
  uint8_t len : 4;    // 0-8 
  uint8_t data[8];    // 8 bytes of data
} control_t;



data_t dbuf[10];


char buf[MAX_MESSAGE_SIZE + 1]; // +1 for termination
int index = 0;
int started = false;



void setup() {
  Serial.begin(9600);
}


void sendMessage() {
  static unsigned long last = millis();
  if (millis() - last > 1000) {
    Serial.print(START_TOKEN);
    Serial.print("1654705626.274 1 1 1");
    Serial.print(START_TOKEN);
    Serial.print("1654705626.274 2 4 1 2 3 4");
    Serial.print(START_TOKEN);
    Serial.print("1654705626.274 3 6 1 2 3 4 5 6");
    last = millis();
  }
}


void printData(int index) {
  Serial.print(dbuf[index].seconds);
  Serial.print(".");
  Serial.print(dbuf[index].milliseconds);
  Serial.print(" - ");
  Serial.print(dbuf[index].id);
  Serial.print(" - ");
  Serial.print(dbuf[index].len);
  Serial.print(" - [");
  for (int i = 0; i < 7; i++) {
    Serial.print(dbuf[index].data[i]);
    Serial.print(",");
  }
  Serial.print(dbuf[index].data[7]);
  Serial.println("]");
}

void sendMessage2() {
  static unsigned long last = millis();
  static int count = 0;
  if (millis() - last > 2000 && count < 10) {
    dbuf[count].seconds = 1654705626 + count;
    dbuf[count].milliseconds = 274 + count;
    dbuf[count].id = 1;
    dbuf[count].len = 4;
    for (int i = 0; i < 4; i++) {
      dbuf[count].data[i] = i;
    }

    //Serial.print(dbuf[count]);
    printData(count);
    last = millis();
    count++;
  }
}

void loop() {
//  static bool didPrint = false;
//
//  if (!didPrint) {
//    Serial.print("Size of Data: ");
//    Serial.println(sizeof(data_t));
//    Serial.print("Size of Control: ");
//    Serial.println(sizeof(control_t));
//    Serial.print("Size of Dbuf:");
//    Serial.println(sizeof(dbuf));
//    didPrint = true;
//  }
//
//  sendMessage2();

  sendMessage();
  
}
