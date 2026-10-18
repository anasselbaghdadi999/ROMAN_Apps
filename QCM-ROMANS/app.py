import tkinter as tk
from config import (
    BG_COLOR,
    FRAME_COLOR,
    FG_COLOR,
    BTN_COLOR,
    BTN_HOVER,
    ANS_COLOR,
    ACCENT_COLOR,
    BTN_FG_DARK,
)
from ai_service import AIServiceMixin, load_api_key_and_create_client


class My_App(AIServiceMixin):
    def __init__(self, master):
        self.master = master
        self.master.title("Générateur de Questions - 1ère Année Bac")
        self.master.geometry("1110x700")
        self.master.minsize(800, 550)

        # Couleurs sombres modernes (نفس القيم الأصلية، مستوردة من config.py)
        self.bg_color = BG_COLOR
        self.frame_color = FRAME_COLOR
        self.fg_color = FG_COLOR
        self.btn_color = BTN_COLOR
        self.btn_hover = BTN_HOVER
        self.ans_color = ANS_COLOR
        self.accent_color = ACCENT_COLOR

        self.master.configure(bg=self.bg_color)

        self.hidden_answer = ""
        self.hidden_source = ""

        # ================== الاتصال بالـ API ==================
        result = load_api_key_and_create_client(self.master)
        if result is None:
            return
        self.API_KEY, self.client = result


        #=============== Frame and Buttons and Labels ===============

        self.left_frame = tk.Frame(master, bg=self.frame_color, width=100, height=40)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Le frame principal qui contiendra tout sur le côté droit
        self.basic_frame = tk.Frame(master, bg=self.bg_color)
        self.basic_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.label_QCM = tk.Label(self.basic_frame, text="", font=("Arial", 13), wraplength=600, justify=tk.CENTER, bg=self.bg_color, fg=self.fg_color)

        self.button_show_answer = tk.Button(self.basic_frame, text="Afficher la réponse", cursor="hand2", command=self.show_answer, state=tk.DISABLED, font=("Arial", 12, "bold"), bg=self.accent_color, fg="#11111B", activebackground=self.btn_hover, activeforeground=self.fg_color, relief=tk.FLAT, width=25, pady=8)

        self.label_Answer = tk.Label(self.basic_frame, text="", font=("Arial", 12, "bold"), fg=self.fg_color, bg=self.bg_color)

        self.answer_frame = tk.Frame(self.basic_frame, bg=self.bg_color)

        self.scrollbar = tk.Scrollbar(self.answer_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.answer_text = tk.Text(self.answer_frame, height=8, width=75, wrap=tk.WORD, yscrollcommand=self.scrollbar.set, font=("Arial", 11), bg=self.bg_color, fg=self.ans_color, relief=tk.FLAT, state=tk.DISABLED)
        self.answer_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.answer_text.yview)

        button_style = {
            "font": ("Arial", 11, "bold"),
            "bg": self.btn_color,
            "fg": self.fg_color,
            "activebackground": self.btn_hover,
            "activeforeground": self.fg_color,
            "relief": tk.FLAT,
            "width": 32,
            "pady": 8
        }

        romon = tk.Label(self.left_frame, text="Choisissez le roman \n pour générer une question", font=("Arial", 14, "bold"), bg=self.frame_color, fg=self.fg_color)
        romon.pack(pady=15)

        self.button_la_boite_a_merveille = tk.Button(self.left_frame, text="La Boîte à Merveilles", cursor="hand2", command=lambda: self.generate_question("La Boîte à Merveilles"), **button_style)
        self.button_la_boite_a_merveille.pack(pady=6)

        self.button_antigone = tk.Button(self.left_frame, text="Antigone", cursor="hand2", command=lambda: self.generate_question("Antigone"), **button_style)
        self.button_antigone.pack(pady=6)

        self.button_le_dernier_jour_d_un_condamne = tk.Button(self.left_frame, text="Le Dernier Jour d'un Condamné", cursor="hand2", command=lambda: self.generate_question("Le Dernier Jour d'un Condamné"), **button_style)
        self.button_le_dernier_jour_d_un_condamne.pack(pady=6)

        # Message de bienvenue au début
        self.label_wilcome = tk.Label(self.basic_frame, text="📚 Prêt pour l'examen ?\n🎯 Choisissez un roman pour commencer.",
                                    font=("Helvetica", 20, "bold"),
                                    wraplength=650,
                                    justify=tk.CENTER,
                                    bg=self.bg_color,
                                    fg=self.fg_color
        )
        self.label_wilcome.pack(pady=20)

    def safe_update_ui(self, target_widget, **kwargs):
        self.master.after(0, lambda: target_widget.config(**kwargs))

    def show_answer(self):
        if self.hidden_answer:
            self.label_Answer.config(text="Réponse :")
            content = self.hidden_answer
            if self.hidden_source:
                content += "\n\n" + "="*50 + "\n" + self.hidden_source

            self.answer_text.config(state=tk.NORMAL)
            self.answer_text.delete("1.0", tk.END)
            self.answer_text.insert(tk.END, content)
            self.answer_text.config(state=tk.DISABLED)
