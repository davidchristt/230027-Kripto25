# DAVID CHRISTIAN NATHANIEL
# 140810230027

import numpy as np
from itertools import combinations
from math import gcd

def text_to_numbers(text):
    """Mengonversi string teks ke daftar angka (A=0, B=1, ..., Z=25)."""
    return [ord(char) - ord('A') for char in text.upper() if char.isalpha()]

def numbers_to_text(numbers):
    """Mengonversi daftar angka kembali ke string huruf."""
    return ''.join(chr(num % 26 + ord('A')) for num in numbers)

def mod_inverse(a, m=26):
    """Mencari invers modular dari bilangan a mod m.
       Digunakan untuk menghitung invers determinan dalam modulo 26."""
    a %= m
    for i in range(1, m):
        if (a * i) % m == 1:   # jika ditemukan i yang membuat (a*i) ≡ 1 (mod m)
            return i
    return None  # Jika tidak ada invers (misalnya gcd(a, m) ≠ 1)

def matrix_mod_inverse(matrix, modulus=26):
    """Mencari invers matriks modulo 26 untuk Hill Cipher."""
    # Hitung determinan matriks
    det = int(round(np.linalg.det(matrix)))
    # Cari invers determinan mod 26
    det_inv = mod_inverse(det, modulus)
    
    # Validasi: matriks tidak bisa dibalik jika gcd(det, 26) ≠ 1
    if det_inv is None or gcd(det, modulus) != 1:
        raise ValueError("Matriks kunci tidak memiliki invers modulo 26!")

    # adj(A) = determinan * invers(A) (dengan nilai integer)
    adjugate = np.round(det * np.linalg.inv(matrix)).astype(int)

    # Matriks invers modulo: det_inv * adj(A) (mod m)
    matrix_inv = (det_inv * adjugate) % modulus
    return matrix_inv

def hill_encrypt(plaintext, key_matrix):
    """Mengenkripsi plaintext dengan matriks kunci Hill Cipher."""
    n = len(key_matrix)  # ukuran matriks (misalnya 2x2 → n=2)
    plaintext_nums = text_to_numbers(plaintext)

    # Tambahkan padding 'X' jika panjang plaintext tidak habis dibagi n
    while len(plaintext_nums) % n != 0:
        plaintext_nums.append(ord('X') - ord('A')) # 'X' = 23

    ciphertext_nums = []
    # Proses enkripsi per blok sepanjang n
    for i in range(0, len(plaintext_nums), n):
        block = np.array(plaintext_nums[i:i+n])            # blok plaintext
        encrypted_block = np.dot(key_matrix, block) % 26   # E = K * P mod 26
        ciphertext_nums.extend(encrypted_block)

    return numbers_to_text(ciphertext_nums)  # konversi ke huruf

def hill_decrypt(ciphertext, key_matrix):
    """Mendekripsi ciphertext dengan matriks kunci Hill Cipher."""
    n = len(key_matrix)
    ciphertext_nums = text_to_numbers(ciphertext)

    # Cari invers matriks kunci mod 26
    key_inv = matrix_mod_inverse(key_matrix, 26)
    
    plaintext_nums = []
    # Proses dekripsi per blok
    for i in range(0, len(ciphertext_nums), n):
        block = np.array(ciphertext_nums[i:i+n])            # blok ciphertext
        decrypted_block = np.dot(key_inv, block) % 26       # P = K^-1 * C mod 26
        plaintext_nums.extend(decrypted_block)

    return numbers_to_text(plaintext_nums)  # hasil dalam huruf

def to_blocks(nums, n):
    """Membagi list angka ke blok kolom berukuran n (hasil: matriks n x jumlah_blok)."""
    blocks = []
    for i in range(0, len(nums), n):
        block = nums[i:i+n]
        if len(block) < n:  # Abaikan blok terakhir kalau tidak penuh
            break
        blocks.append(block)
    return np.array(blocks).T  # Transpose: tiap blok jadi kolom

def find_key(plaintext, ciphertext, n):
    """Mencari matriks kunci Hill Cipher dari pasangan plaintext dan ciphertext."""
    P_nums = text_to_numbers(plaintext)
    C_nums = text_to_numbers(ciphertext)

    # Validasi: untuk kunci n×n butuh minimal n^2 karakter
    if len(P_nums) < n*n:
        raise ValueError(f"Data tidak cukup. Untuk kunci {n}x{n}, butuh minimal {n*n} karakter unik.")

    # Bentuk matriks blok
    P_full = to_blocks(P_nums, n)  # matriks plaintext
    C_full = to_blocks(C_nums, n)  # matriks ciphertext
    
    k = P_full.shape[1]  # jumlah blok tersedia
    if k < n:
        raise ValueError(f"Tidak cukup blok valid. Butuh {n} blok, hanya tersedia {k}.")

    # Coba semua kombinasi n kolom untuk mencari matriks yang bisa diinvers
    for cols in combinations(range(k), n):
        P_sub = P_full[:, cols]  # ambil submatriks plaintext
        C_sub = C_full[:, cols]  # ambil submatriks ciphertext

        try:
            # Cari invers modular dari P_sub
            P_inv_mod = matrix_mod_inverse(P_sub)
            # Matriks kunci = C * P^-1 (mod 26)
            Key = np.dot(C_sub, P_inv_mod) % 26
            return Key, cols
        except ValueError:
            # Jika tidak bisa dibalik, coba kombinasi kolom lain
            continue

    raise ValueError("Tidak ditemukan submatriks plaintext yang invertible. Coba dengan pasangan teks lain.")

def main():
    """Program utama dengan menu interaktif Hill Cipher."""
    while True:
        print("\n===== MENU HILL CIPHER =====")
        print("1. Enkripsi")
        print("2. Dekripsi")
        print("3. Cari Kunci dari Plaintext & Ciphertext")
        print("0. Keluar")
        
        choice = input("Pilih menu: ")

        try:
            if choice == "1":
                # === ENKRIPSI ===
                plaintext = input("Masukkan plaintext: ")
                n = int(input("Ukuran matriks kunci (misal 2 untuk 2x2): "))
                print(f"Masukkan elemen matriks kunci {n}x{n}:")
                key_matrix = [list(map(int, input(f"Baris {i+1}: ").split())) for i in range(n)]
                key_matrix = np.array(key_matrix)
                
                ciphertext = hill_encrypt(plaintext, key_matrix)
                print("\n Hasil Enkripsi (Ciphertext):", ciphertext)

            elif choice == "2":
                # === DEKRIPSI ===
                ciphertext = input("Masukkan ciphertext: ")
                n = int(input("Ukuran matriks kunci (misal 2 untuk 2x2): "))
                print(f"Masukkan elemen matriks kunci {n}x{n}:")
                key_matrix = [list(map(int, input(f"Baris {i+1}: ").split())) for i in range(n)]
                key_matrix = np.array(key_matrix)

                plaintext = hill_decrypt(ciphertext, key_matrix)
                print("\n Hasil Dekripsi (Plaintext):", plaintext)

            elif choice == "3":
                # === CARI KUNCI ===
                plaintext = input("Masukkan plaintext: ")
                ciphertext = input("Masukkan ciphertext: ")
                n = int(input("Ukuran matriks kunci yang dicari (misal 2 untuk 2x2): "))

                key_matrix, cols = find_key(plaintext, ciphertext, n)
                print("\n Matriks kunci ditemukan!")
                print("Menggunakan kolom blok ke:", cols)
                print(key_matrix.astype(int))

            elif choice == "0":
                print("Terima kasih telah menggunakan program ini. Keluar...")
                break  # keluar dari loop

            else:
                print(" Pilihan tidak valid! Silakan pilih antara 1, 2, 3, atau 0.")

        except ValueError as e:
            # Menangkap error khusus (misalnya matriks tidak bisa diinvers)
            print(f"\n Terjadi Kesalahan: {e}")
        except Exception as e:
            # Menangkap error umum lain
            print(f"\n Terjadi kesalahan tak terduga: {e}")

# Jalankan program utama
if __name__ == "__main__":
    main()
