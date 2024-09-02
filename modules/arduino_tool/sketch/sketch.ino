
#include <CapacitiveSensor.h>

const int threshold = 900;
const int delayVal = 40;
const int sensorCount = 3;

const int sensorPins[sensorCount] = {2, 3, 4};
CapacitiveSensor capSensors[sensorCount] = {
    CapacitiveSensor(13, 2),
    CapacitiveSensor(13, 3),
    CapacitiveSensor(13, 4)
};

int currentTrack = 0;

void setup() {
    Serial.begin(115200);
}

void loop() {
    for (int i = 0; i < sensorCount; i++) {
        long sensorValue = capSensors[i].capacitiveSensor(3);
        if (sensorValue > threshold) {
            if (currentTrack != i + 2) {
                Serial.write(i + 2);
                currentTrack = i + 2;
            }
        }
    }

    if (Serial.available()) {
        char val = Serial.read();
        if (val == 'h') {
            // Implement handshake handling if necessary
        } else if (val == 'r') {
            currentTrack = 0;
        }
    }

    delay(delayVal);
}
    