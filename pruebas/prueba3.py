import customtkinter as ctk
from tkinter import messagebox
import os
from PIL import Image, ImageTk
from datetime import datetime
import hashlib

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Usuario:
    def __init__(self, username, password, es_admin=False):
        self.username = username
        self.password_hash = self._hash_password(password)
        self.es_admin = es_admin
    
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verificar_password(self, password):
        return self.password_hash == self._hash_password(password)

class Producto:
    def __init__(self, codigo, nombre, precio, cantidad):
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.cantidad = cantidad

class SistemaInventario:
    def __init__(self):
        self.usuarios = {}
        self.inventario = {}
        self.historial_movimientos = []
        self.usuario_actual = None
        
        # Crear usuario administrador por defecto
        self.agregar_usuario("admin", "admin123", True)
        # Crear usuario por defecto
        self.agregar_usuario("user", "user123", False)
    
    def agregar_usuario(self, username, password, es_admin=False):
        if username in self.usuarios:
            return False, "El usuario ya existe"
        
        nuevo_usuario = Usuario(username, password, es_admin)
        self.usuarios[username] = nuevo_usuario
        return True, "Usuario creado exitosamente"
    
    def login(self, username, password):
        if username not in self.usuarios:
            return False, "Usuario no encontrado"
        
        usuario = self.usuarios[username]
        if usuario.verificar_password(password):
            self.usuario_actual = usuario
            return True, "Inicio de sesión exitoso"
        return False, "Contraseña incorrecta"
    
    def logout(self):
        self.usuario_actual = None
        return True, "Sesión cerrada"

    def es_admin(self):
        return self.usuario_actual and self.usuario_actual.es_admin

    def agregar_producto(self, codigo, nombre, precio, cantidad):
        if not self.es_admin():
            return False, "Se requieren privilegios de administrador"
        
        if codigo in self.inventario:
            return False, "El producto ya existe"
        
        try:
            precio = float(precio)
            cantidad = int(cantidad)
            if precio < 0 or cantidad < 0:
                raise ValueError
        except ValueError:
            return False, "Precio y cantidad deben ser números positivos"
        
        self.inventario[codigo] = Producto(codigo, nombre, precio, cantidad)
        return True, "Producto agregado exitosamente"

    def actualizar_stock(self, codigo, cantidad, tipo="ENTRADA"):
        if codigo not in self.inventario:
            return False, "Producto no encontrado"
        
        try:
            cantidad = int(cantidad)
            if cantidad < 0:
                raise ValueError
        except ValueError:
            return False, "La cantidad debe ser un número positivo"
        
        if tipo == "ENTRADA":
            self.inventario[codigo].cantidad += cantidad
        elif tipo == "SALIDA":
            if self.inventario[codigo].cantidad < cantidad:
                return False, "Stock insuficiente"
            self.inventario[codigo].cantidad -= cantidad
        
        return True, f"Stock actualizado. Nuevo stock: {self.inventario[codigo].cantidad}"

    def obtener_productos(self):
        return self.inventario

class AplicacionInventario(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Inventario")
        self.geometry("900x600")
        self.sistema = SistemaInventario()
        
        # Cargar el logo usando PIL y CustomTkinter
        try:
            # Obtener ruta absoluta del directorio actual
            current_dir = os.path.dirname(os.path.abspath(__file__))
            imagen_path = os.path.join(current_dir, "images", "Ritmichell.png")
            
            # Verificar si el archivo existe
            if not os.path.exists(imagen_path):
                print(f"Error: No se encuentra el archivo en {imagen_path}")
                self.logo_image = None
            else:
                # Cargar y redimensionar la imagen para el ícono de la ventana
                pil_image = Image.open(imagen_path)
                # Crear una copia más pequeña para el ícono de la ventana
                icon_size = (32, 32)
                icon_image = pil_image.resize(icon_size, Image.Resampling.LANCZOS)
                self.icon_photo = ImageTk.PhotoImage(icon_image)
                
                # Establecer el ícono de la ventana
                self.iconphoto(True, self.icon_photo)
                
                # Crear una versión más grande para el logo en el login
                logo_size = (150, 150)  # Ajusta este tamaño según necesites
                logo_image = pil_image.resize(logo_size, Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(logo_image)
                
                # También crear una versión CTk de la imagen para usar con CustomTkinter
                self.logo_ctk = ctk.CTkImage(light_image=pil_image, 
                                            dark_image=pil_image,
                                            size=logo_size)
                
        except Exception as e:
            print(f"Error al cargar el logo: {str(e)}")
            self.logo_image = None
            self.logo_ctk = None
        
        # Centrar ventana en la pantalla
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 900) // 2
        y = (screen_height - 600) // 2
        self.geometry(f"900x600+{x}+{y}")
        
        self.mostrar_login()
    
    def mostrar_login(self):
        # Limpiar ventana
        for widget in self.winfo_children():
            widget.destroy()
        
        # Frame de login
        frame_login = ctk.CTkFrame(self, width=360, height=400)
        frame_login.place(relx=0.5, rely=0.5, anchor="center")
        
        # Mostrar logo en el login
        if hasattr(self, 'logo_ctk') and self.logo_ctk is not None:
            logo_label = ctk.CTkLabel(frame_login, 
                                    image=self.logo_ctk, 
                                    text="")  # Text vacío para mostrar solo la imagen
            logo_label.place(relx=0.5, rely=0.22, anchor="center")
            
            # Título debajo del logo
            titulo = ctk.CTkLabel(frame_login, 
                                text="LOGIN", 
                                font=("Helvetica", 24, "bold"))
            titulo.place(relx=0.5, rely=0.45, anchor="center")
        else:
            # Si no hay logo, solo mostrar el título
            titulo = ctk.CTkLabel(frame_login, 
                                text="LOGIN", 
                                font=("Helvetica", 24, "bold"))
            titulo.place(relx=0.5, rely=0.2, anchor="center")
        
        # Elementos del login
        usuario_label = ctk.CTkLabel(frame_login, text="Usuario:")
        usuario_label.place(relx=0.22, rely=0.5)
        
        self.usuario_entry = ctk.CTkEntry(frame_login, width=200)
        self.usuario_entry.place(relx=0.22, rely=0.57)
        
        password_label = ctk.CTkLabel(frame_login, text="Contraseña:")
        password_label.place(relx=0.22, rely=0.67)
        
        self.password_entry = ctk.CTkEntry(frame_login, width=200, show="*")
        self.password_entry.place(relx=0.22, rely=0.74)
        
        login_button = ctk.CTkButton(frame_login, text="Iniciar Sesión", 
                                    command=self.login, width=200)
        login_button.place(relx=0.5, rely=0.89, anchor="center")


    def login(self):
        username = self.usuario_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return
        
        exito, mensaje = self.sistema.login(username, password)
        if exito:
            self.mostrar_menu_principal()
        else:
            messagebox.showerror("Error", mensaje)
            self.password_entry.delete(0, 'end')
    
    def mostrar_menu_principal(self):
        for widget in self.winfo_children():
            widget.destroy()
        
        # Frame principal
        frame_principal = ctk.CTkFrame(self)
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Menú superior
        frame_menu = ctk.CTkFrame(frame_principal)
        frame_menu.pack(fill="x", padx=10, pady=10)
        
        # Botones del menú
        if self.sistema.es_admin():
            agregar_btn = ctk.CTkButton(frame_menu, text="Agregar Producto", 
                                        command=self.mostrar_agregar_producto)
            agregar_btn.pack(side="left", padx=5)
        
        actualizar_btn = ctk.CTkButton(frame_menu, text="Actualizar Stock", 
                                        command=self.mostrar_actualizar_stock)
        actualizar_btn.pack(side="left", padx=5)
        
        logout_btn = ctk.CTkButton(frame_menu, text="Cerrar Sesión", 
                                    command=self.mostrar_login)
        logout_btn.pack(side="right", padx=5)
        
        # Frame para la tabla de productos
        self.frame_productos = ctk.CTkFrame(frame_principal)
        self.frame_productos.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.actualizar_lista_productos()
    
    def mostrar_agregar_producto(self):
        ventana = ctk.CTkToplevel(self)
        
        ventana.lift()
        
        ventana.title("Agregar Producto")
        ventana.geometry("400x500")
        ventana.focus()
        ventana.grab_set()
        ventana.transient(self)


        
        
        
        # Center window
        ventana.geometry(f"+{self.winfo_x() + 250}+{self.winfo_y() + 50}")
        
        
        frame = ctk.CTkFrame(ventana)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        titulo = ctk.CTkLabel(frame, text="Agregar Nuevo Producto", font=("Helvetica", 20, "bold"))
        titulo.pack(pady=20)
        
        # Campos
        ctk.CTkLabel(frame, text="Código:").pack(pady=5)
        codigo_var = ctk.CTkEntry(frame, width=200)
        codigo_var.pack()
        
        ctk.CTkLabel(frame, text="Nombre:").pack(pady=5)
        nombre_var = ctk.CTkEntry(frame, width=200)
        nombre_var.pack()
        
        ctk.CTkLabel(frame, text="Precio:").pack(pady=5)
        precio_var = ctk.CTkEntry(frame, width=200)
        precio_var.pack()
        
        ctk.CTkLabel(frame, text="Cantidad:").pack(pady=5)
        cantidad_var = ctk.CTkEntry(frame, width=200)
        cantidad_var.pack()
        
        def agregar():
            exito, mensaje = self.sistema.agregar_producto(
                codigo_var.get(),
                nombre_var.get(),
                precio_var.get(),
                cantidad_var.get()
            )
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                ventana.destroy()
                self.actualizar_lista_productos()
            else:
                messagebox.showerror("Error", mensaje)
        
        ctk.CTkButton(frame, text="Agregar", command=agregar, width=200).pack(pady=20)
    
    def mostrar_actualizar_stock(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Actualizar Stock")
        ventana.geometry("400x400")
        ventana.focus()
        ventana.grab_set()
        ventana.transient(self)
        
        # Center window
        ventana.geometry(f"+{self.winfo_x() + 250}+{self.winfo_y() + 50}")
        
        frame = ctk.CTkFrame(ventana)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        titulo = ctk.CTkLabel(frame, text="Actualizar Stock", font=("Helvetica", 20, "bold"))
        titulo.pack(pady=20)
                
        # Campos
        ctk.CTkLabel(frame, text="Código:").pack(pady=5)
        codigo_var = ctk.CTkEntry(frame, width=200)
        codigo_var.pack()
        
        ctk.CTkLabel(frame, text="Cantidad:").pack(pady=5)
        cantidad_var = ctk.CTkEntry(frame, width=200)
        cantidad_var.pack()
        
        tipo_var = ctk.StringVar(value="ENTRADA")
        tipo_frame = ctk.CTkFrame(frame)
        tipo_frame.pack(pady=20)
        
        ctk.CTkRadioButton(tipo_frame, text="Entrada", variable=tipo_var, 
                            value="ENTRADA").pack(side="left", padx=10)
        ctk.CTkRadioButton(tipo_frame, text="Salida", variable=tipo_var, 
                            value="SALIDA").pack(side="left", padx=10)
        
        def actualizar():
            exito, mensaje = self.sistema.actualizar_stock(
                codigo_var.get(),
                cantidad_var.get(),
                tipo_var.get()
            )
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                ventana.destroy()
                self.actualizar_lista_productos()
            else:
                messagebox.showerror("Error", mensaje)
        
        ctk.CTkButton(frame, text="Actualizar", command=actualizar, width=200).pack(pady=20)
    
    def actualizar_lista_productos(self):
        # Limpiar lista actual
        for widget in self.frame_productos.winfo_children():
            widget.destroy()
        
        # Crear tabla personalizada con CustomTkinter
        # Headers
        headers = ['Código', 'Nombre', 'Precio', 'Cantidad']
        for i, header in enumerate(headers):
            ctk.CTkLabel(self.frame_productos, text=header, 
                        font=("Helvetica", 12, "bold")).grid(row=0, column=i, padx=10, pady=5)
        
        # Datos
        row = 1
        for producto in self.sistema.obtener_productos().values():
            ctk.CTkLabel(self.frame_productos, text=producto.codigo).grid(row=row, column=0, padx=10, pady=2)
            ctk.CTkLabel(self.frame_productos, text=producto.nombre).grid(row=row, column=1, padx=10, pady=2)
            ctk.CTkLabel(self.frame_productos, text=f"${producto.precio:.2f}").grid(row=row, column=2, padx=10, pady=2)
            ctk.CTkLabel(self.frame_productos, text=str(producto.cantidad)).grid(row=row, column=3, padx=10, pady=2)
            row += 1
        
        # Configure grid weights
        self.frame_productos.grid_columnconfigure((0,1,2,3), weight=1)

if __name__ == "__main__":
    app = AplicacionInventario()
    app.mainloop()
    