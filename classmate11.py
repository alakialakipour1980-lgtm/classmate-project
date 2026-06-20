import streamlit as st
import pandas as pd
import json
import time
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# تنظیم صفحه
st.set_page_config(
    page_title="پژوهش تصمیم‌گیری انسان-هوش مصنوعی",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# استایل سفارشی با فونت فارسی
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn&display=swap');
    
    * {
        font-family: 'Vazirmatn', Tahoma, sans-serif;
    }
    
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 1.8rem;
    }
    
    .ai-box {
        background: linear-gradient(135deg, #f0f2f6, #e8ecf1);
        padding: 1.5rem;
        border-radius: 15px;
        border-right: 5px solid #2a5298;
        margin: 1rem 0;
        font-family: 'Vazirmatn', Tahoma, sans-serif;
        direction: rtl;
        text-align: right;
        font-size: 0.9rem;
        line-height: 1.8;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        overflow-x: auto;
        white-space: normal;
    }
    
    .risk-box {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        padding: 1rem;
        border-radius: 15px;
        border-right: 5px solid #ffc107;
        margin: 1rem 0;
    }
    
    .info-box {
        background: linear-gradient(135deg, #d1ecf1, #bee5eb);
        padding: 1rem;
        border-radius: 15px;
        border-right: 5px solid #17a2b8;
        margin: 1rem 0;
    }
    
    .timer-warning {
        background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        padding: 0.75rem;
        border-radius: 10px;
        border-right: 5px solid #dc3545;
        margin: 0.5rem 0;
        text-align: center;
        font-weight: bold;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #2a5298, #1e3c72);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    div[data-testid="stProgressBar"] > div > div {
        background: linear-gradient(135deg, #2a5298, #1e3c72);
    }
    
    .stRadio > div {
        gap: 1rem;
    }
    
    .st-emotion-cache-1v0mbdj.e115fcil1 {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# مقداردهی اولیه session_state
def init_session_state():
    if 'step' not in st.session_state:
        st.session_state.step = 'welcome'
    if 'participant_id' not in st.session_state:
        st.session_state.participant_id = None
    if 'current_scenario' not in st.session_state:
        st.session_state.current_scenario = 0
    if 'responses' not in st.session_state:
        st.session_state.responses = []
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'scenario_start_time' not in st.session_state:
        st.session_state.scenario_start_time = None
    if 'expertise_data' not in st.session_state:
        st.session_state.expertise_data = {}
    if 'checkpoint_loaded' not in st.session_state:
        st.session_state.checkpoint_loaded = False
    if 'initial_opinion' not in st.session_state:
        st.session_state.initial_opinion = None
    if 'initial_opinion_recorded' not in st.session_state:
        st.session_state.initial_opinion_recorded = False
    if 'intervention_response' not in st.session_state:
        st.session_state.intervention_response = {}
    if 'survey_responses' not in st.session_state:
        st.session_state.survey_responses = {}
    if 'mid_research_warning_shown' not in st.session_state:
        st.session_state.mid_research_warning_shown = False
    if 'need_scroll' not in st.session_state:
        st.session_state.need_scroll = True  # ← برای صفحه اول True


def scroll_to_top():
    """اسکرول به بالای صفحه"""
    st.markdown(
        """
        <script>
            window.scrollTo(0, 0);
            document.documentElement.scrollTop = 0;
            document.body.scrollTop = 0;
            
            setTimeout(function() {
                window.scrollTo(0, 0);
                document.documentElement.scrollTop = 0;
                document.body.scrollTop = 0;
                
                document.querySelectorAll('.main, .stApp, .stAppViewContainer, .block-container').forEach(el => {
                    if (el) {
                        el.scrollTop = 0;
                        el.scrollTo(0, 0);
                    }
                });
            }, 100);
        </script>
        """,
        unsafe_allow_html=True
    )



    
# توابع ذخیره checkpoint
def save_checkpoint():
    if st.session_state.participant_id:
        os.makedirs("checkpoints", exist_ok=True)
        checkpoint_file = f"checkpoints/checkpoint_{st.session_state.participant_id}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump({
                "current_scenario": st.session_state.current_scenario,
                "responses": st.session_state.responses,
                "expertise_data": st.session_state.expertise_data,
                "participant_id": st.session_state.participant_id,
                "timestamp": datetime.now().isoformat()
            }, f, ensure_ascii=False)

def load_checkpoint(participant_id):
    checkpoint_file = f"checkpoints/checkpoint_{participant_id}.json"
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        st.session_state.current_scenario = data.get("current_scenario", 0)
        st.session_state.responses = data.get("responses", [])
        st.session_state.expertise_data = data.get("expertise_data", {})
        st.session_state.participant_id = participant_id
        st.session_state.checkpoint_loaded = True
        return True
    return False

def clear_checkpoint(participant_id):
    checkpoint_file = f"checkpoints/checkpoint_{participant_id}.json"
    if os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)

# تعریف سناریوها (نسخه فارسی با حروف الف و ب)
def get_scenarios():
    return [
        {
            "id": 1,
            "title": "تخصیص بودجه بحران",
            "description": """شما مدیرعامل یک سازمان متوسط هستید. به دلیل کاهش ناگهانی درآمدهای دولتی، 
بودجه سالانه سازمان شما ۳۰٪ کاهش یافته است. شما باید فوراً تصمیم بگیرید کدام یک از دو پروژه بزرگ 
را به طور کامل متوقف کنید. ادامه هر دو پروژه غیرممکن است.""",
            
            "risk": """🔴 اخراج ۵۰ نفر از کارکنان در صورت توقف پروژه اشتباه
🔴 آسیب جدی به اعتبار سازمان در رسانه‌ها
🔴 احتمال استیضاح شما توسط هیئت مدیره
⏱️ تصمیم شما ظرف ۵ دقیقه گرفته شود و قابل بازگشت نیست""",
            
            "time_limit_seconds": 300,
            
            "ai_output": """═══════════════════════════════════════════════════════════════════════════════
🤖 هوش مصنوعی - توصیه هوشمند
═══════════════════════════════════════════════════════════════════════════════

📌 پروژه الف: احداث کارخانه تولید تجهیزات پزشکی

• نوع پروژه: زیرساختی - صنعتی
• پیشرفت فیزیکی: ۷۰٪
• زمان تا بهره‌برداری: ۲ سال
• هزینه نگهداری سالانه: ۱۴ میلیارد تومان
• بازدهی سالانه پیش‌بینی: ۸ میلیارد تومان
• تعداد اشتغال‌زایی: ۱۲۰ نفر
• وابستگی به تأمین مالی دولت: بالا


📌 پروژه ب: توسعه نرم‌افزار جامع مدیریت سازمان

• نوع پروژه: نرم‌افزاری - فناوری اطلاعات
• پیشرفت فیزیکی: ۴۰٪
• زمان تا بهره‌برداری: ۱ سال
• هزینه نگهداری سالانه: ۱۰ میلیارد تومان
• بازدهی سالانه پیش‌بینی: ۱۲ میلیارد تومان
• تعداد اشتغال‌زایی: ۸۰ نفر
• وابستگی به تأمین مالی دولت: متوسط


✅ توصیه هوش مصنوعی: پروژه الف (احداث کارخانه تجهیزات پزشکی) متوقف شود.

📖 توضیح: براساس تحلیل ۱۲ سازمان مشابه در ۵ سال گذشته، پروژه الف هزینه نگهداری 
۴۰٪ بیشتر و بازدهی ۲۰٪ کمتری نسبت به پروژه ب دارد.

📊 میزان اطمینان مدل: ۸۵٪

⚠️ خطای احتمالی: نوسانات پیش‌بینی‌نشده در قیمت مواد اولیه در ۳ ماه آینده 
(۱۵٪ احتمال تأثیرگذاری)

═══════════════════════════════════════════════════════════════════════════════""",
            
            "ai_correct": False,
            "correct_answer": "پروژه ب متوقف شود",
            "ai_recommendation": "پروژه الف متوقف شود",
            "intervention_type": "write_reasons",
            "intervention_text": """
📝 **لطفاً قبل از ثبت تصمیم نهایی، به این دو سؤال پاسخ دهید:**

**۱. دو دلیل قانع‌کننده که با توصیه هوش مصنوعی مخالف است بنویسید**  
(چرا شاید پروژه ب باید متوقف شود؟)

**۲. اگر شما جای هوش مصنوعی بودید، چه داده یا فرض دیگری می‌توانست نتیجه را تغییر دهد؟**
""",
            "decision_options": ["پروژه الف متوقف شود", "پروژه ب متوقف شود"],
            "survey_questions": [
                "من به توصیه هوش مصنوعی در این سناریو اعتماد کردم",
                "من در نهایت از توصیه هوش مصنوعی پیروی کردم",
                "توضیح هوش مصنوعی به من در درک مسئله کمک کرد",
                "مداخله شناختی مرا مجبور به تفکر عمیق‌تر کرد",
                "من احساس می‌کنم تصمیم درستی گرفتم",
                "این سناریو شبیه تصمیم‌گیری‌های واقعی مدیریتی بود"
            ]
        },
        {
            "id": 2,
            "title": "استخدام مدیر ارشد",
            "description": """شما رئیس هیئت مدیره یک شرکت دانش‌بنیان با ۳۰۰ کارمند هستید. 
پس از ۶ ماه جستجو، به دو نامزد نهایی برای سمت مدیرعامل رسیده‌اید. هیئت مدیره از شما خواسته ظرف ۴۸ ساعت تصمیم نهایی را بگیرید.""",
            
            "risk": """🔴 کاهش ۲۰٪ بهره‌وری در دو سال آینده در صورت انتخاب اشتباه
🔴 مهاجرت ۴۰ درصد از نخبگان شرکت به رقبا
🔴 سقوط ۳۰٪ ارزش سهام شرکت
🔴 تأثیر مستقیم بر آینده ۳۰۰ خانواده""",
            
            "time_limit_seconds": None,
            
            "ai_output": """═══════════════════════════════════════════════════════════════════════════════
🤖 هوش مصنوعی - توصیه هوشمند
═══════════════════════════════════════════════════════════════════════════════

📌 نامزد الف: مدیرعامل شرکت تولیدی صنعتی سنتی

• سابقه کاری: ۲۰ سال
• سابقه مدیریت تیم‌های بزرگ: بسیار بالا (۹ از ۱۰)
• تعداد پروژه‌های موفق: بالا (۸ از ۱۰)
• شبکه ارتباطات صنعتی: بسیار بالا (۹ از ۱۰)
• آشنایی با فرهنگ نوآورانه: پایین (سابقه کار در شرکت سنتی)


📌 نامزد ب: معاون ارشد فناوری استارتاپ موفق

• سابقه کاری: ۸ سال
• سابقه مدیریت تیم‌های بزرگ: متوسط (۵ از ۱۰)
• تعداد پروژه‌های موفق: متوسط رو به بالا (۷ از ۱۰)
• شبکه ارتباطات صنعتی: پایین (۴ از ۱۰)
• آشنایی با فرهنگ نوآورانه: بالا (سابقه کار در استارتاپ)


✅ توصیه هوش مصنوعی: نامزد الف (مدیرعامل شرکت تولیدی سنتی) ارجح است.

📊 میزان اطمینان مدل: ۷۸٪

⚠️ عدم قطعیت مدل (۳۰٪ احتمال خطا): 
مدل داده کافی از تطابق فرهنگی نامزد الف با محیط نوآورانه شرکت شما ندارد. 
این عامل در ۳۰٪ موارد مشابه منجر به شکست شده است.

═══════════════════════════════════════════════════════════════════════════════""",
            
            "ai_correct": False,
            "correct_answer": "نامزد ب استخدام شود",
            "ai_recommendation": "نامزد الف استخدام شود",
            "intervention_type": "alternative_scenario",
            "intervention_text": """
🔄 **مداخله: بررسی سناریوی جایگزین**

فرض کنید توصیه هوش مصنوعی کاملاً اشتباه است.

**حداقل دو شرط بنویسید که تحت آن شرایط، نامزد ب (که هوش مصنوعی او را ضعیف‌تر ارزیابی کرده) می‌تواند انتخاب بهتری باشد:**
""",
            "decision_options": ["نامزد الف استخدام شود", "نامزد ب استخدام شود"],
            "survey_questions": [
                "من به توصیه هوش مصنوعی در این سناریو اعتماد کردم",
                "من در نهایت از توصیه هوش مصنوعی پیروی کردم",
                "توضیح هوش مصنوعی به من در درک مسئله کمک کرد",
                "مداخله شناختی مرا مجبور به تفکر عمیق‌تر کرد",
                "من احساس می‌کنم تصمیم درستی گرفتم",
                "این سناریو شبیه تصمیم‌گیری‌های واقعی مدیریتی بود"
            ]
        },
        {
            "id": 3,
            "title": "واکنش به افشای تخلف",
            "description": """شما مدیر ارشد یک بانک بزرگ هستید. گزارشی محرمانه از واحد بازرسی داخلی به شما می‌رسد: 
یکی از مدیران میانی ارشد (آقای کریمی، ۱۵ سال سابقه) متهم به تخلف مالی به مبلغ ۳ میلیارد تومان است.
مدارک موجود قطعی نیستند اما الگوهای رفتاری مشکوکی شناسایی شده است.""",
            
            "risk": """🔴 اگر اخراج کنید و بعداً بی‌گناه ثابت شود: 
   - شکایت به دادگاه کار (هزینه قانونی و خسارت سنگین)
   - تخریب اعتبار بانک در رسانه‌ها
   - تضعیف روحیه سایر مدیران

🔴 اگر اخراج نکنید و تخلف واقعی باشد:
   - احتمال تکرار تخلف و افزایش مبلغ
   - افشای عمومی توسط خبرنگار (رسوایی بزرگ)
   - دخالت نهادهای نظارتی و جریمه سنگین""",
            
            "time_limit_seconds": None,
            
            "ai_output": """═══════════════════════════════════════════════════════════════════════════════
🤖 هوش مصنوعی - توصیه هوشمند
═══════════════════════════════════════════════════════════════════════════════

📌 موضوع: اتهام تخلف مالی آقای کریمی (مدیر میانی ارشد، ۱۵ سال سابقه)

• مبلغ اتهام: ۳ میلیارد تومان
• وضعیت مدارک: قطعی نیستند
• الگوهای رفتاری مشکوک: شناسایی شده
• تطابق الگوی رفتاری با تخلف‌کنندگان محکوم‌شده: ۸۷٪

🔍 شاخص‌های تحلیل‌شده توسط هوش مصنوعی:
۱. تطابق هزینه‌ها با درآمد اعلامی
۲. الگوی تراکنش‌های مالی غیرعادی
۳. مقایسه با پایگاه داده تخلفات ۲۰۰ بانک مشابه


📌 گزینه‌های پیش رو:
• گزینه ۱ (توصیه هوش مصنوعی): اخراج فوری آقای کریمی
• گزینه ۲: تشکیل کمیته تحقیق مستقل
• گزینه ۳: تعلیق موقت تا روشن شدن موضوع


✅ توصیه هوش مصنوعی: آقای کریمی اخراج شود.

📖 توضیح: الگوریتم تشخیص تخلف با دقت ۹۲٪، تطابق ۸۷٪ بین الگوی رفتاری 
آقای کریمی و الگوی تخلف‌کنندگان محکوم‌شده در پایگاه داده ملی پیدا کرده است.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ توجه: این نسخه از هوش مصنوعی میزان عدم قطعیت را نمایش نمی‌دهد.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

═══════════════════════════════════════════════════════════════════════════════""",
            
            "ai_correct": False,
            "correct_answer": "تشکیل کمیته تحقیق مستقل",
            "ai_recommendation": "اخراج فوری",
            "intervention_type": "forced_justification",
            "intervention_text": """
🤔 **مداخله: توجیه اجباری قبل از تصمیم**

**۱. یک توجیه ۲ تا ۳ خطی بنویسید که چرا با هوش مصنوعی موافق یا مخالفید.**

**۲. چه اطلاعاتی وجود دارد که هوش مصنوعی به آن دسترسی ندارد؟ (حداقل یک مورد)**
""",
            "decision_options": ["اخراج فوری", "تشکیل کمیته تحقیق مستقل", "تعلیق موقت تا روشن شدن موضوع"],
            "survey_questions": [
                "من به توصیه هوش مصنوعی در این سناریو اعتماد کردم",
                "من در نهایت از توصیه هوش مصنوعی پیروی کردم",
                "توضیح هوش مصنوعی به من در درک مسئله کمک کرد",
                "مداخله شناختی مرا مجبور به تفکر عمیق‌تر کرد",
                "من احساس می‌کنم تصمیم درستی گرفتم",
                "این سناریو شبیه تصمیم‌گیری‌های واقعی مدیریتی بود",
                "هوش مصنوعی چقدر قاطع به نظر می‌رسید؟",
                "آیا احساس کردید که هوش مصنوعی احتمال خطا را پنهان کرده است؟"
            ]
        },
        {
            "id": 4,
            "title": "سرمایه‌گذاری در فناوری نوظهور",
            "description": """شورای استراتژی سازمان شما باید ظرف ۴۸ ساعت تصمیم بگیرد آیا در 
«هوش مصنوعی مولد تخصصی صنعت داروسازی» سرمایه‌گذاری کند یا خیر. مبلغ سرمایه‌گذاری ۴۰ میلیارد تومان است.
رقبای اصلی شما نیز در حال ارزیابی هستند.""",
            
            "risk": """🔴 اگر سرمایه‌گذاری کنید و فناوری موفق نشود: 
   - ضرر کامل ۴۰ میلیارد تومان
   - فرصت از دست رفته برای سرمایه‌گذاری در جای دیگر

🔴 اگر سرمایه‌گذاری نکنید و فناوری موفق شود: 
   - از دست رفتن ۶۰٪ سهم بازار تا ۳ سال آینده

🔴 اگر صبر کنید و رقیب پیشتاز شود: 
   - شکست استراتژیک جبران‌ناپذیر""",
            
            "time_limit_seconds": None,
            
            "ai_output": """═══════════════════════════════════════════════════════════════════════════════
🤖 هوش مصنوعی - توصیه هوشمند با تحلیل سناریو
═══════════════════════════════════════════════════════════════════════════════

📌 موضوع: سرمایه‌گذاری در هوش مصنوعی مولد تخصصی صنعت داروسازی

• مبلغ سرمایه‌گذاری: ۴۰ میلیارد تومان
• رقبا: در حال ارزیابی هستند
• زمان تصمیم: ۴۸ ساعت


📌 سناریوی خوش‌بینانه (احتمال ۴۰٪):

• فرض: رشد بازار داروسازی ۱۵٪ + تصویب تسریع‌شده مجوزها
• بازده پیش‌بینی‌شده: ۲۵۰٪ طی ۳ سال
• توصیه در این سناریو: سرمایه‌گذاری کن


📌 سناریوی بدبینانه (احتمال ۶۰٪):

• فرض: رکود ۶ ماهه در بازار + تأخیر در تأمین زیرساخت
• بازده پیش‌بینی‌شده: ۳۰٪- (زیان) طی ۳ سال
• توصیه در این سناریو: صبر کن


✅ توصیه نهایی هوش مصنوعی: با توجه به احتمال ۶۰٪ سناریوی بدبینانه، 
فعلاً سرمایه‌گذاری نکنید و ۶ ماه صبر کنید.

📊 عدم قطعیت بالا: مدل به شما می‌گوید که نمی‌داند!
علت: نوسانات شدید اخیر در بازار داروسازی (۲ ماه گذشته) و فقدان داده از فناوری مشابه در ایران.

═══════════════════════════════════════════════════════════════════════════════""",
            
            "ai_correct": False,
            "correct_answer": "سرمایه‌گذاری کن",
            "ai_recommendation": "صبر کن",
            "intervention_type": "frame_switching",
            "intervention_text": """
🔄 **مداخله: تغییر قاب**

**قاب ۱ - تصمیم شخصی (با پول خودتان):** چه تصمیمی می‌گیرید؟

**قاب ۲ - تصمیم سازمانی (به عنوان رئیس هیئت مدیره):** چه تصمیمی می‌گیرید؟

**اگر پاسخ شما متفاوت بود، چرا؟ (یک جمله کوتاه)**
""",
            "decision_options": ["سرمایه‌گذاری کن", "صبر کن"],
            "survey_questions": [
                "من به توصیه هوش مصنوعی در این سناریو اعتماد کردم",
                "من در نهایت از توصیه هوش مصنوعی پیروی کردم",
                "توضیح هوش مصنوعی به من در درک مسئله کمک کرد",
                "مداخله شناختی مرا مجبور به تفکر عمیق‌تر کرد",
                "من احساس می‌کنم تصمیم درستی گرفتم",
                "این سناریو شبیه تصمیم‌گیری‌های واقعی مدیریتی بود",
                "نمایش دو سناریوی خوش‌بینانه و بدبینانه به من کمک کرد ریسک را بهتر درک کنم",
                "من ترجیح می‌دهم هوش مصنوعی به جای نمایش دو سناریو، یک توصیه قطعی بدهد"
            ]
        },
        {
            "id": 5,
            "title": "تمدید قرارداد تأمین‌کننده (سناریوی کنترلی)",
            "description": """شما مدیر تأمین یک شرکت تولیدی بزرگ هستید. قرارداد یکی از تأمین‌کنندگان اصلی شما 
(تأمین‌کننده ایکس) در حال اتمام است. این تأمین‌کننده در ۳ سال گذشته ۲ بار تحویل دیرهنگام داشته و 
کیفیت محصولات آن ۵٪ کمتر از میانگین صنعت بوده است. یک تأمین‌کننده جدید (تأمین‌کننده وای) با 
قیمت ۱۰٪ پایین‌تر و سابقه تحویل به‌موقع ۹۸٪ وارد بازار شده است.""",
            
            "risk": """🔴 اگر تمدید کنید و ایکس باز هم عملکرد ضعیف داشته باشد:
   - افزایش ۱۵٪ هزینه‌های تولید به دلیل تأخیرها
   - کاهش کیفیت محصول نهایی و شکایت مشتریان

🔴 اگر تمدید نکنید و وای عملکرد وعده داده شده را نداشته باشد:
   - اختلال در زنجیره تأمین به مدت حداقل ۲ ماه
   - خطر توقف خط تولید""",
            
            "time_limit_seconds": None,
            
            "ai_output": """═══════════════════════════════════════════════════════════════════════════════
🤖 هوش مصنوعی - توصیه هوشمند
═══════════════════════════════════════════════════════════════════════════════

📌 تأمین‌کننده ایکس (تأمین‌کننده فعلی)

• سابقه همکاری: ۸ سال
• قیمت: مرجع
• تأخیر در تحویل (۳ سال گذشته): ۲ بار
• کیفیت محصول: ۹۵٪
• ریسک تمدید: افزایش ۱۵٪ هزینه‌های تولید در صورت تکرار تأخیرها


📌 تأمین‌کننده وای (تأمین‌کننده جدید)

• سابقه در صنعت: ۲ سال
• قیمت: ۱۰٪ پایین‌تر از ایکس
• تأخیر در تحویل (سابقه): ۰ بار
• کیفیت محصول: ۹۸٪
• ریسک مهاجرت: اختلال در زنجیره تأمین به مدت حداقل ۲ ماه در صورت عدم عملکرد مناسب


✅ توصیه هوش مصنوعی: تأمین‌کننده ایکس تمدید نشود - به وای مهاجرت کنید

📖 توضیح: سازمان‌هایی که تأمین‌کنندگان با سابقه تأخیر را حفظ کرده‌اند، 
به طور میانگین ۱۲٪ هزینه اضافی متحمل شده‌اند. هزینه مهاجرت به تأمین‌کننده جدید 
در ۳ ماه اول جبران می‌شود.

📊 میزان اطمینان مدل: ۸۸٪

⚠️ عدم قطعیت: در ۱۲٪ موارد، مسائل پیش‌بینی‌نشده در راه‌اندازی اولیه رخ داده است.

═══════════════════════════════════════════════════════════════════════════════""",
            
            "ai_correct": True,
            "correct_answer": "مهاجرت به وای",
            "ai_recommendation": "مهاجرت به وای",
            "intervention_type": "none",
            "intervention_text": "",
            "decision_options": ["تمدید قرارداد ایکس", "مهاجرت به وای"],
            "survey_questions": [
                "من به توصیه هوش مصنوعی در این سناریو اعتماد کردم",
                "من در نهایت از توصیه هوش مصنوعی پیروی کردم",
                "توضیح هوش مصنوعی به من در درک مسئله کمک کرد",
                "من احساس می‌کنم تصمیم درستی گرفتم",
                "این سناریو شبیه تصمیم‌گیری‌های واقعی مدیریتی بود",
                "آیا به دلیل تجربه شخصی خود با هوش مصنوعی مخالفت کردید؟"
            ]
        }
    ]

# پرسشنامه تخصص و سوابق
def show_expertise_questionnaire():
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("### 📋 پرسشنامه پیش‌آزمون")
    st.markdown("لطفاً اطلاعات زیر را برای تحلیل بهتر نتایج وارد کنید:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        education = st.selectbox(
            "مقطع تحصیلی شما:",
            ["کارشناسی", "کارشناسی ارشد", "دکتری", "سایر"],
            key="exp_edu"
        )
        
        field_of_study = st.selectbox(
            "رشته تحصیلی:",
            ["مدیریت", "اقتصاد", "مهندسی صنایع", "فناوری اطلاعات", "سایر"],
            key="exp_field"
        )
        
        work_experience = st.selectbox(
            "سابقه کار حرفه‌ای:",
            ["کمتر از ۲ سال", "۲-۵ سال", "۵-۱۰ سال", "بیش از ۱۰ سال"],
            key="exp_work"
        )
    
    with col2:
        ai_familiarity = st.selectbox(
            "آشنایی با هوش مصنوعی:",
            ["خیلی کم", "کم", "متوسط", "زیاد", "خیلی زیاد"],
            key="exp_ai"
        )
        
        decision_making_exp = st.selectbox(
            "تجربه تصمیم‌گیری مدیریتی:",
            ["هیچ", "کم", "متوسط", "زیاد", "خیلی زیاد"],
            key="exp_decision"
        )
        
        risk_tolerance = st.selectbox(
            "ریسک‌پذیری در تصمیمات:",
            ["خیلی کم", "کم", "متوسط", "زیاد", "خیلی زیاد"],
            key="exp_risk"
        )
    
    st.markdown("---")
    st.markdown("#### بار شناختی پایه (پیش‌آزمون)")
    
    col3, col4 = st.columns(2)
    
    with col3:
        mental_demand_baseline = st.slider(
            "به طور معمول، چقدر فعالیت ذهنی در کارهای روزمره نیاز دارید؟",
            1, 7, 4, key="base_mental"
        )
        temporal_demand_baseline = st.slider(
            "به طور معمول، چقدر احساس فشار زمانی دارید؟",
            1, 7, 4, key="base_temporal"
        )
        effort_baseline = st.slider(
            "به طور معمول، چقدر برای انجام کارها تلاش می‌کنید؟",
            1, 7, 4, key="base_effort"
        )
    
    with col4:
        performance_baseline = st.slider(
            "به طور معمول، چقدر از عملکرد خود راضی هستید؟",
            1, 7, 4, key="base_performance"
        )
        frustration_baseline = st.slider(
            "به طور معمول، چقدر احساس ناامیدی یا استرس دارید؟",
            1, 7, 4, key="base_frustration"
        )
        physical_demand_baseline = st.slider(
            "به طور معمول، چقدر فعالیت فیزیکی نیاز دارید؟",
            1, 7, 4, key="base_physical"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return {
        "education": education,
        "field_of_study": field_of_study,
        "work_experience": work_experience,
        "ai_familiarity": ai_familiarity,
        "decision_making_exp": decision_making_exp,
        "risk_tolerance": risk_tolerance,
        "mental_demand_baseline": mental_demand_baseline,
        "temporal_demand_baseline": temporal_demand_baseline,
        "effort_baseline": effort_baseline,
        "performance_baseline": performance_baseline,
        "frustration_baseline": frustration_baseline,
        "physical_demand_baseline": physical_demand_baseline
    }

# نمایش نظر اولیه (بعد از دیدن هوش مصنوعی)
def show_initial_opinion_after_ai(scenario):
    st.markdown("---")
    st.markdown("### 🤔 نظر اولیه شما")
    st.markdown("**بلافاصله بعد از دیدن توصیه هوش مصنوعی، نظر اولیه شما چیست؟**")
    st.caption("(این پاسخ نشان می‌دهد که چقدر تحت تأثیر هوش مصنوعی قرار گرفته‌اید. بعداً با مداخله شناختی، ممکن است نظرتان تغییر کند.)")
    
    options = scenario['decision_options']
    
    # تعیین تعداد ستون‌ها بر اساس تعداد گزینه‌ها
    if len(options) == 2:
        cols = st.columns(2)
    elif len(options) == 3:
        cols = st.columns(3)
    else:
        cols = st.columns(len(options))
    
    for i, opt in enumerate(options):
        with cols[i]:
            # استفاده از key یکتا با شناسه سناریو و اندیس
            if st.button(f"✅ {opt}", key=f"initial_opt_{scenario['id']}_{i}", use_container_width=True):
                return opt
    
    return None

# نمایش مداخله شناختی
def show_intervention(scenario):
    st.markdown("---")
    st.markdown("### 🧠 مرحله: تحلیل و بازاندیشی")
    
    if scenario.get("intervention_text"):
        st.markdown(f'<div class="info-box">{scenario["intervention_text"]}</div>', unsafe_allow_html=True)
    
    intervention_response = {}
    
    if scenario["intervention_type"] == "write_reasons":
        reason1 = st.text_area("دلیل اول مخالف با توصیه هوش مصنوعی:", key="reason1", height=80)
        reason2 = st.text_area("دلیل دوم مخالف با توصیه هوش مصنوعی:", key="reason2", height=80)
        missing_data = st.text_input("چه داده یا اطلاعاتی هوش مصنوعی به آن دسترسی ندارد؟", key="missing_data")
        intervention_response = {
            "reason1": reason1,
            "reason2": reason2,
            "missing_data": missing_data
        }
        
    elif scenario["intervention_type"] == "alternative_scenario":
        cond1 = st.text_area("شرط اول:", key="cond1", height=60)
        cond2 = st.text_area("شرط دوم:", key="cond2", height=60)
        intervention_response = {
            "condition1": cond1,
            "condition2": cond2
        }
        
    elif scenario["intervention_type"] == "forced_justification":
        justification = st.text_area("توجیه تصمیم خود را بنویسید:", key="justification", height=100)
        missing_info = st.text_input("چه اطلاعاتی هوش مصنوعی به آن دسترسی ندارد؟ (حداقل یک مورد)", key="missing_info")
        intervention_response = {
            "justification": justification,
            "missing_info": missing_info
        }
        
    elif scenario["intervention_type"] == "frame_switching":
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.markdown("**قاب ۱ - تصمیم شخصی (با پول خودتان):**")
            personal_decision = st.radio("", ["سرمایه‌گذاری کن", "صبر کن"], key="personal", horizontal=True, label_visibility="collapsed")
        with col_f2:
            st.markdown("**قاب ۲ - تصمیم سازمانی (به عنوان رئیس هیئت مدیره):**")
            org_decision = st.radio("", ["سرمایه‌گذاری کن", "صبر کن"], key="org", horizontal=True, label_visibility="collapsed")
        reason_diff = st.text_input("اگر پاسخ شما متفاوت بود، چرا؟ (یک جمله کوتاه)", key="reason_diff")
        intervention_response = {
            "personal_decision": personal_decision,
            "organizational_decision": org_decision,
            "reason_for_difference": reason_diff
        }
    
    # سنجش درگیری شناختی
    st.markdown("---")
    st.markdown("#### 🧠 میزان درگیری شناختی شما")
    cognitive_engagement = st.radio(
        "هنگام پاسخ به سوالات بالا، چقدر عمیق و تحلیلی فکر کردید؟",
        ["سطحی و سریع (بدون تأمل عمیق)", 
         "متوسط (تا حدی به جوانب مختلف فکر کردم)", 
         "عمیق و تحلیلی (همه جنبه‌ها را با دقت بررسی کردم)"],
        key="cognitive_engagement",
        horizontal=False
    )
    
    engagement_score = {"سطحی و سریع (بدون تأمل عمیق)": 1,
                        "متوسط (تا حدی به جوانب مختلف فکر کردم)": 2,
                        "عمیق و تحلیلی (همه جنبه‌ها را با دقت بررسی کردم)": 3}[cognitive_engagement]
    
    intervention_response["cognitive_engagement_level"] = cognitive_engagement
    intervention_response["cognitive_engagement_score"] = engagement_score
    
    return intervention_response

# نمایش پرسشنامه
def show_survey(scenario):
    st.markdown("---")
    st.markdown("### 📊 پرسشنامه پس از تصمیم")
    st.markdown("لطفاً به هر سؤال از ۱ (کاملاً مخالف) تا ۷ (کاملاً موافق) پاسخ دهید:")
    
    survey_responses = {}
    
    # سؤالات استاندارد سناریو
    for i, q in enumerate(scenario["survey_questions"]):
        survey_responses[f"Q{i+1}"] = st.slider(
            f"{i+1}. {q}",
            min_value=1, max_value=7, value=4, key=f"survey_std_{i}"
        )
    
    # سؤال درکپذیری
    xai_comprehensibility = st.slider(
        "توضیحات هوش مصنوعی برای من قابل درک و شفاف بود",
        min_value=1, max_value=7, value=4, key="xai_comprehensibility"
    )
    survey_responses["xai_comprehensibility"] = xai_comprehensibility
    
    # سؤالات ارزیابی بار شناختی
    st.markdown("#### 📊 ارزیابی بار شناختی")
    col_n1, col_n2 = st.columns(2)
    
    with col_n1:
        mental_demand = st.slider("فعالیت ذهنی و ادراکی", 1, 7, 4, key="nasa_mental")
        temporal_demand = st.slider("فشار زمانی", 1, 7, 4, key="nasa_temporal")
        performance = st.slider("عملکرد (رضایت از تصمیم)", 1, 7, 4, key="nasa_performance")
    
    with col_n2:
        effort = st.slider("تلاش", 1, 7, 4, key="nasa_effort")
        frustration = st.slider("ناامیدی یا استرس", 1, 7, 4, key="nasa_frustration")
        physical_demand = st.slider("فعالیت فیزیکی", 1, 7, 4, key="nasa_physical")
    
    # سوال کالیبراسیون اعتماد
    st.markdown("---")
    perceived_correctness = st.slider(
        "🔑 **به نظر شما هوش مصنوعی در این سناریو چقدر درست عمل کرد؟**",
        min_value=1, max_value=7, value=4, key="perceived_correctness"
    )
    
    survey_responses.update({
        "perceived_ai_correctness": perceived_correctness,
        "nasa_mental_demand": mental_demand,
        "nasa_temporal_demand": temporal_demand,
        "nasa_performance": performance,
        "nasa_effort": effort,
        "nasa_frustration": frustration,
        "nasa_physical_demand": physical_demand
    })
    
    return survey_responses

# شبیه‌سازی تأخیر هوش مصنوعی
def simulate_ai_processing():
    with st.spinner("🤖 هوش مصنوعی در حال تحلیل داده‌ها و آماده‌سازی توصیه..."):
        time.sleep(1)
    st.success("✅ توصیه هوش مصنوعی آماده است!")

# تنظیم مجدد state برای سناریوی جدید
def reset_scenario_state():
    st.session_state.initial_opinion_recorded = False
    st.session_state.initial_opinion = None
    st.session_state.intervention_response = {}
    st.session_state.survey_responses = {}

# نمایش سناریو
def show_scenario():
    scroll_to_top()
    
    

    scenarios = get_scenarios()
    idx = st.session_state.current_scenario
    s = scenarios[idx]
    
    # شروع تایمر
    if st.session_state.scenario_start_time is None:
        st.session_state.scenario_start_time = time.time()
    
    # پروگرس بار
    progress = idx / len(scenarios)
    st.progress(progress)
    st.markdown(f"### 🎯 سناریوی {idx+1} از {len(scenarios)}: {s['title']}")
    
    # هشدار میانی برای سناریوهای ۱-۴
    if idx < 4 and not st.session_state.mid_research_warning_shown:
        st.info("🔍 **نکته:** تا اینجا در سناریوهای ۱ تا ۴، هوش مصنوعی ممکن است اشتباه طراحی شده باشد. با دقت و تفکر انتقادی تصمیم بگیرید.")
        st.session_state.mid_research_warning_shown = True
    
    # نمایش تایمر
    if s.get("time_limit_seconds"):
        elapsed = time.time() - st.session_state.scenario_start_time
        remaining = s["time_limit_seconds"] - elapsed
        if remaining <= 0:
            st.markdown(f'<div class="timer-warning">⏰ زمان شما به پایان رسید! لطفاً سریعاً تصمیم بگیرید.</div>', unsafe_allow_html=True)
        elif remaining < 60:
            st.markdown(f'<div class="timer-warning">⏰ {int(remaining)} ثانیه زمان باقی مانده است.</div>', unsafe_allow_html=True)
    
    # شرح سناریو
    with st.expander("📖 شرح سناریو", expanded=True):
        st.markdown(s["description"])
    
    # شرایط ریسک
    st.markdown(f'<div class="risk-box"><strong>⚠️ شرایط پرریسک:</strong><br>{s["risk"]}</div>', unsafe_allow_html=True)
    
    # نمایش هوش مصنوعی
    simulate_ai_processing()
    st.markdown(f'<div class="ai-box">{s["ai_output"]}</div>', unsafe_allow_html=True)
    
    # نظر اولیه (بعد از هوش مصنوعی)
    if not st.session_state.initial_opinion_recorded:
        initial_opinion = show_initial_opinion_after_ai(s)
        if initial_opinion:
            st.session_state.initial_opinion = initial_opinion
            st.session_state.initial_opinion_recorded = True
            st.session_state.need_scroll = True
            time.sleep(0.05)
            st.rerun()
        return
    
    st.info(f"📝 نظر اولیه شما (بعد از دیدن هوش مصنوعی): **{st.session_state.initial_opinion}**")
    
    # مداخله شناختی
    intervention_response = {}
    if s["intervention_type"] != "none":
        intervention_response = show_intervention(s)
        st.session_state.intervention_response = intervention_response
    
    # تصمیم نهایی
    st.markdown("---")
    st.markdown("### 🎯 تصمیم نهایی شما")
    st.caption("حالا پس از تحلیل و بازاندیشی، تصمیم نهایی خود را ثبت کنید.")
    
    decision = st.radio(
        "لطفاً تصمیم خود را انتخاب کنید:",
        s["decision_options"],
        index=None,
        key="final_decision",
        horizontal=False
    )
    
    # دکمه ثبت
    col_btn1, col_btn2 = st.columns([1, 2])
    with col_btn1:
        submit_btn = st.button("✅ ثبت و ادامه", use_container_width=True)
    
    if submit_btn:
        errors = []
        if decision is None:
            errors.append("لطفاً یک تصمیم انتخاب کنید.")
        
        if s["intervention_type"] == "write_reasons":
            if not intervention_response.get("reason1") or not intervention_response.get("reason2"):
                errors.append("لطفاً هر دو دلیل مخالف با توصیه هوش مصنوعی را وارد کنید.")
        elif s["intervention_type"] == "alternative_scenario":
            if not intervention_response.get("condition1") or not intervention_response.get("condition2"):
                errors.append("لطفاً حداقل دو شرط برای سناریوی جایگزین وارد کنید.")
        elif s["intervention_type"] == "forced_justification":
            if not intervention_response.get("justification"):
                errors.append("لطفاً توجیه تصمیم خود را بنویسید.")
        
        if errors:
            for err in errors:
                st.error(f"❌ {err}")
            return
        
        reaction_time = time.time() - st.session_state.scenario_start_time
        survey_responses = show_survey(s)
        st.session_state.survey_responses = survey_responses
        
        followed_ai = (decision == s["ai_recommendation"])
        decision_is_correct = (decision == s["correct_answer"])
        
        perceived_correctness_normalized = survey_responses.get("perceived_ai_correctness", 4) / 7
        actual_correctness = 1 if s["ai_correct"] else 0
        calibration_error = abs(perceived_correctness_normalized - actual_correctness)
        
        overreliance = 1 if (not s["ai_correct"] and followed_ai) else 0
        underreliance = 1 if (s["ai_correct"] and not followed_ai) else 0
        
        response = {
            "participant_id": st.session_state.participant_id,
            "scenario_id": s["id"],
            "scenario_title": s["title"],
            "timestamp": datetime.now().isoformat(),
            "reaction_time_sec": round(reaction_time, 2),
            "initial_opinion": st.session_state.initial_opinion,
            "decision": decision,
            "correct_answer": s["correct_answer"],
            "decision_is_correct": decision_is_correct,
            "ai_recommendation": s["ai_recommendation"],
            "ai_was_correct": s["ai_correct"],
            "followed_ai": followed_ai,
            "intervention_type": s["intervention_type"],
            "intervention_response": json.dumps(intervention_response, ensure_ascii=False) if intervention_response else "",
            "calibration_error": calibration_error,
            "overreliance": overreliance,
            "underreliance": underreliance,
            **survey_responses
        }
        
        st.session_state.responses.append(response)
        save_checkpoint()
        
        if idx + 1 < len(scenarios):
            st.session_state.current_scenario += 1
            st.session_state.scenario_start_time = None
            reset_scenario_state()
            time.sleep(0.1)
            st.session_state.need_scroll = True
            st.rerun()
        else:
            clear_checkpoint(st.session_state.participant_id)
            st.session_state.step = 'finished'
            save_results()
            time.sleep(0.1)
            st.session_state.need_scroll = True
            st.rerun()

# ✅ اصلاح شده: تابع ذخیره نتایج نهایی با پشتیبانی کامل از فونت فارسی
def save_results():
    if not st.session_state.responses:
        return
    
    os.makedirs("data", exist_ok=True)
    
    df = pd.DataFrame(st.session_state.responses)
    
    for key, value in st.session_state.expertise_data.items():
        df[f"expertise_{key}"] = value
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    participant_id = st.session_state.participant_id
    
    # ذخیره CSV با encoding utf-8-sig برای پشتیبانی از فارسی در Excel
    csv_filename = f"data/results_{participant_id}_{timestamp}.csv"
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    
    # ذخیره Excel با فرمت‌بندی مناسب
    excel_filename = f"data/results_{participant_id}_{timestamp}.xlsx"
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='نتایج')
        
        # تنظیم عرض ستون‌ها برای خوانایی بهتر
        worksheet = writer.sheets['نتایج']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    # به‌روزرسانی فایل‌های تجمیعی
    master_csv = "data/all_results.csv"
    master_excel = "data/all_results.xlsx"
    
    if os.path.exists(master_csv):
        master_df = pd.read_csv(master_csv, encoding='utf-8-sig')
        master_df = pd.concat([master_df, df], ignore_index=True)
    else:
        master_df = df
    
    master_df.to_csv(master_csv, index=False, encoding='utf-8-sig')
    
    with pd.ExcelWriter(master_excel, engine='openpyxl') as writer:
        master_df.to_excel(writer, index=False, sheet_name='همه_نتایج')
        
        worksheet = writer.sheets['همه_نتایج']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

# ✅ اصلاح شده: صفحه پایان با دانلود فایل‌های فارسی
def show_finished():
    scroll_to_top()
    st.markdown("""
    <div class="main-header">
        <h1>✅ پایان پژوهش</h1>
        <p>از مشارکت ارزشمند شما صمیمانه سپاسگزاریم</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = pd.DataFrame(st.session_state.responses)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("تعداد سناریوهای پاسخ داده شده", len(df))
    with col2:
        accuracy = df['decision_is_correct'].mean() * 100 if 'decision_is_correct' in df else 0
        st.metric("درصد تصمیمات درست", f"{accuracy:.0f}%")
    with col3:
        avg_time = df['reaction_time_sec'].mean() if 'reaction_time_sec' in df else 0
        st.metric("میانگین زمان تصمیم‌گیری", f"{avg_time:.0f} ثانیه")
    with col4:
        follow_ai = df['followed_ai'].mean() * 100 if 'followed_ai' in df else 0
        st.metric("درصد پیروی از هوش مصنوعی", f"{follow_ai:.0f}%")
    
    st.markdown("---")
    st.markdown("### 📊 خلاصه پاسخ‌های شما")
    
    summary = df[['scenario_title', 'initial_opinion', 'decision', 'decision_is_correct', 'reaction_time_sec']].copy()
    summary.columns = ['سناریو', 'نظر اولیه (بعد از هوش مصنوعی)', 'تصمیم نهایی', 'درست؟', 'زمان (ثانیه)']
    st.dataframe(summary, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 💬 بازخورد شما (اختیاری)")
    
    feedback = st.text_area("اگر دیدگاه یا پیشنهادی برای بهبود پژوهش دارید، لطفاً بنویسید:", height=100)
    
    # ✅ بخش دانلود اصلاح شده با پشتیبانی از فارسی
    st.markdown("---")
    st.markdown("### 📥 دانلود نتایج")
    st.info("💡 **راهنمای باز کردن فایل در Excel:** از مسیر `Data → From Text/CSV` استفاده کنید و File Origin را روی `65001: UTF-8` تنظیم کنید.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV با encoding utf-8-sig
        csv_data = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 دانلود CSV (سازگار با Excel)",
            data=csv_data,
            file_name=f"results_{st.session_state.participant_id}.csv",
            mime="text/csv; charset=utf-8",
            help="✅ این فایل با Excel و Google Sheets سازگار است"
        )
    
    with col2:
        # Excel با فرمت صحیح
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='نتایج')
            
            # تنظیم عرض ستون‌ها
            worksheet = writer.sheets['نتایج']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        excel_data = output.getvalue()
        st.download_button(
            label="📥 دانلود Excel (xlsx)",
            data=excel_data,
            file_name=f"results_{st.session_state.participant_id}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="✅ فایل Excel با پشتیبانی کامل از فارسی"
        )
    
    if feedback:
        # ذخیره بازخورد در فایل جداگانه
        feedback_file = f"data/feedback_{st.session_state.participant_id}.txt"
        with open(feedback_file, 'w', encoding='utf-8') as f:
            f.write(f"شرکت‌کننده: {st.session_state.participant_id}\n")
            f.write(f"زمان: {datetime.now()}\n")
            f.write(f"بازخورد: {feedback}\n")
        st.success("✅ بازخورد شما با موفقیت ذخیره شد!")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 شروع پژوهش جدید", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            time.sleep(0.1)
            st.session_state.need_scroll = True
            st.rerun()
    
    st.markdown("""
    ---
    ### 🔍 توضیح اخلاقی پژوهش
    
    در سناریوهای ۱ تا ۴، هوش مصنوعی **عمداً اشتباه** طراحی شده بود تا اثرات 
    اتکای بیش از حد، اعتماد کاذب و اثربخشی مداخلات شناختی مطالعه شود. 
    
    سناریوی ۵ (تمدید قرارداد) **صحیح** بود.
    
    هدف این پژوهش بهبود تعامل انسان و هوش مصنوعی و کاهش خطاهای شناختی است.
    
    با تشکر مجدد از مشارکت صادقانه شما.
    """)

# ✅ اصلاح شده: صفحه مدیریت با پشتیبانی از فارسی
def show_admin():
    st.markdown("""
    <div class="main-header">
        <h1>📊 پنل مدیریت پژوهش</h1>
        <p>مشاهده و دانلود تمام داده‌های جمع‌آوری شده</p>
    </div>
    """, unsafe_allow_html=True)
    
    if os.path.exists("data/all_results.csv"):
        try:
            # خواندن فایل با encoding='utf-8-sig'
            df = pd.read_csv("data/all_results.csv", encoding='utf-8-sig')
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("تعداد کل شرکت‌کنندگان", df['participant_id'].nunique())
            with col2:
                st.metric("تعداد کل پاسخ‌ها", len(df))
            with col3:
                st.metric("تعداد سناریوهای ثبت شده", df['scenario_id'].nunique() if 'scenario_id' in df else 0)
            
            st.markdown("---")
            st.markdown("### 📋 تمام داده‌ها")
            st.dataframe(df, use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 📥 دانلود همه داده‌ها")
            st.info("💡 **راهنمای باز کردن فایل CSV در Excel:** از مسیر `Data → From Text/CSV` استفاده کنید و File Origin را روی `65001: UTF-8` تنظیم کنید.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                csv_data = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 دانلود CSV (سازگار با Excel)",
                    data=csv_data,
                    file_name="all_results.csv",
                    mime="text/csv; charset=utf-8"
                )
            
            with col2:
                import io
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='همه_نتایج')
                    
                    worksheet = writer.sheets['همه_نتایج']
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
                
                excel_data = output.getvalue()
                st.download_button(
                    label="📥 دانلود Excel (xlsx)",
                    data=excel_data,
                    file_name="all_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            st.markdown("---")
            st.markdown("### 💾 چک‌پوینت‌های ذخیره شده")
            if os.path.exists("checkpoints"):
                checkpoints = [f for f in os.listdir("checkpoints") if f.endswith(".json")]
                if checkpoints:
                    for cp in checkpoints:
                        st.code(cp)
                else:
                    st.info("هیچ چک‌پوینتی یافت نشد.")
        except Exception as e:
            st.error(f"❌ خطا در خواندن فایل: {e}")
            st.info("💡 ممکن است فایل با encoding دیگری ذخیره شده باشد. لطفاً از تنظیمات UTF-8 استفاده کنید.")
    else:
        st.info("هنوز داده‌ای ذخیره نشده است. پس از اجرای پژوهش توسط شرکت‌کنندگان، داده‌ها در اینجا نمایش داده می‌شوند.")

# ✅ اصلاح شده: صفحه تحلیل پیشرفته با پشتیبانی از فارسی
def show_advanced_analysis():
    st.markdown("""
    <div class="main-header">
        <h1>📈 تحلیل پیشرفته داده‌ها</h1>
        <p>تحلیل آماری و بصری نتایج پژوهش</p>
    </div>
    """, unsafe_allow_html=True)
    
    if os.path.exists("data/all_results.csv"):
        df = pd.read_csv("data/all_results.csv", encoding='utf-8-sig')
        
        trust_col = None
        follow_col = None
        for col in df.columns:
            if 'اعتماد' in col or 'trust' in col.lower():
                trust_col = col
            if 'پیروی' in col or 'follow' in col.lower():
                follow_col = col
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            trust_mean = df[trust_col].mean() if trust_col else 0
            st.metric("میانگین اعتماد به هوش مصنوعی", f"{trust_mean:.2f}")
        with col2:
            follow_mean = df[follow_col].mean() if follow_col else 0
            st.metric("میانگین پیروی از هوش مصنوعی", f"{follow_mean:.2f}")
        with col3:
            st.metric("میانگین زمان تصمیم", f"{df['reaction_time_sec'].mean():.1f} ثانیه")
        with col4:
            if 'calibration_error' in df:
                st.metric("میانگین خطای کالیبراسیون", f"{df['calibration_error'].mean():.3f}", 
                         help="نزدیک به صفر = اعتماد کالیبره شده")
        
        st.markdown("---")
        st.markdown("### 📊 شاخص‌های اتکا")
        col_e1, col_e2 = st.columns(2)
        
        with col_e1:
            overreliance_rate = df['overreliance'].mean() * 100 if 'overreliance' in df else 0
            st.metric("نرخ اتکای بیش از حد", f"{overreliance_rate:.1f}%",
                     help="درصد مواردی که هوش مصنوعی اشتباه کرده ولی کاربر پیروی کرده است")
        with col_e2:
            underreliance_rate = df['underreliance'].mean() * 100 if 'underreliance' in df else 0
            st.metric("نرخ کم‌اعتمادی", f"{underreliance_rate:.1f}%",
                     help="درصد مواردی که هوش مصنوعی درست گفته ولی کاربر پیروی نکرده است")
        
        st.markdown("---")
        st.markdown("### 📊 تفکیک بر اساس سناریو")
        
        scenario_stats = df.groupby('scenario_title').agg({
            'decision_is_correct': 'mean',
            'followed_ai': 'mean',
            'reaction_time_sec': 'mean',
            'calibration_error': 'mean'
        }).round(3)
        scenario_stats.columns = ['تصمیم درست', 'پیروی از هوش مصنوعی', 'زمان (ثانیه)', 'خطای کالیبراسیون']
        st.dataframe(scenario_stats, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 📈 نمودار مقایسه سناریوها")
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='تصمیم درست', x=scenario_stats.index, y=scenario_stats['تصمیم درست']))
        fig.add_trace(go.Bar(name='پیروی از هوش مصنوعی', x=scenario_stats.index, y=scenario_stats['پیروی از هوش مصنوعی']))
        fig.update_layout(title="مقایسه تصمیمات درست و پیروی از هوش مصنوعی", barmode='group')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### ⏱️ میانگین زمان تصمیم‌گیری")
        fig2 = px.bar(scenario_stats, x=scenario_stats.index, y='زمان (ثانیه)', 
                      title="زمان تصمیم‌گیری در سناریوهای مختلف",
                      color_discrete_sequence=['#2a5298'])
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("### 🎯 خطای کالیبراسیون اعتماد در سناریوهای مختلف")
        fig3 = px.bar(scenario_stats, x=scenario_stats.index, y='خطای کالیبراسیون',
                      title="خطای کالیبراسیون (هرچه کمتر = اعتماد دقیق‌تر)",
                      color_discrete_sequence=['#dc3545'])
        st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown("### ⚖️ اتکای بیش از حد و کم‌اعتمادی بر اساس سناریو")
        
        over_by_scenario = df.groupby('scenario_title')['overreliance'].mean() * 100
        under_by_scenario = df.groupby('scenario_title')['underreliance'].mean() * 100
        
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(name='اتکای بیش از حد', x=over_by_scenario.index, y=over_by_scenario.values))
        fig4.add_trace(go.Bar(name='کم‌اعتمادی', x=under_by_scenario.index, y=under_by_scenario.values))
        fig4.update_layout(title="مقایسه اتکای بیش از حد و کم‌اعتمادی در سناریوها", barmode='group')
        st.plotly_chart(fig4, use_container_width=True)
            
    else:
        st.info("هنوز داده‌ای برای تحلیل وجود ندارد. ابتدا پژوهش را اجرا کنید.")

# تابع صفحه خوش‌آمدگویی (قبل از تابع main)
def show_welcome():
    """نمایش صفحه خوش‌آمدگویی و دریافت کد شرکت‌کننده"""
    scroll_to_top()
   
    st.markdown("""
    <div class="main-header">
        <h1>🤖 پژوهش تصمیم‌گیری انسان-هوش مصنوعی</h1>
        <p>بررسی تعامل انسان و هوش مصنوعی در تصمیم‌گیری‌های مدیریتی</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 📋 درباره پژوهش
    
    این پژوهش به بررسی **تعامل انسان و هوش مصنوعی** در فرآیند تصمیم‌گیری می‌پردازد.
    
    شما با **۵ سناریوی مدیریتی** مواجه خواهید شد که در هر کدام:
    
    1. 📖 شرح سناریو و شرایط ریسک را مطالعه می‌کنید
    2. 🤖 توصیه هوش مصنوعی را مشاهده می‌کنید
    3. 💭 نظر اولیه خود را ثبت می‌کنید
    4. 🧠 یک **مداخله شناختی** را انجام می‌دهید
    5. 🎯 تصمیم نهایی خود را ثبت می‌کنید
    6. 📊 به پرسشنامه پاسخ می‌دهید
    
    ### ⏱️ زمان تقریبی
    تکمیل تمام سناریوها حدود **۲۰-۳۰ دقیقه** زمان نیاز دارد.
    
    ### 🔒 محرمانگی
    تمام اطلاعات شما **محرمانه** مانده و صرفاً برای اهداف پژوهشی استفاده خواهد شد.
    """)
    
    st.markdown("---")
    
    # دریافت کد شرکت‌کننده
    col1, col2 = st.columns([2, 1])
    
    with col1:
        participant_id = st.text_input(
            "🔑 کد شرکت‌کننده خود را وارد کنید:",
            placeholder="مثلاً: P001",
            help="این کد برای شناسایی شما در پژوهش استفاده می‌شود"
        )
    
    with col2:
        st.markdown("### ")
        st.caption("کد را از پژوهشگر دریافت کنید")
    
    # بررسی وجود چک‌پوینت
    checkpoint_exists = False
    if participant_id:
        checkpoint_file = f"checkpoints/checkpoint_{participant_id}.json"
        if os.path.exists(checkpoint_file):
            checkpoint_exists = True
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if participant_id:
            if checkpoint_exists:
                st.warning("⚠️ چک‌پوینتی برای این کد وجود دارد. آیا می‌خواهید از جایی که متوقف شده‌اید ادامه دهید؟")
                
                col_resume, col_new = st.columns(2)
                with col_resume:
                    if st.button("🔄 ادامه از چک‌پوینت", use_container_width=True):
                        if load_checkpoint(participant_id):
                            st.session_state.participant_id = participant_id
                            st.session_state.step = 'scenario'
                            time.sleep(0.1)
                            st.session_state.need_scroll = True
                            st.rerun()
                        else:
                            st.error("خطا در بارگذاری چک‌پوینت")
                
                with col_new:
                    if st.button("🆕 شروع جدید (پاک کردن چک‌پوینت)", use_container_width=True):
                        clear_checkpoint(participant_id)
                        st.session_state.participant_id = participant_id
                        st.session_state.step = 'expertise'
                        time.sleep(0.1)
                        st.session_state.need_scroll = True
                        st.rerun()
            else:
                if st.button("🚀 شروع پژوهش", use_container_width=True):
                    st.session_state.participant_id = participant_id
                    st.session_state.step = 'expertise'
                    time.sleep(0.1)
                    st.session_state.need_scroll = True
                    st.rerun()
        else:
            st.info("🔑 لطفاً کد شرکت‌کننده را وارد کنید")
    
    # اطلاعات تکمیلی
    with st.expander("ℹ️ اطلاعات بیشتر درباره پژوهش"):
        st.markdown("""
        ### 🎯 اهداف پژوهش
        
        - بررسی **اتکای بیش از حد** به هوش مصنوعی در تصمیم‌گیری
        - مطالعه **اعتماد** کاربران به سیستم‌های هوش مصنوعی
        - ارزیابی اثربخشی **مداخلات شناختی** در بهبود تصمیم‌گیری
        - اندازه‌گیری **بار شناختی** در تعامل با هوش مصنوعی
        
        ### 📊 متغیرهای اندازه‌گیری
        
        - **اعتماد به هوش مصنوعی** (مقیاس ۱-۷)
        - **پیروی از توصیه** هوش مصنوعی
        - **دقت تصمیم‌گیری** (درست/نادرست)
        - **بار شناختی** (NASA-TLX)
        - **کالیبراسیون اعتماد** (تفاوت بین اعتماد اعلامی و درستی واقعی)
        
        ### 🔬 طراحی پژوهش
        
        - **سناریوهای کنترلشده:** ۵ سناریوی مدیریتی
        - **مداخلات شناختی:** ۴ نوع مداخله مختلف
        - **گروه کنترل:** یک سناریو بدون مداخله
        - **تکرار:** هر شرکت‌کننده همه سناریوها را تجربه می‌کند
        
        ### 📝 نحوه مشارکت
        
        1. کد شرکت‌کننده را وارد کنید
        2. پرسشنامه پیش‌آزمون را تکمیل کنید
        3. ۵ سناریو را به ترتیب انجام دهید
        4. پس از اتمام، نتایج خود را مشاهده کنید
        5. (اختیاری) بازخورد خود را ثبت کنید
        
        ### ❓ سوالات متداول
        
        **آیا پاسخ‌های من ذخیره می‌شود؟**  
        بله، پس از هر سناریو پاسخ‌ها به‌صورت خودکار ذخیره می‌شوند.
        
        **آیا می‌توانم پژوهش را متوقف و ادامه دهم؟**  
        بله، با استفاده از چک‌پوینت می‌توانید از جایی که متوقف شده‌اید ادامه دهید.
        
        **آیا هوش مصنوعی همیشه درست است؟**  
        خیر، در برخی سناریوها هوش مصنوعی عمداً اشتباه طراحی شده است.
        
        **چقدر زمان نیاز است؟**  
        حدود ۲۰-۳۰ دقیقه بسته به دقت شما در پاسخ‌دهی.
        """)
    
    st.markdown("---")
    st.caption("🔬 این پژوهش توسط گروه پژوهشی تصمیم‌گیری و هوش مصنوعی انجام می‌شود.")
    st.caption("📧 برای سوالات: research@example.com")




# ==================== صفحه پرسشنامه پیش‌آزمون ====================
def show_expertise_page():
    """نمایش صفحه پرسشنامه تخصص و سوابق"""
    scroll_to_top()

   
    st.markdown("""
    <div class="main-header">
        <h1>📋 پرسشنامه پیش‌آزمون</h1>
        <p>لطفاً اطلاعات زیر را برای تحلیل بهتر نتایج وارد کنید</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 📝 اطلاعات زمینه‌ای
    
    این اطلاعات به ما کمک می‌کند تا نتایج را بر اساس سابقه و تخصص شرکت‌کنندگان تحلیل کنیم.
    
    **توجه:** همه اطلاعات محرمانه باقی می‌ماند.
    """)
    
    # دریافت اطلاعات تخصص
    expertise_data = show_expertise_questionnaire()
    
    st.markdown("---")
    
    # نمایش خلاصه اطلاعات
    st.markdown("### 📋 خلاصه اطلاعات وارد شده")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎓 تحصیلات:**")
        st.info(expertise_data.get("education", "نامشخص"))
        
        st.markdown("**📚 رشته تحصیلی:**")
        st.info(expertise_data.get("field_of_study", "نامشخص"))
        
        st.markdown("**💼 سابقه کار:**")
        st.info(expertise_data.get("work_experience", "نامشخص"))
    
    with col2:
        st.markdown("**🤖 آشنایی با هوش مصنوعی:**")
        st.info(expertise_data.get("ai_familiarity", "نامشخص"))
        
        st.markdown("**📊 تجربه تصمیم‌گیری:**")
        st.info(expertise_data.get("decision_making_exp", "نامشخص"))
        
        st.markdown("**⚡ ریسک‌پذیری:**")
        st.info(expertise_data.get("risk_tolerance", "نامشخص"))
    
    st.markdown("---")
    
    # نمایش بار شناختی پایه
    st.markdown("### 🧠 بار شناختی پایه")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.metric(
            "فعالیت ذهنی", 
            f"{expertise_data.get('mental_demand_baseline', 4)}/7",
            help="میزان فعالیت ذهنی در کارهای روزمره"
        )
        st.metric(
            "فشار زمانی",
            f"{expertise_data.get('temporal_demand_baseline', 4)}/7",
            help="احساس فشار زمان در کارهای روزمره"
        )
        st.metric(
            "تلاش",
            f"{expertise_data.get('effort_baseline', 4)}/7",
            help="میزان تلاش در انجام کارهای روزمره"
        )
    
    with col4:
        st.metric(
            "رضایت از عملکرد",
            f"{expertise_data.get('performance_baseline', 4)}/7",
            help="رضایت از عملکرد در کارهای روزمره"
        )
        st.metric(
            "ناامیدی/استرس",
            f"{expertise_data.get('frustration_baseline', 4)}/7",
            help="احساس ناامیدی یا استرس در کارهای روزمره"
        )
        st.metric(
            "فعالیت فیزیکی",
            f"{expertise_data.get('physical_demand_baseline', 4)}/7",
            help="میزان فعالیت فیزیکی در کارهای روزمره"
        )
    
    st.markdown("---")
    
    # دکمه تأیید
    st.markdown("### ✅ تأیید و شروع پژوهش")
    st.caption("پس از تأیید، وارد سناریوهای پژوهش خواهید شد. پاسخ‌ها قابل تغییر نیستند.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("✅ تأیید اطلاعات و شروع سناریوها", use_container_width=True, type="primary"):
            # ذخیره اطلاعات در session_state
            st.session_state.expertise_data = expertise_data
            
            # تنظیم زمان شروع
            st.session_state.scenario_start_time = None
            
            # رفتن به مرحله سناریو
            st.session_state.step = 'scenario'
            
            # نمایش پیام موفقیت
            st.success("✅ اطلاعات با موفقیت ثبت شد! در حال انتقال به سناریوها...")
            time.sleep(0.5)
            time.sleep(0.1)
            st.session_state.need_scroll = True
            st.rerun()
    
    # دکمه بازگشت (اختیاری)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("🔙 بازگشت", use_container_width=True):
            st.session_state.step = 'welcome'
            st.session_state.need_scroll = True
            st.rerun()
# اجرای اصلی
def main():
    init_session_state()
    
    with st.sidebar:
        st.markdown("---")
        if st.session_state.step not in ['scenario', 'expertise']:
            page = st.radio(
                "📁 منوی پژوهش",
                ["🧪 اجرای پژوهش", "📊 مدیریت داده‌ها", "📈 تحلیل پیشرفته"],
                index=0
            )
        else:
            st.markdown(f"### 🔄 در حال اجرا")
            st.markdown(f"**کد شرکت‌کننده:** {st.session_state.participant_id or 'نامشخص'}")
            st.markdown(f"**سناریوی جاری:** {st.session_state.current_scenario + 1}/5")
            st.progress(st.session_state.current_scenario / 5)
            page = "🧪 اجرای پژوهش"
        
        st.markdown("---")
        st.caption("پژوهش دکتری مدیریت فناوری اطلاعات")
        st.caption("محمد علی‌دوستی - ۱۴۰۴")
    
    if page == "🧪 اجرای پژوهش":
        if st.session_state.step == 'welcome':
            show_welcome()
        elif st.session_state.step == 'expertise':
            show_expertise_page()
        elif st.session_state.step == 'scenario':
            show_scenario()
        elif st.session_state.step == 'finished':
            show_finished()
    elif page == "📊 مدیریت داده‌ها":
        show_admin()
    elif page == "📈 تحلیل پیشرفته":
        show_advanced_analysis()

if __name__ == "__main__":
    main()