import tkinter as tk
from tkinter import messagebox
from app import My_App

# Fonction de protection globale pour capturer les erreurs de l'interface et des callbacks
def show_error(exc, val, tb):
    import traceback
    error_details = "".join(traceback.format_exception(exc, val, tb))
    messagebox.showerror("Erreur interne du système", f"Une erreur inattendue est survenue dans l'interface :\n{val}\n\nDétails techniques de l'erreur :\n{error_details}")

if __name__ == "__main__":
    root = tk.Tk()
    root.report_callback_exception = show_error  # Activation de la sécurité globale de l'interface
    app = My_App(root)
    root.mainloop()
