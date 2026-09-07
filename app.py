from flask import Flask, jsonify, request
from database import conectar_bd

app = Flask(__name__)

"""PROBAR CONEXIÓN A LA BASE DE DATOS"""

@app.route("/probar_conexion")
def probar_conexion():
    conexion = conectar_bd()
    if conexion.is_connected():
        conexion.close()
        return {"mensaje": "Conexión exitosa con MySQL"}
    else:
        return {"mensaje": "Error al conectar con MySQL"}
    

@app.route("/")
def inicio():
    return "API Hoja de Vida funcionando"




"""REGISTRAR HOJAS DE VIDA"""

@app.route("/api/registrohv", methods=["POST"])
def registrohv():
    conexion = conectar_bd()
    cursor = conexion.cursor()
    datos = request.json
    valor = (
        datos["foto"],
        datos["nombres"],
        datos["apellidos"],
        datos["correo"],
        datos["direccion"],
        datos["perfil_profesional"]
    )


    buscar_sql = "SELECT * FROM hojas_vida WHERE correo = %s"
    cursor.execute(buscar_sql, (datos["correo"],))
    hoja_vida_existente = cursor.fetchone()
    if hoja_vida_existente:
        return jsonify({"mensaje": "El correo ya está registrado"}), 400

    sql = """INSERT INTO hojas_vida (foto, nombres, apellidos, correo, direccion, perfil_profesional) VALUES (%s, %s, %s, %s, %s, %s)"""
    cursor.execute(sql, valor)
    conexion.commit()

    id_generado = cursor.lastrowid

    cursor.close()
    conexion.close()
    return {"mensaje": "Hoja de vida registrada correctamente", "id": id_generado}



"""VERIFICAR HOJAS DE VIDA POR CORREO O ID"""

@app.route("/api/hojas-vida/correo/<string:correo>", methods=["GET"])
def obtener_hoja_vida_por_correo(correo):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    sql = "SELECT id, nombres, apellidos, correo, direccion, perfil_profesional FROM hojas_vida WHERE correo = %s"
    cursor.execute(sql, (correo,))
    hoja_vida = cursor.fetchone()
    cursor.close()
    conexion.close()
    return jsonify({
        "mensaje": "Hoja de vida encontrada",
        "data": hoja_vida
    })


"""LISTAR TODAS LAS HOJAS DE VIDA"""

@app.route("/api/hojas-vida/listado", methods=["GET"])
def listar_hojas_vida():
    conexion = conectar_bd()
    cursor = conexion.cursor()
    sql = "SELECT id, nombres, apellidos, correo, direccion, perfil_profesional FROM hojas_vida"
    cursor.execute(sql)
    hojas_vida = cursor.fetchall()
    cursor.close()
    conexion.close()
    return jsonify({
        "mensaje": "Hojas de vida encontradas",
        "data": hojas_vida
    })



"""VERIFICAR HOJAS DE VIDA POR ID"""

@app.route("/api/consultar_hoja_vida/<int:id>")
def obtener_hoja_vida_por_id(id):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    sql = "SELECT * FROM hojas_vida WHERE id = %s"
    cursor.execute(sql, (id,))
    hoja_vida = cursor.fetchone()
    cursor.close()
    conexion.close()
    return jsonify({
        "mensaje": "Hoja de vida encontrada",
        "data": hoja_vida,
        "id": id
    })

""" ELIMINAR HOJAS DE VIDA POR ID"""

@app.route("/api/borrar_hoja_vida/<int:id>", methods=["DELETE"])
def eliminar_hoja_vida(id):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    sql = """DELETE FROM hojas_vida WHERE id = %s"""
    cursor.execute(sql, (id,))

    if cursor.rowcount == 0:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "No se encontró la hoja de vida con el ID proporcionado"}), 404
    
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({
        "mensaje": "Hoja de vida eliminada correctamente",
        "id": id
    })




"""ACTUALIZAR HOJAS DE VIDA POR ID"""

@app.route("/api/actualizar_hoja_vida/<int:id>", methods=["PUT"])
def actualizar_hoja_vida(id):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    datos = request.json
    valor = (
        datos["foto"],
        datos["nombres"],
        datos["apellidos"],
        datos["correo"],
        datos["direccion"],
        datos["perfil_profesional"],
        id
    )

    sql = """UPDATE hojas_vida SET foto = %s, nombres = %s, apellidos = %s, correo = %s, direccion = %s, perfil_profesional = %s WHERE id = %s"""
    cursor.execute(sql, valor)



    if cursor.rowcount == 0:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "No se encontró la hoja de vida con el ID proporcionado"}), 404



    buscar_sql = "SELECT * FROM hojas_vida WHERE correo = %s AND id != %s"
    cursor.execute(buscar_sql, (datos["correo"], id))
    hoja_vida_existente = cursor.fetchone()
    if hoja_vida_existente:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "El correo ya está registrado por otra hoja de vida"}), 400



    
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({
        "mensaje": "Hoja de vida actualizada correctamente",
        "id": id
    })



@app.route("/api/hojas-vida")
def obtener_todas_hojas_vida(): 
    hojas_vida = [
        {
            "id": 1,
            "foto": "foto1.jpg",
            "nombres": "Nicolas",
            "apellidos": "Gonzalez",
            "correo": "nicolasgonzalez@gmail.com",
            "direccion": "Calle 123",
            "perfil_profesional": "Ingeniero de Software"
        }
    ]
    return hojas_vida


if __name__ == "__main__":
    app.run(debug=True)