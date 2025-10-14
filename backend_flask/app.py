from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

INVENTARIO_FILE = "inventario.json"


def cargar_inventario():
    """Carga el inventario desde el archivo JSON"""
    if not os.path.exists(INVENTARIO_FILE):
        return []
    try:
        with open(INVENTARIO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def guardar_inventario(inventario):
    """Guarda el inventario en el archivo JSON"""
    with open(INVENTARIO_FILE, "w", encoding="utf-8") as f:
        json.dump(inventario, f, indent=4, ensure_ascii=False)


def validar_producto(data):
    """Valida los datos del producto"""
    errores = []

    if not data.get("nombre"):
        errores.append("El nombre es requerido")

    if not data.get("categoria"):
        errores.append("La categoría es requerida")

    if not data.get("precio"):
        errores.append("El precio es requerido")
    else:
        try:
            precio = float(data.get("precio"))
            if precio < 0:
                errores.append("El precio debe ser mayor o igual a 0")
        except (ValueError, TypeError):
            errores.append("El precio debe ser un número válido")

    if not data.get("cantidad"):
        errores.append("La cantidad es requerida")
    else:
        try:
            cantidad = int(data.get("cantidad"))
            if cantidad < 0:
                errores.append("La cantidad debe ser mayor o igual a 0")
        except (ValueError, TypeError):
            errores.append("La cantidad debe ser un número entero válido")

    # Validar fecha de vencimiento si existe
    if data.get("fecha_vencimiento"):
        try:
            datetime.strptime(data.get("fecha_vencimiento"), "%Y-%m-%d")
        except ValueError:
            errores.append("La fecha de vencimiento debe tener formato YYYY-MM-DD")

    return errores


@app.route("/")
def home():
    """Endpoint de bienvenida"""
    return jsonify(
        {
            "mensaje": "API de Gestión de Inventario",
            "version": "1.0",
            "endpoints": {
                "GET /api/productos": "Obtener todos los productos",
                "GET /api/productos/<id>": "Obtener un producto específico",
                "POST /api/productos": "Crear un nuevo producto",
                "PUT /api/productos/<id>": "Actualizar un producto",
                "DELETE /api/productos/<id>": "Eliminar un producto",
            },
        }
    )


@app.route("/api/productos", methods=["GET"])
def obtener_productos():
    """GET - Obtener todos los productos"""
    try:
        inventario = cargar_inventario()
        return (
            jsonify({"success": True, "data": inventario, "total": len(inventario)}),
            200,
        )
    except Exception as e:
        return (
            jsonify(
                {"success": False, "error": f"Error al obtener productos: {str(e)}"}
            ),
            500,
        )


@app.route("/api/productos/<int:producto_id>", methods=["GET"])
def obtener_producto(producto_id):
    """GET - Obtener un producto específico por ID"""
    try:
        inventario = cargar_inventario()
        producto = next((p for p in inventario if p["id"] == producto_id), None)

        if producto:
            return jsonify({"success": True, "data": producto}), 200
        else:
            return jsonify({"success": False, "error": "Producto no encontrado"}), 404
    except Exception as e:
        return (
            jsonify(
                {"success": False, "error": f"Error al obtener producto: {str(e)}"}
            ),
            500,
        )


@app.route("/api/productos", methods=["POST"])
def crear_producto():
    """POST - Crear un nuevo producto"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No se recibieron datos"}), 400

        # Validar datos
        errores = validar_producto(data)
        if errores:
            return jsonify({"success": False, "errores": errores}), 400

        inventario = cargar_inventario()

        # Generar nuevo ID
        nuevo_id = max([p["id"] for p in inventario], default=0) + 1

        # Crear nuevo producto
        nuevo_producto = {
            "id": nuevo_id,
            "nombre": data.get("nombre"),
            "categoria": data.get("categoria"),
            "descripcion": data.get("descripcion", ""),
            "precio": float(data.get("precio")),
            "cantidad": int(data.get("cantidad")),
            "fecha_vencimiento": data.get("fecha_vencimiento", ""),
            "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        inventario.append(nuevo_producto)
        guardar_inventario(inventario)

        return (
            jsonify(
                {
                    "success": True,
                    "mensaje": "Producto creado exitosamente",
                    "data": nuevo_producto,
                }
            ),
            201,
        )
    except Exception as e:
        return (
            jsonify({"success": False, "error": f"Error al crear producto: {str(e)}"}),
            500,
        )


@app.route("/api/productos/<int:producto_id>", methods=["PUT"])
def actualizar_producto(producto_id):
    """PUT - Actualizar un producto existente"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No se recibieron datos"}), 400

        # Validar datos
        errores = validar_producto(data)
        if errores:
            return jsonify({"success": False, "errores": errores}), 400

        inventario = cargar_inventario()
        producto = next((p for p in inventario if p["id"] == producto_id), None)

        if not producto:
            return jsonify({"success": False, "error": "Producto no encontrado"}), 404

        # Actualizar producto
        producto["nombre"] = data.get("nombre")
        producto["categoria"] = data.get("categoria")
        producto["descripcion"] = data.get("descripcion", "")
        producto["precio"] = float(data.get("precio"))
        producto["cantidad"] = int(data.get("cantidad"))
        producto["fecha_vencimiento"] = data.get("fecha_vencimiento", "")
        producto["fecha_actualizacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        guardar_inventario(inventario)

        return (
            jsonify(
                {
                    "success": True,
                    "mensaje": "Producto actualizado exitosamente",
                    "data": producto,
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify(
                {"success": False, "error": f"Error al actualizar producto: {str(e)}"}
            ),
            500,
        )


@app.route("/api/productos/<int:producto_id>", methods=["DELETE"])
def eliminar_producto(producto_id):
    """DELETE - Eliminar un producto"""
    try:
        inventario = cargar_inventario()
        producto = next((p for p in inventario if p["id"] == producto_id), None)

        if not producto:
            return jsonify({"success": False, "error": "Producto no encontrado"}), 404

        inventario = [p for p in inventario if p["id"] != producto_id]
        guardar_inventario(inventario)

        return (
            jsonify({"success": True, "mensaje": "Producto eliminado exitosamente"}),
            200,
        )
    except Exception as e:
        return (
            jsonify(
                {"success": False, "error": f"Error al eliminar producto: {str(e)}"}
            ),
            500,
        )


@app.errorhandler(404)
def no_encontrado(e):
    return jsonify({"success": False, "error": "Endpoint no encontrado"}), 404


@app.errorhandler(500)
def error_servidor(e):
    return jsonify({"success": False, "error": "Error interno del servidor"}), 500


if __name__ == "__main__":
    # Crear archivo inventario.json si no existe
    if not os.path.exists(INVENTARIO_FILE):
        guardar_inventario([])

    app.run(debug=True, port=5000)
