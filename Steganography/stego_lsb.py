#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
David Christian Nathanaiel 140810230027
"""

from PIL import Image
import zlib, struct, sys, os

MAGIC = b"STEG"

# ----------------------- Fungsi dasar -----------------------
def _bytes_to_bits(data: bytes):
    for b in data:
        for i in range(7, -1, -1):
            yield (b >> i) & 1

def _bits_to_bytes(bits):
    out = bytearray()
    cur = 0
    nbits = 0
    for bit in bits:
        cur = (cur << 1) | (bit & 1)
        nbits += 1
        if nbits == 8:
            out.append(cur)
            cur = 0
            nbits = 0
    return bytes(out)

def _capacity_px(img: Image.Image) -> int:
    return img.width * img.height * 3  # 3 bit per pixel

def _encode_bits(img, bits):
    if img.mode != "RGB":
        img = img.convert("RGB")
    pixels = img.load()
    w, h = img.size
    idx = 0
    total = len(bits)
    for y in range(h):
        for x in range(w):
            if idx >= total:
                return img
            r, g, b = pixels[x, y]
            rgb = [r, g, b]
            for c in range(3):
                if idx < total:
                    rgb[c] = (rgb[c] & ~1) | bits[idx]
                    idx += 1
            pixels[x, y] = tuple(rgb)
    return img

def _extract_bits(img, n_bits):
    if img.mode != "RGB":
        img = img.convert("RGB")
    pixels = img.load()
    w, h = img.size
    bits = []
    idx = 0
    for y in range(h):
        for x in range(w):
            if idx >= n_bits:
                break
            r, g, b = pixels[x, y]
            for val in (r, g, b):
                if idx < n_bits:
                    bits.append(val & 1)
                    idx += 1
    return bits

def _pack_header(mode, payload):
    crc = zlib.crc32(payload) & 0xFFFFFFFF
    return MAGIC + bytes([mode]) + struct.pack(">I", len(payload)) + struct.pack(">I", crc)

def _unpack_header(header):
    if header[:4] != MAGIC:
        raise ValueError("File bukan hasil steganografi program ini!")
    mode = header[4]
    length = struct.unpack(">I", header[5:9])[0]
    crc = struct.unpack(">I", header[9:13])[0]
    return mode, length, crc

# ----------------------- Encode / Decode -----------------------
def encode_text(cover, output, message):
    img = Image.open(cover)
    payload = message.encode()
    header = _pack_header(0, payload)
    data = header + payload
    bits = list(_bytes_to_bits(data))
    if len(bits) > _capacity_px(img):
        raise ValueError("Pesan terlalu besar untuk gambar ini!")
    stego = _encode_bits(img, bits)
    stego.save(output, "PNG")
    print(f"[OK] Pesan berhasil disembunyikan ke {output}")

def decode_text(stego_path):
    img = Image.open(stego_path)
    header_bits = _extract_bits(img, 13*8)
    header = _bits_to_bytes(header_bits)
    mode, length, crc = _unpack_header(header)
    if mode != 0:
        raise ValueError("File ini menyimpan data biner, bukan teks.")
    payload_bits = _extract_bits(img, (13+length)*8)[13*8:]
    payload = _bits_to_bytes(payload_bits)
    if (zlib.crc32(payload) & 0xFFFFFFFF) != crc:
        raise ValueError("CRC tidak cocok, data rusak.")
    print("\n[Pesan Tersembunyi]")
    print(payload.decode(errors="replace"))

def encode_file(cover, output, file_path):
    img = Image.open(cover)
    data = open(file_path, "rb").read()
    header = _pack_header(1, data)
    full = header + data
    bits = list(_bytes_to_bits(full))
    if len(bits) > _capacity_px(img):
        raise ValueError("File terlalu besar untuk disembunyikan!")
    stego = _encode_bits(img, bits)
    stego.save(output, "PNG")
    print(f"[OK] File '{file_path}' berhasil disembunyikan ke {output}")

def decode_file(stego_path, output):
    img = Image.open(stego_path)
    header_bits = _extract_bits(img, 13*8)
    header = _bits_to_bytes(header_bits)
    mode, length, crc = _unpack_header(header)
    if mode != 1:
        raise ValueError("File ini menyimpan teks, bukan file biner.")
    payload_bits = _extract_bits(img, (13+length)*8)[13*8:]
    payload = _bits_to_bytes(payload_bits)
    if (zlib.crc32(payload) & 0xFFFFFFFF) != crc:
        raise ValueError("CRC tidak cocok, data rusak.")
    with open(output, "wb") as f:
        f.write(payload)
    print(f"[OK] File berhasil diekstrak ke {output}")

# ----------------------- Menu Utama -----------------------
def main_menu():
    while True:
        print("\n=========================")
        print("   STEGANOGRAFI LSB")
        print("=========================")
        print("1. Encode pesan teks")
        print("2. Decode pesan teks")
        print("3. Encode file")
        print("4. Decode file")
        print("5. Keluar")

        choice = input("Pilih menu (1-5): ").strip()
        try:
            if choice == "1":
                cover = input("Masukkan file cover (mis. cover.png): ").strip()
                output = input("Masukkan nama file output (mis. stego.png): ").strip()
                message = input("Masukkan pesan rahasia: ").strip()
                encode_text(cover, output, message)
            elif choice == "2":
                stego = input("Masukkan file stego (mis. stego.png): ").strip()
                decode_text(stego)
            elif choice == "3":
                cover = input("Masukkan file cover (mis. cover.png): ").strip()
                output = input("Masukkan nama file output (mis. stego.png): ").strip()
                secret = input("Masukkan file yang ingin disembunyikan (mis. rahasia.png): ").strip()
                encode_file(cover, output, secret)
            elif choice == "4":
                stego = input("Masukkan file stego (mis. stego.png): ").strip()
                output = input("Masukkan nama file hasil ekstraksi (mis. hasil.png): ").strip()
                decode_file(stego, output)
            elif choice == "5":
                print("Keluar dari program.")
                break
            else:
                print("Pilihan tidak valid!")
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    main_menu()
