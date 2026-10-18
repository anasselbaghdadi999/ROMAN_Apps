import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from google import genai
from google.genai import types
import threading
import re


def load_api_key_and_create_client(master):
    """الاتصال بـ Gemini API — منقول حرفياً من My_App.__init__ الأصلي."""
    home_directory = Path.home()
    api_file_path = home_directory / ".QCM_ROMON_API_GEMINI"

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
    """ميكسين يجمع منطق Gemini API + GoogleSearch + threading + Grounding — منقول قصاً ولصقاً."""

    def generate_question(self, novel_name):
        if self.label_wilcome.winfo_exists():
            self.label_wilcome.pack_forget()

        self.label_QCM.pack(pady=20, fill=tk.X)
        self.button_show_answer.pack(pady=15)
        self.label_Answer.pack(pady=5)
        self.answer_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.label_QCM.config(text="🔍 Recherche dans les sources éducatives réelles en cours...")
        self.label_Answer.config(text="")

        self.answer_text.config(state=tk.NORMAL)
        self.answer_text.delete("1.0", tk.END)
        self.answer_text.config(state=tk.DISABLED)

        self.button_show_answer.config(state=tk.DISABLED)

        def api_worker():
            prompt = (
                f"Tu es un professeur de français expert, spécialisé dans la préparation "
                f"au baccalauréat marocain (1ère année Bac).\n\n"
                f"TÂCHE : Recherche sur Internet une VRAIE question d'examen ou d'exercice "
                f"provenant d'un site éducatif marocain fiable, concernant le roman "
                f"'{novel_name}'.\n\n"
                "CONTRAINTES STRICTES :\n"
                "- Une seule question, de type analysis littéraire ou comprehension.\n"
                "- Si aucune source fiable n'est trouvée, indique-le clairement au lieu "
                "d'inventer une question.\n"
                "- N'écris RIEN en dehors des balises ci-dessous.\n\n"
                "FORMAT DE SORTIE (obligatoire, respecte exactement) :\n"
                "[QUESTION] ... [/QUESTION]\n"
                "[ANSWER] ... [/ANSWER]\n"
                "[SOURCE] ... [/SOURCE]\n\n"
                "EXEMPLE :\n"
                "[QUESTION] Quel est le rôle du personnage de Lalla Zoubida dans "
                "La Boîte à Merveilles ? [/QUESTION]\n"
                "[ANSWER] Elle représente... [/ANSWER]\n"
                "[SOURCE] alloschool.com [/SOURCE]"
            )

            try:
                response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "Tu es un professeur et chercheur universitaire spécialisé en littérature française "
                        "et au programme du baccalauréat marocain. Tes analyses doivent être profondes, "
                        "rigoureuses, pédagogiques et très détaillées."
                    ),
                    temperature=0.3,
                    tools=[types.Tool(google_search=types.GoogleSearch())] # فقط في مشروع QCM
                )
            )

                response_text = response.text

                question_match = re.search(r'\[QUESTION\](.*?)\[/QUESTION\]', response_text, re.DOTALL)
                answer_match = re.search(r'\[ANSWER\](.*?)\[/ANSWER\]', response_text, re.DOTALL)
                source_match = re.search(r'\[SOURCE\](.*?)\[/SOURCE\]', response_text, re.DOTALL)

                if question_match and answer_match:
                    question_part = question_match.group(1).strip()
                    self.hidden_answer = answer_match.group(1).strip()
                    source_text = source_match.group(1).strip() if source_match else ""

                    grounding_info = self._extract_grounding_sources(response)

                    final_source = source_text
                    if grounding_info:
                        if final_source: final_source += "\n\n"
                        final_source += "📚 Sources trouvées via Google :\n" + grounding_info

                    self.hidden_source = final_source

                    self.safe_update_ui(self.label_QCM, text=question_part)
                    self.safe_update_ui(self.button_show_answer, state=tk.NORMAL)
                else:
                    self.safe_update_ui(self.label_QCM, text="❌ Erreur de formatage des balises, veuillez réessayer.")

            except Exception as e:
                # Analyse intelligente de l'erreur pour afficher des messages compréhensibles en français
                error_msg = str(e)
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                    friendly_error = "⚠️ Vous avez dépassé la limite de requêtes par minute (Rate Limit).\nVeuillez attendre une minute complète avant de choisir un autre roman et de générer une nouvelle question."
                elif "network" in error_msg.lower() or "connection" in error_msg.lower() or "http" in error_msg.lower():
                    friendly_error = "❌ Erreur de connexion : Le programme n'a pas pu contacter le serveur.\nVeuillez vérifier votre connexion Internet et réessayer."
                elif "api_key" in error_msg.lower() or "invalid" in error_msg.lower():
                    friendly_error = "❌ Votre clé API est incorrecte ou a expiré. Veuillez vérifier votre fichier caché."
                else:
                    friendly_error = f"❌ Une erreur inattendue est survenue lors de l'exécution de votre requête :\n{error_msg}"

                self.safe_update_ui(self.label_QCM, text=friendly_error)

        threading.Thread(target=api_worker, daemon=True).start()

    def _extract_grounding_sources(self, response):
        sources = []
        try:
            if response.candidates and len(response.candidates) > 0:
                metadata = response.candidates[0].grounding_metadata
                if metadata and metadata.grounding_chunks:
                    for chunk in metadata.grounding_chunks:
                        if chunk.web:
                            title = chunk.web.title or "Source"
                            uri = chunk.web.uri or ""
                            sources.append(f"• {title}\n  {uri}")
        except Exception as e:
            print(f"⚠️ Impossible d'extraire les sources : {e}")
        return "\n".join(sources) if sources else ""
