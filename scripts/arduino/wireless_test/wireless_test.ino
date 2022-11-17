#define SEND_INTERVAL 100 // ms
#define START_TOKEN 'T'
#define END_TOKEN '\r'

typedef struct {
  uint64_t timestamp;
  uint16_t id;
  uint8_t len;
  uint8_t dataBuf[8];
} message_t;

message_t messageBuf[1];
message_t *message = messageBuf;
uint64_t startTime = 1654705626000;
int dataCount = 0;
int timeCount = 0;


void setup() {
  Serial.begin(115200);
  message->timestamp = startTime;
  message->id = 514;
  message->len = 8;
  message->dataBuf[0] = 0;
  message->dataBuf[1] = 0;
  message->dataBuf[2] = 24;
  message->dataBuf[3] = 0;
  message->dataBuf[4] = 0;
  message->dataBuf[5] = 0;
  message->dataBuf[6] = 0;
  message->dataBuf[7] = 0;
}

void updateMessage() {
  message->timestamp = startTime + timeCount;
  message->dataBuf[0] = dataCount % 255;
  dataCount++;
  timeCount++;
}

void sendMessage() {
  uint32_t upper = message->timestamp / 1000000000;
  uint32_t lower = message->timestamp % 1000000000;
  
  char encodedMessage[20 + message->len*2];
  snprintf(&encodedMessage[0], 19, "%c%.4lu%.9lu%.3x%.1hu", START_TOKEN, upper, lower, message->id, message->len);
  for (int i = 0; i < message->len; i++) {
    snprintf(&encodedMessage[18 + 2*i], 3, "%.2x", message->dataBuf[i]);
  }
  snprintf(&encodedMessage[18 + message->len*2], 2, "%c", END_TOKEN);
  Serial.print(encodedMessage);
}

void loop() {
  static long lastSend = millis();
  if (millis() - lastSend > SEND_INTERVAL) {
    updateMessage();
    sendMessage();
    lastSend = millis();
  }
}
