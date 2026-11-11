#Janerys M. Ortiz Aviles (Y00631857)

print("Janerys M. Ortiz Aviles (Y00631857)")

"""BASE EDUCATIVA INSEGURA. Corregir los TODO antes de la entrega."""
import json
from pathlib import Path
#el import para la funcion autenticar()
from seguridad import verificar_clave
#el import para la funcion registrar_evento()
from datetime import datetime

RAIZ = Path(__file__).resolve().parent
DATOS = RAIZ / "inventario.json"
USUARIOS = RAIZ / "usuarios.json"
LOG = RAIZ / "auditoria.jsonl"
 

def cargar_inventario():
    # TODO: controlar archivo ausente y JSON inválido. No sobrescribirlos.
    try:
        return json.loads(
            DATOS.read_text(encoding="utf-8")
        )

    except FileNotFoundError:
        print("ERROR: No se encontró el archivo 'inventario.json'.")
        return []

    except json.JSONDecodeError:
        print("ERROR: El archivo 'inventario.json' contiene un JSON inválido.")
        return []


def guardar_inventario(productos):
    DATOS.write_text(json.dumps(productos, indent=2), encoding="utf-8")


def registrar_evento(usuario, accion, resultado, **detalles):
    # TODO: guardar un objeto JSON por línea; fecha/hora, usuario, acción,
    # resultado y detalles no sensibles. Nunca guardar contraseña ni hash.
    with open(LOG, "a", encoding="utf-8") as f: #abre el archivo
        #convierte la info del evento al formato json
        json.dump({
            "fecha": datetime.now().isoformat(),
            "usuario": usuario,
            "accion": accion,
            "resultado": resultado,
            **detalles
        }, f)
        f.write("\n")#basicamente escribe un enter para que cada evento quede en una linea diferente


def autenticar(nombre, clave):
    usuarios = json.loads(USUARIOS.read_text(encoding="utf-8"))
    # TODO: integrar seguridad.py y migrar usuarios.json sin claves legibles.
    for usuario in usuarios:
        if usuario["usuario"] == nombre: #se verif. que el usuario exista
            if verificar_clave(usuario["password_hash"], clave): #se verif. que el pass. del usuario coincida con el hash
                registrar_evento(nombre, "login", "exitoso") #registra el acceso
                return {"usuario": nombre, "rol": usuario["rol"]}
    # TODO: registrar también el intento fallido.
    registrar_evento(nombre, "login", "fallido") #registra el intento fallido
    print("Credenciales incorrectas.")
    return None


def consultar_inventario(sesion):
    # TODO: rechazar si no existe sesión válida.
    if sesion is None: #Verifica si la sesion es valida
        print("ERROR: Sesion invalida. No puede acceder.")
        return
    productos = cargar_inventario() #si es valida, carga y muestra los prod.
    for producto in productos:
        print(producto["id"], producto["nombre"], producto["cantidad"])


def modificar_cantidad(sesion, identificador, entrada):
    # TODO: verificar sesión y rol AQUÍ, antes de modificar.
    if sesion is None: #verifica que la sesion este "activa"
        print("Acceso denegado.")
        return False
    if sesion["rol"] != "admin": #verifica que el rol sea el de administrador

        #registra el rechazo de modificar por falta de los permisos 
        registrar_evento(
            sesion["usuario"], "modificar", "rechazado"
        )
        print("No puede modificar. No tiene los permisos")
        return False

    # TODO: validar entero entre 0 y 1000, sin interrumpir el programa
    try: #la entrada es convertida a un int
        cantidad = int(entrada)
        if not (0 <= cantidad <= 1000): #verifica que este dentro del rango
            print("ERROR: Cantidad invalidad. Solo se aceptan enteros entre 0 y 1000.")
            return False
    except ValueError: #si el usuario ingresa letras, se ejecuta el except y se muestra el mensaje de error
        print("ERROR: Cantidad invalidad. Solo se aceptan enteros entre 0 y 1000.")
        return False
    
    productos = cargar_inventario()
    for producto in productos:
        if producto["id"] == identificador:
            anterior = producto["cantidad"]
            producto["cantidad"] = cantidad
            guardar_inventario(productos)
            registrar_evento(
                sesion["usuario"], "modificar", "exitoso",
                producto=identificador, anterior=anterior, nueva=cantidad
            )
            print("Cantidad actualizada.")
            return True
    # TODO: informar identificador inexistente, sin crear productos.
    print("ERROR: Producto no encontrado.") 
    return False


def main():
    print("Inventario académico — BASE CON DEBILIDADES")
    print("Estudiante:", input("Escriba su nombre: "))
    sesion = None
    while True:
        if sesion is None:
            nombre = input("Usuario (o salir): ")
            if nombre == "salir":
                break
            sesion = autenticar(nombre, input("Contraseña de prueba: "))
            continue
        print("1. Consultar | 2. Modificar | 3. Cerrar sesión | 0. Salir")
        opcion = input("Opción: ")
        if opcion == "1":
            consultar_inventario(sesion)
        elif opcion == "2":
            identificador = input("ID del producto: ")
            entrada = input("Nueva cantidad: ")
            modificar_cantidad(sesion, identificador, entrada)
        elif opcion == "3":
            sesion = None
        elif opcion == "0":
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()
