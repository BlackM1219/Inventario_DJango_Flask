from django.shortcuts import render, redirect
from django.contrib import messages
import requests

API_BASE_URL = "http://127.0.0.1:5000/api/productos"


def manejar_error_api(response):
    try:
        error_data = response.json()
        if "error" in error_data:
            return error_data["error"]
        elif "errores" in error_data:
            return ", ".join(error_data["errores"])
        else:
            return "Error desconocido en la API"
    except:
        return f"Error de conexión con la API (Código: {response.status_code})"


def lista_productos(request):
    try:
        response = requests.get(API_BASE_URL, timeout=5)

        if response.status_code == 200:
            data = response.json()
            productos = data.get("data", [])
            productos = sorted(productos, key=lambda x: x.get("id", 0))

            context = {"productos": productos, "total": len(productos)}
            return render(request, "productos/lista_productos.html", context)
        else:
            error = manejar_error_api(response)
            messages.error(request, f"Error al obtener productos: {error}")
            return render(request, "productos/lista_productos.html", {"productos": []})

    except requests.exceptions.ConnectionError:
        messages.error(
            request,
            "No se pudo conectar con el servidor Flask. Asegúrate de que esté ejecutándose en http://127.0.0.1:5000",
        )
        return render(request, "productos/lista_productos.html", {"productos": []})
    except requests.exceptions.Timeout:
        messages.error(request, "La conexión con el servidor tardó demasiado tiempo")
        return render(request, "productos/lista_productos.html", {"productos": []})
    except Exception as e:
        messages.error(request, f"Error inesperado: {str(e)}")
        return render(request, "productos/lista_productos.html", {"productos": []})


def detalle_producto(request, producto_id):
    try:
        response = requests.get(f"{API_BASE_URL}/{producto_id}", timeout=5)

        if response.status_code == 200:
            data = response.json()
            producto = data.get("data", {})
            return render(
                request, "productos/detalle_producto.html", {"producto": producto}
            )
        elif response.status_code == 404:
            messages.error(request, "Producto no encontrado")
            return redirect("lista_productos")
        else:
            error = manejar_error_api(response)
            messages.error(request, f"Error al obtener producto: {error}")
            return redirect("lista_productos")

    except requests.exceptions.ConnectionError:
        messages.error(request, "No se pudo conectar con el servidor Flask")
        return redirect("lista_productos")
    except Exception as e:
        messages.error(request, f"Error inesperado: {str(e)}")
        return redirect("lista_productos")


def crear_producto(request):
    if request.method == "POST":
        try:
            producto_data = {
                "nombre": request.POST.get("nombre", "").strip(),
                "categoria": request.POST.get("categoria", "").strip(),
                "descripcion": request.POST.get("descripcion", "").strip(),
                "precio": request.POST.get("precio", ""),
                "cantidad": request.POST.get("cantidad", ""),
                "fecha_vencimiento": request.POST.get("fecha_vencimiento", "").strip(),
            }

            response = requests.post(
                API_BASE_URL,
                json=producto_data,
                headers={"Content-Type": "application/json"},
                timeout=5,
            )

            if response.status_code == 201:
                messages.success(request, "Producto creado exitosamente")
                return redirect("lista_productos")
            else:
                error = manejar_error_api(response)
                messages.error(request, f"Error al crear producto: {error}")
                return render(
                    request,
                    "productos/crear_producto.html",
                    {"form_data": producto_data},
                )

        except requests.exceptions.ConnectionError:
            messages.error(request, "No se pudo conectar con el servidor Flask")
            return render(
                request, "productos/crear_producto.html", {"form_data": request.POST}
            )
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
            return render(
                request, "productos/crear_producto.html", {"form_data": request.POST}
            )

    return render(request, "productos/crear_producto.html")


def editar_producto(request, producto_id):
    if request.method == "POST":
        try:
            producto_data = {
                "nombre": request.POST.get("nombre", "").strip(),
                "categoria": request.POST.get("categoria", "").strip(),
                "descripcion": request.POST.get("descripcion", "").strip(),
                "precio": request.POST.get("precio", ""),
                "cantidad": request.POST.get("cantidad", ""),
                "fecha_vencimiento": request.POST.get("fecha_vencimiento", "").strip(),
            }

            response = requests.put(
                f"{API_BASE_URL}/{producto_id}",
                json=producto_data,
                headers={"Content-Type": "application/json"},
                timeout=5,
            )

            if response.status_code == 200:
                messages.success(request, "Producto actualizado exitosamente")
                return redirect("detalle_producto", producto_id=producto_id)
            else:
                error = manejar_error_api(response)
                messages.error(request, f"Error al actualizar producto: {error}")
                producto_data["id"] = producto_id
                return render(
                    request,
                    "productos/editar_producto.html",
                    {"producto": producto_data},
                )

        except requests.exceptions.ConnectionError:
            messages.error(request, "No se pudo conectar con el servidor Flask")
            return redirect("lista_productos")
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
            return redirect("lista_productos")

    try:
        response = requests.get(f"{API_BASE_URL}/{producto_id}", timeout=5)

        if response.status_code == 200:
            data = response.json()
            producto = data.get("data", {})
            return render(
                request, "productos/editar_producto.html", {"producto": producto}
            )
        elif response.status_code == 404:
            messages.error(request, "Producto no encontrado")
            return redirect("lista_productos")
        else:
            error = manejar_error_api(response)
            messages.error(request, f"Error al obtener producto: {error}")
            return redirect("lista_productos")

    except requests.exceptions.ConnectionError:
        messages.error(request, "No se pudo conectar con el servidor Flask")
        return redirect("lista_productos")
    except Exception as e:
        messages.error(request, f"Error inesperado: {str(e)}")
        return redirect("lista_productos")


def eliminar_producto(request, producto_id):
    if request.method == "POST":
        try:
            response = requests.delete(f"{API_BASE_URL}/{producto_id}", timeout=5)

            if response.status_code == 200:
                messages.success(request, "Producto eliminado exitosamente")
            elif response.status_code == 404:
                messages.error(request, "Producto no encontrado")
            else:
                error = manejar_error_api(response)
                messages.error(request, f"Error al eliminar producto: {error}")

        except requests.exceptions.ConnectionError:
            messages.error(request, "No se pudo conectar con el servidor Flask")
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")

    return redirect("lista_productos")
