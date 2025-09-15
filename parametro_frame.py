import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sensores import sensores_disponibles
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
        self.sensor_func = None

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

        ttk.Label(frame_top, text="Mín:").pack(side="left")
        self.min_entry = ttk.Entry(frame_top, width=6)
        self.min_entry.insert(0, "10")
        self.min_entry.pack(side="left", padx=5)

        ttk.Label(frame_top, text="Máx:").pack(side="left")
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

        self.btn_start = ttk.Button(frame_btns, text="Iniciar", command=self.iniciar)
        self.btn_start.pack(side="left", padx=5)
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
        self.valor_label.pack(side="left")

        # --- Gráfico (ocupa todo el ancho) ---
        self.fig, self.ax = plt.subplots(figsize=(5,2))
        self.linea, = self.ax.plot([], [], "o-", color=self.color, label=self.nombre)
        self.ax.set_title(self.nombre)
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Valor")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

    def iniciar(self):
        self.running = True
        self.status_canvas.itemconfig(self.estado_punto, fill="green")
        self.medir()

    def detener(self):
        self.running = False
        self.status_canvas.itemconfig(self.estado_punto, fill="red")

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
            min_val = float(self.min_entry.get())
            max_val = float(self.max_entry.get())
            intervalo = int(self.int_entry.get())
        except ValueError:
            messagebox.showwarning("Error", "Introduce valores numéricos válidos")
            return

        sensor_sel = self.sensor_var.get()
        self.sensor_func = sensores_disponibles.get(sensor_sel)
        if self.sensor_func is None:
            messagebox.showwarning("Error", "Selecciona un sensor válido")
            return

        self.ciclo += 1
        valor = self.sensor_func()
        self.tiempo.append(self.ciclo)
        self.valores.append(valor)

        self.valor_label.config(text=f"Último valor: {valor:.2f}")

        # Log en consola
        if valor < min_val:
            print(f"[{self.nombre}] {valor:.2f} -> Respuesta BAJA")
        elif valor > max_val:
            print(f"[{self.nombre}] {valor:.2f} -> Respuesta ALTA")
        else:
            print(f"[{self.nombre}] {valor:.2f} -> En rango")

        # Actualizar gráfico (limpiamos líneas previas de referencia antes de dibujar)
        # Para evitar acumulación de líneas de límite, borramos y redibujamos el eje
        self.ax.cla()
        self.ax.plot(self.tiempo, self.valores, "o-", color=self.color, label=self.nombre)
        self.ax.set_title(self.nombre)
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Valor")
        # Líneas de referencia
        self.ax.axhline(y=min_val, color="red", linestyle="--", linewidth=0.8)
        self.ax.axhline(y=max_val, color="red", linestyle="--", linewidth=0.8)
        self.ax.legend(loc="upper right", fontsize="small")
        self.canvas.draw()

        self.after(intervalo * 1000, self.medir)

    def cerrar(self):
        if messagebox.askyesno("Confirmar", f"¿Seguro que deseas eliminar el parámetro '{self.nombre}'?"):
            if self.running:
                self.detener()
            self.destroy()
