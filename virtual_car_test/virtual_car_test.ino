#define MAX_MESSAGE_SIZE 100
#define START_TOKEN 's'
#define MESSAGE "CONNECT"

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

void loop() {
  sendMessage();
  //  if (Serial.available() > 0) {
//    char readByte = Serial.read();
//
//    // Restart the message buffer
//    if (strcmp(readByte, START_TOKEN) == 0) {
//      index = 0;
//      started = true;
//    }
//    // Check for overflow of message
//    else if (index >= MAX_MESSAGE_SIZE) {
//      index = 0;
//      started = false;
//    }
//    // Only look at the data if message has been started
//    else if (started) {
//      buf[index] = readByte;
//      index++;
//      buf[index] = '\0';
//
//      if (strcmp(readByte, MESSAGE) == 0) {
//        Serial.print("ACK");
//      }
//    }
//  }
}
