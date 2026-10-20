import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# 1. إعدادات الصفحة الأساسية للتجاوب مع الموبايل
st.set_page_config(
    page_title="نظام متابعة كروات الجروب",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. تحسين مظهر الواجهة وإلغاء القائمة الجانبية تماماً لمنع خربطة النصوص على الموبايل
st.markdown("""
    <style>
    /* اتجاه اللغة العربية والخطوط */
    html, body, [class*="css"], .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* إلغاء القائمة الجانبية تماماً لمنع انضغاط الكلمات عمودياً */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* تصغير العناوين لتناسب شاشات الموبايل تماماً */
    h1 {
        font-size: 1.2rem !important;
        line-height: 1.3 !important;
        white-space: normal !important;
        word-break: break-word !important;
        margin-bottom: 0.3rem !important;
    }
    h2 {
        font-size: 1.05rem !important;
        line-height: 1.3 !important;
    }
    h3, h4 {
        font-size: 0.95rem !important;
        line-height: 1.3 !important;
    }

    /* تنظيف الهوامش الزائدة على شاشة الهاتف */
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.4rem !important;
        padding-right: 0.4rem !important;
        max-width: 100% !important;
    }

    /* جعل التبويبات (Tabs) تنزل بانتظام وبدون تداخل */
    div[data-baseweb="tab-list"] {
        gap: 2px !important;
        flex-wrap: wrap !important;
    }
    button[data-baseweb="tab"] {
        font-size: 0.82rem !important;
        padding: 5px 7px !important;
    }

    /* أزرار الإدخال والتنفيذ */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }

    /* إخفاء القوائم والأشرطة الزائدة */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "drivers_data.json"

# أنواع الكروات والرزق
RESQ_TYPES = [
    "كروة كاملة",
    "نفر",
    "نفرين",
    "حوض",
    "بريد",
    "بريد كامل",
    "كروة مرجع"
]

# تحميل البيانات المخزنة
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "drivers" not in data:
                    data["drivers"] = []
                if "trips" not in data:
                    data["trips"] = []
                # تحديث هيكل بيانات السواق
                updated_drivers = []
                for d in data["drivers"]:
                    if isinstance(d, str):
                        updated_drivers.append({"name": d, "phone": "", "car": "", "address": "", "frozen": False})
                    elif isinstance(d, dict):
                        if "frozen" not in d:
                            d["frozen"] = False
                        if "phone" not in d:
                            d["phone"] = ""
                        if "car" not in d:
                            d["car"] = ""
                        if "address" not in d:
                            d["address"] = ""
                        updated_drivers.append(d)
                data["drivers"] = updated_drivers
                return data
        except Exception:
            return {"drivers": [], "trips": []}
    return {"drivers": [], "trips": []}

# حفظ البيانات
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# ---------------- الهيدر الرئيسي واختيار الصلاحية أعلى الصفحة ----------------
col_title, col_role = st.columns([1.8, 1.2])
with col_title:
    st.title("🚗 كروات الجروب")
with col_role:
    role = st.selectbox("🔐 الصلاحية:", ["مشرف", "مدير عام"])

st.markdown("---")

# ---------------- التبويبات الرئيسية ----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 تسجيل رزق", 
    "👥 إدارة السواق", 
    "📋 سجل الرزق", 
    "📊 الملخص والتقارير"
])

# --- التبويب الأول: تسجيل رزق جديد ---
with tab1:
    st.subheader("تسجيل طلب / رزق جديد")
    
    active_drivers = [d["name"] for d in data["drivers"] if not d.get("frozen", False)]
    
    if not active_drivers:
        st.warning("لا يوجد سواق نشطون حالياً! (يرجى إضافة سواق من تبويب إدارة السواق).")
    else:
        col1, col2 = st.columns(2)
        with col1:
            giver = st.selectbox("السائق المعطي (صاحب الكروة):", active_drivers, key="giver")
        with col2:
            receiver = st.selectbox("السائق المستلم:", active_drivers, key="receiver")
            
        resq_type = st.selectbox("نوع الرزق / الكروة:", RESQ_TYPES)
        notes = st.text_input("ملاحظات إضافية (اختياري):")
        
        if st.button("➕ تسجيل الرزق الآن", type="primary"):
            if giver == receiver:
                st.error("⚠️ لا يمكن أن يكون السائق المعطي هو نفسه السائق المستلم!")
            else:
                new_trip = {
                    "id": len(data["trips"]) + 1,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "giver": giver,
                    "receiver": receiver,
                    "type": resq_type,
                    "notes": notes
                }
                data["trips"].append(new_trip)
                save_data(data)
                st.success(f"✅ تم تسجيل كروة ({resq_type}) من [{giver}] إلى [{receiver}] بنجاح!")
                st.rerun()

# --- التبويب الثاني: إدارة السواق والتفاصيل والعقوبات ---
with tab2:
    st.subheader("👥 إدارة الأعضاء والتفاصيل والعقوبات")
    
    with st.expander("📁 1. استيراد ورَفْع سواق (Excel/CSV)"):
        uploaded_file = st.file_uploader("اختر ملف Excel أو CSV:", type=["xlsx", "xls", "csv"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_import = pd.read_csv(uploaded_file)
                else:
                    df_import = pd.read_excel(uploaded_file)
                
                name_col = None
                for col in df_import.columns:
                    if "اسم" in str(col) or "name" in str(col).lower() or "سائق" in str(col):
                        name_col = col
                        break
                if not name_col and len(df_import.columns) > 0:
                    name_col = df_import.columns[0]
                
                if name_col:
                    existing_names = {d["name"] for d in data["drivers"]}
                    count_added = 0
                    for _, row in df_import.iterrows():
                        driver_name = str(row[name_col]).strip()
                        if driver_name and driver_name not in existing_names and driver_name.lower() != "nan":
                            phone = str(row.get("رقم الهاتف", row.get("هاتف", ""))).replace("nan", "")
                            car = str(row.get("نوع السيارة", row.get("السيارة", ""))).replace("nan", "")
                            address = str(row.get("العنوان", row.get("السكن", ""))).replace("nan", "")
                            
                            data["drivers"].append({
                                "name": driver_name,
                                "phone": phone,
                                "car": car,
                                "address": address,
                                "frozen": False
                            })
                            existing_names.add(driver_name)
                            count_added += 1
                    
                    save_data(data)
                    st.success(f"🎉 تم استيراد إضافة {count_added} سائق جديد بنجاح!")
                    st.rerun()
            except Exception as e:
                st.error(f"حدث خطأ أثناء قراءة الملف: {e}")

    with st.expander("➕ 2. إضافة سائق جديد يدوياً"):
        with st.form("add_driver_form"):
            new_name = st.text_input("اسم السائق الكامل *:")
            new_phone = st.text_input("رقم الهاتف:")
            new_car = st.text_input("نوع وموديل السيارة:")
            new_address = st.text_input("عنوان السكن / المنطقة:")
            submit_add = st.form_submit_button("إضافة السائق")
            
            if submit_add:
                new_name = new_name.strip()
                existing_names = [d["name"] for d in data["drivers"]]
                if not new_name:
                    st.error("يرجى إدخال اسم السائق!")
                elif new_name in existing_names:
                    st.error("السائق موجود بالفعل!")
                else:
                    data["drivers"].append({
                        "name": new_name,
                        "phone": new_phone,
                        "car": new_car,
                        "address": new_address,
                        "frozen": False
                    })
                    save_data(data)
                    st.success(f"✅ تم إضافة السائق {new_name} بنجاح!")
                    st.rerun()

    st.markdown("---")
    st.subheader("🧊 عقوبة التجميد ومسح الأعضاء")
    
    if data["drivers"]:
        all_driver_names = [d["name"] for d in data["drivers"]]
        selected_d = st.selectbox("اختر السائق للتعديل أو التجميد:", all_driver_names)
        
        driver_obj = next((d for d in data["drivers"] if d["name"] == selected_d), None)
        
        if driver_obj:
            col_f1, col_f2 = st.columns(2)
            
            with col_f1:
                is_frozen = driver_obj.get("frozen", False)
                if is_frozen:
                    st.warning("⚠️ هذا السائق مجمد حالياً.")
                    if st.button("🔥 فك تجميد السائق"):
                        driver_obj["frozen"] = False
                        save_data(data)
                        st.success("✅ تم فك تجميد السائق!")
                        st.rerun()
                else:
                    st.info("✅ هذا السائق نشط حالياً.")
                    if st.button("🧊 تجميد السائق (عقوبة)"):
                        driver_obj["frozen"] = True
                        save_data(data)
                        st.warning("تم تجميد السائق بنجاح!")
                        st.rerun()
                        
            with col_f2:
                if role == "مدير عام":
                    if st.button("🗑️ حذف السائق نهائياً"):
                        data["drivers"] = [d for d in data["drivers"] if d["name"] != selected_d]
                        save_data(data)
                        st.success("تم حذف السائق نهائياً.")
                        st.rerun()

    st.markdown("---")
    st.subheader("📋 دليل بيانات جميع سواق الجروب")
    if data["drivers"]:
        df_drivers_show = pd.DataFrame(data["drivers"])
        df_drivers_show["الحالة"] = df_drivers_show["frozen"].apply(lambda x: "🧊 مجمد" if x else "✅ نشط")
        df_drivers_show = df_drivers_show.rename(columns={
            "name": "الاسم", 
            "phone": "رقم الهاتف", 
            "car": "السيارة", 
            "address": "السكن"
        })
        st.dataframe(df_drivers_show[["الاسم", "الحالة", "رقم الهاتف", "السيارة", "السكن"]], use_container_width=True)

# --- التبويب الثالث: سجل الرزق التفصيلي ---
with tab3:
    st.subheader("📜 سجل الكروات التفصيلي")
    
    if not data["trips"]:
        st.info("لا توجد كروات مسجلة حتى الآن.")
    else:
        df_trips = pd.DataFrame(data["trips"])
        df_trips_display = df_trips.rename(columns={
            "id": "ت",
            "time": "التاريخ والوقت",
            "giver": "المعطي (صاحب الكروة)",
            "receiver": "المستلم",
            "type": "نوع الرزق",
            "notes": "الملاحظات"
        })
        st.dataframe(df_trips_display, use_container_width=True)
        
        st.markdown("---")
        st.write("❌ **إلغاء أو حذف كروة خطأ:**")
        trip_ids = [t["id"] for t in data["trips"]]
        selected_trip_id = st.selectbox("اختر رقم الكروة (ت) للحذف:", trip_ids)
        if st.button("حذف الكروة المحددة"):
            data["trips"] = [t for t in data["trips"] if t["id"] != selected_trip_id]
            save_data(data)
            st.success(f"تم حذف الكروة رقم {selected_trip_id} بنجاح!")
            st.rerun()

# --- التبويب الرابع: الملخص والتقارير وميزان العدالة ---
with tab4:
    st.subheader("📊 جدول ميزان السواق (العدالة والحسابات)")
    
    if not data["drivers"]:
        st.info("يرجى إضافة سواق أولاً لرؤية الحسابات.")
    else:
        balances = {d["name"]: {"given": 0, "received": 0} for d in data["drivers"]}
        
        for t in data["trips"]:
            g = t.get("giver")
            r = t.get("receiver")
            if g in balances:
                balances[g]["given"] += 1
            if r in balances:
                balances[r]["received"] += 1
                
        summary_data = []
        for d in data["drivers"]:
            name = d["name"]
            given = balances[name]["given"]
            received = balances[name]["received"]
            net = given - received
            status = "🧊 مجمد" if d.get("frozen", False) else "✅ نشط"
            summary_data.append({
                "اسم السائق": name,
                "الحالة": status,
                "أنطى (معطي)": given,
                "أخذ (مستلم)": received,
                "الصافي / الميزان": net
            })
            
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📥 تصدير التقارير إلى Excel / CSV")
        
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            csv_summary = df_summary.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 تحميل جدول الميزان (CSV/Excel)",
                data=csv_summary,
                file_name="ميزان_سواق_الجروب.csv",
                mime="text/csv"
            )
        with col_ex2:
            if data["trips"]:
                csv_trips = pd.DataFrame(data["trips"]).to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 تحميل السجل التفصيلي (CSV/Excel)",
                    data=csv_trips,
                    file_name="سجل_الكروات_التفصيلي.csv",
                    mime="text/csv"
                )
