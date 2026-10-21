import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="النظام الإداري المركزي 🏢",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. التنسيق والواجهة العصرية باللون البنفسجي الفخم
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');
    
    html, body, [class*="css"], .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Tajawal', sans-serif;
        background-color: #f3f4f6;
    }
    
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { 
        display: none !important; 
    }

    h1, h2, h3, h4 {
        font-family: 'Tajawal', sans-serif !important;
        font-weight: 700 !important;
        color: #3b0764;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }

    div[data-testid="stForm"], div.stExpander {
        background: #ffffff;
        padding: 16px;
        border-radius: 16px;
        border: 1px solid #e9d5ff;
        box-shadow: 0 4px 12px rgba(107, 33, 168, 0.05);
        margin-bottom: 12px;
    }

    .stButton>button, div[data-testid="stForm"] button {
        width: 100% !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        font-family: 'Tajawal', sans-serif !important;
        padding: 10px 14px !important;
        border: none !important;
        box-shadow: 0 2px 6px rgba(107, 33, 168, 0.15);
    }

    button[kind="primary"] {
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%) !important;
        color: #ffffff !important;
    }

    div[data-baseweb="tab-list"] {
        gap: 6px !important;
        background-color: #ede9fe;
        padding: 6px;
        border-radius: 14px;
        margin-bottom: 15px;
        flex-wrap: wrap !important;
    }
    
    button[data-baseweb="tab"] {
        font-family: 'Tajawal', sans-serif !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        color: #581c87 !important;
    }

    button[aria-selected="true"] {
        background-color: #ffffff !important;
        color: #7c3aed !important;
        box-shadow: 0 2px 6px rgba(107, 33, 168, 0.1) !important;
    }

    #MainMenu, header, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "admin_system_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "admin_dept": [],       # قسم الإدارة (الكتب والتعاميم)
        "comms_dept": [],       # شعبة الاتصالات (الأجهزة والمنظومات)
        "training_dept": [],    # قسم التدريب (الدورات والمنتسبين)
        "it_dept": [],          # نظم المعلومات (البصمة والأجهزة)
        "accounts_dept": []     # الحسابات والعهد
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

if "success_msg" in st.session_state:
    st.success(st.session_state.pop("success_msg"))

# الهيدر العصري
st.markdown("""
    <div style="text-align: center; padding: 10px 0 15px 0;">
        <div style="font-size: 3rem; line-height: 1;">🏢🎖️</div>
        <h2 style="color: #6d28d9; font-weight: 800; margin: 5px 0 0 0;">النظام الإداري والخدمي المركزي</h2>
        <p style="color: #6b7280; font-size: 0.85rem;">إدارة الأقسام، الاتصالات، التدريب، نظم المعلومات، والحسابات بدقة واحترافية</p>
    </div>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "📂 الإدارة والكتب", 
    "📡 الاتصالات والمنظومات", 
    "🎯 التدريب والمنتسبين", 
    "💻 نظم المعلومات والبصمة", 
    "💰 الحسابات والعهد"
])

tab_admin, tab_comms, tab_train, tab_it, tab_acc = tabs[0], tabs[1], tabs[2], tabs[3], tabs[4]

# ---------------- 1. قسم الإدارة والكتب ----------------
with tab_admin:
    st.subheader("📂 قسم الإدارة (الصادر والوارد والتعاميم)")
    
    with st.expander("➕ تسجيل كتاب إداري جديد"):
        with st.form("admin_form", clear_on_submit=True):
            doc_title = st.text_input("موضوع الكتاب / التعميم:")
            doc_num = st.text_input("رقم الكتاب:")
            doc_type = st.selectbox("نوع الكتاب:", ["صادر رسمي", "وارد رسمي", "مذكرة داخلية", "برقية"])
            doc_date = st.date_input("تاريخ الكتاب:")
            doc_notes = st.text_input("ملاحظات / الخلاصة:")
            
            if st.form_submit_button("حفظ وإرشفة الكتاب 📂", type="primary"):
                if doc_title.strip() and doc_num.strip():
                    data["admin_dept"].append({
                        "date_saved": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "title": doc_title.strip(),
                        "number": doc_num.strip(),
                        "type": doc_type,
                        "date": str(doc_date),
                        "notes": doc_notes.strip()
                    })
                    save_data(data)
                    st.session_state["success_msg"] = "✅ تمت أرشفة الكتاب الإداري بنجاح!"
                    st.rerun()

    if data["admin_dept"]:
        st.markdown("##### 📋 سجل الكتب والتعاميم المؤرشفة")
        st.dataframe(pd.DataFrame(data["admin_dept"]), use_container_width=True)
    else:
        st.info("لا توجد كتب مسجلة في قسم الإدارة حالياً.")

# ---------------- 2. شعبة الاتصالات ----------------
with tab_comms:
    st.subheader("📡 شعبة الاتصالات (إدارة أجهزة الراديو والمقاحل والمنظومات)")
    
    with st.expander("➕ تسجيل جهاز / منظومة اتصالات جديدة"):
        with st.form("comms_form", clear_on_submit=True):
            device_name = st.text_input("نوع الجهاز / المنظومة (مثلاً: هاريس 50W، ربيتر، محطة):")
            device_serial = st.text_input("الرقم التعريفي (Serial / السيريال):")
            device_loc = st.text_input("الموقع / النقطة المرابطة فيها:")
            device_status = st.selectbox("حالة الجهاز:", ["🟢 صالح للعمل وعامل", "🟡 يحتاج صيانة", "🔴 عاطل عن العمل"])
            
            if st.form_submit_button("حفظ بيانات الاتصالات 📡", type="primary"):
                if device_name.strip():
                    data["comms_dept"].append({
                        "time": datetime.now().strftime("%Y-%m-%d"),
                        "device": device_name.strip(),
                        "serial": device_serial.strip(),
                        "location": device_loc.strip(),
                        "status": device_status
                    })
                    save_data(data)
                    st.session_state["success_msg"] = "✅ تمت إضافة بيانات جهاز الاتصالات بنجاح!"
                    st.rerun()

    if data["comms_dept"]:
        st.markdown("##### 📋 جرد أجهزة ومنظومات الاتصالات")
        st.dataframe(pd.DataFrame(data["comms_dept"]), use_container_width=True)
    else:
        st.info("لا توجد أجهزة مسجلة في شعبة الاتصالات حالياً.")

# ---------------- 3. قسم التدريب ----------------
with tab_train:
    st.subheader("🎯 قسم التدريب (الدورات وتوزيع المنتسبين)")
    
    with st.expander("➕ تسجيل دورة أو جدول تدريبي جديد"):
        with st.form("train_form", clear_on_submit=True):
            course_name = st.text_input("عنوان الدورة / الوجبة التدريبية:")
            trainer = st.text_input("المشرف أو المدرب المسؤول:")
            trainees_count = st.number_input("عدد المنتسبين المشاركين:", value=10, step=1)
            duration = st.text_input("فترة الدورة (مثلاً: أسبوعين):")
            
            if st.form_submit_button("حفظ الدورة التدريبية 🎯", type="primary"):
                if course_name.strip():
                    data["training_dept"].append({
                        "time": datetime.now().strftime("%Y-%m-%d"),
                        "course": course_name.strip(),
                        "trainer": trainer.strip(),
                        "count": int(trainees_count),
                        "duration": duration.strip()
                    })
                    save_data(data)
                    st.session_state["success_msg"] = "✅ تم تسجيل الدورة التدريبية بنجاح!"
                    st.rerun()

    if data["training_dept"]:
        st.markdown("##### 📋 سجل الدورات التدريبية")
        st.dataframe(pd.DataFrame(data["training_dept"]), use_container_width=True)
    else:
        st.info("لا توجد دورات تدريبية مسجلة حالياً.")

# ---------------- 4. نظم المعلومات والبصمة ----------------
with tab_it:
    st.subheader("💻 نظم المعلومات (إدارة أجهزة البصمة والمنظومات البرمجية)")
    
    with st.expander("➕ تسجيل إجراء أو صيانة برمجية/بصمة"):
        with st.form("it_form", clear_on_submit=True):
            it_action = st.text_input("نوع الإجراء (مثلاً: تحديث قاعدة بيانات البصمة، صيانة جهاز ZKTeco):")
            it_tech = st.text_input("اسم الفني أو المبرمج القائم بالإجراء:")
            it_status = st.selectbox("الحالة:", ["تم الإنجاز بنجاح", "قيد المتابعة", "تتطلب قطع غيار / تحديث"])
            it_notes = st.text_input("ملاحظات إضافية:")
            
            if st.form_submit_button("حفظ سجل نظم المعلومات 💻", type="primary"):
                if it_action.strip():
                    data["it_dept"].append({
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "action": it_action.strip(),
                        "tech": it_tech.strip(),
                        "status": it_status,
                        "notes": it_notes.strip()
                    })
                    save_data(data)
                    st.session_state["success_msg"] = "✅ تم حفظ سجل نظم المعلومات بنجاح!"
                    st.rerun()

    if data["it_dept"]:
        st.markdown("##### 📋 سجل أعمال نظم المعلومات والبصمة")
        st.dataframe(pd.DataFrame(data["it_dept"]), use_container_width=True)
    else:
        st.info("لا توجد سجلات في قسم نظم المعلومات حالياً.")

# ---------------- 5. الحسابات والعهد ----------------
with tab_acc:
    st.subheader("💰 الحسابات والعهد والمصاريف")
    
    with st.expander("➕ تسجيل قيد مالي أو عهدة جديدة"):
        with st.form("acc_form", clear_on_submit=True):
            acc_title = st.text_input("بيان الصرف / العهدة / التخصيص:")
            acc_type = st.selectbox("نوع الحركة:", ["صرف مالي", "استلام عهدة", "تسوية حسابات"])
            acc_amount = st.number_input("المبلغ (د.ع):", value=50000, step=5000)
            acc_person = st.text_input("المستفيد أو المسؤول عن العهدة:")
            
            if st.form_submit_button("حفظ القيد المالي 💰", type="primary"):
                if acc_title.strip() and acc_amount > 0:
                    data["accounts_dept"].append({
                        "time": datetime.now().strftime("%Y-%m-%d"),
                        "title": acc_title.strip(),
                        "type": acc_type,
                        "amount": float(acc_amount),
                        "person": acc_person.strip()
                    })
                    save_data(data)
                    st.session_state["success_msg"] = "✅ تم حفظ القيد المالي بنجاح!"
                    st.rerun()

    if data["accounts_dept"]:
        st.markdown("##### 📋 سجل الحسابات والعهد")
        df_acc = pd.DataFrame(data["accounts_dept"])
        st.dataframe(df_acc, use_container_width=True)
        total_money = df_acc["amount"].sum()
        st.markdown(f"### 💵 إجمالي المبالغ المرصودة: `{total_money:,.0f}` د.ع")
    else:
        st.info("لا توجد قيود مالية مسجلة حالياً.")
