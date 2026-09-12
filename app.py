from flask import Flask, jsonify, request
from database import conectar_bd


app = Flask(__name__)


# =========================================================
# RUTAS GENERALES
# =========================================================


"""PROBAR CONEXIÓN A LA BASE DE DATOS"""

@app.route("/probar_conexion", methods=["GET"])
def probar_conexion():
    conexion = None

    try:
        conexion = conectar_bd()

        if conexion.is_connected():
            return jsonify({"mensaje": "Conexión exitosa con MySQL"}), 200

        return jsonify({"mensaje": "Error al conectar con MySQL"}), 500

    except Exception as error:
        return jsonify({"mensaje": "No fue posible conectar con la base de datos", "error": str(error)}), 500

    finally:
        if conexion and conexion.is_connected():
            conexion.close()


"""RUTA DE INICIO"""

@app.route("/", methods=["GET"])
def inicio():
    return jsonify({"mensaje": "API Hoja de Vida funcionando"}), 200


# =========================================================
# RUTAS PARA HOJAS DE VIDA
# =========================================================


"""REGISTRAR UNA HOJA DE VIDA"""

@app.route("/api/registrohv", methods=["POST"])
def registrohv():
    conexion = None
    cursor = None

    try:
        datos = request.get_json(silent=True)

        if not datos:
            return jsonify({"mensaje": "Debe enviar la información en formato JSON"}), 400

        campos_obligatorios = ["nombres", "apellidos", "correo", "direccion", "perfil_profesional"]
        campos_faltantes = [campo for campo in campos_obligatorios if campo not in datos or datos[campo] in [None, ""]]

        if campos_faltantes:
            return jsonify({"mensaje": "Faltan campos obligatorios", "campos_faltantes": campos_faltantes}), 400

        conexion = conectar_bd()
        cursor = conexion.cursor()

        """VALIDAR QUE EL CORREO NO ESTÉ REGISTRADO"""

        sql_correo = "SELECT id FROM hojas_vida WHERE correo = %s"
        cursor.execute(sql_correo, (datos["correo"],))
        hoja_vida_existente = cursor.fetchone()

        if hoja_vida_existente:
            return jsonify({"mensaje": "El correo ya está registrado"}), 409

        """REGISTRAR LA HOJA DE VIDA"""

        sql = "INSERT INTO hojas_vida (foto, nombres, apellidos, correo, direccion, perfil_profesional) VALUES (%s, %s, %s, %s, %s, %s)"
        valores = (datos.get("foto"), datos["nombres"], datos["apellidos"], datos["correo"], datos["direccion"], datos["perfil_profesional"])

        cursor.execute(sql, valores)
        conexion.commit()

        id_generado = cursor.lastrowid

        return jsonify({"mensaje": "Hoja de vida registrada correctamente", "id": id_generado}), 201

    except Exception as error:
        if conexion:
            conexion.rollback()

        return jsonify({"mensaje": "Error al registrar la hoja de vida", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""LISTAR TODAS LAS HOJAS DE VIDA"""

@app.route("/api/hojas-vida/listado", methods=["GET"])
def listar_hojas_vida():
    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)

        # Listar todas las hojas de vida
        sql = "SELECT id, foto, nombres, apellidos, correo, direccion, perfil_profesional FROM hojas_vida"
        cursor.execute(sql)
        hojas_vida = cursor.fetchall()

        return jsonify({"mensaje": "Hojas de vida encontradas", "cantidad": len(hojas_vida), "data": hojas_vida}), 200

    except Exception as error:
        return jsonify({"mensaje": "Error al consultar las hojas de vida", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""CONSULTAR UNA HOJA DE VIDA POR CORREO"""

@app.route("/api/hojas-vida/correo/<string:correo>", methods=["GET"])
def obtener_hoja_vida_por_correo(correo):
    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)

        # Consultar la hoja de vida por correo
        sql = "SELECT id, foto, nombres, apellidos, correo, direccion, perfil_profesional FROM hojas_vida WHERE correo = %s"
        cursor.execute(sql, (correo,))
        hoja_vida = cursor.fetchone()

        if not hoja_vida:
            return jsonify({"mensaje": "No se encontró una hoja de vida con ese correo"}), 404

        return jsonify({"mensaje": "Hoja de vida encontrada", "data": hoja_vida}), 200

    except Exception as error:
        return jsonify({"mensaje": "Error al consultar la hoja de vida por correo", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""CONSULTAR UNA HOJA DE VIDA POR ID"""

@app.route("/api/consultar_hoja_vida/<int:id>", methods=["GET"])
def obtener_hoja_vida_por_id(id):
    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)

        # Consultar la hoja de vida por ID
        sql = "SELECT id, foto, nombres, apellidos, correo, direccion, perfil_profesional FROM hojas_vida WHERE id = %s"
        cursor.execute(sql, (id,))
        hoja_vida = cursor.fetchone()

        if not hoja_vida:
            return jsonify({"mensaje": "No se encontró la hoja de vida con el ID proporcionado"}), 404

        return jsonify({"mensaje": "Hoja de vida encontrada", "data": hoja_vida}), 200

    except Exception as error:
        return jsonify({"mensaje": "Error al consultar la hoja de vida por ID", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""ACTUALIZAR UNA HOJA DE VIDA POR ID"""

@app.route("/api/actualizar_hoja_vida/<int:id>", methods=["PUT"])
def actualizar_hoja_vida(id):
    conexion = None
    cursor = None

    try:
        datos = request.get_json(silent=True)

        if not datos:
            return jsonify({"mensaje": "Debe enviar la información en formato JSON"}), 400

        campos_obligatorios = ["nombres", "apellidos", "correo", "direccion", "perfil_profesional"]
        campos_faltantes = [campo for campo in campos_obligatorios if campo not in datos or datos[campo] in [None, ""]]

        if campos_faltantes:
            return jsonify({"mensaje": "Faltan campos obligatorios", "campos_faltantes": campos_faltantes}), 400

        conexion = conectar_bd()
        cursor = conexion.cursor()

        """VERIFICAR QUE LA HOJA DE VIDA EXISTA"""

        sql_existencia = "SELECT id FROM hojas_vida WHERE id = %s"
        cursor.execute(sql_existencia, (id,))
        hoja_vida = cursor.fetchone()

        if not hoja_vida:
            return jsonify({"mensaje": "No se encontró la hoja de vida con el ID proporcionado"}), 404

        """VALIDAR QUE EL CORREO NO PERTENEZCA A OTRA HOJA DE VIDA"""

        sql_correo = "SELECT id FROM hojas_vida WHERE correo = %s AND id != %s"
        cursor.execute(sql_correo, (datos["correo"], id))
        correo_existente = cursor.fetchone()

        if correo_existente:
            return jsonify({"mensaje": "El correo ya está registrado por otra hoja de vida"}), 409

        """ACTUALIZAR LA HOJA DE VIDA"""

        sql = "UPDATE hojas_vida SET foto = %s, nombres = %s, apellidos = %s, correo = %s, direccion = %s, perfil_profesional = %s WHERE id = %s"
        valores = (datos.get("foto"), datos["nombres"], datos["apellidos"], datos["correo"], datos["direccion"], datos["perfil_profesional"], id)

        cursor.execute(sql, valores)
        conexion.commit()

        return jsonify({"mensaje": "Hoja de vida actualizada correctamente", "id": id}), 200

    except Exception as error:
        if conexion:
            conexion.rollback()

        return jsonify({"mensaje": "Error al actualizar la hoja de vida", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""ELIMINAR UNA HOJA DE VIDA POR ID"""

@app.route("/api/borrar_hoja_vida/<int:id>", methods=["DELETE"])
def eliminar_hoja_vida(id):
    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        """VERIFICAR SI LA HOJA DE VIDA EXISTE"""

        sql_existencia = "SELECT id FROM hojas_vida WHERE id = %s"
        cursor.execute(sql_existencia, (id,))
        hoja_vida = cursor.fetchone()

        if not hoja_vida:
            return jsonify({"mensaje": "No se encontró la hoja de vida con el ID proporcionado"}), 404

        """ELIMINAR LA HOJA DE VIDA"""

        sql = "DELETE FROM hojas_vida WHERE id = %s"
        cursor.execute(sql, (id,))
        conexion.commit()

        return jsonify({"mensaje": "Hoja de vida eliminada correctamente", "id": id}), 200

    except Exception as error:
        if conexion:
            conexion.rollback()

        return jsonify({"mensaje": "Error al eliminar la hoja de vida", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# =========================================================
# RUTAS PARA ESTUDIOS
# =========================================================


"""OBTENER TODOS LOS ESTUDIOS DE UNA HOJA DE VIDA"""

@app.route("/api/hojas-vida/<int:hoja_vida_id>/estudios_obtener", methods=["GET"])
def obtener_estudios_por_hoja_vida(hoja_vida_id):
    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)

        """VERIFICAR QUE LA HOJA DE VIDA EXISTA"""

        sql_hoja_vida = "SELECT id FROM hojas_vida WHERE id = %s"
        cursor.execute(sql_hoja_vida, (hoja_vida_id,))
        hoja_vida = cursor.fetchone()

        if not hoja_vida:
            return jsonify({"mensaje": "No se encontró la hoja de vida con el ID proporcionado"}), 404

        """CONSULTAR LOS ESTUDIOS RELACIONADOS"""

        sql = "SELECT nivel_formacion, institucion, titulo_obtenido, fecha_inicio_academico, fecha_fin_academico, promedio FROM formaciones_academicas WHERE hoja_vida_id = %s ORDER BY fecha_inicio_academico DESC"
        cursor.execute(sql, (hoja_vida_id,))
        estudios = cursor.fetchall()

        return jsonify({"mensaje": "Estudios encontrados", "hoja_vida_id": hoja_vida_id, "cantidad": len(estudios), "data": estudios}), 200

    except Exception as error:
        return jsonify({"mensaje": "Error al consultar los estudios", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""REGISTRAR UN ESTUDIO PARA UNA HOJA DE VIDA"""

@app.route("/api/hojas-vida/<int:hoja_vida_id>/estudios_registrar", methods=["POST"])
def registrar_estudio_por_hoja_vida(hoja_vida_id):
    conexion = None
    cursor = None

    try:
        datos = request.get_json(silent=True)

        if not datos:
            return jsonify({"mensaje": "Debe enviar la información del estudio en formato JSON"}), 400

        campos_obligatorios = ["nivel_formacion", "institucion", "titulo_obtenido", "fecha_inicio_academico", "fecha_fin_academico", "promedio"]
        campos_faltantes = [campo for campo in campos_obligatorios if campo not in datos or datos[campo] in [None, ""]]

        if campos_faltantes:
            return jsonify({"mensaje": "Faltan campos obligatorios para registrar el estudio", "campos_faltantes": campos_faltantes}), 400

        conexion = conectar_bd()
        cursor = conexion.cursor()

        """VERIFICAR QUE LA HOJA DE VIDA EXISTA"""

        sql_hoja_vida = "SELECT id FROM hojas_vida WHERE id = %s"
        cursor.execute(sql_hoja_vida, (hoja_vida_id,))
        hoja_vida = cursor.fetchone()

        if not hoja_vida:
            return jsonify({"mensaje": "No se encontró la hoja de vida con el ID proporcionado"}), 404

        """REGISTRAR EL ESTUDIO"""

        sql = "INSERT INTO formaciones_academicas (hoja_vida_id, nivel_formacion, institucion, titulo_obtenido, fecha_inicio_academico, fecha_fin_academico, promedio) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        valores = (hoja_vida_id, datos["nivel_formacion"], datos["institucion"], datos["titulo_obtenido"], datos["fecha_inicio_academico"], datos["fecha_fin_academico"], datos["promedio"])

        cursor.execute(sql, valores)
        conexion.commit()

        id_estudio_generado = cursor.lastrowid

        return jsonify({"mensaje": "Estudio registrado correctamente", "id_estudio": id_estudio_generado, "hoja_vida_id": hoja_vida_id}), 201

    except Exception as error:
        if conexion:
            conexion.rollback()

        return jsonify({"mensaje": "Error al registrar el estudio", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""CONSULTAR UN ESTUDIO ESPECÍFICO"""

@app.route("/api/hojas-vida/<int:hoja_vida_id>/estudios/<int:estudio_id>", methods=["GET"])
def obtener_estudio_especifico(hoja_vida_id, estudio_id):
    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)
    
        # Consultar un estudio específico
        sql = "SELECT hoja_vida_id, nivel_formacion, institucion, titulo_obtenido, fecha_inicio_academico, fecha_fin_academico, promedio FROM formaciones_academicas WHERE id = %s AND hoja_vida_id = %s"
        cursor.execute(sql, (estudio_id, hoja_vida_id))
        estudio = cursor.fetchone()

        if not estudio:
            return jsonify({"mensaje": "No se encontró el estudio para la hoja de vida indicada"}), 404

        return jsonify({"mensaje": "Estudio encontrado", "data": estudio}), 200

    except Exception as error:
        return jsonify({"mensaje": "Error al consultar el estudio", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""ACTUALIZAR UN ESTUDIO"""

@app.route("/api/hojas-vida/<int:hoja_vida_id>/estudios/<int:estudio_id>", methods=["PUT"])
def actualizar_estudio(hoja_vida_id, estudio_id):
    conexion = None
    cursor = None

    try:
        datos = request.get_json(silent=True)

        if not datos:
            return jsonify({"mensaje": "Debe enviar la información del estudio en formato JSON"}), 400

        campos_obligatorios = ["nivel_formacion", "institucion", "titulo_obtenido", "fecha_inicio_academico", "fecha_fin_academico", "promedio"]
        campos_faltantes = [campo for campo in campos_obligatorios if campo not in datos or datos[campo] in [None, ""]]

        if campos_faltantes:
            return jsonify({"mensaje": "Faltan campos obligatorios para actualizar el estudio", "campos_faltantes": campos_faltantes}), 400

        conexion = conectar_bd()
        cursor = conexion.cursor()

        """ACTUALIZAR EL ESTUDIO RELACIONADO CON LA HOJA DE VIDA"""

        sql = "UPDATE formaciones_academicas SET nivel_formacion = %s, institucion = %s, titulo_obtenido = %s, fecha_inicio_academico = %s, fecha_fin_academico = %s, promedio = %s WHERE id = %s AND hoja_vida_id = %s"
        valores = (datos["nivel_formacion"], datos["institucion"], datos["titulo_obtenido"], datos["fecha_inicio_academico"], datos["fecha_fin_academico"], datos["promedio"], estudio_id, hoja_vida_id)

        cursor.execute(sql, valores)

        if cursor.rowcount == 0:
            return jsonify({"mensaje": "No se encontró el estudio para la hoja de vida indicada"}), 404

        conexion.commit()

        return jsonify({"mensaje": "Estudio actualizado correctamente", "id_estudio": estudio_id, "hoja_vida_id": hoja_vida_id}), 200

    except Exception as error:
        if conexion:
            conexion.rollback()

        return jsonify({"mensaje": "Error al actualizar el estudio", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""ELIMINAR UN ESTUDIO"""

@app.route("/api/hojas-vida/<int:hoja_vida_id>/estudios/<int:estudio_id>", methods=["DELETE"])
def eliminar_estudio(hoja_vida_id, estudio_id):
    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        """ELIMINAR EL ESTUDIO RELACIONADO CON LA HOJA DE VIDA"""

        sql = "DELETE FROM formaciones_academicas WHERE id = %s AND hoja_vida_id = %s"
        cursor.execute(sql, (estudio_id, hoja_vida_id))

        if cursor.rowcount == 0:
            return jsonify({"mensaje": "No se encontró el estudio para la hoja de vida indicada"}), 404

        conexion.commit()

        return jsonify({"mensaje": "Estudio eliminado correctamente", "id_estudio": estudio_id, "hoja_vida_id": hoja_vida_id}), 200

    except Exception as error:
        if conexion:
            conexion.rollback()

        return jsonify({"mensaje": "Error al eliminar el estudio", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# =========================================================
# RUTAS PARA EXPERIENCIAS LABORALES
# =========================================================

"""OBTENER TODAS LAS EXPERIENCIAS DE UNA HOJA DE VIDA"""

@app.route("/api/hojas-vida/<int:hoja_vida_id>/experiencias_obtener", methods=["GET"])
def obtener_experiencias_por_hoja_vida(hoja_vida_id):
    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)

        """VERIFICAR QUE LA HOJA DE VIDA EXISTA"""

        sql_hoja_vida = "SELECT id FROM hojas_vida WHERE id = %s"
        cursor.execute(sql_hoja_vida, (hoja_vida_id,))
        hoja_vida = cursor.fetchone()

        if not hoja_vida:
            return jsonify({"mensaje": "No se encontró la hoja de vida con el ID proporcionado"}), 404

        """CONSULTAR LAS EXPERIENCIAS RELACIONADAS"""

        sql = "SELECT hoja_vida_id, empresa, cargo, area, fecha_ingreso, fecha_retiro, funciones, referencia_laboral, certificado_laboral FROM experiencias WHERE hoja_vida_id = %s ORDER BY fecha_ingreso DESC"
        cursor.execute(sql, (hoja_vida_id,))
        experiencias = cursor.fetchall()

        return jsonify({"mensaje": "Experiencias laborales encontradas", "hoja_vida_id": hoja_vida_id, "cantidad": len(experiencias), "data": experiencias}), 200

    except Exception as error:
        return jsonify({"mensaje": "Error al consultar las experiencias laborales", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""REGISTRAR UNA EXPERIENCIA LABORAL"""

@app.route("/api/hojas-vida/<int:hoja_vida_id>/experiencias_registrar", methods=["POST"])
def registrar_experiencia_por_hoja_vida(hoja_vida_id):
    conexion = None
    cursor = None

    try:
        datos = request.get_json(silent=True)

        if not datos:
            return jsonify({"mensaje": "Debe enviar la información de la experiencia en formato JSON"}), 400

        campos_obligatorios = ["empresa", "cargo", "area", "fecha_ingreso", "funciones", "referencia_laboral"]
        campos_faltantes = [campo for campo in campos_obligatorios if campo not in datos or datos[campo] in [None, ""]]

        if campos_faltantes:
            return jsonify({"mensaje": "Faltan campos obligatorios para registrar la experiencia", "campos_faltantes": campos_faltantes}), 400

        conexion = conectar_bd()
        cursor = conexion.cursor()

        """VERIFICAR QUE LA HOJA DE VIDA EXISTA"""

        sql_hoja_vida = "SELECT id FROM hojas_vida WHERE id = %s"
        cursor.execute(sql_hoja_vida, (hoja_vida_id,))
        hoja_vida = cursor.fetchone()

        if not hoja_vida:
            return jsonify({"mensaje": "No se encontró la hoja de vida con el ID proporcionado"}), 404

        """REGISTRAR LA EXPERIENCIA LABORAL"""

        sql = "INSERT INTO experiencias (hoja_vida_id, empresa, cargo, area, fecha_ingreso, fecha_retiro, funciones, referencia_laboral, certificado_laboral) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        valores = (hoja_vida_id, datos["empresa"], datos["cargo"], datos["area"], datos["fecha_ingreso"], datos.get("fecha_retiro"), datos["funciones"], datos["referencia_laboral"], datos.get("certificado_laboral"))

        cursor.execute(sql, valores)
        conexion.commit()

        id_experiencia_generado = cursor.lastrowid

        return jsonify({"mensaje": "Experiencia laboral registrada correctamente", "id_experiencia": id_experiencia_generado, "hoja_vida_id": hoja_vida_id}), 201

    except Exception as error:
        if conexion:
            conexion.rollback()

        return jsonify({"mensaje": "Error al registrar la experiencia laboral", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""CONSULTAR UNA EXPERIENCIA LABORAL ESPECÍFICA"""

@app.route("/api/hojas-vida/<int:hoja_vida_id>/experiencias/<int:experiencia_id>", methods=["GET"])
def obtener_experiencia_especifica(hoja_vida_id, experiencia_id):
    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)

        sql = "SELECT hoja_vida_id, empresa, cargo, area, fecha_ingreso, fecha_retiro, funciones, referencia_laboral, certificado_laboral FROM experiencias WHERE id = %s AND hoja_vida_id = %s"
        cursor.execute(sql, (experiencia_id, hoja_vida_id))
        experiencia = cursor.fetchone()

        if not experiencia:
            return jsonify({"mensaje": "No se encontró la experiencia para la hoja de vida indicada"}), 404

        return jsonify({"mensaje": "Experiencia laboral encontrada", "data": experiencia}), 200

    except Exception as error:
        return jsonify({"mensaje": "Error al consultar la experiencia laboral", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""ACTUALIZAR UNA EXPERIENCIA LABORAL"""

@app.route("/api/hojas-vida/<int:hoja_vida_id>/experiencias/<int:experiencia_id>", methods=["PUT"])
def actualizar_experiencia(hoja_vida_id, experiencia_id):
    conexion = None
    cursor = None

    try:
        datos = request.get_json(silent=True)

        if not datos:
            return jsonify({"mensaje": "Debe enviar la información de la experiencia en formato JSON"}), 400

        """VERIFICAR QUE SE HAYAN ENVIADO LOS CAMPOS OBLIGATORIOS"""

        campos_obligatorios = ["empresa", "cargo", "area", "fecha_ingreso", "funciones", "referencia_laboral"]
        campos_faltantes = [campo for campo in campos_obligatorios if campo not in datos or datos[campo] in [None, ""]]

        if campos_faltantes:
            return jsonify({"mensaje": "Faltan campos obligatorios para actualizar la experiencia", "campos_faltantes": campos_faltantes}), 400

        conexion = conectar_bd()
        cursor = conexion.cursor()

        """ACTUALIZAR LA EXPERIENCIA RELACIONADA CON LA HOJA DE VIDA"""

        sql = "UPDATE experiencias SET empresa = %s, cargo = %s, area = %s, fecha_ingreso = %s, fecha_retiro = %s, funciones = %s, referencia_laboral = %s, certificado_laboral = %s WHERE id = %s AND hoja_vida_id = %s"
        valores = (datos["empresa"], datos["cargo"], datos["area"], datos["fecha_ingreso"], datos.get("fecha_retiro"), datos["funciones"], datos["referencia_laboral"], datos.get("certificado_laboral"), experiencia_id, hoja_vida_id)

        cursor.execute(sql, valores)

        if cursor.rowcount == 0:
            return jsonify({"mensaje": "No se encontró la experiencia para la hoja de vida indicada"}), 404

        conexion.commit()

        return jsonify({"mensaje": "Experiencia laboral actualizada correctamente", "id_experiencia": experiencia_id, "hoja_vida_id": hoja_vida_id}), 200

    except Exception as error:
        if conexion:
            conexion.rollback()

        return jsonify({"mensaje": "Error al actualizar la experiencia laboral", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""ELIMINAR UNA EXPERIENCIA LABORAL"""

@app.route("/api/hojas-vida/<int:hoja_vida_id>/experiencias/<int:experiencia_id>", methods=["DELETE"])
def eliminar_experiencia(hoja_vida_id, experiencia_id):
    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        """ELIMINAR LA EXPERIENCIA RELACIONADA CON LA HOJA DE VIDA"""

        sql = "DELETE FROM experiencias WHERE id = %s AND hoja_vida_id = %s"
        cursor.execute(sql, (experiencia_id, hoja_vida_id))

        if cursor.rowcount == 0:
            return jsonify({"mensaje": "No se encontró la experiencia para la hoja de vida indicada"}), 404

        conexion.commit()

        return jsonify({"mensaje": "Experiencia laboral eliminada correctamente", "id_experiencia": experiencia_id, "hoja_vida_id": hoja_vida_id}), 200

    except Exception as error:
        if conexion:
            conexion.rollback()

        return jsonify({"mensaje": "Error al eliminar la experiencia laboral", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()



# =========================================================
# RUTAS PARA HABILIDADES
# =========================================================


"""OBTENER TODAS LAS HABILIDADES DE UNA EXPERIENCIA"""

@app.route("/api/experiencias/<int:experiencia_id>/habilidades_obtener", methods=["GET"])
def obtener_habilidades_por_experiencia(experiencia_id):
    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)

        """VERIFICAR QUE LA EXPERIENCIA EXISTA"""

        sql_experiencia = "SELECT id FROM experiencias WHERE id = %s"
        cursor.execute(sql_experiencia, (experiencia_id,))
        experiencia = cursor.fetchone()

        if not experiencia:
            return jsonify({"mensaje": "No se encontró la experiencia con el ID proporcionado"}), 404

        """CONSULTAR LAS HABILIDADES RELACIONADAS"""

        sql = "SELECT id, experiencia_id, nombre_habilidad FROM habilidades WHERE experiencia_id = %s ORDER BY id ASC"
        cursor.execute(sql, (experiencia_id,))
        habilidades = cursor.fetchall()

        return jsonify({"mensaje": "Habilidades encontradas", "experiencia_id": experiencia_id, "cantidad": len(habilidades), "data": habilidades}), 200

    except Exception as error:
        return jsonify({"mensaje": "Error al consultar las habilidades", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""REGISTRAR UNA HABILIDAD PARA UNA EXPERIENCIA"""

@app.route("/api/experiencias/<int:experiencia_id>/habilidades_registrar", methods=["POST"])
def registrar_habilidad_por_experiencia(experiencia_id):
    conexion = None
    cursor = None

    try:
        datos = request.get_json(silent=True)

        if not datos:
            return jsonify({"mensaje": "Debe enviar la información de la habilidad en formato JSON"}), 400

        if "nombre_habilidad" not in datos or datos["nombre_habilidad"] in [None, ""]:
            return jsonify({"mensaje": "El campo nombre_habilidad es obligatorio"}), 400

        conexion = conectar_bd()
        cursor = conexion.cursor()

        """VERIFICAR QUE LA EXPERIENCIA EXISTA"""

        sql_experiencia = "SELECT id FROM experiencias WHERE id = %s"
        cursor.execute(sql_experiencia, (experiencia_id,))
        experiencia = cursor.fetchone()

        if not experiencia:
            return jsonify({"mensaje": "No se encontró la experiencia con el ID proporcionado"}), 404

        """VERIFICAR SI LA HABILIDAD YA ESTÁ REGISTRADA"""

        sql_habilidad = "SELECT id FROM habilidades WHERE experiencia_id = %s AND nombre_habilidad = %s"
        cursor.execute(sql_habilidad, (experiencia_id, datos["nombre_habilidad"]))
        habilidad_existente = cursor.fetchone()

        if habilidad_existente:
            return jsonify({"mensaje": "La habilidad ya está registrada para esta experiencia"}), 409

        """REGISTRAR LA HABILIDAD"""

        sql = "INSERT INTO habilidades (experiencia_id, nombre_habilidad) VALUES (%s, %s)"
        cursor.execute(sql, (experiencia_id, datos["nombre_habilidad"]))
        conexion.commit()

        id_habilidad_generado = cursor.lastrowid

        return jsonify({"mensaje": "Habilidad registrada correctamente", "id_habilidad": id_habilidad_generado, "experiencia_id": experiencia_id}), 201

    except Exception as error:
        if conexion:
            conexion.rollback()

        return jsonify({"mensaje": "Error al registrar la habilidad", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""ACTUALIZAR UNA HABILIDAD"""

@app.route("/api/experiencias/<int:experiencia_id>/habilidades/<int:habilidad_id>", methods=["PUT"])
def actualizar_habilidad(experiencia_id, habilidad_id):
    conexion = None
    cursor = None

    try:
        datos = request.get_json(silent=True)

        if not datos:
            return jsonify({"mensaje": "Debe enviar la información de la habilidad en formato JSON"}), 400

        if "nombre_habilidad" not in datos or datos["nombre_habilidad"] in [None, ""]:
            return jsonify({"mensaje": "El campo nombre_habilidad es obligatorio"}), 400

        conexion = conectar_bd()
        cursor = conexion.cursor()

        """ACTUALIZAR LA HABILIDAD RELACIONADA CON LA EXPERIENCIA"""

        sql = "UPDATE habilidades SET nombre_habilidad = %s WHERE id = %s AND experiencia_id = %s"
        cursor.execute(sql, (datos["nombre_habilidad"], habilidad_id, experiencia_id))

        if cursor.rowcount == 0:
            return jsonify({"mensaje": "No se encontró la habilidad para la experiencia indicada"}), 404

        conexion.commit()

        return jsonify({"mensaje": "Habilidad actualizada correctamente", "id_habilidad": habilidad_id, "experiencia_id": experiencia_id}), 200

    except Exception as error:
        if conexion:
            conexion.rollback()

        return jsonify({"mensaje": "Error al actualizar la habilidad", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""ELIMINAR UNA HABILIDAD"""

@app.route("/api/experiencias/<int:experiencia_id>/habilidades/<int:habilidad_id>", methods=["DELETE"])
def eliminar_habilidad(experiencia_id, habilidad_id):
    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        """ELIMINAR LA HABILIDAD RELACIONADA CON LA EXPERIENCIA"""

        sql = "DELETE FROM habilidades WHERE id = %s AND experiencia_id = %s"
        cursor.execute(sql, (habilidad_id, experiencia_id))

        if cursor.rowcount == 0:
            return jsonify({"mensaje": "No se encontró la habilidad para la experiencia indicada"}), 404

        conexion.commit()

        return jsonify({"mensaje": "Habilidad eliminada correctamente", "id_habilidad": habilidad_id, "experiencia_id": experiencia_id}), 200

    except Exception as error:
        if conexion:
            conexion.rollback()

        return jsonify({"mensaje": "Error al eliminar la habilidad", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# =========================================================
# RUTAS PARA CURSOS
# =========================================================


"""OBTENER TODOS LOS CURSOS DE UNA HOJA DE VIDA"""

@app.route("/api/hojas-vida/<int:hoja_vida_id>/cursos_obtener", methods=["GET"])
def obtener_cursos_por_hoja_vida(hoja_vida_id):
    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)

        """VERIFICAR QUE LA HOJA DE VIDA EXISTA"""

        sql_hoja_vida = "SELECT id FROM hojas_vida WHERE id = %s"
        cursor.execute(sql_hoja_vida, (hoja_vida_id,))
        hoja_vida = cursor.fetchone()

        if not hoja_vida:
            return jsonify({"mensaje": "No se encontró la hoja de vida con el ID proporcionado"}), 404

        """CONSULTAR LOS CURSOS RELACIONADOS"""

        sql = "SELECT id, hoja_vida_id, nombre_curso FROM cursos WHERE hoja_vida_id = %s ORDER BY id ASC"
        cursor.execute(sql, (hoja_vida_id,))
        cursos = cursor.fetchall()

        return jsonify({"mensaje": "Cursos encontrados", "hoja_vida_id": hoja_vida_id, "cantidad": len(cursos), "data": cursos}), 200

    except Exception as error:
        return jsonify({"mensaje": "Error al consultar los cursos", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""REGISTRAR UN CURSO PARA UNA HOJA DE VIDA"""

@app.route("/api/hojas-vida/<int:hoja_vida_id>/cursos_registrar", methods=["POST"])
def registrar_curso_por_hoja_vida(hoja_vida_id):
    conexion = None
    cursor = None

    try:
        datos = request.get_json(silent=True)

        if not datos:
            return jsonify({"mensaje": "Debe enviar la información del curso en formato JSON"}), 400

        if "nombre_curso" not in datos or datos["nombre_curso"] in [None, ""]:
            return jsonify({"mensaje": "El campo nombre_curso es obligatorio"}), 400

        conexion = conectar_bd()
        cursor = conexion.cursor()

        """VERIFICAR QUE LA HOJA DE VIDA EXISTA"""

        sql_hoja_vida = "SELECT id FROM hojas_vida WHERE id = %s"
        cursor.execute(sql_hoja_vida, (hoja_vida_id,))
        hoja_vida = cursor.fetchone()

        if not hoja_vida:
            return jsonify({"mensaje": "No se encontró la hoja de vida con el ID proporcionado"}), 404

        """REGISTRAR EL CURSO"""

        sql = "INSERT INTO cursos (hoja_vida_id, nombre_curso) VALUES (%s, %s)"
        cursor.execute(sql, (hoja_vida_id, datos["nombre_curso"]))
        conexion.commit()

        id_curso_generado = cursor.lastrowid

        return jsonify({"mensaje": "Curso registrado correctamente", "id_curso": id_curso_generado, "hoja_vida_id": hoja_vida_id}), 201

    except Exception as error:
        if conexion:
            conexion.rollback()

        return jsonify({"mensaje": "Error al registrar el curso", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""CONSULTAR UN CURSO ESPECÍFICO"""

@app.route("/api/hojas-vida/<int:hoja_vida_id>/cursos/<int:curso_id>", methods=["GET"])
def obtener_curso_especifico(hoja_vida_id, curso_id):
    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)

        sql = "SELECT id, hoja_vida_id, nombre_curso FROM cursos WHERE id = %s AND hoja_vida_id = %s"
        cursor.execute(sql, (curso_id, hoja_vida_id))
        curso = cursor.fetchone()

        if not curso:
            return jsonify({"mensaje": "No se encontró el curso para la hoja de vida indicada"}), 404

        return jsonify({"mensaje": "Curso encontrado", "data": curso}), 200

    except Exception as error:
        return jsonify({"mensaje": "Error al consultar el curso", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""ACTUALIZAR UN CURSO"""

@app.route("/api/hojas-vida/<int:hoja_vida_id>/cursos/<int:curso_id>", methods=["PUT"])
def actualizar_curso(hoja_vida_id, curso_id):
    conexion = None
    cursor = None

    try:
        datos = request.get_json(silent=True)

        if not datos:
            return jsonify({"mensaje": "Debe enviar la información del curso en formato JSON"}), 400

        if "nombre_curso" not in datos or datos["nombre_curso"] in [None, ""]:
            return jsonify({"mensaje": "El campo nombre_curso es obligatorio"}), 400

        conexion = conectar_bd()
        cursor = conexion.cursor()

        """ACTUALIZAR EL CURSO RELACIONADO CON LA HOJA DE VIDA"""

        sql = "UPDATE cursos SET nombre_curso = %s WHERE id = %s AND hoja_vida_id = %s"
        cursor.execute(sql, (datos["nombre_curso"], curso_id, hoja_vida_id))

        if cursor.rowcount == 0:
            return jsonify({"mensaje": "No se encontró el curso para la hoja de vida indicada"}), 404

        conexion.commit()

        return jsonify({"mensaje": "Curso actualizado correctamente", "id_curso": curso_id, "hoja_vida_id": hoja_vida_id}), 200

    except Exception as error:
        if conexion:
            conexion.rollback()

        return jsonify({"mensaje": "Error al actualizar el curso", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


"""ELIMINAR UN CURSO"""

@app.route("/api/hojas-vida/<int:hoja_vida_id>/cursos/<int:curso_id>", methods=["DELETE"])
def eliminar_curso(hoja_vida_id, curso_id):
    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        """ELIMINAR EL CURSO RELACIONADO CON LA HOJA DE VIDA"""

        sql = "DELETE FROM cursos WHERE id = %s AND hoja_vida_id = %s"
        cursor.execute(sql, (curso_id, hoja_vida_id))

        if cursor.rowcount == 0:
            return jsonify({"mensaje": "No se encontró el curso para la hoja de vida indicada"}), 404

        conexion.commit()

        return jsonify({"mensaje": "Curso eliminado correctamente", "id_curso": curso_id, "hoja_vida_id": hoja_vida_id}), 200

    except Exception as error:
        if conexion:
            conexion.rollback()

        return jsonify({"mensaje": "Error al eliminar el curso", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()



# =========================================================
# RUTA PARA CONSULTA COMPLETA DE LA HOJA DE VIDA
# =========================================================


"""CONSULTAR TODA LA INFORMACIÓN DE UNA HOJA DE VIDA"""

@app.route("/api/hojas-vida/<int:hoja_vida_id>/consulta_completa", methods=["GET"])
def consultar_hoja_vida_completa(hoja_vida_id):
    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)

        """CONSULTAR LOS DATOS PERSONALES"""

        sql_hoja_vida = "SELECT foto, nombres, apellidos, correo, direccion, perfil_profesional, fecha_registro FROM hojas_vida WHERE id = %s"
        cursor.execute(sql_hoja_vida, (hoja_vida_id,))
        hoja_vida = cursor.fetchone()

        if not hoja_vida:
            return jsonify({"mensaje": "No se encontró la hoja de vida con el ID proporcionado"}), 404

        """CONSULTAR LAS FORMACIONES ACADÉMICAS"""

        sql_estudios = "SELECT nivel_formacion, institucion, titulo_obtenido, fecha_inicio_academico, fecha_fin_academico, promedio FROM formaciones_academicas WHERE hoja_vida_id = %s ORDER BY fecha_inicio_academico DESC"
        cursor.execute(sql_estudios, (hoja_vida_id,))
        estudios = cursor.fetchall()

        """CONSULTAR LOS CURSOS"""

        sql_cursos = "SELECT nombre_curso FROM cursos WHERE hoja_vida_id = %s ORDER BY nombre_curso ASC"
        cursor.execute(sql_cursos, (hoja_vida_id,))
        cursos = cursor.fetchall()

        """CONSULTAR LAS EXPERIENCIAS LABORALES"""

        sql_experiencias = "SELECT id, hoja_vida_id, empresa, cargo, area, fecha_ingreso, fecha_retiro, funciones, referencia_laboral, certificado_laboral FROM experiencias WHERE hoja_vida_id = %s ORDER BY fecha_ingreso DESC"
        cursor.execute(sql_experiencias, (hoja_vida_id,))
        experiencias = cursor.fetchall()

        """CONSULTAR LAS HABILIDADES DE CADA EXPERIENCIA"""

        for experiencia in experiencias:
            sql_habilidades = "SELECT nombre_habilidad FROM habilidades WHERE experiencia_id = %s ORDER BY id ASC"
            cursor.execute(sql_habilidades, (experiencia["id"],))
            habilidades = cursor.fetchall()
            experiencia["habilidades"] = habilidades

        """ORGANIZAR TODA LA INFORMACIÓN"""

        resultado = {
            "datos_personales": hoja_vida,
            "estudios": estudios,
            "cursos": cursos,
            "experiencias": experiencias
        }

        return jsonify({"mensaje": "Información completa de la hoja de vida encontrada", "data": resultado}), 200

    except Exception as error:
        return jsonify({"mensaje": "Error al consultar la información completa de la hoja de vida", "error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()



# =========================================================
# INICIAR LA APLICACIÓN
# =========================================================


if __name__ == "__main__":
    app.run(debug=True)