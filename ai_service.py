import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from google import genai
from google.genai import types
import threading
import re
from utils import ar


def load_api_key_and_create_client(master):
    """الاتصال بـ Gemini API — منقول حرفياً من My_App.__init__ الأصلي."""
    home_directory = Path.home()
    api_file_path = home_directory / ".EXPLICE_ROMAN_API_GEMINI"

    if api_file_path.exists():
        with open(api_file_path, "r") as file:
            API_KEY = file.read().strip()
    else:
        messagebox.showerror("Erreur", f"Le fichier caché est introuvable dans :\n{api_file_path}")
        master.destroy()
        return None

    try:
        client = genai.Client(api_key=API_KEY)
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur d'initialisation du client :\n{e}")
        master.destroy()
        return None

    return API_KEY, client


class AIServiceMixin:
    """ميكسين يجمع كل منطق البحث والذكاء الاصطناعي والحفظ — منقول قصاً ولصقاً من الكلاس الأصلي."""

    def _resolve_data_file(self, filename):
        """يرجع مسار الملف داخل مجلد romans، مع توافق قديم إذا كان بجانب الكود."""
        primary = self.data_dir / filename
        if primary.exists():
            return primary
        legacy = self.project_path / filename
        if legacy.exists():
            return legacy
        return primary

    def search_word_context(self, word_entry, result_listbox, file_name):
        target_phrase = word_entry.get().strip().lower()
        if not target_phrase:
            messagebox.showwarning("Attention", "Veuillez saisir un mot !")
            return

        result_listbox.delete(0, tk.END)
        self.context_choices = []

        target_file_path = self._resolve_data_file(file_name)

        if not target_file_path.exists():
            messagebox.showerror("Erreur", f"Le fichier '{file_name}' est introuvable dans :\n{target_file_path.parent}")
            return

        try:
            with open(target_file_path, "r", encoding="utf-8") as file:
                full_text = file.read()

            all_words = full_text.split()
            target_words = target_phrase.split()
            n_target = len(target_words)

            cleaned_words = []
            for w in all_words:
                w_low = w.lower()
                cleaned_prefix = re.sub(r"^(l|d|j|m|t|s|qu)'", "", w_low)
                final_cleaned_word = re.sub(r'[^\w]', '', cleaned_prefix)
                cleaned_words.append(final_cleaned_word)

            i = 0
            while i <= len(cleaned_words) - n_target:
                if cleaned_words[i : i + n_target] == target_words:
                    start_index = max(0, i - 7)
                    end_index = min(len(all_words), i + n_target + 7)
                    context_chunk = all_words[start_index : end_index]
                    context_sentence = " ".join(context_chunk)

                    self.context_choices.append(context_sentence)
                    result_listbox.insert(tk.END, f"Occurence {len(self.context_choices)}: {context_sentence}...")
                i += 1

            if not self.context_choices:
                result_listbox.insert(tk.END, "Aucun résultat trouvé pour ce mot.")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de lecture :\n{e}")

    def get_saved_explanation(self, roman, word, context):
        """البحث عن الشرح المحفوظ سابقاً في ملفات المشروع"""
        if "boîte" in roman.lower() or "boite" in roman.lower():
            filename = "explication_la_boite_a_merveilles.txt"
        elif "antigone" in roman.lower():
            filename = "explication_antigone.txt"
        else:
            filename = "explication_le_dernier_jour_d_un_condamne.txt"

        output_file_path = self._resolve_data_file(filename)

        if not output_file_path.exists():
            return None

        try:
            with open(output_file_path, "r", encoding="utf-8") as file:
                content = file.read()

            # تقسيم الملف إلى كتل شروحات بناءً على الفاصل الخطي
            entries = content.split("-" * 50)
            target_word = word.strip().lower()
            target_context = context.strip().lower()

            for entry in entries:
                if not entry.strip():
                    continue

                word_match = re.search(r"Mot/Expression:\s*(.+)", entry)
                context_match = re.search(r"Contexte:\s*(.+)", entry)
                explanation_match = re.search(r"Explication:\n([\s\S]+)", entry)

                if word_match and explanation_match:
                    saved_word = word_match.group(1).strip().lower()
                    saved_context = context_match.group(1).strip().lower() if context_match else ""

                    # المطابقة بناءً على الكلمة والسياق
                    if saved_word == target_word and saved_context == target_context:
                        return explanation_match.group(1).strip()

            return None
        except Exception:
            return None

    def on_context_select(self, event, result_listbox, word_entry, explanation_box, roman_name):
        if self.is_processing:
            return

        selection = result_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if index >= len(self.context_choices):
            return

        selected_context = self.context_choices[index]
        target_word = word_entry.get().strip()

        # 1. البحث في الملفات المحفوظة أولاً
        saved_explanation = self.get_saved_explanation(roman_name, target_word, selected_context)
        if saved_explanation:
            # إذا وُجد الشرح، يتم عرضه فوراً وبدون الاتصال بالـ API
            formatted_saved = ar(saved_explanation)
            self.update_textbox_content(explanation_box, formatted_saved, self.ans_color)
            return

        # 2. إذا لم يوجد الشرح سابقاً، نطلب الشرح من Gemini API
        self.is_processing = True
        waiting_msg = ar("Analyse en cours par Gemini API... Veuillez patienter. | جاري التحليل، يرجى الانتظار...")
        self.update_textbox_content(explanation_box, waiting_msg, self.accent_color)

        ai_thread = threading.Thread(target=self.fetch_ai_explanation, args=(target_word, selected_context, explanation_box, roman_name))
        ai_thread.daemon = True
        ai_thread.start()

    def save_explanation_to_file(self, roman, word, context, ai_response_text):
        """حفظ الشروحات مباشرة في مجلد المشروع لسهولة الوصول إليها"""
        try:
            if not self.data_dir.exists():
                self.data_dir.mkdir(parents=True, exist_ok=True)

            if "boîte" in roman.lower() or "boite" in roman.lower():
                output_file_path = self.data_dir / "explication_la_boite_a_merveilles.txt"
            elif "antigone" in roman.lower():
                output_file_path = self.data_dir / "explication_antigone.txt"
            else:
                output_file_path = self.data_dir / "explication_le_dernier_jour_d_un_condamne.txt"

            with open(output_file_path, "a", encoding="utf-8") as output_file:
                output_file.write(f"=== {roman} ===\n")
                output_file.write(f"Mot/Expression: {word}\n")
                output_file.write(f"Contexte: {context}\n")
                output_file.write(f"Explication:\n{ai_response_text}\n")
                output_file.write("-" * 50 + "\n\n")

        except Exception as e:
            self.master.after(0, lambda err=e: messagebox.showerror("Erreur de sauvegarde", f"Le fichier n'a pas pu être enregistré :\n{err}"))

    def fetch_ai_explanation(self, word, context, explanation_box, roman):
        prompt = (
            f"Tu es un professeur de français expert du programme du bac marocain. "
            f"Explique le sens du mot ou de l'expression '{word}' basé sur ce contexte extrait du roman '{roman}' : '{context}'. "
            f"Utilise une approche pédagogique bilingue : explique principalement en français, mais intègre des mots ou des termes en arabe lorsque cela aide à mieux comprendre les nuances littéraires ou le sens profond. "
            f"Pour terminer, ajoute une brève synthèse ou une traduction claire en arabe pour confirmer ma compréhension. "
            f"Sois concis, clair et structuré (maximum 4 phrases au total)."
        )

        try:
            response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "Tu es un professeur de littérature française spécialisé dans le programme du bac marocain. "
                    "Tes explications doivent être claires, pédagogiques et concises."
                ),
                temperature=0.3
            )
        )

            raw_response = response.text.strip()
            ai_response_text = ar(raw_response)
            self.update_textbox_content(explanation_box, ai_response_text, self.ans_color)

            # حفظ الشرح لاستخدامه مستقبلاً
            self.save_explanation_to_file(roman, word, context, raw_response)

        except Exception as e:
            error_str = str(e)

            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                user_friendly_error = ar(
                    "Trop de requêtes simultanées ! Veuillez patienter 20 à 30 secondes avant de cliquer sur un autre mot.\n\n"
                    "لقد أرسلت الكثير من الطلبات في وقت قصير! يرجى الانتظار من 20 إلى 30 ثانية قبل الضغط على كلمة أخرى."
                )
                self.update_textbox_content(explanation_box, user_friendly_error, "#F38BA8")
            else:
                error_msg = f"Impossible de récupérer l'explication :\n{e}"
                self.update_textbox_content(explanation_box, ar(error_msg), "#F38BA8")

        finally:
            self.is_processing = False
