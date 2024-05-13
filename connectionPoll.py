import pymysql
import os

class ConnectionPool:
    def __init__(self, max_connections):
        self.max_connections = max_connections
        self.connections = []

    def get_connection(self):
        if len(self.connections) < self.max_connections:
            # Crie uma nova conexão e adicione à lista
            conn = pymysql.connect(
                charset="utf8mb4",
                connect_timeout=30,
                cursorclass=pymysql.cursors.DictCursor,
                db=os.getenv('MYSQL_DB'),
                host=os.getenv('MYSQL_HOST'),
                password=os.getenv('MYSQL_PASSWORD'),
                read_timeout=30,
                port=11025,
                user=os.getenv('MYSQL_USER'),
                write_timeout=30,
            )
            self.connections.append(conn)
            return conn
        else:
            # Reutilize uma conexão existente
            return self.connections.pop(0)

    def return_connection(self, conn):
        self.connections.append(conn)