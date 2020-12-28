import bcrypt


def hash_password_string(password):
    password = str.encode(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed
