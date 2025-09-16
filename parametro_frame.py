import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sensores import sensores_disponibles
from controlador import Controlador # Importamos el nuevo controlador
import csv

# Paleta simple
COLORES = ["#1f77b4", "#2ca02c", "#d62728", "#ff7f0e", "#9467bd", "#17becf"]

class ParametroFrame(ttk.Frame):
    color_index = 0

    def __init__(self, master, nombre):
        super().__init__(master, relief="raised", borderwidth=2, padding=5)
        self.nombre = nombre
        self.tiempo = []
        self.valores = []
        self.ciclo = 0
        self.running = False
        self.modo_control = "rango" # Nuevo atributo para el modo de operación
        self.sensor_func = None
        self.controlador = Controlador() # Instancia del controlador

        # Color asignado
        self.color = COLORES[ParametroFrame.color_index % len(COLORES)]
        ParametroFrame.color_index += 1

        # --- Cabecera: título + botón cerrar ---
        frame_header = ttk.Frame(self)
        frame_header.pack(fill="x", pady=2, padx=2)

        lbl = ttk.Label(frame_header, text=f"Parámetro: {self.nombre}", font=("Arial", 11, "bold"))
        lbl.pack(side="left", anchor="w")

        btn_close = ttk.Button(frame_header, text="❌", width=3, command=self.cerrar)
        btn_close.pack(side="right")

        # --- Selección sensor y entradas en una única fila ---
        frame_top = ttk.Frame(self)
        frame_top.pack(fill="x", pady=4, padx=6)

        ttk.Label(frame_top, text="Sensor:").pack(side="left")
        self.sensor_var = tk.StringVar()
        self.sensor_box = ttk.Combobox(
            frame_top,
            textvariable=self.sensor_var,
            values=list(sensores_disponibles.keys()),
            state="readonly",
            width=10
        )
        self.sensor_box.current(0)
        self.sensor_box.pack(side="left", padx=(5, 15))

        # --- Entradas de rango (se ocultarán en modo de control) ---
        self.min_entry_label = ttk.Label(frame_top, text="Mín:")
        self.min_entry_label.pack(side="left")
        self.min_entry = ttk.Entry(frame_top, width=6)
        self.min_entry.insert(0, "10")
        self.min_entry.pack(side="left", padx=5)

        self.max_entry_label = ttk.Label(frame_top, text="Máx:")
        self.max_entry_label.pack(side="left")
        self.max_entry = ttk.Entry(frame_top, width=6)
        self.max_entry.insert(0, "30")
        self.max_entry.pack(side="left", padx=5)

        ttk.Label(frame_top, text="Intervalo (s):").pack(side="left", padx=(10,0))
        self.int_entry = ttk.Entry(frame_top, width=5)
        self.int_entry.insert(0, "5")
        self.int_entry.pack(side="left", padx=5)

        # --- Botones iniciar/detener/exportar ---
        frame_btns = ttk.Frame(self)
        frame_btns.pack(fill="x", pady=4, padx=6)

        self.btn_start_rango = ttk.Button(frame_btns, text="Iniciar (Rango)", command=lambda: self.iniciar("rango"))
        self.btn_start_rango.pack(side="left", padx=5)
        self.btn_start_diario = ttk.Button(frame_btns, text="Iniciar (Diario)", command=lambda: self.iniciar("diario"))
        self.btn_start_diario.pack(side="left", padx=5)
        self.btn_stop = ttk.Button(frame_btns, text="Detener", command=self.detener)
        self.btn_stop.pack(side="left", padx=5)

        self.btn_export = ttk.Button(frame_btns, text="Exportar CSV", command=self.exportar_csv)
        self.btn_export.pack(side="left", padx=5)

        # --- Estado y último valor ---
        frame_status = ttk.Frame(self)
        frame_status.pack(fill="x", pady=4, padx=6)

        ttk.Label(frame_status, text="Estado:").pack(side="left")
        self.status_canvas = tk.Canvas(frame_status, width=18, height=18, highlightthickness=0)
        self.status_canvas.pack(side="left", padx=(5,10))
        self.estado_punto = self.status_canvas.create_oval(3, 3, 15, 15, fill="red")

        self.valor_label = ttk.Label(frame_status, text="Último valor: ---")
        self.valor_label.pack(side="left", padx=(0, 20))
        
        self.modo_label = ttk.Label(frame_status, text="Modo: Inactivo")
        self.modo_label.pack(side="left", padx=(0, 20))

        self.objetivo_label = ttk.Label(frame_status, text="Objetivo: ---")
        self.objetivo_label.pack(side="left")

        # --- Gráfico (ocupa todo el ancho) ---
        self.fig, self.ax = plt.subplots(figsize=(5,2))
        self.linea, = self.ax.plot([], [], "o-", color=self.color, label=self.nombre)
        self.ax.set_title(self.nombre)
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Valor")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

    def iniciar(self, modo):
        self.running = True
        self.modo_control = modo
        self.status_canvas.itemconfig(self.estado_punto, fill="green")
        self.modo_label.config(text=f"Modo: {modo.capitalize()}")

        # Ocultar o mostrar elementos según el modo
        if modo == "diario":
            self.min_entry_label.pack_forget()
            self.min_entry.pack_forget()
            self.max_entry_label.pack_forget()
            self.max_entry.pack_forget()
        else: # modo == "rango"
            self.min_entry_label.pack(side="left")
            self.min_entry.pack(side="left", padx=5)
            self.max_entry_label.pack(side="left")
            self.max_entry.pack(side="left", padx=5)

        self.medir()

    def detener(self):
        self.running = False
        self.status_canvas.itemconfig(self.estado_punto, fill="red")
        self.modo_label.config(text="Modo: Inactivo")
        self.objetivo_label.config(text="Objetivo: ---")

    def exportar_csv(self):
        if not self.tiempo:
            messagebox.showinfo("Exportar", "No hay datos para exportar.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if filepath:
            with open(filepath, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Tiempo", "Valor"])
                writer.writerows(zip(self.tiempo, self.valores))
            messagebox.showinfo("Exportar", f"Datos exportados a {filepath}")

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
        self.tiempo.append(self.ciclo)
        self.valores.append(valor)
        self.valor_label.config(text=f"Último valor: {valor:.2f}")

        # Lógica de control basada en el modo
        if self.modo_control == "rango":
            try:
                min_val = float(self.min_entry.get())
                max_val = float(self.max_entry.get())
            except ValueError:
                messagebox.showwarning("Error", "Introduce valores de rango numéricos válidos")
                self.detener()
                return

            if valor < min_val:
                print(f"[{self.nombre}] {valor:.2f} -> Respuesta BAJA")
            elif valor > max_val:
                print(f"[{self.nombre}] {valor:.2f} -> Respuesta ALTA")
            else:
                print(f"[{self.nombre}] {valor:.2f} -> En rango")
            
            self.objetivo_label.config(text="Objetivo: ---")
            
            # Gráfico con líneas de rango
            self.ax.cla()
            self.ax.plot(self.tiempo, self.valores, "o-", color=self.color, label=self.nombre)
            self.ax.axhline(y=min_val, color="red", linestyle="--", linewidth=0.8)
            self.ax.axhline(y=max_val, color="red", linestyle="--", linewidth=0.8)

        elif self.modo_control == "diario":
            # Usamos el nuevo controlador
            respuesta = self.controlador.generar_respuesta(self.sensor_var.get(), valor)
            valor_objetivo = self.controlador.get_valor_objetivo(self.sensor_var.get())
            print(f"[{self.nombre}] {valor:.2f} -> {respuesta}")
            self.objetivo_label.config(text=f"Objetivo: {valor_objetivo:.2f}" if valor_objetivo is not None else "Objetivo: N/A")
            
            # Gráfico con línea de objetivo
            self.ax.cla()
            self.ax.plot(self.tiempo, self.valores, "o-", color=self.color, label=self.nombre)
            if valor_objetivo is not None:
                self.ax.axhline(y=valor_objetivo, color="green", linestyle="-", linewidth=1.5)

        self.ax.set_title(self.nombre)
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Valor")
        self.ax.legend(loc="upper right", fontsize="small")
        self.canvas.draw()

        self.after(intervalo * 1000, self.medir)

    def cerrar(self):
        if messagebox.askyesno("Confirmar", f"¿Seguro que deseas eliminar el parámetro '{self.nombre}'?"):
            if self.running:
                self.detener()
            self.destroy()