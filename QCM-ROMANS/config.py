# config.py — قواميس الألوان والثوابت المرئية
# مقتطعة حرفياً من My_App.__init__ الأصلي (نفس القيم دون أي تغيير)

BG_COLOR = "#1E1E2E"
FRAME_COLOR = "#272733"
FG_COLOR = "#CDD6F4"
BTN_COLOR = "#313244"
BTN_HOVER = "#45475A"
ANS_COLOR = "#A6E3A1"
ACCENT_COLOR = "#5E7394"
BTN_FG_DARK = "#11111B"

# إعدادات Gemini (نفس القيم الحرفية المستعملة في generate_question الأصلي)
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_TEMPERATURE = 0.3
GEMINI_SYSTEM_INSTRUCTION = (
    "Tu es un professeur et chercheur universitaire spécialisé en littérature française "
    "et au programme du baccalauréat marocain. Tes analyses doivent être profondes, "
    "rigoureuses, pédagogiques et très détaillées."
)
