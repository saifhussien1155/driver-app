import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="نظام متابعة كروات الجروب",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. تحسين مظهر الواجهة وإلغاء القائمة الجانبية تماماً
st.markdown("""
    <style>
    html, body, [class*="css"], .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }
    h1 { font-size: 1.2rem !important; line-height: 1.3 !important; }
    h2 { font-size: 1.05rem !important; line-height: 1.3 !important; }
    h3, h4 { font-size: 0.95rem !important; line-height: 1.3 !important; }
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.4rem !important;
        padding-right: 0.4rem !important;
        max-width: 100% !important;
    }
    div[data-baseweb="tab-list"] { gap: 2px !important; flex-wrap: wrap !important; }
    button[data-baseweb="tab"] { font-size: 0.82rem !important; padding: 5px 7px !important; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    #MainMenu, header, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "drivers_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "drivers" not in data: data["drivers"] = []
                if "trips" not in data: data["trips"] = []
                if "supervisors" not in data:
                    data["supervisors"] = [
                        {"name": "مشرف 1", "pin": "7788", "frozen": False}
                    ]
                if "manager_pin" not in data:
                    data["manager_pin"] = "1234"
                
                # تحديث هيكل السواق
                updated_drivers = []
                for d in data["drivers"]:
                    if isinstance(d, str):
                        updated_drivers.append({"name": d, "phone": "", "car": "", "address": "", "frozen": False})
                    elif isinstance(d, dict):
                        if "frozen" not in d: d["frozen"] = False
                        if "phone" not in d: d["phone"] = ""
                        if "car" not in d: d["car"] = ""
                        if "address" not in d: d["address"] = ""
                        updated_drivers.append(d)
                data["drivers"] = updated_drivers
                return data
        except Exception:
            pass
    return {
        "drivers": [],
        "trips": [],
        "supervisors": [{"name": "مشرف 1", "pin": "7788", "frozen": False}],
        "manager_pin": "1234"
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# ---------------- 🔒 نظام تسجيل الدخول بالحسابات والرموز ----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.user_name = None

if not st.session_state.authenticated:
    st.title("🚗 تسجيل الدخول لتطبيق كروات الجروب")
    st.info("🔒 يرجى إدخال الرمز السري الخاص بك (رمز المدير العام أو رمز المشرف).")
    
    pin_entry = st.text_input("🔑 الرمز السري (PIN):", type="password")
    if st.button("دخول النظام 🚀", type="primary"):
        # 1. فحص رمز المدير العام
        if pin_entry == data.get("manager_pin", "1234"):
            st.session_state.authenticated = True
            st.session_state.role = "manager"
            st.session_state.user_name = "المدير العام"
            st.success("🔓 مرحباً بك يا مديرنا العام!")
            st.rerun()
        else:
            # 2. فحص رمز المشرفين
            supervisor = next((s for s in data.get("supervisors", []) if str(s.get("pin")) == pin_entry), None)
            if supervisor:
                if supervisor.get("frozen", False):
                    st.error("⚠️ حساب المشرف هذا مجمد حالياً بقرار من المدير العام!")
                else:
                    st.session_state.authenticated = True
                    st.session_state.role = "supervisor"
                    st.session_state.user_name = supervisor["name"]
                    st.success(f"✅ مرحباً بك المشرف: {supervisor['name']}")
                    st.rerun()
            else:
                st.error("❌ الرمز السري خاطئ! تأكد من الرمز الخاص بك.")
    st.stop()

# ---------------- بداية التطبيق بعد تسجيل الدخول ----------------
RESQ_TYPES = [
    "كروة كاملة",
    "نفر",
    "نفرين",
    "حوض",
    "بريد",
    "بريد كامل",
    "كروة مرجع"
]

# هيدر التطبيق + معلومات الدخول وزر الخروج
col_title, col_user = st.columns([1.5, 1.5])
with col_title:
    st.title("🚗 كروات الجروب")
with col_user:
    role_label = "👑 المدير العام" if st.session_state.role == "manager" else f"👤 المشرف: {st.session_state.user_name}"
    st.caption(f"الحساب الحالي: **{role_label}**")
    if st.button("تسجيل الخروج 🚪"):
        st.session_state.authenticated = False
        st.session_state.role = None
        st.session_state.user_name = None
        st.rerun()

st.markdown("---")

# ---------------- التبويبات الرئيسية ----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 تسجيل رزق", 
    "👥 إدارة الأعضاء والمشرفين", 
    "📋 سجل الرزق", 
    "📊 الملخص والتقارير"
])

# --- التبويب الأول: تسجيل رزق جديد ---
with tab1:
    st.subheader("تسجيل طلب / رزق جديد")
    active_drivers = [d["name"] for d in data["drivers"] if not d.get("frozen", False)]
    
    if not active_drivers:
        st.warning("لا يوجد سواق نشطون حالياً! (يرجى إضافة سواق من تبويب إدارة الأعضاء).")
    else:
        col1, col2 = st.columns(2)
        with col1:
            giver = st.selectbox("السائق المعطي (صاحب الكروة):", active_drivers, key="giver")
        with col2:
            receiver = st.selectbox("السائق المستلم:", active_drivers, key="receiver")
            
        resq_type = st.selectbox("نوع الرزق / الكروة:", RESQ_TYPES)
        notes = st.text_input("ملاحظات (اختياري):")
        
        if st.button("➕ تسجيل الرزق الآن", type="primary"):
            if giver == receiver:
                st.error("⚠️ لا يمكن أن يكون السائق المعطي هو نفسه المستلم!")
            else:
                new_trip = {
                    "id": len(data["trips"]) + 1,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "giver": giver,
                    "receiver": receiver,
                    "type": resq_type,
                    "notes": notes,
                    "added_by": st.session_state.user_name
                }
                data["trips"].append(new_trip)
                save_data(data)
                st.success(f"✅ تم تسجيل كروة ({resq_type}) بنجاح بواسطة [{st.session_state.user_name}]!")
                st.rerun()

# --- التبويب الثاني: إدارة السواق + إدارة المشرفين للمدير ---
with tab2:
    st.subheader("👥 إدارة السواق والمشرفين")
    
    # قسم خاص بالمدير العام لإدارة المشرفين
    if st.session_state.role == "manager":
        with st.expander("👑 قسم التحكم بالمشرفين (خاص بالمدير العام)", expanded=True):
            st.markdown("#### 1️⃣ إضافة مشرف جديد:")
            with st.form("add_supervisor_form"):
                sup_name = st.text_input("اسم المشرف الجديد *:")
                sup_pin = st.text_input("الرمز السري للمشرف (PIN) *:", type="password")
                submit_sup = st.form_submit_button("إضافة المشرف ➕")
                if submit_sup:
                    sup_name = sup_name.strip()
                    sup_pin = sup_pin.strip()
                    existing_pins = [str(s.get("pin")) for s in data["supervisors"]] + [str(data.get("manager_pin"))]
                    if not sup_name or not sup_pin:
                        st.error("يرجى ملء جميع حقول المشرف!")
                    elif sup_pin in existing_pins:
                        st.error("هذا الرمز السري مستخدم مسبقاً! اختر رمزا آخر.")
                    else:
                        data["supervisors"].append({"name": sup_name, "pin": sup_pin, "frozen": False})
                        save_data(data)
                        st.success(f"✅ تم إضافة المشرف ({sup_name}) برمز ({sup_pin}) بنجاح!")
                        st.rerun()

            st.markdown("---")
            st.markdown("#### 2️⃣ التحكم بالمشرفين (تجميد / فك تجميد / طرد):")
            if data["supervisors"]:
                sup_names = [s["name"] for s in data["supervisors"]]
                selected_sup_name = st.selectbox("اختر المشرف للإجراء:", sup_names)
                sup_obj = next((s for s in data["supervisors"] if s["name"] == selected_sup_name), None)
                
                if sup_obj:
                    col_s1, col_s2 = st.columns(2)
                    with col_s1:
                        if sup_obj.get("frozen", False):
                            st.warning(f"⚠️ المشرف ({selected_sup_name}) مجمد حالياً.")
                            if st.button("🔥 فك تجميد المشرف"):
                                sup_obj["frozen"] = False
                                save_data(data)
                                st.success("✅ تم فك تجميد المشرف!")
                                st.rerun()
                        else:
                            st.info(f"✅ المشرف ({selected_sup_name}) نشط.")
                            if st.button("🧊 تجميد المشرف (منع الدخول)"):
                                sup_obj["frozen"] = True
                                save_data(data)
                                st.warning("تم تجميد المشرف بنجاح!")
                                st.rerun()
                    with col_s2:
                        if st.button("🗑️ طرد / حذف المشرف نهائياً"):
                            data["supervisors"] = [s for s in data["supervisors"] if s["name"] != selected_sup_name]
                            save_data(data)
                            st.success("تم طرد وحذف المشرف نهائياً!")
                            st.rerun()

            st.markdown("---")
            st.markdown("#### 📋 قائمة المشرفين الحالية:")
            if data["supervisors"]:
                df_sup = pd.DataFrame(data["supervisors"])
                df_sup["الحالة"] = df_sup["frozen"].apply(lambda x: "🧊 مجمد" if x else "✅ نشط")
                df_sup = df_sup.rename(columns={"name": "اسم المشرف", "pin": "الرمز السري (PIN)"})
                st.dataframe(df_sup[["اسم المشرف", "الرمز السري (PIN)", "الحالة"]], use_container_width=True)

        st.markdown("---")

    # استيراد وإضافة السواق (للمشرف والمدير)
    with st.expander("📁 1. استيراد ورَفْع سواق (Excel/CSV)"):
        uploaded_file = st.file_uploader("اختر ملف Excel أو CSV:", type=["xlsx", "xls", "csv"])
        if uploaded_file is not None:
            try:
                df_import = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                name_col = next((c for c in df_import.columns if "اسم" in str(c) or "name" in str(c).lower()), df_import.columns[0] if len(df_import.columns)>0 else None)
                if name_col:
                    existing_names = {d["name"] for d in data["drivers"]}
                    count_added = 0
                    for _, row in df_import.iterrows():
                        driver_name = str(row[name_col]).strip()
                        if driver_name and driver_name not in existing_names and driver_name.lower() != "nan":
                            data["drivers"].append({
                                "name": driver_name,
                                "phone": str(row.get("رقم الهاتف", "")).replace("nan", ""),
                                "car": str(row.get("السيارة", "")).replace("nan", ""),
                                "address": str(row.get("العنوان", "")).replace("nan", ""),
                                "frozen": False
                            })
                            existing_names.add(driver_name)
                            count_added += 1
                    save_data(data)
                    st.success(f"🎉 تم إضافة {count_added} سائق بنجاح!")
                    st.rerun()
            except Exception as e:
                st.error(f"خطأ في الملف: {e}")

    with st.expander("➕ 2. إضافة سائق جديد يدوياً"):
        with st.form("add_driver_form"):
            new_name = st.text_input("اسم السائق الكامل *:")
            new_phone = st.text_input("رقم الهاتف:")
            new_car = st.text_input("نوع وموديل السيارة:")
            new_address = st.text_input("عنوان السكن:")
            submit_add = st.form_submit_button("إضافة السائق")
            
            if submit_add:
                new_name = new_name.strip()
                if not new_name:
                    st.error("يرجى إدخال الاسم!")
                elif new_name in [d["name"] for d in data["drivers"]]:
                    st.error("السائق موجود بالفعل!")
                else:
                    data["drivers"].append({"name": new_name, "phone": new_phone, "car": new_car, "address": new_address, "frozen": False})
                    save_data(data)
                    st.success(f"✅ تم إضافة {new_name}")
                    st.rerun()

    st.markdown("---")
    st.subheader("🧊 عقوبة تجميد ومسح السواق")
    if data["drivers"]:
        selected_d = st.selectbox("اختر السائق:", [d["name"] for d in data["drivers"]])
        driver_obj = next((d for d in data["drivers"] if d["name"] == selected_d), None)
        
        if driver_obj:
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                if driver_obj.get("frozen", False):
                    st.warning("⚠️ السائق مجمد حالياً")
                    if st.button("🔥 فك تجميد السائق"):
                        driver_obj["frozen"] = False
                        save_data(data)
                        st.success("✅ تم فك التجميد")
                        st.rerun()
                else:
                    st.info("✅ السائق نشط")
                    if st.button("🧊 تجميد السائق (عقوبة)"):
                        driver_obj["frozen"] = True
                        save_data(data)
                        st.warning("تم التجميد بنجاح")
                        st.rerun()
            with col_f2:
                if st.session_state.role == "manager":
                    if st.button("🗑️ حذف السائق نهائياً"):
                        data["drivers"] = [d for d in data["drivers"] if d["name"] != selected_d]
                        save_data(data)
                        st.success("تم الحذف بنجاح")
                        st.rerun()
                else:
                    st.caption("🔒 (حذف السائق حصراً للمدير العام)")

    st.markdown("---")
    st.subheader("📋 دليل جميع سواق الجروب")
    if data["drivers"]:
        df_show = pd.DataFrame(data["drivers"])
        df_show["الحالة"] = df_show["frozen"].apply(lambda x: "🧊 مجمد" if x else "✅ نشط")
        df_show = df_show.rename(columns={"name": "الاسم", "phone": "الهاتف", "car": "السيارة", "address": "السكن"})
        st.dataframe(df_show[["الاسم", "الحالة", "الهاتف", "السيارة", "السكن"]], use_container_width=True)

# --- التبويب الثالث: سجل الرزق ---
with tab3:
    st.subheader("📜 سجل الكروات التفصيلي")
    if not data["trips"]:
        st.info("لا توجد كروات مسجلة حتى الآن.")
    else:
        df_trips_display = pd.DataFrame(data["trips"]).rename(columns={
            "id": "ت", "time": "الوقت", "giver": "المعطي", 
            "receiver": "المستلم", "type": "النوع", "notes": "ملاحظات", "added_by": "سجل بواسطة"
        })
        st.dataframe(df_trips_display, use_container_width=True)
        st.markdown("---")
        selected_trip_id = st.selectbox("اختر رقم الكروة للحذف:", [t["id"] for t in data["trips"]])
        if st.button("حذف الكروة المحددة"):
            data["trips"] = [t for t in data["trips"] if t["id"] != selected_trip_id]
            save_data(data)
            st.success("تم حذف الكروة")
            st.rerun()

# --- التبويب الرابع: الملخص وميزان العدالة ---
with tab4:
    st.subheader("📊 جدول ميزان السواق (الحسابات)")
    if data["drivers"]:
        balances = {d["name"]: {"given": 0, "received": 0} for d in data["drivers"]}
        for t in data["trips"]:
            if t.get("giver") in balances: balances[t["giver"]]["given"] += 1
            if t.get("receiver") in balances: balances[t["receiver"]]["received"] += 1
                
        summary_data = [{
            "اسم السائق": d["name"],
            "الحالة": "🧊 مجمد" if d.get("frozen", False) else "✅ نشط",
            "أنطى (معطي)": balances[d["name"]]["given"],
            "أخذ (مستلم)": balances[d["name"]]["received"],
            "الصافي / الميزان": balances[d["name"]]["given"] - balances[d["name"]]["received"]
        } for d in data["drivers"]]
            
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, use_container_width=True)
        st.markdown("---")
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            st.download_button("📥 تحميل الميزان (Excel)", df_summary.to_csv(index=False, encoding='utf-8-sig'), "ميزان_الجروب.csv", "text/csv")
        with col_ex2:
            if data["trips"]:
                st.download_button("📥 تحميل السجل التفصيلي", pd.DataFrame(data["trips"]).to_csv(index=False, encoding='utf-8-sig'), "سجل_الكروات.csv", "text/csv")
