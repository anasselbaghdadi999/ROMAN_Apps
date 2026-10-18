import arabic_reshaper
from bidi.algorithm import get_display

def ar(text):
    """دالة لإصلاح الحروف العربية وعرضها بشكل متصل وصحيح من اليمين لليسار"""
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)
