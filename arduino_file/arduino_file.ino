const int entryLedPin = 9;  // Pin for entry LED
const int exitLedPin = 8;   // Pin for exit LED

void setup() {
    pinMode(entryLedPin, OUTPUT);
    pinMode(exitLedPin, OUTPUT);
    Serial.begin(9600);
}

void loop() {
    if (Serial.available() > 0) {
        char command = Serial.read();
        
        if (command == '1') {  // Entry LED
            digitalWrite(entryLedPin, HIGH);  // Turn on entry LED
            delay(500);  // Keep it on for 500 ms
            digitalWrite(entryLedPin, LOW);   // Turn off entry LED
        }
        else if (command == '2') {  // Exit LED
            digitalWrite(exitLedPin, HIGH);  // Turn on exit LED
            delay(500);  // Keep it on for 500 ms
            digitalWrite(exitLedPin, LOW);   // Turn off exit LED
        }
    }
}
