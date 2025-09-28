# parametro_frame.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import Cursor
from sensores import sensores_disponibles
from controlador import Controlador
from tema import tema_manager
import csv
from datetime import datetime
import numpy as np

class ParametroFrame(ttk.Frame):
    color_index = 0
    COLORS = ["#1f77b4", "#2ca02c", "#d62728", "#ff7f0e", "#9467bd", "#17becf"]

    def __init__(self, master, nombre, on_close=None):
        self.tema = tema_manager.tema_actual
        super().__init__(master, style="Card.TFrame" if self.tema == "claro" else "TFrame")
        
        self.nombre = nombre
        self.on_close_callback = on_close  # Callback para notificar cierre
        self.tiempo = []
        self.valores = []
        self.ciclo = 0
        self.running = False
        self.modo_control = "rango"
        self.sensor_func = None
        self.controlador = Controlador()
        
        # Configuración de estilo
        self.config(relief="raised", borderwidth=1, padding=10)
        self.color = self.COLORS[ParametroFrame.color_index % len(self.COLORS)]
        ParametroFrame.color_index += 1
        
        # Cabecera con arrastre
        self.crear_cabecera()
        
        # Controles
        self.crear_controles()
        
        # Gráfico
        self.crear_grafico()
        
        # Estado
        self.crear_barra_estado()
        
        # Configurar eventos
        self.bind_events()

    def crear_cabecera(self):
        frame_header = ttk.Frame(self)
        frame_header.pack(fill="x", pady=(0, 10))
        
        # Título con icono
        icon_label = ttk.Label(frame_header, text="●", foreground=self.color, 
                              font=("Arial", 12))
        icon_label.pack(side="left", padx=(0, 5))
        
        title_label = ttk.Label(frame_header, text=f"Parámetro: {self.nombre}", 
                               style="Title.TLabel")
        title_label.pack(side="left", fill="x", expand=True)
        
        # Botones de control
        btn_menu = ttk.Button(frame_header, text="⋯", width=2, 
                             command=self.mostrar_menu_contextual)
        btn_menu.pack(side="right", padx=(5, 0))
        
        btn_close = ttk.Button(frame_header, text="×", width=2, 
                              command=self.cerrar)
        btn_close.pack(side="right", padx=(5, 0))

    def crear_controles(self):
        frame_controls = ttk.Frame(self)
        frame_controls.pack(fill="x", pady=5)
        
        # Sensor selection
        ttk.Label(frame_controls, text="Sensor:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.sensor_var = tk.StringVar()
        self.sensor_box = ttk.Combobox(frame_controls, textvariable=self.sensor_var,
                                      values=list(sensores_disponibles.keys()),
                                      state="readonly", width=12)
        self.sensor_box.current(0)
        self.sensor_box.grid(row=0, column=1, padx=(0, 15))
        
        # Rango inputs
        self.min_entry_label = ttk.Label(frame_controls, text="Mín:")
        self.min_entry_label.grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.min_entry = ttk.Entry(frame_controls, width=6)
        self.min_entry.insert(0, "10")
        self.min_entry.grid(row=0, column=3, padx=(0, 10))
        
        self.max_entry_label = ttk.Label(frame_controls, text="Máx:")
        self.max_entry_label.grid(row=0, column=4, sticky="w", padx=(0, 5))
        self.max_entry = ttk.Entry(frame_controls, width=6)
        self.max_entry.insert(0, "30")
        self.max_entry.grid(row=0, column=5, padx=(0, 15))
        
        # Intervalo
        ttk.Label(frame_controls, text="Intervalo (s):").grid(row=0, column=6, sticky="w", padx=(0, 5))
        self.int_entry = ttk.Entry(frame_controls, width=5)
        self.int_entry.insert(0, "5")
        self.int_entry.grid(row=0, column=7, padx=(0, 15))
        
        # Botones de acción
        btn_frame = ttk.Frame(frame_controls)
        btn_frame.grid(row=0, column=8, columnspan=3, sticky="e")
        
        self.btn_start_rango = ttk.Button(btn_frame, text="Rango", width=8,
                                         command=lambda: self.iniciar("rango"),
                                         style="Secondary.TButton")
        self.btn_start_rango.pack(side="left", padx=2)
        
        self.btn_start_diario = ttk.Button(btn_frame, text="Diario", width=8,
                                          command=lambda: self.iniciar("diario"),
                                          style="Secondary.TButton")
        self.btn_start_diario.pack(side="left", padx=2)
        
        self.btn_stop = ttk.Button(btn_frame, text="Detener", width=8,
                                  command=self.detener,
                                  style="Secondary.TButton")
        self.btn_stop.pack(side="left", padx=2)
        
        self.btn_export = ttk.Button(btn_frame, text="Exportar", width=8,
                                    command=self.exportar_csv,
                                    style="Secondary.TButton")
        self.btn_export.pack(side="left", padx=2)

    def crear_grafico(self):
        # Configurar el estilo del gráfico según el tema
        plt.style.use("default")
        if tema_manager.tema_actual == "oscuro":
            plt.style.use("dark_background")
        
        # Crear figura y ejes
        self.fig, self.ax = plt.subplots(figsize=(6, 3))
        self.fig.patch.set_alpha(0)  # Hacer el fondo transparente
        
        # Crear línea inicial
        self.linea, = self.ax.plot([], [], "o-", color=self.color, 
                                  markersize=4, linewidth=1.5, label=self.nombre)
        
        # Configurar ejes
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Valor")
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc="upper right")
        
        # Crear canvas de matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        
        # Añadir toolbar de navegación
        toolbar_frame = ttk.Frame(self)
        toolbar_frame.pack(fill="x")
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
        
        # Empaquetar el canvas
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=(5, 0))
        
        # Añadir cursor
        self.cursor = Cursor(self.ax, useblit=True, color='red', linewidth=1)

    def crear_barra_estado(self):
        status_frame = ttk.Frame(self)
        status_frame.pack(fill="x", pady=(10, 0))
        
        # Indicador de estado
        self.status_canvas = tk.Canvas(status_frame, width=20, height=20, 
                                      highlightthickness=0, bg=self.tema_colors("bg_secondary"))
        self.status_canvas.pack(side="left", padx=(0, 10))
        self.estado_punto = self.status_canvas.create_oval(5, 5, 15, 15, fill="red")
        
        # Valor actual
        self.valor_label = ttk.Label(status_frame, text="Último valor: ---")
        self.valor_label.pack(side="left", padx=(0, 20))
        
        # Modo
        self.modo_label = ttk.Label(status_frame, text="Modo: Inactivo")
        self.modo_label.pack(side="left", padx=(0, 20))
        
        # Objetivo
        self.objetivo_label = ttk.Label(status_frame, text="Objetivo: ---")
        self.objetivo_label.pack(side="left")
        
        # Timestamp
        self.time_label = ttk.Label(status_frame, text="", style="Subtitle.TLabel")
        self.time_label.pack(side="right")

    def bind_events(self):
        # Eventos para arrastrar el panel
        self.bind("<ButtonPress-1>", self.start_drag)
        self.bind("<B1-Motion>", self.drag)
        
        # Eventos para redimensionar
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def tema_colors(self, key):
        return tema_manager.temas[tema_manager.tema_actual][key]

    def iniciar(self, modo):
        self.running = True
        self.modo_control = modo
        self.status_canvas.itemconfig(self.estado_punto, fill="green")
        self.modo_label.config(text=f"Modo: {modo.capitalize()}")
        
        # Ocultar/mostrar controles según el modo
        if modo == "diario":
            self.min_entry_label.grid_remove()
            self.min_entry.grid_remove()
            self.max_entry_label.grid_remove()
            self.max_entry.grid_remove()
        else:
            self.min_entry_label.grid()
            self.min_entry.grid()
            self.max_entry_label.grid()
            self.max_entry.grid()
        
        self.medir()

    def detener(self):
        self.running = False
        self.status_canvas.itemconfig(self.estado_punto, fill="red")
        self.modo_label.config(text="Modo: Inactivo")
        self.objetivo_label.config(text="Objetivo: ---")

    def medir(self):
        if not self.running:
            return
        
        try:
            intervalo = int(self.int_entry.get())
        except ValueError:
            messagebox.showwarning("Error", "Introduce un intervalo numérico válido")
            self.detener()
            return
        
        sensor_sel = self.sensor_var.get()
        self.sensor_func = sensores_disponibles.get(sensor_sel)
        if self.sensor_func is None:
            messagebox.showwarning("Error", "Selecciona un sensor válido")
            self.detener()
            return
        
        self.ciclo += 1
        valor = self.sensor_func()
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.tiempo.append(self.ciclo)
        self.valores.append(valor)
        
        # Actualizar interfaz
        self.valor_label.config(text=f"Último valor: {valor:.2f}")
        self.time_label.config(text=timestamp)
        
        # Lógica de control
        if self.modo_control == "rango":
            try:
                min_val = float(self.min_entry.get())
                max_val = float(self.max_entry.get())
            except ValueError:
                messagebox.showwarning("Error", "Introduce valores de rango numéricos válidos")
                self.detener()
                return
            
            # Imprimir respuesta de control en terminal
            if valor < min_val:
                respuesta = f"[{self.nombre}] Valor bajo ({valor:.2f}) -> Necesita subir (mín: {min_val:.2f})"
            elif valor > max_val:
                respuesta = f"[{self.nombre}] Valor alto ({valor:.2f}) -> Necesita bajar (máx: {max_val:.2f})"
            else:
                respuesta = f"[{self.nombre}] En objetivo ({valor:.2f}) dentro del rango [{min_val:.2f}, {max_val:.2f}]"
            hora = datetime.now().strftime('%H:%M:%S')
            print(f"[{hora}] {respuesta}")
            self.objetivo_label.config(text="Objetivo: ---")
            
            # Actualizar gráfico con rangos
            self.actualizar_grafico_rango(min_val, max_val)
            
        elif self.modo_control == "diario":
            respuesta = self.controlador.generar_respuesta(self.sensor_var.get(), valor)
            valor_objetivo = self.controlador.get_valor_objetivo(self.sensor_var.get())
            hora = datetime.now().strftime('%H:%M:%S')
            # Imprimir respuesta de control en terminal con hora
            print(f"[{hora}] [{self.nombre}] {respuesta}")
            self.objetivo_label.config(text=f"Objetivo: {valor_objetivo:.2f}" if valor_objetivo else "Objetivo: N/A")
            
            # Actualizar gráfico con objetivo
            self.actualizar_grafico_objetivo(valor_objetivo)
        
        # Programar próxima medición
        self.after(intervalo * 1000, self.medir)

    def actualizar_grafico_rango(self, min_val, max_val):
        self.ax.clear()
        
        # Dibujar datos
        self.ax.plot(self.tiempo, self.valores, "o-", color=self.color, 
                    markersize=4, linewidth=1.5, label=self.nombre)
        
        # Dibujar rangos
        self.ax.axhline(y=min_val, color="red", linestyle="--", linewidth=1, alpha=0.7, label="Mínimo")
        self.ax.axhline(y=max_val, color="red", linestyle="--", linewidth=1, alpha=0.7, label="Máximo")
        
        # Rellenar área entre rangos
        self.ax.axhspan(min_val, max_val, alpha=0.1, color="green")
        
        # Configurar ejes
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Valor")
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc="upper right")
        
        # Actualizar canvas
        self.canvas.draw()

    def actualizar_grafico_objetivo(self, valor_objetivo):
        self.ax.clear()
        
        # Dibujar datos
        self.ax.plot(self.tiempo, self.valores, "o-", color=self.color, 
                    markersize=4, linewidth=1.5, label=self.nombre)
        
        # Dibujar objetivo si está disponible
        if valor_objetivo is not None:
            self.ax.axhline(y=valor_objetivo, color="green", linestyle="-", 
                           linewidth=2, alpha=0.7, label="Objetivo")
        
        # Configurar ejes
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Valor")
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc="upper right")
        
        # Actualizar canvas
        self.canvas.draw()

    def exportar_csv(self):
        if not self.tiempo:
            messagebox.showinfo("Exportar", "No hay datos para exportar.")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv", 
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialfile=f"{self.nombre}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filepath:
            with open(filepath, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Tiempo", "Valor", "Parámetro", "Sensor"])
                for t, v in zip(self.tiempo, self.valores):
                    writer.writerow([t, v, self.nombre, self.sensor_var.get()])
            
            messagebox.showinfo("Exportar", f"Datos exportados a {filepath}")

    def mostrar_menu_contextual(self):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Duplicar", command=self.duplicar)
        menu.add_command(label="Renombrar", command=self.renombrar)
        menu.add_separator()
        menu.add_command(label="Configuración avanzada", command=self.config_avanzada)
        
        # Mostrar menú en la posición del ratón
        try:
            menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())
        finally:
            menu.grab_release()

    def duplicar(self):
        # Crear una copia de este parámetro
        master = self.master.master  # Navegar hasta el dashboard
        master.agregar_parametro(f"{self.nombre}_copia")

    def renombrar(self):
        nuevo_nombre = simpledialog.askstring("Renombrar", "Nuevo nombre:", initialvalue=self.nombre)
        if nuevo_nombre and nuevo_nombre != self.nombre:
            # Notificar al dashboard del cambio de nombre
            if self.on_close_callback:
                self.on_close_callback(self.nombre)  # Notificar cierre del nombre anterior
            
            self.nombre = nuevo_nombre
            # Actualizar la interfaz con el nuevo nombre
            for child in self.winfo_children():
                if isinstance(child, ttk.Frame) and hasattr(child, 'winfo_children'):
                    for subchild in child.winfo_children():
                        if isinstance(subchild, ttk.Label) and "Parámetro:" in subchild.cget("text"):
                            subchild.config(text=f"Parámetro: {self.nombre}")
            
            # Notificar al dashboard del nuevo nombre
            if self.on_close_callback:
                # En este caso, necesitaríamos una callback diferente para renombrar
                # Por simplicidad, guardaremos la configuración desde el dashboard
                pass

    def config_avanzada(self):
        # Diálogo de configuración avanzada
        pass

    def start_drag(self, event):
        self._drag_data = {"x": event.x, "y": event.y}

    def drag(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        
        # Mover el frame (solo para diseño con grid)
        if self.grid_info():
            row = self.grid_info()["row"]
            column = self.grid_info()["column"]
            # Lógica para reorganizar los paneles al arrastrar

    def on_enter(self, event):
        # Resaltar al pasar el ratón
        self.config(relief="solid")

    def on_leave(self, event):
        # Restaurar el estilo normal
        self.config(relief="raised")

    def cerrar(self):
        if messagebox.askyesno("Confirmar", f"¿Eliminar el parámetro '{self.nombre}'?"):
            if self.running:
                self.detener()
            
            # Notificar al dashboard antes de destruir
            if self.on_close_callback:
                self.on_close_callback(self.nombre)
            
            self.destroy()

    def winfo_exists(self):
    #Método auxiliar para verificar si el widget aún existe"""
        try:
        # Intentar acceder a una propiedad del widget
            return self.winfo_viewable() is not None
        except tk.TclError:
            return False