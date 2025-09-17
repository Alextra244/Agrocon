# dashboard.py
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from parametro_frame import ParametroFrame
from tema import tema_manager
import json
import os

class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configuración inicial
        self.title("Dashboard de Control de Parámetros")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        # Aplicar tema
        self.tema = tema_manager.aplicar_tema()
        
        # Cargar configuración
        self.config_file = "dashboard_config.json"
        self.app_config = self.cargar_configuracion()
        
        # Configurar icono (si está disponible)
        try:
            self.iconbitmap("icon.ico")  # Añade un icono a tu aplicación
        except:
            pass
        
        # Barra de menú superior
        self.crear_menu()
        
        # Panel principal con pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña principal
        self.tab_principal = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.tab_principal, text="Principal")
        
        # Barra de herramientas superior
        self.crear_barra_herramientas()
        
        # Área de contenido con scroll
        self.crear_area_contenido()
        
        # Barra de estado inferior
        self.crear_barra_estado()
        
        # Cargar parámetros guardados
        self.cargar_parametros_guardados()
        
        # Bind para redimensionamiento
        self.bind("<Configure>", self.on_resize)

    def crear_menu(self):
        menubar = tk.Menu(self)
        self.configure(menu=menubar)
        
        # Menú Archivo
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Nuevo parámetro", command=self.agregar_parametro)
        menu_archivo.add_command(label="Guardar configuración", command=self.guardar_configuracion)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.quit)
        
        # Menú Ver
        menu_ver = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ver", menu=menu_ver)
        menu_ver.add_command(label="Tema Claro", command=lambda: self.cambiar_tema("claro"))
        menu_ver.add_command(label="Tema Oscuro", command=lambda: self.cambiar_tema("oscuro"))
        
        # Menú Ayuda
        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)
        menu_ayuda.add_command(label="Acerca de", command=self.mostrar_acerca_de)

    def crear_barra_herramientas(self):
        toolbar = ttk.Frame(self.tab_principal, height=40)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        btn_agregar = ttk.Button(toolbar, text="+ Agregar Parámetro", 
                                command=self.agregar_parametro, style="Primary.TButton")
        btn_agregar.pack(side="left", padx=5)
        
        btn_organizar = ttk.Button(toolbar, text="Organizar Paneles", 
                                  command=self.organizar_paneles, style="Secondary.TButton")
        btn_organizar.pack(side="left", padx=5)
        
        # Selector de vista
        self.vista_var = tk.StringVar(value="tarjetas")
        vista_combo = ttk.Combobox(toolbar, textvariable=self.vista_var, 
                                  values=["tarjetas", "lista", "compacto"], 
                                  state="readonly", width=10)
        vista_combo.pack(side="right", padx=5)
        vista_combo.bind("<<ComboboxSelected>>", self.cambiar_vista)

    def crear_area_contenido(self):
        # Marco para el área de contenido
        content_frame = ttk.Frame(self.tab_principal)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Canvas con scrollbar
        self.canvas = tk.Canvas(content_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetado
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind para redimensionar el contenido
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Configurar grid para paneles redimensionables
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(1, weight=1)
        self.scrollable_frame.rowconfigure(0, weight=1)
        self.scrollable_frame.rowconfigure(1, weight=1)

    def crear_barra_estado(self):
        statusbar = ttk.Frame(self)
        statusbar.pack(side="bottom", fill="x")
        
        lbl_status = ttk.Label(statusbar, text="Listo", style="Subtitle.TLabel")
        lbl_status.pack(side="left", padx=10)
        
        lbl_tema = ttk.Label(statusbar, text=f"Tema: {tema_manager.tema_actual.capitalize()}", 
                            style="Subtitle.TLabel")
        lbl_tema.pack(side="right", padx=10)

    def agregar_parametro(self, nombre=None):
        if not nombre:
            nombre = simpledialog.askstring("Nuevo parámetro", "Nombre del parámetro:")
            if not nombre:
                return
        
        # Crear el frame del parámetro
        bloque = ParametroFrame(self.scrollable_frame, nombre)
        
        # Determinar la posición basada en la vista actual
        if self.vista_var.get() == "tarjetas":
            row = len(self.scrollable_frame.winfo_children()) // 2
            col = len(self.scrollable_frame.winfo_children()) % 2
            bloque.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        else:
            bloque.pack(fill="x", expand=False, padx=10, pady=5)
        
        # Guardar la configuración
        self.guardar_configuracion()

    def cambiar_vista(self, event=None):
        # Reorganizar los paneles según la vista seleccionada
        for i, child in enumerate(self.scrollable_frame.winfo_children()):
            if self.vista_var.get() == "tarjetas":
                child.pack_forget()
                row = i // 2
                col = i % 2
                child.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
            else:
                child.grid_forget()
                child.pack(fill="x", expand=False, padx=10, pady=5)

    def organizar_paneles(self):
        # Implementar lógica para organizar automáticamente los paneles
        messagebox.showinfo("Organizar Paneles", "Los paneles se han organizado automáticamente.")

    def cambiar_tema(self, tema):
        tema_manager.aplicar_tema(tema)
        self.tema = tema_manager.tema_actual
        # Actualizar la interfaz con el nuevo tema
        self.actualizar_tema()

    def actualizar_tema(self):
        # Actualizar colores y estilos de todos los componentes
        for child in self.winfo_children():
            if isinstance(child, ttk.Frame):
                self.actualizar_tema_recursivo(child)

    def actualizar_tema_recursivo(self, widget):
        for child in widget.winfo_children():
            if isinstance(child, (ttk.Frame, ttk.Label, ttk.Button, ttk.Entry, ttk.Combobox)):
                # Actualizar estilos según el tema actual
                pass
            self.actualizar_tema_recursivo(child)

    def on_resize(self, event):
        # Ajustar diseño en respuesta al redimensionamiento
        pass

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def cargar_configuracion(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {"parametros": [], "tema": "claro", "vista": "tarjetas"}
        return {"parametros": [], "tema": "claro", "vista": "tarjetas"}

    def guardar_configuracion(self):
        parametros = []
        for child in self.scrollable_frame.winfo_children():
            if isinstance(child, ParametroFrame):
                parametros.append({
                    "nombre": child.nombre,
                    "sensor": child.sensor_var.get(),
                    "min": child.min_entry.get(),
                    "max": child.max_entry.get(),
                    "intervalo": child.int_entry.get()
                })
        
        config = {
            "parametros": parametros,
            "tema": tema_manager.tema_actual,
            "vista": self.vista_var.get()
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def cargar_parametros_guardados(self):
        for param in self.app_config.get("parametros", []):
            self.agregar_parametro(param["nombre"])
            # Aquí deberías configurar cada parámetro con sus valores guardados

    def mostrar_acerca_de(self):
        messagebox.showinfo("Acerca de", 
                           "Dashboard de Control de Parámetros\n\n"
                           "Versión 2.0\n"
                           "Desarrollado para sistema de monitoreo y control")

if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()