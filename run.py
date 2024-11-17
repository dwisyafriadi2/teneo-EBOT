from cryptography.fernet import Fernet

# Load the encryption key
with open('config.key', 'rb') as key_file:
    key = key_file.read()

cipher_suite = Fernet(key)

# Read the encrypted code
with open('config.py', 'rb') as enc_file:
    encrypted_code = enc_file.read()

# Decrypt the code
decrypted_code = cipher_suite.decrypt(encrypted_code)

# Execute the decrypted code
exec(decrypted_code.decode())
