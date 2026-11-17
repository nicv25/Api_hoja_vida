# crear_admin.py
# Crea una cuenta con rol reclutador. El reclutador NO se registra desde el formulario público,
# por eso se crea con este programa independiente, ejecutado desde la terminal:
#   python crear_admin.py

from getpass import getpass

from werkzeug.security import generate_password_hash

from app import validar_datos_registro
from database import conectar_bd


def crear_reclutador():
    """SOLICITAR LOS DATOS DESDE LA TERMINAL"""

    nombre = input("Nombre del reclutador: ").strip()
    correo = input("Correo electrónico: ").strip().lower()
    password = getpass("Contraseña: ")

    # Se aplican las mismas validaciones del registro público (campos obligatorios y contraseña segura)
    error_validacion = validar_datos_registro({"nombre": nombre, "correo": correo, "password": password})

    if error_validacion:
        print("Verifica los datos:", error_validacion["mensaje"])
        return

    conexion = conectar_bd()

    if not conexion:
        print("No fue posible conectar con la base de datos")
        return

    cursor = conexion.cursor()

    try:
        """VERIFICAR QUE EL CORREO NO ESTÉ REGISTRADO"""

        cursor.execute("SELECT id FROM usuarios WHERE correo = %s", (correo,))

        if cursor.fetchone():
            print("Este correo ya está registrado")
            return

        """GUARDAR EL RECLUTADOR CON LA CONTRASEÑA PROTEGIDA (HASH) Y LA CUENTA ACTIVA"""

        password_hash = generate_password_hash(password)

        sql = "INSERT INTO usuarios (nombre, correo, password, rol, estado) VALUES (%s, %s, %s, 'reclutador', 1)"
        cursor.execute(sql, (nombre, correo, password_hash))
        conexion.commit()

        print("Reclutador creado correctamente")

    except Exception as error:
        conexion.rollback()
        print("Error:", error)

    finally:
        cursor.close()
        conexion.close()


if __name__ == "__main__":
    crear_reclutador()
