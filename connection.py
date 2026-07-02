import cx_Oracle

cx_Oracle.init_oracle_client(lib_dir=r"C:\instantclient_21_8")

# database details
HOST     = "localhost"
PORT     = 1521
SERVICE  = "xe"
USERNAME = "username"
PASSWORD = "password"

# connection function
def get_connection():
    dsn  = cx_Oracle.makedsn(HOST, PORT, service_name=SERVICE)
    conn = cx_Oracle.connect(USERNAME, PASSWORD, dsn)
    return conn