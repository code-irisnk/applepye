"""Hashes a password using MD5"""

import hashlib

password = input("Password to hash: ")
HASH = hashlib.md5(password.encode("utf-8")).hexdigest()
print(HASH)
