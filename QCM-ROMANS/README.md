# ROMON Apps - 1ère Année Bac Maroc

**ROMON Apps** est une application de bureau interactive développée en Python (Tkinter) conçue spécialement pour aider les élèves de la **1ère année du Baccalauréat marocain** à réviser et à s'entraîner sur les trois œuvres majeures du programme de français :
- *La Boîte à Merveilles*
- *Antigone*
- *Le Dernier Jour d'un Condamné*

L'application intègre l'intelligence artificielle **Google Gemini** (via `gemini-2.5-flash`) combinée à la recherche Google en temps réel (**Google Search Grounding**) pour générer des questions d'examen authentiques accompagnées de corrections détaillées et de sources vérifiées.

---

## Fonctionnalités principales

- **Génération dynamique de questions :** Extraction de vraies questions d'examens ou d'exercices depuis des sources éducatives marocaines fiables.
- **Support des 3 romans du programme :** Accès rapide à des quiz ciblés pour chaque œuvre.
- **Recherche en temps réel (Grounding) :** Utilisation de l'outil Google Search pour garantir l'exactitude des sources pédagogiques.
- **Gestion des erreurs intelligente :** Messages d'erreur clairs et ergonomiques (gestion des quotas, de la connexion, etc.).
- **Interface sombre moderne :** Design épuré, confortable pour les yeux, basé sur une palette de couleurs personnalisée.

---

## Structure du Projet

```text
ROMON_Apps/
│
├── main.py          # Point d'entrée principal de l'application (avec gestion globale des erreurs)
├── app.py           # Interface graphique principale (Tkinter) et logique de l'application
├── ai_service.py    # Service de communication avec Gemini API, threading et extraction des sources
├── config.py        # Configuration des thèmes, couleurs et paramètres du modèle Gemini
└── utils.py         # Fonctions utilitaires (gestion du texte arabe, etc.)
```

---

## Prérequis et Installation

1. **Cloner le dépôt :**
   ```bash
   git clone https://github.com/anasselbaghdadi999/ROMON_Apps.git
   cd ROMON_Apps
   ```

2. **Installer les dépendances nécessaires :**
   ```bash
   pip install google-genai
   ```

3. **Obtenir et configurer la clé API Gemini :**
   - Rendez-vous sur la plateforme [Google AI Studio](https://aistudio.google.com/).
   - Connectez-vous avec votre compte Google.
   - Cliquez sur **"Get API key"** et générez une nouvelle clé.
   - Créez un fichier caché nommé `.QCM_ROMON_API_GEMINI` dans votre répertoire personnel (`~/.`) et ajoutez-y votre clé API :
     ```bash
     echo "VOTRE_CLE_API" > ~/.QCM_ROMON_API_GEMINI
     ```

4. **Lancer l'application :**
   ```bash
   python main.py
   ```

---

## Auteur

Développé par **Anass Elbaghdadi**  
*Étudiant passionné par la programmation et la cybersécurité.*