import os
import json
import qrcode

# 1. Pastikan folder output untuk menampung gambar QR sudah ada
OUTPUT_FOLDER = "kartu_qr_mahasiswa"
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# 2. Muat data mahasiswa dari file JSON Anda
try:
    with open("mahasiswa.json", "r") as f:
        mahasiswa_db = json.load(f)
    print(f"Mengubah {len(mahasiswa_db)} data mahasiswa menjadi QR Code...")
except Exception as e:
    print(f"Gagal membaca file mahasiswa.json: {e}")
    exit()

# 3. Proses generate QR Code untuk setiap mahasiswa otomatis
for index, mhs in enumerate(mahasiswa_db, 1):
    nim = mhs["NIM"]
    nama = mhs["NAMA"]
    
    # Inisialisasi konfigurasi QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Isi QR Code HANYA dengan string NIM (agar dibaca valid oleh main.py)
    qr.add_data(nim)
    qr.make(fit=True)
    
    # Atur warna QR Code (Biru gelap UNESA dengan background putih)
    img = qr.make_image(fill_color="#003366", back_color="#FFFFFF")
    
    # Beri nama file gambar berdasarkan NIM dan Nama Mahasiswa
    # Karakter spasi diganti underscore agar aman di sistem file
    nama_bersih = nama.replace(" ", "_")
    file_name = f"{nim}_{nama_bersih}.png"
    file_path = os.path.join(OUTPUT_FOLDER, file_name)
    
    # Simpan gambar ke folder
    img.save(file_path)
    print(f"[{index}/{len(mahasiswa_db)}] Sukses membuat QR: {file_name}")

print(f"\n Selesai! Semua QR Code siap cetak ada di folder: '{OUTPUT_FOLDER}'")
