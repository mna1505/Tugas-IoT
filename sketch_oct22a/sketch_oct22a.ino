#include <Servo.h>

Servo myservo;
const int servoPin = 9; // Hubungkan kabel data servo ke Pin 9 Arduino

void setup() {
  Serial.begin(9600);   // Membuka komunikasi serial dengan baudrate 9600
  myservo.attach(servoPin);
  myservo.write(0);     // Posisi awal palang pintu tertutup (0 derajat)
}

void loop() {
  if (Serial.available() > 0) {
    char data = Serial.read(); // Membaca data kiriman dari Python
    
    if (data == '1') {
      myservo.write(90);  // Buka palang pintu (90 derajat)
      delay(3000);        // Biarkan terbuka selama 3 detik
      myservo.write(0);   // Tutup kembali palang pintu
    }
  }
}
