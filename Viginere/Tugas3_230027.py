# David Christian Nathaniel
def char_to_num(ch):
    return ord(ch.upper()) - ord('A')

def num_to_char(num):
    return chr((num % 26) + ord('A'))

def vigenere_encrypt(plaintext, key):
    ciphertext = ""
    key_nums = [char_to_num(k) for k in key]
    key_len = len(key)
    
    for i, ch in enumerate(plaintext):
        if ch.isalpha():
            p = char_to_num(ch)
            k = key_nums[i % key_len]
            c = (p + k) % 26
            ciphertext += num_to_char(c)
        else:
            ciphertext += ch
    return ciphertext

def vigenere_decrypt(ciphertext, key):
    plaintext = ""
    key_nums = [char_to_num(k) for k in key]
    key_len = len(key)
    
    for i, ch in enumerate(ciphertext):
        if ch.isalpha():
            c = char_to_num(ch)
            k = key_nums[i % key_len]
            p = (c - k) % 26
            plaintext += num_to_char(p)
        else:
            plaintext += ch
    return plaintext


plaintext = "ASPRAKGANTENG"
key = "DAVID"

encrypted = vigenere_encrypt(plaintext, key)
decrypted = vigenere_decrypt(encrypted, key)

print("=== Vigenere Cipher ===")
print("Plaintext :", plaintext)
print("Key       :", key)
print("Encrypted :", encrypted)
print("Decrypted :", decrypted)
