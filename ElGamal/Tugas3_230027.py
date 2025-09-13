# David Christian Nathaniel
# ==========================
# ElGamal Cryptosystem
# ==========================

# Fungsi mencari invers modulo dengan Extended Euclidean Algorithm
def mod_inverse(a, m):
    t, newt = 0, 1
    r, newr = m, a
    while newr != 0:
        q = r // newr
        t, newt = newt, t - q * newt
        r, newr = newr, r - q * newr
    if r > 1:      # tidak ada invers
        raise Exception("No inverse")
    if t < 0:      # hasil negatif → ubah jadi positif
        t += m
    return t

# Membuat public key dari p, g, dan private key x
def elgamal_keygen(p, g, x):
    # Public key dihitung y = g^x mod p
    y = pow(g, x, p)
    return (p, g, y)  # kembalikan public key (p,g,y)

# Fungsi enkripsi ElGamal
def elgamal_encrypt(p, g, y, m, k):
    # c1 = g^k mod p
    c1 = pow(g, k, p)
    # c2 = m * y^k mod p
    c2 = (m * pow(y, k, p)) % p
    return (c1, c2)

# Fungsi dekripsi ElGamal
def elgamal_decrypt(p, x, c1, c2):
    # s = c1^x mod p (shared secret)
    s = pow(c1, x, p)
    # cari invers dari s mod p
    inv_s = mod_inverse(s, p)
    # m = c2 * s^-1 mod p
    m = (c2 * inv_s) % p
    return m

# Mapping huruf A-Z ke angka 0-25
def char_to_num(ch): 
    return ord(ch.upper()) - ord('A')

def num_to_char(num): 
    return chr(num + ord('A'))


p = 37       # bilangan prima > 26
g = 3        # generator
x = 2        # private key (rahasia)
k = 15       # ephemeral key (acak setiap enkripsi)
plaintext = "EZKRIPTOGRAFI"

# 1. Key generation
p, g, y = elgamal_keygen(p, g, x)
print("=== ElGamal ===")
print("Public key (p,g,y):", (p, g, y))
print("Private key x:", x)

# 2. Enkripsi plaintext huruf per huruf
ciphertext = []
for ch in plaintext:
    m = char_to_num(ch)                   # ubah huruf jadi angka
    c1, c2 = elgamal_encrypt(p, g, y, m, k)  # enkripsi angka
    ciphertext.append((c1, c2))

print("Plaintext :", plaintext)
print("Ciphertext:", ciphertext)

# 3. Dekripsi kembali ke plaintext
decrypted_nums = [elgamal_decrypt(p, x, c1, c2) for (c1, c2) in ciphertext]
decrypted_text = "".join(num_to_char(n) for n in decrypted_nums)

print("Decrypted :", decrypted_text)
