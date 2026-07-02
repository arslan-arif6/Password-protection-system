import hashlib
import random
import smtplib
from email.mime.text import MIMEText
from connection import get_connection
# import hashlaib is python's built in library used for password encryption
# imprt rendom is a python library used to genrate rendom 6 digit password
# imprt smtplib is a python  built in library used to send e-mail
# import NIMEText is python library used to reate e-mail bodey

def hash_password(password, salt):   # its hash function used for password encryption
    combined = password + salt
    return hashlib.sha256(combined.encode()).hexdigest()


def check_password_strength(password):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("select min_lenght, uppercase_required, lowercase_required, require_special_character from privacy_policy where policy_id = 1")
    policy       = cursor.fetchone()
    cursor.close()
    conn.close()

    min_length   = policy[0]
    need_upper   = policy[1]
    need_lower   = policy[2]
    need_special = policy[3]
    specials     = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    if len(password) < min_length:
        print(f"password kam az kam {min_length} characters ka hona chahiye")
        return False
    if need_upper == 'Y' and not any(c.isupper() for c in password):
        print("at least one uppercase latter like A B C")
        return False
    if need_lower == 'Y' and not any(c.islower() for c in password):
        print("at least one lowercase latter like a b c")
        return False
    if need_special == 'Y' and not any(c in specials for c in password):
        print("at least one special character like  !@#$")
        return False
    return True


def register_user(username, e_mail, full_name, password): # this is function used to register new user
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("select count(*) from users where username = :1", [username])
    if cursor.fetchone()[0] > 0:
        print("this username already exsist choose another one")
        cursor.close()
        conn.close()
        return

    salt  = username + "SALT2024"
    phash = hash_password(password, salt)

    cursor.execute("""
        insert into users
        (username, e_mail, full_name, role_id, status, failed_attempts, created_at, update_at)
        values (:1, :2, :3, 5, 'active', 0, sysdate, sysdate)
    """, [username, e_mail, full_name])

    cursor.execute("select user_id from users where username = :1", [username])
    user_id = cursor.fetchone()[0]

    cursor.execute("""
        insert into passwords (user_id, password_hash, salt, created_at, is_temporary)
        values (:1, :2, :3, sysdate, 'N')
    """, [user_id, phash, salt])

    conn.commit()
    cursor.close()
    conn.close()
    print(f"user '{username}' rigestered successfully ")


def login_user(username, password): # this function used for login user
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("select user_id, status from users where username = :1", [username])
    user = cursor.fetchone()

    if user is None:
        print("this username dosen't exsist")
        cursor.execute("insert into login_attempts (user_id, username_try, status, ip_address, attempt_time, failure_reason) values (null, :1, 'failed', '127.0.0.1', sysdate, 'user not found')", [username])
        conn.commit()
        cursor.close()
        conn.close()
        return

    user_id = user[0]
    status  = user[1]

    if status == 'locked':
        print("your account is locked... talk to admin")
        cursor.execute("insert into login_attempts (user_id, username_try, status, ip_address, attempt_time, failure_reason) values (:1, :2, 'locked', '127.0.0.1', sysdate, 'account locked')", [user_id, username])
        conn.commit()
        cursor.close()
        conn.close()
        return

    cursor.execute("select password_hash, salt from passwords where user_id = :1", [user_id])
    row          = cursor.fetchone()
    entered_hash = hash_password(password, row[1])

    if entered_hash == row[0]:
        cursor.execute("update users set failed_attempts = 0, last_login = sysdate where user_id = :1", [user_id])
        cursor.execute("insert into login_attempts (user_id, username_try, status, ip_address, attempt_time, failure_reason) values (:1, :2, 'success', '127.0.0.1', sysdate, null)", [user_id, username])
        conn.commit()
        print(f"welcome '{username}' -- login kamyab!")
        view_user_info(username)
    else:
        cursor.execute("update users set failed_attempts = failed_attempts + 1 where user_id = :1", [user_id])
        cursor.execute("insert into login_attempts (user_id, username_try, status, ip_address, attempt_time, failure_reason) values (:1, :2, 'failed', '127.0.0.1', sysdate, 'wrong password')", [user_id, username])
        conn.commit()
        print("wrong password try again!")

    cursor.close()
    conn.close()


def change_password(username, old_password, new_password): # this function used to change password
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("select user_id from users where username = :1", [username])
    user = cursor.fetchone()

    if user is None:
        print(" username is not exsist")
        cursor.close()
        conn.close()
        return

    user_id = user[0]

    cursor.execute("select password_hash, salt from passwords where user_id = :1", [user_id])
    row = cursor.fetchone()

    if hash_password(old_password, row[1]) != row[0]:
        print("old password is wrong")
        cursor.close()
        conn.close()
        return

    new_salt = username + "SALT2024"
    new_hash = hash_password(new_password, new_salt)

    cursor.execute("select password_hash from password_history where user_id = :1", [user_id])
    for old in cursor.fetchall():
        if old[0] == new_hash:
            print("yeh password pehle use ho chuka hai -- naya socho")
            cursor.close()
            conn.close()
            return

    cursor.execute("insert into password_history (user_id, password_hash, salt, changed_at) values (:1, :2, :3, sysdate)", [user_id, row[0], row[1]])
    cursor.execute("update passwords set password_hash = :1, salt = :2, created_at = sysdate where user_id = :3", [new_hash, new_salt, user_id])
    conn.commit()
    cursor.close()
    conn.close()
    print(f"'{username}' ka password successfully change ho gaya!")


def unlock_account(admin_username, target_username): # function for account unlock
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("select role_id from users where username = :1", [admin_username])
    admin = cursor.fetchone()

    if admin is None or admin[0] != 4:
        print("sirf admin yeh kaam kar sakta hai")
        cursor.close()
        conn.close()
        return

    cursor.execute("select user_id, status from users where username = :1", [target_username])
    user = cursor.fetchone()

    if user is None:
        print("yeh username exist nahi karta")
        cursor.close()
        conn.close()
        return

    if user[1] != 'locked':
        print(f"'{target_username}' ka account pehle se active hai")
        cursor.close()
        conn.close()
        return

    cursor.execute("update users set status = 'active', failed_attempts = 0, locked_at = null where username = :1", [target_username])
    conn.commit()
    cursor.close()
    conn.close()
    print(f"'{target_username}' ka account successfully unlock ho gaya!")


def view_user_info(username): # this function used  to see user info
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        select u.username, u.e_mail, u.full_name, r.role_name,
               u.status, u.failed_attempts, u.last_login
        from   users u join roles r on u.role_id = r.role_id
        where  u.username = :1
    """, [username])

    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user is None:
        print("yeh username exist nahi karta")
        return

    print("------------------------------")
    print(f"username       : {user[0]}")
    print(f"email          : {user[1]}")
    print(f"full name      : {user[2]}")
    print(f"role           : {user[3]}")
    print(f"status         : {user[4]}")
    print(f"failed attempts: {user[5]}")
    print(f"last login     : {user[6]}")
    print("------------------------------")

def get_login_history(username): # function te see login history
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        select attempt_time, status, ip_address, failure_reason
        from   login_attempts
        where  username_try = :1
        order  by attempt_time desc
    """, [username])

    history = cursor.fetchall()
    cursor.close()
    conn.close()
    return history


def check_password_expiry(username): #function to check  expiry date
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        select expires_at, round(expires_at - sysdate) as days_left
        from   passwords
        where  user_id = (select user_id from users where username = :1)
    """, [username])

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None:
        return None

    return {
        "expires_at" : str(row[0]),
        "days_left"  : int(row[1])
    }

def get_all_users(): # this function show all users
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        select u.user_id, u.username, u.e_mail, r.role_name,
               u.status, u.failed_attempts, u.last_login
        from   users u join roles r on u.role_id = r.role_id
        order  by u.user_id
    """)

    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users


def change_user_role(admin_username, target_username, new_role_name):
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("select role_id from users where username = :1", [admin_username])
    admin = cursor.fetchone()

    if admin is None or admin[0] != 4:
        cursor.close()
        conn.close()
        return "not_admin"

    cursor.execute("select role_id from roles where role_name = :1", [new_role_name.lower()])
    role = cursor.fetchone()

    if role is None:
        cursor.close()
        conn.close()
        return "role_not_found"

    cursor.execute("update users set role_id = :1 where username = :2", [role[0], target_username])
    conn.commit()
    cursor.close()
    conn.close()
    return "success"



GMAIL_ADDRESS  = "abcxyz@gmail.com"   # use your email API here
GMAIL_APP_PASS = "YOUR API KEY"


def send_otp(username):
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("select e_mail from users where username = :1", [username])
    row = cursor.fetchone()

    if row is None:
        cursor.close()
        conn.close()
        return False

    email    = row[0]
    otp_code = str(random.randint(100000, 999999))

    cursor.execute("""
        update users
        set    otp_code   = :1,
               otp_expiry = sysdate + (5/1440)
        where  username   = :2
    """, [otp_code, username])

    conn.commit()
    cursor.close()
    conn.close()

    try:
        msg          = MIMEText(f"""
Welcome sir {username}!

It's your login otp :

        {otp_code}

It will EXPIRE in next 5 mints.
If you not request it please ignore it .

Password Management & Protection System
        """)
        msg["Subject"] = f"Login OTP - {otp_code}"
        msg["From"]    = GMAIL_ADDRESS
        msg["To"]      = email

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASS)
        server.sendmail(GMAIL_ADDRESS, email, msg.as_string())
        server.quit()
        return True

    except Exception as ex:
        print(f"Email error: {ex}")
        return False


def verify_otp(username, entered_otp):
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        select otp_code, otp_expiry
        from   users
        where  username = :1
    """, [username])

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None or row[0] is None:
        return "no_otp"

    if row[1] < __import__('datetime').datetime.now():
        return "expired"

    if str(row[0]).strip() != str(entered_otp).strip():
        return "wrong"

    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("update users set otp_code = null, otp_expiry = null where username = :1", [username])
    conn.commit()
    cursor.close()
    conn.close()

    return "success"

def main():
    print("=============================")
    print("  password protection system ")
    print("=============================")

    while True:
        print("\n1. register")
        print("2. login")
        print("3. password change karo")
        print("4. account unlock karo (admin)")
        print("5. user info dekho")
        print("6. exit")

        choice = input("\napna choice enter karo: ")

        if choice == "1":
            username  = input("username: ")
            email     = input("email: ")
            full_name = input("full name: ")
            while True:
                print("\npassword mein yeh hona chahiye:")
                print("  - kam az kam 8 characters, ek uppercase, ek lowercase, ek special character")
                password = input("password: ")
                if check_password_strength(password):
                    break
            register_user(username, email, full_name, password)

        elif choice == "2":
            username = input("username: ")
            password = input("password: ")
            login_user(username, password)

        elif choice == "3":
            username     = input("username: ")
            old_password = input("purana password: ")
            new_password = input("naya password: ")
            change_password(username, old_password, new_password)

        elif choice == "4":
            admin_username  = input("admin username: ")
            target_username = input("jis ka account unlock karna hai: ")
            unlock_account(admin_username, target_username)

        elif choice == "5":
            username = input("username: ")
            view_user_info(username)

        elif choice == "6":
            print("program band ho raha hai -- khuda hafiz!")
            break

        else:
            print("galat choice -- 1 se 6 tak enter karo")
def set_security_question(username, question, answer):
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("select user_id from users where username = :1", [username])
    user = cursor.fetchone()

    if user is None:
        cursor.close()
        conn.close()
        return False

    cursor.execute("""
        update users
        set    security_question = :1,
               security_answer   = :2
        where  username = :3
    """, [question, answer.lower().strip(), username])

    conn.commit()
    cursor.close()
    conn.close()
    return True


def reset_password_with_question(username, answer, new_password):
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        select user_id, security_question, security_answer
        from   users
        where  username = :1
    """, [username])

    user = cursor.fetchone()

    if user is None:
        cursor.close()
        conn.close()
        return "not_found"

    if user[2] is None:
        cursor.close()
        conn.close()
        return "no_question"

    if answer.lower().strip() != user[2]:
        cursor.close()
        conn.close()
        return "wrong_answer"

    new_salt = username + "SALT2024"
    new_hash = hash_password(new_password, new_salt)

    cursor.execute("""
        update passwords
        set    password_hash = :1,
               salt          = :2,
               created_at    = sysdate
        where  user_id = :3
    """, [new_hash, new_salt, user[0]])

    cursor.execute("""
        update users
        set    status          = 'active',
               failed_attempts = 0,
               locked_at       = null
        where  username = :1
    """, [username])

    conn.commit()
    cursor.close()
    conn.close()
    return "success"


def get_security_question(username):
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("select security_question from users where username = :1", [username])
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None or row[0] is None:
        return None
    return row[0]

if __name__ == "__main__":
    main()