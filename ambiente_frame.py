import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from parametro_frame import ParametroFrame
from tema import tema_manager

class AmbienteFrame(ttk.Frame):
    def __init__(self, master, nombre, on_close=None, on_parametro_change=None):
        self.tema = tema_manager.tema_actual
        super().__init__(master, style="Card.TFrame" if self.tema == "claro" else "TFrame")
        
        self.nombre = nombre
        self.on_close_callback = on_close
        self.on_parametro_change = on_parametro_change
        self.parametros_activos = {}
        
        self.config(relief="raised", borderwidth=2, padding=10)
        
        # Cabecera del ambiente
        self.crear_cabecera()
        
        # Área de parámetros
        self.crear_area_parametros()
        
        # Bind eventos
        self.bind_events()

    def crear_cabecera(self):
        frame_header = ttk.Frame(self)
        frame_header.pack(fill="x", pady=(0, 10))
        
        # Título del ambiente
        title_label = ttk.Label(frame_header, text=f"🏠 {self.nombre}", 
                               style="Title.TLabel", font=("Arial", 14, "bold"))
        title_label.pack(side="left", fill="x", expand=True)
        
        # Botones de control
        btn_add_param = ttk.Button(frame_header, text="+ Parámetro", 
                                  command=self.agregar_parametro, style="Secondary.TButton")
        btn_add_param.pack(side="right", padx=(5, 0))
        
        btn_menu = ttk.Button(frame_header, text="⋯", width=2, 
                             command=self.mostrar_menu_contextual)
        btn_menu.pack(side="right", padx=(5, 0))
        
        btn_close = ttk.Button(frame_header, text="×", width=2, 
                              command=self.cerrar)
        btn_close.pack(side="right", padx=(5, 0))

    def crear_area_parametros(self):
        # Frame para los parámetros con scroll
        self.parametros_frame = ttk.Frame(self)
        self.parametros_frame.pack(fill="x", expand=True)
        
        # Configurar grid para organización responsive
        self.parametros_frame.columnconfigure(0, weight=1)
        self.parametros_frame.columnconfigure(1, weight=1)

    def agregar_parametro(self, nombre=None, config=None):
        if not nombre:
            nombre = simpledialog.askstring("Nuevo Parámetro", "Nombre del parámetro:")
            if not nombre:
                return
        
        # Verificar si el parámetro ya existe en este ambiente
        if nombre in self.parametros_activos:
            messagebox.showwarning("Advertencia", f"Ya existe un parámetro '{nombre}' en este ambiente")
            return
        
        # Crear el frame del parámetro
        parametro_frame = ParametroFrame(self.parametros_frame, nombre, 
                                       on_close=self.parametro_cerrado)
        
        # Configurar valores si se proporciona configuración
        if config:
            parametro_frame.sensor_var.set(config.get("sensor", "DHT22"))
            parametro_frame.min_entry.delete(0, tk.END)
            parametro_frame.min_entry.insert(0, config.get("min", "10"))
            parametro_frame.max_entry.delete(0, tk.END)
            parametro_frame.max_entry.insert(0, config.get("max", "30"))
            parametro_frame.int_entry.delete(0, tk.END)
            parametro_frame.int_entry.insert(0, config.get("intervalo", "5"))
        
        # Registrar parámetro activo
        self.parametros_activos[nombre] = parametro_frame
        
        # Organizar en grid
        num_parametros = len(self.parametros_activos)
        row = (num_parametros - 1) // 2
        col = (num_parametros - 1) % 2
        
        parametro_frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        
        # Notificar cambio
        if self.on_parametro_change:
            self.on_parametro_change()

    def agregar_parametro_desde_config(self, config):
        """Agrega un parámetro desde configuración sin diálogo"""
        nombre = config.get("nombre", f"Parámetro_{len(self.parametros_activos)+1}")
        self.agregar_parametro(nombre, config)

    def parametro_cerrado(self, nombre_parametro):
        """Callback llamado cuando se cierra un parámetro"""
        if nombre_parametro in self.parametros_activos:
            del self.parametros_activos[nombre_parametro]
            self.reorganizar_parametros()
            
            # Notificar cambio
            if self.on_parametro_change:
                self.on_parametro_change()

    def reorganizar_parametros(self):
        """Reorganiza los parámetros en el grid después de eliminar uno"""
        # Limpiar grid
        for widget in self.parametros_frame.winfo_children():
            widget.grid_forget()
        
        # Recolocar todos los parámetros
        for i, (nombre, param_frame) in enumerate(self.parametros_activos.items()):
            row = i // 2
            col = i % 2
            param_frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

    def obtener_configuracion_parametros(self):
        """Obtiene la configuración de todos los parámetros del ambiente"""
        parametros = []
        for nombre, parametro_frame in self.parametros_activos.items():
            if hasattr(parametro_frame, 'winfo_exists') and parametro_frame.winfo_exists():
                parametros.append({
                    "nombre": nombre,
                    "sensor": parametro_frame.sensor_var.get(),
                    "min": parametro_frame.min_entry.get(),
                    "max": parametro_frame.max_entry.get(),
                    "intervalo": parametro_frame.int_entry.get()
                })
        return parametros

    def mostrar_menu_contextual(self):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Renombrar Ambiente", command=self.renombrar)
        menu.add_command(label="Duplicar Ambiente", command=self.duplicar)
        menu.add_separator()
        menu.add_command(label="Exportar Configuración", command=self.exportar_config)
        
        try:
            menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())
        finally:
            menu.grab_release()

    def renombrar(self):
        nuevo_nombre = simpledialog.askstring("Renombrar Ambiente", 
                                            "Nuevo nombre:", 
                                            initialvalue=self.nombre)
        if nuevo_nombre and nuevo_nombre != self.nombre:
            self.nombre = nuevo_nombre
            # Actualizar la interfaz
            for child in self.winfo_children():
                if isinstance(child, ttk.Frame):
                    for subchild in child.winfo_children():
                        if isinstance(subchild, ttk.Label) and "🏠" in subchild.cget("text"):
                            subchild.config(text=f"🏠 {self.nombre}")

    def duplicar(self):
        # Esta funcionalidad requeriría comunicación con el Dashboard
        pass

    def exportar_config(self):
        # Exportar configuración del ambiente
        pass

    def bind_events(self):
        self.bind("<ButtonPress-1>", self.start_drag)
        self.bind("<B1-Motion>", self.drag)

    def start_drag(self, event):
        self._drag_data = {"x": event.x, "y": event.y}

    def drag(self, event):
        # Lógica básica de arrastre para reordenar ambientes
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        # Implementación completa requeriría más lógica de reordenamiento

    def cerrar(self):
        if messagebox.askyesno("Confirmar", f"¿Eliminar el ambiente '{self.nombre}' y todos sus parámetros?"):
            # Detener todos los parámetros activos
            for nombre, param_frame in self.parametros_activos.items():
                if hasattr(param_frame, 'detener'):
                    param_frame.detener()
            
            # Notificar al dashboard
            if self.on_close_callback:
                self.on_close_callback(self.nombre)
            
            self.destroy()

    def winfo_exists(self):
        try:
            return self.winfo_viewable() is not None
        except tk.TclError:
            return False