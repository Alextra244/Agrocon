import tkinter as tk
from tkinter import ttk, simpledialog
from parametro_frame import ParametroFrame

def aplicar_estilos():
    style = ttk.Style()

    # Selecciona un tema base (vista, clam, default)
    style.theme_use("clam")

    # Colores base
    COLOR_BG = "#f5f6fa"     # fondo general
    COLOR_FRAME = "#ffffff"  # fondo de bloques
    COLOR_ACCENT = "#4a90e2" # azul moderno
    COLOR_TEXT = "#333333"   # texto principal

    # Frame
    style.configure("TFrame",
                    background=COLOR_BG)

    # Labels
    style.configure("TLabel",
                    background=COLOR_FRAME,
                    foreground=COLOR_TEXT,
                    font=("Segoe UI", 10))

    # Buttons
    style.configure("TButton",
                    background=COLOR_ACCENT,
                    foreground="white",
                    font=("Segoe UI", 10, "bold"),
                    padding=6)
    style.map("TButton",
              background=[("active", "#357ABD")])

    # Entry
    style.configure("TEntry",
                    fieldbackground="#f0f0f0",
                    foreground=COLOR_TEXT,
                    padding=4)

    # Combobox
    style.configure("TCombobox",
                    fieldbackground="#f0f0f0",
                    foreground=COLOR_TEXT,
                    padding=4)


class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()

        # 👉 Aplicamos los estilos
        aplicar_estilos()

        self.title("Dashboard de Parámetros")
        self.geometry("1000x600")

        # Barra superior
        top_bar = ttk.Frame(self)
        top_bar.pack(side="top", fill="x")

        btn_add = ttk.Button(top_bar, text="+", command=self.agregar_parametro)
        btn_add.pack(side="right", padx=10, pady=10)

        # Contenedor principal
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        # Canvas + scrollbar
        self.canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Actualiza el scrollregion
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Ventana del canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Ajusta ancho dinámicamente
        def _on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)

        self.canvas.bind("<Configure>", _on_canvas_configure)

        # Empaquetado
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def agregar_parametro(self):
        nombre = simpledialog.askstring("Nuevo parámetro", "Nombre del parámetro:")
        if nombre:
            bloque = ParametroFrame(self.scrollable_frame, nombre)
            bloque.pack(fill="x", expand=False, padx=10, pady=10)


if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()
