import tkinter as tk
from tkinter import messagebox, ttk, PhotoImage
from librouteros import connect
import os

# Variables globales
api = None
router = None
conexion_establecida = False

# ------------------ FUNCIONES ------------------ #

def conectar_mikrotik(ip, usuario, contrasena):
    global api, router, conexion_establecida
    try:
        router = connect(username=usuario, password=contrasena, host=ip)
        conexion_establecida = True
        return True
    except Exception as e:
        messagebox.showerror("Error de conexión", str(e))
        return False

def cerrar_sesion():
    global conexion_establecida
    conexion_establecida = False
    frame_usuarios.pack_forget()
    frame_login.pack()

def crear_usuario():
    nombre = entry_nombre.get()
    clave = entry_clave.get()
    tiempo = combo_tiempo.get()
    velocidad = combo_velocidad.get()

    if not all([nombre, clave, tiempo, velocidad]):
        messagebox.showwarning("Campos vacíos", "Por favor complete todos los campos")
        return

    try:
        router(cmd='/ip/hotspot/user/add', **{
            'name': nombre,
            'password': clave,
            'limit-uptime': tiempo,
            'rate-limit': velocidad
        })
        entry_nombre.delete(0, tk.END)
        entry_clave.delete(0, tk.END)
        cargar_usuarios()
    except Exception as e:
        messagebox.showerror("Error al crear usuario", str(e))

def cargar_usuarios():
    for i in tabla_usuarios.get_children():
        tabla_usuarios.delete(i)

    try:
        usuarios = router(cmd='/ip/hotspot/user/print')
        for user in usuarios:
            tabla_usuarios.insert("", tk.END, values=(
                user.get('name', ''),
                user.get('password', ''),
                user.get('rate-limit', ''),
                user.get('limit-uptime', '')
            ))
    except Exception as e:
        messagebox.showerror("Error al cargar usuarios", str(e))

def eliminar_usuario():
    seleccionado = tabla_usuarios.focus()
    if not seleccionado:
        return

    datos = tabla_usuarios.item(seleccionado, "values")
    nombre = datos[0]

    if messagebox.askyesno("Eliminar", f"¿Deseas eliminar el usuario '{nombre}'?"):
        try:
            usuarios = router(cmd='/ip/hotspot/user/print')
            for user in usuarios:
                if user.get('name') == nombre:
                    router(cmd='/ip/hotspot/user/remove', **{'.id': user['.id']})
                    break
            cargar_usuarios()
        except Exception as e:
            messagebox.showerror("Error al eliminar", str(e))


# ------------------ INTERFAZ ------------------ #

root = tk.Tk()
root.title("Gestión de Usuarios Hotspot MikroTik")
root.configure(bg="#f0f4f8")
root.geometry("600x550")
root.resizable(False, False)

# Cargar logo si existe
logo_img = None
if os.path.exists("image.png"):
    logo_img = PhotoImage(file="image.png")

# -------- Login --------
frame_login = tk.Frame(root, bg="#f0f4f8", padx=20, pady=20)
frame_login.pack()

if logo_img:
    tk.Label(frame_login, image=logo_img, bg="#f0f4f8").pack(pady=(0, 10))

tk.Label(frame_login, text="Conectar a MikroTik", font=("Arial", 16, "bold"), bg="#f0f4f8").pack(pady=10)

formulario = tk.Frame(frame_login, bg="#f0f4f8")
formulario.pack()

tk.Label(formulario, text="IP MikroTik:", bg="#f0f4f8").grid(row=0, column=0, sticky="e")
entry_ip = tk.Entry(formulario)
entry_ip.insert(0, "192.168.88.1")
entry_ip.grid(row=0, column=1, padx=5, pady=5)

tk.Label(formulario, text="Usuario:", bg="#f0f4f8").grid(row=1, column=0, sticky="e")
entry_user = tk.Entry(formulario)
entry_user.insert(0, "admin")
entry_user.grid(row=1, column=1, padx=5, pady=5)

tk.Label(formulario, text="Contraseña:", bg="#f0f4f8").grid(row=2, column=0, sticky="e")
entry_pass = tk.Entry(formulario, show="*")
entry_pass.grid(row=2, column=1, padx=5, pady=5)

def iniciar_conexion():
    if conectar_mikrotik(entry_ip.get(), entry_user.get(), entry_pass.get()):
        frame_login.pack_forget()
        frame_usuarios.pack()
        cargar_usuarios()

tk.Button(frame_login, text="Conectar", command=iniciar_conexion, bg="#007bff", fg="white").pack(pady=15)

# -------- Usuarios --------
frame_usuarios = tk.Frame(root, bg="#ffffff", padx=20, pady=20)

barra_superior = tk.Frame(frame_usuarios, bg="#ffffff")
barra_superior.pack(fill="x")
tk.Label(barra_superior, text="Gestión de Usuarios Hotspot", bg="#ffffff", font=("Arial", 14, "bold")).pack(side="left")
tk.Button(barra_superior, text="Cerrar Sesión", bg="#dc3545", fg="white", command=cerrar_sesion).pack(side="right")

# Formulario usuario
form_usuario = tk.Frame(frame_usuarios, bg="#ffffff")
form_usuario.pack(pady=10)

tk.Label(form_usuario, text="Usuario:", bg="#ffffff").grid(row=0, column=0, sticky="e")
entry_nombre = tk.Entry(form_usuario)
entry_nombre.grid(row=0, column=1, padx=5, pady=5)

tk.Label(form_usuario, text="Contraseña:", bg="#ffffff").grid(row=1, column=0, sticky="e")
entry_clave = tk.Entry(form_usuario)
entry_clave.grid(row=1, column=1, padx=5, pady=5)

tk.Label(form_usuario, text="Velocidad:", bg="#ffffff").grid(row=2, column=0, sticky="e")
combo_velocidad = ttk.Combobox(form_usuario, values=["512k/512k", "1M/2M", "2M/4M", "5M/10M"], state="readonly")
combo_velocidad.current(0)
combo_velocidad.grid(row=2, column=1, padx=5, pady=5)

tk.Label(form_usuario, text="Duración:", bg="#ffffff").grid(row=3, column=0, sticky="e")
combo_tiempo = ttk.Combobox(form_usuario, values=["30m", "1h", "2h", "4h", "1d"], state="readonly")
combo_tiempo.current(0)
combo_tiempo.grid(row=3, column=1, padx=5, pady=5)

tk.Button(form_usuario, text="Crear Usuario", bg="#28a745", fg="white", command=crear_usuario).grid(row=4, column=0, columnspan=2, pady=10)

# Tabla usuarios
tabla = tk.Frame(frame_usuarios)
tabla.pack(pady=10)

tabla_usuarios = ttk.Treeview(tabla, columns=("Usuario", "Clave", "Velocidad", "Duración"), show="headings")
for col in ("Usuario", "Clave", "Velocidad", "Duración"):
    tabla_usuarios.heading(col, text=col)
    tabla_usuarios.column(col, width=100)

tabla_usuarios.pack()

tk.Button(frame_usuarios, text="Eliminar Usuario", bg="#ffc107", command=eliminar_usuario).pack(pady=5)

# -------------------
root.mainloop()
