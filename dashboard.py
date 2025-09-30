# dashboard.py
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from parametro_frame import ParametroFrame
from tema import tema_manager
import json
import os
# Añadir estas importaciones al inicio
from ambiente_frame import AmbienteFrame
import json
import os

class Dashboard(tk.Tk):
    def on_resize(self, event):
        # Aquí puedes agregar lógica para ajustar el layout si es necesario
        pass
    def crear_barra_estado(self):
        statusbar = ttk.Frame(self)
        statusbar.pack(side="bottom", fill="x")
        lbl_status = ttk.Label(statusbar, text="Listo", style="Subtitle.TLabel")
        lbl_status.pack(side="left", padx=10)
        lbl_tema = ttk.Label(statusbar, text=f"Tema: {tema_manager.tema_actual.capitalize()}", style="Subtitle.TLabel")
        lbl_tema.pack(side="right", padx=10)
    def organizar_paneles(self):
        messagebox.showinfo("Organizar Paneles", "Los ambientes se han organizado automáticamente.")
    def mostrar_acerca_de(self):
        messagebox.showinfo("Acerca de", 
            "Dashboard de Control de Ambientes\n\n"
            "Versión multiambiente\n"
            "Desarrollado para sistema de monitoreo y control ambiental")
    def crear_menu(self):
        menubar = tk.Menu(self)
        self.configure(menu=menubar)
        # Menú Archivo
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Nuevo ambiente", command=self.agregar_ambiente)
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
    def __init__(self):
        super().__init__()
        
        # Configuración inicial
        self.title("Dashboard de Control de Ambientes")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        # Aplicar tema
        self.tema = tema_manager.aplicar_tema()
        
        # Cargar configuración
        self.config_file = "dashboard_config.json"
        self.app_config = self.cargar_configuracion()
        
        # Lista para rastrear ambientes activos
        self.ambientes_activos = {}
        
        # Configurar icono
        try:
            self.iconbitmap("icon.ico")
        except:
            pass
        
        # Barra de menú superior
        self.crear_menu()
        
        # Panel principal con pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña de ambientes
        self.tab_ambientes = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.tab_ambientes, text="Ambientes")
        
        # Barra de herramientas superior
        self.crear_barra_herramientas()
        
        # Área de contenido con scroll para ambientes
        self.crear_area_contenido_ambientes()
        
        # Barra de estado inferior
        self.crear_barra_estado()
        
        # Cargar ambientes guardados
        self.cargar_ambientes_guardados()
        
        self.bind("<Configure>", self.on_resize)

    def crear_barra_herramientas(self):
        toolbar = ttk.Frame(self.tab_ambientes, height=40)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        btn_agregar_ambiente = ttk.Button(toolbar, text="+ Agregar Ambiente", 
                                        command=self.agregar_ambiente, style="Primary.TButton")
        btn_agregar_ambiente.pack(side="left", padx=5)
        
        btn_organizar = ttk.Button(toolbar, text="Organizar Paneles", 
                                  command=self.organizar_paneles, style="Secondary.TButton")
        btn_organizar.pack(side="left", padx=5)

    def crear_area_contenido_ambientes(self):
        # Marco para el área de contenido de ambientes
        content_frame = ttk.Frame(self.tab_ambientes)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Canvas con scrollbar para ambientes
        self.canvas_ambientes = tk.Canvas(content_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.canvas_ambientes.yview)
        self.scrollable_frame_ambientes = ttk.Frame(self.canvas_ambientes)
        
        self.scrollable_frame_ambientes.bind(
            "<Configure>",
            lambda e: self.canvas_ambientes.configure(scrollregion=self.canvas_ambientes.bbox("all"))
        )
        
        self.canvas_window_ambientes = self.canvas_ambientes.create_window((0, 0), 
                                                                         window=self.scrollable_frame_ambientes, 
                                                                         anchor="nw")
        self.canvas_ambientes.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetado
        self.canvas_ambientes.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind para redimensionar el contenido
        self.canvas_ambientes.bind("<Configure>", self.on_canvas_ambientes_configure)

    def agregar_ambiente(self, nombre=None, config=None):
        if not nombre:
            nombre = simpledialog.askstring("Nuevo Ambiente", "Nombre del ambiente:")
            if not nombre:
                return
        
        # Verificar si el ambiente ya existe
        if nombre in self.ambientes_activos:
            messagebox.showwarning("Advertencia", f"Ya existe un ambiente con el nombre '{nombre}'")
            return
        
        # Crear el frame del ambiente
        ambiente_frame = AmbienteFrame(self.scrollable_frame_ambientes, nombre, 
                                     on_close=self.ambiente_cerrado,
                                     on_parametro_change=self.guardar_configuracion)
        
        # Configurar parámetros si se proporciona configuración
        if config and "parametros" in config:
            for param_config in config["parametros"]:
                ambiente_frame.agregar_parametro_desde_config(param_config)
        
        # Registrar ambiente activo
        self.ambientes_activos[nombre] = ambiente_frame
        
        # Organizar en la vista
        ambiente_frame.pack(fill="x", expand=False, padx=10, pady=10)
        
        # Guardar la configuración
        self.guardar_configuracion()

    def ambiente_cerrado(self, nombre_ambiente):
        """Callback llamado cuando se cierra un ambiente"""
        if nombre_ambiente in self.ambientes_activos:
            del self.ambientes_activos[nombre_ambiente]
            self.guardar_configuracion()

    def cargar_configuracion(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Mantener compatibilidad con versiones anteriores
                    if "ambientes" not in config and "parametros" in config:
                        # Convertir configuración antigua a nueva estructura
                        config = {
                            "tema": config.get("tema", "claro"),
                            "vista": config.get("vista", "tarjetas"),
                            "ambientes": [{
                                "nombre": "Ambiente Principal",
                                "parametros": config.get("parametros", [])
                            }]
                        }
                    return config
            except Exception as e:
                print(f"Error cargando configuración: {e}")
        return {"tema": "claro", "vista": "tarjetas", "ambientes": []}

    def guardar_configuracion(self):
        ambientes_config = []
        
        for nombre, ambiente_frame in self.ambientes_activos.items():
            if hasattr(ambiente_frame, 'winfo_exists') and ambiente_frame.winfo_exists():
                parametros = ambiente_frame.obtener_configuracion_parametros()
                ambientes_config.append({
                    "nombre": nombre,
                    "parametros": parametros
                })
        
        config = {
            "tema": tema_manager.tema_actual,
            "vista": self.vista_var.get() if hasattr(self, 'vista_var') else "tarjetas",
            "ambientes": ambientes_config
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error guardando configuración: {e}")

    def cargar_ambientes_guardados(self):
        for ambiente_config in self.app_config.get("ambientes", []):
            self.agregar_ambiente(ambiente_config["nombre"], ambiente_config)

    def on_canvas_ambientes_configure(self, event):
        self.canvas_ambientes.itemconfig(self.canvas_window_ambientes, width=event.width)
