# tema.py
import tkinter as tk
from tkinter import ttk

class TemaManager:
    def __init__(self):
        self.tema_actual = "claro"
        self.temas = {
            "claro": {
                "bg_primary": "#f8f9fa",
                "bg_secondary": "#ffffff",
                "bg_accent": "#0d6efd",
                "text_primary": "#212529",
                "text_secondary": "#6c757d",
                "success": "#198754",
                "warning": "#ffc107",
                "danger": "#dc3545",
                "border": "#dee2e6"
            },
            "oscuro": {
                "bg_primary": "#212529",
                "bg_secondary": "#343a40",
                "bg_accent": "#0d6efd",
                "text_primary": "#f8f9fa",
                "text_secondary": "#adb5bd",
                "success": "#198754",
                "warning": "#ffc107",
                "danger": "#dc3545",
                "border": "#495057"
            }
        }
    
    def aplicar_tema(self, tema_nombre=None):
        if tema_nombre:
            self.tema_actual = tema_nombre
        
        tema = self.temas[self.tema_actual]
        style = ttk.Style()
        
        # Configurar el tema base
        style.theme_use("clam")
        
        # Configurar estilos
        style.configure("TFrame", background=tema["bg_primary"])
        style.configure("TLabel", background=tema["bg_secondary"], foreground=tema["text_primary"])
        style.configure("Title.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10, "bold"))
        
        # Botones
        style.configure("Primary.TButton", 
                       background=tema["bg_accent"],
                       foreground="white",
                       font=("Segoe UI", 10, "bold"),
                       padding=(10, 5))
        style.map("Primary.TButton",
                 background=[("active", "#0b5ed7")])
                 
        style.configure("Secondary.TButton",
                       background=tema["bg_secondary"],
                       foreground=tema["text_primary"],
                       font=("Segoe UI", 9),
                       padding=(8, 4))
        
        # Entradas
        style.configure("TEntry",
                       fieldbackground=tema["bg_secondary"],
                       foreground=tema["text_primary"],
                       borderwidth=1,
                       focusthickness=1,
                       focuscolor=tema["bg_accent"])
        
        # Combobox
        style.configure("TCombobox",
                       fieldbackground=tema["bg_secondary"],
                       foreground=tema["text_primary"],
                       selectbackground=tema["bg_accent"])
        
        # Scrollbar
        style.configure("TScrollbar",
                       background=tema["bg_secondary"],
                       troughcolor=tema["bg_primary"],
                       bordercolor=tema["border"],
                       arrowcolor=tema["text_primary"])
        
        return tema

# Instancia global del gestor de temas
tema_manager = TemaManager()