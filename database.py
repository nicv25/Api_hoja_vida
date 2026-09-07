import mysql.connector
from mysql.connector import Error


def conectar_bd():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="",  
            database="hoja_vida_db"
        )

        if conexion.is_connected():
            print("✅ Conexión exitosa con MySQL")
            return conexion

    except Error as error:
        # Este mensaje aparecerá en la terminal donde ejecutaste Flask.
        print(f"❌ Error de MySQL: {error}")

    return None