import bcrypt


def validate_password(password_candidate):
    validation_errors = []
    if len(password_candidate) < 8:
        validation_errors.append(
            "password must have at least eight characters")
    if not any(c.isupper() for c in password_candidate):
        validation_errors.append(
            "password must have at least one uppercase letter")
    if not any(c.isdigit() for c in password_candidate):
        validation_errors.append(
            "password must have at least one number")
    return validation_errors


def save_password(password):
    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt)
    with open('password.bfe', 'w+') as secrets:
        secrets.write(hashed_password.decode('utf-8'))
    secrets.close()


def password_is_correct(password_attempt):
    password_attempt = password_attempt.encode('utf-8')
    saved_password_file = open('password.bfe', 'r')
    if saved_password_file.mode == 'r':
        saved_password = saved_password_file.read().encode('utf-8')
        return bcrypt.checkpw(password_attempt, saved_password)
    else:
        return False
