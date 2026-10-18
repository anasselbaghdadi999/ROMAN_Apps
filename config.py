# config.py — قواميس الألوان وإعدادات الثيم المرئية
# مقتطع حرفياً من My_App.__init__ الأصلي (نفس القيم دون أي تغيير)

BG_COLOR = "#1E1E2E"       # لون الخلفية الرئيسي
SIDEBAR_COLOR = "#181825"  # لون القائمة الجانبية والصناديق
FG_COLOR = "#CDD6F4"       # لون النصوص الأساسية
BTN_COLOR = "#313244"      # لون الأزرار
BTN_HOVER = "#45475A"      # لون الأزرار عند تمرير الماوس
ANS_COLOR = "#A6E3A1"      # لون الإجابة
ACCENT_COLOR = "#5E7394"   # لون التحديد
ERROR_COLOR = "#F38BA8"    # لون رسائل الخطأ (كان مكتوباً حرفياً في fetch_ai_explanation)

APPEARANCE_MODE = "dark"

# إعدادات Gemini (نفس القيم الحرفية المستعملة في fetch_ai_explanation الأصلي)
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_TEMPERATURE = 0.3
GEMINI_SYSTEM_INSTRUCTION = (
    "Tu es un professeur de littérature française spécialisé dans le programme du bac marocain. "
    "Tes explications doivent être claires, pédagogiques et concises."
)

# مجلد ملفات الروايات والشروحات داخل مجلد المشروع
ROMANS_FOLDER = "romans"
