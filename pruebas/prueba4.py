import customtkinter as ctk
from tkinter import messagebox
import os
from PIL import Image, ImageTk
from datetime import datetime
import hashlib

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
    def __init__(self, colegio, tipo_uniforme, prenda, talla, cantidad):
        self.colegio = colegio
        self.tipo_uniforme = tipo_uniforme
        self.prenda = prenda
        self.talla = talla
        self.cantidad = cantidad
        self.id = hashlib.md5(f"{colegio}{tipo_uniforme}{prenda}{talla}".encode()).hexdigest()

class SistemaInventario:
    def __init__(self):
        self.usuarios = {}
        self.inventario = {}
        self.historial_movimientos = []
        self.usuario_actual = None
        
        self.agregar_usuario("admin", "admin123", True)
        self.agregar_usuario("user", "user123", False)
        
        self.colegios = set()
        self.tipos_uniforme = {"Uniforme Diario", "Uniforme Deportivo"}
        self.prendas = {
            "Uniforme Diario": {"Camisa", "Pantalón", "Falda", "Suéter"},
            "Uniforme Deportivo": {"Camiseta", "Pantaloneta", "Sudadera", "Chaqueta"}
        }
        self.tallas = {"4", "6", "8", "10", "12", "14", "16", "S", "M", "L", "XL"}
    
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

    def agregar_producto(self, colegio, tipo_uniforme, prenda, talla, cantidad):
        if not self.es_admin():
            return False, "Se requieren privilegios de administrador"
        
        try:
            cantidad = int(cantidad)
            if cantidad < 0:
                raise ValueError
        except ValueError:
            return False, "La cantidad debe ser un número positivo"
        
        self.colegios.add(colegio)
        producto = Producto(colegio, tipo_uniforme, prenda, talla, cantidad)
        
        if producto.id in self.inventario:
            return False, "El producto ya existe"
        
        self.inventario[producto.id] = producto
        return True, "Producto agregado exitosamente"

    def actualizar_stock(self, colegio, tipo_uniforme, prenda, talla, cantidad, tipo="ENTRADA"):
        producto_id = hashlib.md5(f"{colegio}{tipo_uniforme}{prenda}{talla}".encode()).hexdigest()
        
        if producto_id not in self.inventario:
            return False, "Producto no encontrado"
        
        try:
            cantidad = int(cantidad)
            if cantidad < 0:
                raise ValueError
        except ValueError:
            return False, "La cantidad debe ser un número positivo"
        
        if tipo == "ENTRADA":
            self.inventario[producto_id].cantidad += cantidad
        elif tipo == "SALIDA":
            if self.inventario[producto_id].cantidad < cantidad:
                return False, "Stock insuficiente"
            self.inventario[producto_id].cantidad -= cantidad
        
        return True, f"Stock actualizado. Nuevo stock: {self.inventario[producto_id].cantidad}"

    def obtener_productos(self, filtros=None):
        if not filtros:
            return self.inventario.values()
        
        productos_filtrados = []
        for producto in self.inventario.values():
            cumple_filtros = True
            for campo, valor in filtros.items():
                if valor and getattr(producto, campo) != valor:
                    cumple_filtros = False
                    break
            if cumple_filtros:
                productos_filtrados.append(producto)
        
        return productos_filtrados

class AplicacionInventario(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Inventario - Uniformes Escolares")
        self.geometry("1000x700")
        self.sistema = SistemaInventario()
        
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            imagen_path = os.path.join(current_dir, "images", "Ritmichell.png")
            
            if not os.path.exists(imagen_path):
                print(f"Error: No se encuentra el archivo en {imagen_path}")
                self.logo_image = None
            else:
                pil_image = Image.open(imagen_path)
                icon_size = (32, 32)
                icon_image = pil_image.resize(icon_size, Image.Resampling.LANCZOS)
                self.icon_photo = ImageTk.PhotoImage(icon_image)
                self.iconphoto(True, self.icon_photo)
                
                logo_size = (150, 150)
                logo_image = pil_image.resize(logo_size, Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(logo_image)
                self.logo_ctk = ctk.CTkImage(light_image=pil_image, 
                                           dark_image=pil_image,
                                           size=logo_size)
                
        except Exception as e:
            print(f"Error al cargar el logo: {str(e)}")
            self.logo_image = None
            self.logo_ctk = None
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 1000) // 2
        y = (screen_height - 700) // 2
        self.geometry(f"1000x700+{x}+{y}")
        
        self.mostrar_login()
    
    def mostrar_login(self):
        for widget in self.winfo_children():
            widget.destroy()
        
        frame_login = ctk.CTkFrame(self, width=360, height=400)
        frame_login.place(relx=0.5, rely=0.5, anchor="center")
        
        if hasattr(self, 'logo_ctk') and self.logo_ctk is not None:
            logo_label = ctk.CTkLabel(frame_login, image=self.logo_ctk, text="")
            logo_label.place(relx=0.5, rely=0.22, anchor="center")
            
            titulo = ctk.CTkLabel(frame_login, text="LOGIN", font=("Helvetica", 24, "bold"))
            titulo.place(relx=0.5, rely=0.45, anchor="center")
        else:
            titulo = ctk.CTkLabel(frame_login, text="LOGIN", font=("Helvetica", 24, "bold"))
            titulo.place(relx=0.5, rely=0.2, anchor="center")
        
        usuario_label = ctk.CTkLabel(frame_login, text="Usuario:")
        usuario_label.place(relx=0.22, rely=0.5)
        
        self.usuario_entry = ctk.CTkEntry(frame_login, width=200)
        self.usuario_entry.place(relx=0.22, rely=0.57)
        
        password_label = ctk.CTkLabel(frame_login, text="Contraseña:")
        password_label.place(relx=0.22, rely=0.67)
        
        self.password_entry = ctk.CTkEntry(frame_login, width=200, show="*")
        self.password_entry.place(relx=0.22, rely=0.74)
        
        login_button = ctk.CTkButton(frame_login, text="Iniciar Sesión", command=self.login, width=200)
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
        
        frame_principal = ctk.CTkFrame(self)
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
        
        frame_menu = ctk.CTkFrame(frame_principal)
        frame_menu.pack(fill="x", padx=10, pady=10)
        
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
        
        frame_filtros = ctk.CTkFrame(frame_principal)
        frame_filtros.pack(fill="x", padx=10, pady=10)
        
        self.filtro_colegio = ctk.CTkComboBox(frame_filtros, values=[""] + list(self.sistema.colegios),
                                             command=self.aplicar_filtros)
        self.filtro_colegio.set("Seleccionar Colegio")
        self.filtro_colegio.pack(side="left", padx=5)
        
        self.filtro_tipo = ctk.CTkComboBox(frame_filtros, values=[""] + list(self.sistema.tipos_uniforme),
                                          command=self.actualizar_prendas)
        self.filtro_tipo.set("Seleccionar Tipo")
        self.filtro_tipo.pack(side="left", padx=5)
        
        self.filtro_prenda = ctk.CTkComboBox(frame_filtros, values=[""],
                                            command=self.aplicar_filtros)
        self.filtro_prenda.set("Seleccionar Prenda")
        self.filtro_prenda.pack(side="left", padx=5)
        
        self.filtro_talla = ctk.CTkComboBox(frame_filtros, values=[""] + list(self.sistema.tallas),
                                           command=self.aplicar_filtros)
        self.filtro_talla.set("Seleccionar Talla")
        self.filtro_talla.pack(side="left", padx=5)
        
        self.frame_productos = ctk.CTkFrame(frame_principal)
        self.frame_productos.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.actualizar_lista_productos()

    def actualizar_prendas(self, *args):
        tipo_seleccionado = self.filtro_tipo.get()
        if tipo_seleccionado in self.sistema.prendas:
            prendas = [""] + list(self.sistema.prendas[tipo_seleccionado])
            self.filtro_prenda.configure(values=prendas)
            self.filtro_prenda.set("Seleccionar Prenda")
        self.aplicar_filtros()
    
    def aplicar_filtros(self, *args):
        filtros = {}
        if self.filtro_colegio.get() != "Seleccionar Colegio":
            filtros['colegio'] = self.filtro_colegio.get()
        if self.filtro_tipo.get() != "Seleccionar Tipo":
            filtros['tipo_uniforme'] = self.filtro_tipo.get()
        if self.filtro_prenda.get() != "Seleccionar Prenda":
            filtros['prenda'] = self.filtro_prenda.get()
        if self.filtro_talla.get() != "Seleccionar Talla":
            filtros['talla'] = self.filtro_talla.get()
        
        self.actualizar_lista_productos(filtros)

    def mostrar_agregar_producto(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Agregar Producto")
        ventana.geometry("400x600")
        ventana.focus()
        ventana.grab_set()
        ventana.transient(self)
        ventana.geometry(f"+{self.winfo_x() + 250}+{self.winfo_y() + 50}")
        
        frame = ctk.CTkFrame(ventana)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        titulo = ctk.CTkLabel(frame, text="Agregar Nuevo Producto", font=("Helvetica", 20, "bold"))
        titulo.pack(pady=20)
        
        ctk.CTkLabel(frame, text="Colegio:").pack(pady=5)
        colegio_entry = ctk.CTkEntry(frame, width=200)
        colegio_entry.pack()
        
        ctk.CTkLabel(frame, text="Tipo de Uniforme:").pack(pady=5)
        tipo_var = ctk.StringVar(value="Uniforme Diario")
        tipo_combobox = ctk.CTkComboBox(frame, values=list(self.sistema.tipos_uniforme),
                                       variable=tipo_var, width=200)
        tipo_combobox.pack()
        
        ctk.CTkLabel(frame, text="Prenda:").pack(pady=5)
        prenda_var = ctk.StringVar()
        prenda_combobox = ctk.CTkComboBox(frame, values=list(self.sistema.prendas["Uniforme Diario"]),
                                         variable=prenda_var, width=200)
        prenda_combobox.pack()
        
        def actualizar_prendas(*args):
            tipo_seleccionado = tipo_var.get()
            if tipo_seleccionado in self.sistema.prendas:
                prenda_combobox.configure(values=list(self.sistema.prendas[tipo_seleccionado]))
                prenda_combobox.set(list(self.sistema.prendas[tipo_seleccionado])[0])
        
        tipo_var.trace('w', actualizar_prendas)
        
        ctk.CTkLabel(frame, text="Talla:").pack(pady=5)
        talla_combobox = ctk.CTkComboBox(frame, values=list(self.sistema.tallas), width=200)
        talla_combobox.pack()
        
        ctk.CTkLabel(frame, text="Cantidad:").pack(pady=5)
        cantidad_entry = ctk.CTkEntry(frame, width=200)
        cantidad_entry.pack()
        
        def agregar():
            exito, mensaje = self.sistema.agregar_producto(
                colegio_entry.get(),
                tipo_combobox.get(),
                prenda_combobox.get(),
                talla_combobox.get(),
                cantidad_entry.get()
            )
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                ventana.destroy()
                self.actualizar_lista_productos()
                # Actualizar lista de colegios en el filtro
                self.filtro_colegio.configure(values=[""] + list(self.sistema.colegios))
            else:
                messagebox.showerror("Error", mensaje)
        
        ctk.CTkButton(frame, text="Agregar", command=agregar, width=200).pack(pady=20)
    
    def mostrar_actualizar_stock(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Actualizar Stock")
        ventana.geometry("400x600")
        ventana.focus()
        ventana.grab_set()
        ventana.transient(self)
        ventana.geometry(f"+{self.winfo_x() + 250}+{self.winfo_y() + 50}")
        
        frame = ctk.CTkFrame(ventana)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        titulo = ctk.CTkLabel(frame, text="Actualizar Stock", font=("Helvetica", 20, "bold"))
        titulo.pack(pady=20)
        
        ctk.CTkLabel(frame, text="Colegio:").pack(pady=5)
        colegio_combobox = ctk.CTkComboBox(frame, values=list(self.sistema.colegios), width=200)
        colegio_combobox.pack()
        
        ctk.CTkLabel(frame, text="Tipo de Uniforme:").pack(pady=5)
        tipo_var = ctk.StringVar(value="Uniforme Diario")
        tipo_combobox = ctk.CTkComboBox(frame, values=list(self.sistema.tipos_uniforme),
                                    variable=tipo_var, width=200)
        tipo_combobox.pack()
        
        ctk.CTkLabel(frame, text="Prenda:").pack(pady=5)
        prenda_var = ctk.StringVar()
        prenda_combobox = ctk.CTkComboBox(frame, values=list(self.sistema.prendas["Uniforme Diario"]),
                                        variable=prenda_var, width=200)
        prenda_combobox.pack()
        
        def actualizar_prendas(*args):
            tipo_seleccionado = tipo_var.get()
            if tipo_seleccionado in self.sistema.prendas:
                prenda_combobox.configure(values=list(self.sistema.prendas[tipo_seleccionado]))
                prenda_combobox.set(list(self.sistema.prendas[tipo_seleccionado])[0])
        
        tipo_var.trace('w', actualizar_prendas)
        
        ctk.CTkLabel(frame, text="Talla:").pack(pady=5)
        talla_combobox = ctk.CTkComboBox(frame, values=list(self.sistema.tallas), width=200)
        talla_combobox.pack()
        
        ctk.CTkLabel(frame, text="Cantidad:").pack(pady=5)
        cantidad_entry = ctk.CTkEntry(frame, width=200)
        cantidad_entry.pack()
        
        tipo_mov_var = ctk.StringVar(value="ENTRADA")
        tipo_frame = ctk.CTkFrame(frame)
        tipo_frame.pack(pady=20)
        
        ctk.CTkRadioButton(tipo_frame, text="Entrada", variable=tipo_mov_var,
                            value="ENTRADA").pack(side="left", padx=10)
        ctk.CTkRadioButton(tipo_frame, text="Salida", variable=tipo_mov_var,
                            value="SALIDA").pack(side="left", padx=10)
        
        def actualizar():
            exito, mensaje = self.sistema.actualizar_stock(
                colegio_combobox.get(),
                tipo_combobox.get(),
                prenda_combobox.get(),
                talla_combobox.get(),
                cantidad_entry.get(),
                tipo_mov_var.get()
            )
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                ventana.destroy()
                self.actualizar_lista_productos()
            else:
                messagebox.showerror("Error", mensaje)
        
        ctk.CTkButton(frame, text="Actualizar", command=actualizar, width=200).pack(pady=20)
    
    def actualizar_lista_productos(self, filtros=None):
        for widget in self.frame_productos.winfo_children():
            widget.destroy()
        
        headers = ['Colegio', 'Tipo Uniforme', 'Prenda', 'Talla', 'Cantidad']
        for i, header in enumerate(headers):
            ctk.CTkLabel(self.frame_productos, text=header,
                        font=("Helvetica", 12, "bold")).grid(row=0, column=i, padx=10, pady=5)
        
        row = 1
        for producto in self.sistema.obtener_productos(filtros):
            ctk.CTkLabel(self.frame_productos, text=producto.colegio).grid(row=row, column=0, padx=10, pady=2)
            ctk.CTkLabel(self.frame_productos, text=producto.tipo_uniforme).grid(row=row, column=1, padx=10, pady=2)
            ctk.CTkLabel(self.frame_productos, text=producto.prenda).grid(row=row, column=2, padx=10, pady=2)
            ctk.CTkLabel(self.frame_productos, text=producto.talla).grid(row=row, column=3, padx=10, pady=2)
            ctk.CTkLabel(self.frame_productos, text=str(producto.cantidad)).grid(row=row, column=4, padx=10, pady=2)
            row += 1
        
        self.frame_productos.grid_columnconfigure((0,1,2,3,4), weight=1)

if __name__ == "__main__":
    app = AplicacionInventario()
    app.mainloop()