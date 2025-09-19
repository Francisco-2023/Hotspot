import tkinter as tk
from tkinter import ttk, messagebox
from routeros_api import RouterOsApiPool

# Variables globales
api_pool = None
api = None

# ---------- FUNCIONES PRINCIPALES ----------

def conectar_mikrotik():
    global api_pool, api
    ip = entry_ip.get()
    user = entry_usuario.get()
    password = entry_contrasena.get()

    try:
        api_pool = RouterOsApiPool(ip, username=user, password=password, plaintext_login=True)
        api = api_pool.get_api()
        messagebox.showinfo("Conexión exitosa", "✅ Se conectó correctamente al MikroTik.")
        frame_conexion.place_forget()
        frame_contenido.place(relx=0.5, rely=0.5, anchor="center")
        cargar_usuarios()
        escribir_log("Conexión exitosa a MikroTik.")
    except Exception as e:
        messagebox.showerror("Error de conexión", str(e))
        escribir_log(f"❌ Error de conexión: {e}")

def crear_usuario_hotspot():
    nombre = entry_usuario_hotspot.get()
    contrasena = entry_contrasena_hotspot.get()
    duracion = combo_duracion.get()
    velocidad = combo_velocidad.get()

    perfil_nombre = f"{velocidad}_{duracion}"
    try:
        # Crear perfil temporal
        perfil = api.get_resource('/ip/hotspot/user/profile')
        perfil.add(
            name=perfil_nombre,
            rate_limit=velocidad,
            session_timeout=duracion,
            keepalive_timeout="1m",
            idle_timeout="none",
            shared_users="1"
        )

        # Crear usuario
        user = api.get_resource('/ip/hotspot/user')
        user.add(name=nombre, password=contrasena, profile=perfil_nombre)
        messagebox.showinfo("Usuario creado", f"✅ Usuario '{nombre}' creado.")
        escribir_log(f"✅ Usuario: {nombre} - Velocidad: {velocidad} - Tiempo: {duracion}")
        entry_usuario_hotspot.delete(0, tk.END)
        entry_contrasena_hotspot.delete(0, tk.END)
        cargar_usuarios()
    except Exception as e:
        messagebox.showerror("Error al crear usuario", str(e))
        escribir_log(f"❌ Error al crear usuario: {e}")

def escribir_log(mensaje):
    txt_log.config(state="normal")
    txt_log.insert(tk.END, mensaje + "\n")
    txt_log.see(tk.END)
    txt_log.config(state="disabled")

def cargar_usuarios():
    for row in tree_usuarios.get_children():
        tree_usuarios.delete(row)

    try:
        usuarios = api.get_resource('/ip/hotspot/user').get()
        for u in usuarios:
            tree_usuarios.insert('', tk.END, values=(u['name'], u['password'], u['profile']))
    except Exception as e:
        escribir_log(f"❌ Error al cargar usuarios: {e}")

# ---------------- INTERFAZ ----------------

ventana = tk.Tk()
ventana.title("Gestión Hotspot MikroTik")
ventana.geometry("700x600")
ventana.configure(bg="#f0f2f5")
ventana.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", font=("Segoe UI", 10), background="#f0f2f5")
style.configure("TButton", font=("Segoe UI", 10, "bold"))
style.configure("TEntry", font=("Segoe UI", 10))
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

# Frame conexión inicial
frame_conexion = ttk.LabelFrame(ventana, text="🔗 Conexión MikroTik")
frame_conexion.place(relx=0.5, rely=0.4, anchor="center")

ttk.Label(frame_conexion, text="IP MikroTik:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_ip = ttk.Entry(frame_conexion, width=25)
entry_ip.insert(0, "192.168.88.1")
entry_ip.grid(row=0, column=1, pady=5)

ttk.Label(frame_conexion, text="Usuario:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_usuario = ttk.Entry(frame_conexion, width=25)
entry_usuario.insert(0, "Francisco")
entry_usuario.grid(row=1, column=1, pady=5)

ttk.Label(frame_conexion, text="Contraseña:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
entry_contrasena = ttk.Entry(frame_conexion, show="*", width=25)
entry_contrasena.insert(0, "1251301881")
entry_contrasena.grid(row=2, column=1, pady=5)

ttk.Button(frame_conexion, text="Conectar", command=conectar_mikrotik).grid(row=3, column=0, columnspan=2, pady=10)

# Frame de contenido (se muestra después de conexión)
frame_contenido = tk.Frame(ventana, bg="#f0f2f5")

# Formulario usuario
frame_form = ttk.LabelFrame(frame_contenido, text="🧾 Crear Usuario Hotspot")
frame_form.grid(row=0, column=0, padx=10, pady=10, sticky="n")

ttk.Label(frame_form, text="Usuario:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_usuario_hotspot = ttk.Entry(frame_form, width=22)
entry_usuario_hotspot.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_form, text="Contraseña:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_contrasena_hotspot = ttk.Entry(frame_form, show="*", width=22)
entry_contrasena_hotspot.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_form, text="Duración:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
combo_duracion = ttk.Combobox(frame_form, values=["30m", "1h", "2h", "4h", "12h", "1d"], width=20)
combo_duracion.current(1)
combo_duracion.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(frame_form, text="Velocidad:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
combo_velocidad = ttk.Combobox(frame_form, values=["512k/1M", "1M/2M", "2M/4M", "3M/6M", "5M/10M"], width=20)
combo_velocidad.current(1)
combo_velocidad.grid(row=3, column=1, padx=5, pady=5)

ttk.Button(frame_form, text="Crear Usuario", command=crear_usuario_hotspot).grid(row=4, column=0, columnspan=2, pady=10)

# Tabla usuarios
frame_tabla = ttk.LabelFrame(frame_contenido, text="📄 Usuarios Hotspot")
frame_tabla.grid(row=0, column=1, padx=10, pady=10)

columns = ("Usuario", "Contraseña", "Perfil")
tree_usuarios = ttk.Treeview(frame_tabla, columns=columns, show="headings", height=10)
for col in columns:
    tree_usuarios.heading(col, text=col)
    tree_usuarios.column(col, anchor="center", width=130)
tree_usuarios.pack(fill="both", padx=5, pady=5)

# Log
frame_log = ttk.LabelFrame(frame_contenido, text="📋 Registro de acciones")
frame_log.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="we")

txt_log = tk.Text(frame_log, height=6, state="disabled", bg="#ffffff")
txt_log.pack(fill="both", expand=True)

ventana.mainloop()
