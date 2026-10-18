import tkinter as tk
import customtkinter as ctk
from pathlib import Path
from utils import ar
from config import (
    BG_COLOR,
    SIDEBAR_COLOR,
    FG_COLOR,
    BTN_COLOR,
    BTN_HOVER,
    ANS_COLOR,
    ACCENT_COLOR,
    APPEARANCE_MODE,
    ROMANS_FOLDER,
)
from ai_service import AIServiceMixin, load_api_key_and_create_client


class My_App(AIServiceMixin):
    def __init__(self, master):
        self.master = master
        self.master.title("Lexique des Romans")
        self.master.geometry("1000x750")
        self.master.minsize(850, 650)

        # الألوان العصرية الداكنة (نفس القيم الأصلية، مستوردة من config.py)
        self.bg_color = BG_COLOR       # لون الخلفية الرئيسي
        self.sidebar_color = SIDEBAR_COLOR  # لون القائمة الجانبية والصناديق
        self.fg_color = FG_COLOR       # لون النصوص الأساسية
        self.btn_color = BTN_COLOR      # لون الأزرار
        self.btn_hover = BTN_HOVER      # لون الأزرار عند تمرير الماوس
        self.ans_color = ANS_COLOR      # لون الإجابة
        self.accent_color = ACCENT_COLOR   # لون التحديد

        # إعداد ثيم CustomTkinter
        ctk.set_appearance_mode(APPEARANCE_MODE)
        self.master.configure(fg_color=self.bg_color)

        self.hidden_answer = ""
        self.hidden_source = ""
        self.context_choices = []
        self.is_processing = False  # القفل لمنع تكرار الطلبات

        # مسار مجلد المشروع الأساسي لضمان ثبات القراءة والحفظ
        self.project_path = Path(__file__).parent
        # مجلد الروايات الفرعي: lexique-romans/romans/
        self.data_dir = self.project_path / ROMANS_FOLDER
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # ================== الاتصال بالـ API ==================
        result = load_api_key_and_create_client(self.master)
        if result is None:
            return
        self.API_KEY, self.client = result

        # ================== تخطيط الواجهة (Layout) ==================
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)

        # 1. شريط القائمة الجانبية (Sidebar)
        self.sidebar_frame = ctk.CTkFrame(self.master, width=280, corner_radius=0, fg_color=self.sidebar_color)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        logo_label = ctk.CTkLabel(self.sidebar_frame, text="📚 Lexique\nBac Marocain",
                                   font=ctk.CTkFont(size=24, weight="bold"), text_color=self.fg_color)
        logo_label.grid(row=0, column=0, padx=20, pady=(40, 30))

        btn_font = ctk.CTkFont(size=14, weight="bold")

        self.btn_boite = ctk.CTkButton(self.sidebar_frame, text="La Boîte à Merveilles", font=btn_font, height=45, cursor="hand2",
                                       fg_color=self.btn_color, hover_color=self.btn_hover, command=self.la_boite_a_merveilles)
        self.btn_boite.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_antigone = ctk.CTkButton(self.sidebar_frame, text="Antigone", font=btn_font, height=45, cursor="hand2",
                                          fg_color=self.btn_color, hover_color=self.btn_hover, command=self.antigone)
        self.btn_antigone.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_condamne = ctk.CTkButton(self.sidebar_frame, text="Le Dernier Jour...", font=btn_font, height=45, cursor="hand2",
                                          fg_color=self.btn_color, hover_color=self.btn_hover, command=self.le_dernier_jour_d_un_condamne)
        self.btn_condamne.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # 2. الإطار الرئيسي (Main View)
        self.main_frame = ctk.CTkFrame(self.master, corner_radius=0, fg_color=self.bg_color)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.show_welcome_screen()

    # ================== وظائف واجهة المستخدم الديناميكية ==================

    def show_welcome_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        welcome_label = ctk.CTkLabel(self.main_frame, text="👋 Bienvenue dans le Lexique",
                                      font=ctk.CTkFont(size=30, weight="bold"), text_color=self.fg_color)
        welcome_label.pack(expand=True, pady=(0, 10))

        sub_label = ctk.CTkLabel(self.main_frame, text="Veuillez sélectionner un roman depuis le menu à gauche.",
                                  font=ctk.CTkFont(size=16), text_color=self.accent_color)
        sub_label.pack(expand=True, pady=(0, 150))

    def build_novel_view(self, roman_name, file_name):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        header_label = ctk.CTkLabel(self.main_frame, text=f"📖 {roman_name}",
                                     font=ctk.CTkFont(size=24, weight="bold"), text_color=self.fg_color)
        header_label.pack(pady=(20, 10))

        search_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        search_container.pack(pady=15, fill="x", padx=40)

        word_entry = ctk.CTkEntry(search_container, font=ctk.CTkFont(size=14), height=40,
                                   placeholder_text="Entrez le mot ou la phrase à chercher...",
                                   fg_color=self.btn_color, border_color=self.accent_color, border_width=1)
        word_entry.pack(side="left", expand=True, fill="x", padx=(0, 15))

        search_button = ctk.CTkButton(search_container, text="🔍 Chercher", font=ctk.CTkFont(size=14, weight="bold"), cursor="hand2",
                                       height=40, fg_color=self.accent_color, hover_color=self.btn_hover,
                                       command=lambda: self.search_word_context(word_entry, result_listbox, file_name))
        search_button.pack(side="right")

        list_frame = ctk.CTkFrame(self.main_frame, fg_color=self.sidebar_color, corner_radius=10)
        list_frame.pack(pady=10, fill="both", expand=True, padx=40)

        scrollbar = ctk.CTkScrollbar(list_frame)
        scrollbar.pack(side="right", fill="y", padx=5, pady=5)

        result_listbox = tk.Listbox(list_frame, font=("Arial", 12), bg=self.sidebar_color, fg=self.fg_color,
                                     selectbackground=self.accent_color, selectforeground=self.fg_color,
                                     bd=0, highlightthickness=0, yscrollcommand=scrollbar.set)
        result_listbox.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        scrollbar.configure(command=result_listbox.yview)

        explanation_box = ctk.CTkTextbox(self.main_frame, font=("Arial", 14), height=130,
                                          fg_color=self.sidebar_color, text_color=self.ans_color,
                                          border_width=1, border_color=self.accent_color, corner_radius=10,
                                          wrap="word")
        explanation_box.pack(pady=(10, 20), fill="x", padx=40)

        initial_text = ar("Sélectionnez une occurrence dans la liste ci-dessus pour l'expliquer via Gemini...")
        explanation_box.insert("1.0", initial_text)
        explanation_box.configure(state="disabled")

        result_listbox.bind("<<ListboxSelect>>", lambda event: self.on_context_select(event, result_listbox, word_entry, explanation_box, roman_name))

    # ================== استدعاء الواجهات ==================

    def la_boite_a_merveilles(self):
        self.build_novel_view("La Boîte à Merveilles", "la boite a merveilles.txt")

    def antigone(self):
        self.build_novel_view("Antigone", "Antigone.txt")

    def le_dernier_jour_d_un_condamne(self):
        self.build_novel_view("Le Dernier Jour d'un Condamné", "Le dernier jour d'un condamne.txt")

    # ================== المنطق الأساسي ==================

    def update_textbox_content(self, textbox_widget, content_text, text_color):
        def action():
            textbox_widget.configure(state="normal")
            textbox_widget.delete("1.0", tk.END)
            textbox_widget.insert("1.0", content_text)
            textbox_widget.configure(text_color=text_color, state="disabled")
        self.master.after(0, action)
