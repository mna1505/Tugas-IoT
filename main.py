# import json  # Tambahkan library untuk membaca JSON
# import serial
# import time
# import paho.mqtt.client as mqtt

# # === KONFIGURASI SERIAL ARDUINO ===
# SERIAL_PORT = "COM5"
# BAUD_RATE = 9600

# try:
#     arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
#     print(f" Berhasil terhubung ke Arduino di {SERIAL_PORT}")
#     time.sleep(2)
# except Exception as e:
#     print(f" Gagal membuka Port Serial: {e}")
#     exit()

# # === LOAD DATABASE MAHASISWA (MENYAMBUNGKAN JSON) ===
# try:
#     # Ganti 'daftar_mahasiswa.json' sesuai nama file JSON Anda
#     with open("mahasiswa.json", "r") as f:
#         mahasiswa_db = json.load(f)
#     # Buat daftar NIM saja untuk mempermudah pengecekan
#     daftar_nim = [mhs["NIM"] for mhs in mahasiswa_db]
#     print(f" Berhasil memuat {len(daftar_nim)} data mahasiswa dari database.")
# except Exception as e:
#     print(f" Gagal membaca database JSON: {e}")
#     exit()

# # === KONFIGURASI MQTT ===
# MQTT_BROKER = "broker.emqx.io"
# MQTT_PORT = 1883
# MQTT_TOPIC = "unesa/iot/boomgate"


# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         print(" Berhasil terhubung ke MQTT Broker!")
#         client.subscribe(MQTT_TOPIC)
#     else:
#         print(f"Gagal terhubung, kode respon: {rc}")


# # Fungsi Callback saat menerima hasil scan QR
# def on_message(client, userdata, msg):
#     data_qr = msg.payload.decode("utf-8").strip()
#     print(f"\n Data QR Diterima: {data_qr}")

#     # --- LOGIKA VALIDASI SEKARANG SUDAH TERSAMBUNG ---
#     if data_qr in daftar_nim:
#         # Cari nama mahasiswanya berdasarkan NIM
#         mahasiswa = next(mhs for mhs in mahasiswa_db if mhs["NIM"] == data_qr)
#         print(
#             f" [AKSES DITERIMA] Mahasiswa Terdaftar: {mahasiswa['NAMA']} ({data_qr})"
#         )
#         print("Mengirim perintah buka palang ke Arduino...")
#         arduino.write(b"1")  # Kirim perintah buka ke Arduino
#     else:
#         print(
#             f" [AKSES DITOLAK] QR Code ({data_qr}) tidak terdaftar di database!"
#         )


# # Inisialisasi MQTT
# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message

# print("Menghubungkan ke MQTT Broker...")
# client.connect(MQTT_BROKER, MQTT_PORT, 60)

# try:
#     client.loop_forever()
# except KeyboardInterrupt:
#     print("\nProgram dihentikan oleh pengguna.")
#     arduino.close()

import json  # Library untuk membaca berkas mahasiswa.json
import serial
import time
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion # Diperlukan untuk paho-mqtt versi terbaru

# === KONFIGURASI SERIAL ARDUINO ===
SERIAL_PORT = "COM5"
BAUD_RATE = 9600

try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"✅ Berhasil terhubung ke Arduino di {SERIAL_PORT}")
    time.sleep(2)
except Exception as e:
    print(f"❌ Gagal membuka Port Serial: {e}")
    exit()

# === LOAD DATABASE MAHASISWA (MENYAMBUNGKAN JSON) ===
try:
    with open("mahasiswa.json", "r") as f:
        mahasiswa_db = json.load(f)
    # Membuat list daftar NIM untuk mempercepat validasi kecocokan data
    daftar_nim = [mhs["NIM"] for mhs in mahasiswa_db]
    print(f"📂 Berhasil memuat {len(daftar_nim)} data mahasiswa dari database JSON.")
except Exception as e:
    print(f"❌ Gagal membaca database JSON: {e}")
    exit()

# === KONFIGURASI MQTT BROKER ===
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "unesa/iot/boomgate"

# Fungsi Callback saat Python sukses tersambung ke Server Broker EMQX
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("🌐 Berhasil terhubung ke MQTT Broker EMQX Internet!")
        client.subscribe(MQTT_TOPIC)
        print(f"📡 Menyimak kiriman data scan QR pada topik: {MQTT_TOPIC}")
    else:
        print(f"❌ Gagal terhubung ke Broker, kode respon: {rc}")

# Fungsi Callback utama yang otomatis memproses kiriman data string NIM dari HP/GitHub Pages
def on_message(client, userdata, msg):
    data_qr = msg.payload.decode("utf-8").strip()
    print(f"\n📥 Data QR Diterima: {data_qr}")

    # --- LOGIKA VALIDASI COCOK DATA JSON ---
    if data_qr in daftar_nim:
        # Menarik data Nama mahasiswa yang memiliki NIM sesuai isi QR Code
        mahasiswa = next(mhs for mhs in mahasiswa_db if mhs["NIM"] == data_qr)
        print(f"🔓 [AKSES DITERIMA] Mahasiswa Terdaftar: {mahasiswa['NAMA']} ({data_qr})")
        print("🚀 Mengirim sinyal byte data b'1' ke Arduino untuk membuka Servo...")
        arduino.write(b"1")  # Kirim karakter '1' lewat jalur kabel data USB ke Arduino
    else:
        print(f"🔒 [AKSES DITOLAK] QR Code ({data_qr}) tidak terdaftar di berkas JSON!")

# Inisialisasi Instance Client MQTT dengan penyesuaian standardisasi API versi terbaru
client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

print("⏳ Menghubungkan ke EMQX Public MQTT Broker...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

try:
    # Menjalankan pemantauan jaringan MQTT secara terus-menerus tanpa henti
    client.loop_forever()
except KeyboardInterrupt:
    print("\n👋 Program dihentikan secara manual oleh pengguna.")
    arduino.close()
