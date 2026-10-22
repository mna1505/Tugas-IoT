import json  # Tambahkan library untuk membaca JSON
import serial
import time
import paho.mqtt.client as mqtt

# === KONFIGURASI SERIAL ARDUINO ===
SERIAL_PORT = "COM5"
BAUD_RATE = 9600

try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f" Berhasil terhubung ke Arduino di {SERIAL_PORT}")
    time.sleep(2)
except Exception as e:
    print(f" Gagal membuka Port Serial: {e}")
    exit()

# === LOAD DATABASE MAHASISWA (MENYAMBUNGKAN JSON) ===
try:
    # Ganti 'daftar_mahasiswa.json' sesuai nama file JSON Anda
    with open("mahasiswa.json", "r") as f:
        mahasiswa_db = json.load(f)
    # Buat daftar NIM saja untuk mempermudah pengecekan
    daftar_nim = [mhs["NIM"] for mhs in mahasiswa_db]
    print(f" Berhasil memuat {len(daftar_nim)} data mahasiswa dari database.")
except Exception as e:
    print(f" Gagal membaca database JSON: {e}")
    exit()

# === KONFIGURASI MQTT ===
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "unesa/iot/boomgate"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(" Berhasil terhubung ke MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Gagal terhubung, kode respon: {rc}")


# Fungsi Callback saat menerima hasil scan QR
def on_message(client, userdata, msg):
    data_qr = msg.payload.decode("utf-8").strip()
    print(f"\n Data QR Diterima: {data_qr}")

    # --- LOGIKA VALIDASI SEKARANG SUDAH TERSAMBUNG ---
    if data_qr in daftar_nim:
        # Cari nama mahasiswanya berdasarkan NIM
        mahasiswa = next(mhs for mhs in mahasiswa_db if mhs["NIM"] == data_qr)
        print(
            f" [AKSES DITERIMA] Mahasiswa Terdaftar: {mahasiswa['NAMA']} ({data_qr})"
        )
        print("Mengirim perintah buka palang ke Arduino...")
        arduino.write(b"1")  # Kirim perintah buka ke Arduino
    else:
        print(
            f" [AKSES DITOLAK] QR Code ({data_qr}) tidak terdaftar di database!"
        )


# Inisialisasi MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print("Menghubungkan ke MQTT Broker...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\nProgram dihentikan oleh pengguna.")
    arduino.close()
