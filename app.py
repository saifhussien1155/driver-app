import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

DATA_FILE = "drivers_data.json"

# أنواع الرزق والطلبات
RESQ_TYPES = [
    "كروة كاملة",
    "نفر",
    "نفرين",
    "حوض",
    "بريد",
    "بريد كامل",
    "كروة مرجع"
]

# تحسين مظهر الواجهة لدعم اللغة العربية والاتجاه من اليمين لليسار (RTL)
st.set_page_config(page_title="نظام كروات الجروب", page_icon="🚗", layout="centered")

st.markdown("""
    <style>
    body, div, input, select, button {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stApp {
        direction: rtl;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# تحميل البيانات
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "drivers" not in data: data["drivers"] = []
                if "frozen_drivers" not in data: data["frozen_drivers"] = []
                if "trips" not in data: data["trips"] = []
                if "driver_info" not in data: data["driver_info"] = {}
                return data
        except Exception:
            pass
    return {"drivers": [], "frozen_drivers": [], "trips": [], "driver_info": {}}

# حفظ البيانات
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

st.title("🚗 نظام متابعة وحسابات كروات الجروب")
st.write("تطبيق الموبايل الموحد للمدير العام والمشرفين")

# شريط اختيار حساب المستخدم
role = st.sidebar.selectbox("تسجيل الدخول كـ:", ["👷 مشرف (Supervisor)", "👑 مدير عام (General Manager)"])
st.sidebar.success(f"مرحباً بك بصلاحية: {role}")

# تبويبات التنقل الرئيسية
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 تسجيل رزق",
    "👥 إدارة السواق والتفاصيل",
    "📋 سجل الرزق التفصيلي",
    "📊 الملخص والتقارير"
])

# السواق النشطون فقط (غير المجمدين) لتسجيل الكروات
active_drivers = [d for d in data["drivers"] if d not in data.get("frozen_drivers", [])]

# -------------------------------------------------------------
# التبويب الأول: تسجيل رزق جديد
# -------------------------------------------------------------
with tab1:
    st.subheader("تسجيل طلب / رزق جديد")
    if not active_drivers:
        st.warning("لا يوجد سواق نشطون حالياً! (إما القائمة فارغة أو جميع السواق مجمدون).")
    else:
        col1, col2 = st.columns(2)
        with col1:
            d_from = st.selectbox("السائق الذي نزل رزقه:", active_drivers, key="from_driver")
        with col2:
            d_to = st.selectbox("السائق الذي أخذ الرزق:", active_drivers, key="to_driver")

        resq_type = st.selectbox("شنو أخذ (نوع الرزق):", RESQ_TYPES)

        if st.button("✅ تسجيل الرزق الآن", type="primary"):
            if d_from == d_to:
                st.error("لا يمكن اختيار نفس السائق في الطرفين!")
            else:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                trip_entry = {
                    "time": now_str,
                    "from": d_from,
                    "to": d_to,
                    "type": resq_type,
                    "by_role": role
                }
                data["trips"].append(trip_entry)
                save_data(data)
                st.success(f"تم تسجيل ({resq_type}) بين ({d_from}) و ({d_to}) بنجاح!")
                st.rerun()

# -------------------------------------------------------------
# التبويب الثاني: إدارة السواق والتفاصيل + رفع Excel + تجميد
# -------------------------------------------------------------
with tab2:
    st.subheader("👥 إدارة الأعضاء والتفاصيل والعقوبات")
    st.info("متاحة للمشرفين والمدير العام (إضافة، استيراد Excel، بيانات التفاصيل، والتجميد)")

    # 1. قسم رفع سواق من ملف Excel
    with st.expander("📁 1. استيراد ورَفْع سواق دفعة واحدة عن طريق ملف Excel أو CSV", expanded=False):
        st.write("يمكنك رفع ملف Excel يحتوي على بيانات السواق وإضافتهم فوراً للنظام:")
        uploaded_file = st.file_uploader("اختر ملف Excel أو CSV:", type=["xlsx", "xls", "csv"])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_upload = pd.read_csv(uploaded_file)
                else:
                    df_upload = pd.read_excel(uploaded_file)

                st.write("معاينة البيانات بالملف:")
                st.dataframe(df_upload.head(3), use_container_width=True)

                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    col_name_match = st.selectbox("عمود اسم السائق:", df_upload.columns)
                    col_phone_match = st.selectbox("عمود رقم الهاتف (اختياري):", ["بدون"] + list(df_upload.columns))
                with col_m2:
                    col_car_match = st.selectbox("عمود نوع السيارة (اختياري):", ["بدون"] + list(df_upload.columns))
                    col_addr_match = st.selectbox("عمود مكان السكن/العنوان (اختياري):", ["بدون"] + list(df_upload.columns))

                if st.button("🚀 إضافة كافة السواق من الملف الآن"):
                    count_added = 0
                    if "driver_info" not in data: data["driver_info"] = {}

                    for _, row in df_upload.iterrows():
                        name_val = str(row[col_name_match]).strip() if pd.notna(row[col_name_match]) else ""
                        if name_val and name_val not in data["drivers"]:
                            data["drivers"].append(name_val)
                            phone_val = str(row[col_phone_match]).strip() if col_phone_match != "بدون" and pd.notna(row[col_phone_match]) else ""
                            car_val = str(row[col_car_match]).strip() if col_car_match != "بدون" and pd.notna(row[col_car_match]) else ""
                            addr_val = str(row[col_addr_match]).strip() if col_addr_match != "بدون" and pd.notna(row[col_addr_match]) else ""

                            data["driver_info"][name_val] = {
                                "phone": phone_val,
                                "car": car_val,
                                "address": addr_val
                            }
                            count_added += 1

                    save_data(data)
                    st.success(f"تمت إضافة ({count_added}) سائق جديد دفعة واحدة بنجاح!")
                    st.rerun()

            except Exception as e:
                st.error(f"حدث خطأ أثناء قراءة الملف: {e}")

    # 2. قسم إضافة سائق يدوي مع التفاصيل
    with st.expander("➕ 2. إضافة سائق جديد يدوياً مع التفاصيل", expanded=False):
        col_n1, col_n2 = st.columns(2)
        with col_n1:
            d_name = st.text_input("اسم السائق الكامل:")
            d_phone = st.text_input("رقم الهاتف:")
        with col_n2:
            d_car = st.text_input("نوع وموديل السيارة:")
            d_address = st.text_input("مكان السكن / العنوان:")

        if st.button("حفظ وإضافة السائق اليدوي"):
            d_name_clean = d_name.strip()
            if not d_name_clean:
                st.warning("يرجى كتابة اسم السائق!")
            elif d_name_clean in data["drivers"]:
                st.warning("هذا السائق موجود بالفعل!")
            else:
                data["drivers"].append(d_name_clean)
                if "driver_info" not in data: data["driver_info"] = {}
                data["driver_info"][d_name_clean] = {
                    "phone": d_phone.strip(),
                    "car": d_car.strip(),
                    "address": d_address.strip()
                }
                save_data(data)
                st.success(f"تمت إضافة السائق ({d_name_clean}) بنجاح!")
                st.rerun()

    # 3. قسم التجميد والمسح
    st.markdown("---")
    st.markdown("### 🧊 عقوبة التجميد ومسح الأعضاء")
    
    if data["drivers"]:
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            selected_for_freeze = st.selectbox("اختر السائق للتجميد/التنشيط:", data["drivers"], key="freeze_select")
            is_frozen = selected_for_freeze in data.get("frozen_drivers", [])
            if is_frozen:
                if st.button("🔓 فك التجميد"):
                    data["frozen_drivers"].remove(selected_for_freeze)
                    save_data(data)
                    st.success(f"تم فك تجميد السائق ({selected_for_freeze})!")
                    st.rerun()
            else:
                if st.button("🧊 تجميد السائق"):
                    if "frozen_drivers" not in data: data["frozen_drivers"] = []
                    data["frozen_drivers"].append(selected_for_freeze)
                    save_data(data)
                    st.warning(f"تم تجميد السائق ({selected_for_freeze})!")
                    st.rerun()

        with c_f2:
            driver_to_delete = st.selectbox("اختر السائق للمسح النهائي:", data["drivers"], key="del_select")
            if st.button("🗑️ مسح السائق نهائياً"):
                data["drivers"].remove(driver_to_delete)
                if driver_to_delete in data.get("frozen_drivers", []):
                    data["frozen_drivers"].remove(driver_to_delete)
                if "driver_info" in data and driver_to_delete in data["driver_info"]:
                    del data["driver_info"][driver_to_delete]
                save_data(data)
                st.success(f"تم مسح السائق ({driver_to_delete}) بنجاح!")
                st.rerun()

    # 4. عرض كافة السواق وتفاصيلهم
    st.markdown("---")
    st.write("**📋 دليل بيانات جميع سواق الجروب:**")
    
    full_info_list = []
    d_info_dict = data.get("driver_info", {})
    
    for d in data["drivers"]:
        info = d_info_dict.get(d, {})
        status = "🧊 مجمد" if d in data.get("frozen_drivers", []) else "✅ نشط"
        full_info_list.append({
            "اسم السائق": d,
            "الحالة": status,
            "رقم الهاتف": info.get("phone", "-"),
            "السيارة": info.get("car", "-"),
            "مكان السكن/العنوان": info.get("address", "-")
        })
    st.dataframe(pd.DataFrame(full_info_list), use_container_width=True)

# -------------------------------------------------------------
# التبويب الثالث: سجل الرزق التفصيلي مع خيار الحذف
# -------------------------------------------------------------
with tab3:
    st.subheader("📋 سجل الكروات والطلبات المسجلة")
    if not data["trips"]:
        st.info("لا توجد طلبات مسجلة حتى الآن.")
    else:
        df_trips = pd.DataFrame(data["trips"])
        df_trips.columns = ["الوقت والتاريخ", "نزل رزقه", "أخذ الرزق", "نوع الرزق", "تم التسجيل بواسطة"]
        st.dataframe(df_trips, use_container_width=True)

        st.markdown("---")
        st.markdown("### 🗑️ إلغاء / حذف طلب محدد")
        trip_options = [f"#{i+1} - {t['type']} ({t['from']} ⬅️ {t['to']}) - {t['time']}" for i, t in enumerate(data["trips"])]
        selected_trip_idx = st.selectbox("اختر الطلب المراد إلغاؤه:", range(len(trip_options)), format_func=lambda x: trip_options[x])

        if st.button("إلغاء هذا الطلب"):
            deleted = data["trips"].pop(selected_trip_idx)
            save_data(data)
            st.success("تم إلغاء الطلب وتحديث الحسابات!")
            st.rerun()

# -------------------------------------------------------------
# التبويب الرابع: ملخص الحسابات وسحب تقارير Excel
# -------------------------------------------------------------
with tab4:
    st.subheader("📊 ملخص حسابات كل سائق")

    if data["drivers"]:
        summary_rows = []
        for d in data["drivers"]:
            given_dict = {}
            taken_dict = {}

            for t in data["trips"]:
                t_type = t.get("type", "كروة كاملة")
                if t["from"] == d:
                    given_dict[t_type] = given_dict.get(t_type, 0) + 1
                if t["to"] == d:
                    taken_dict[t_type] = taken_dict.get(t_type, 0) + 1

            g_str = " | ".join([f"{k}: {v}" for k, v in given_dict.items()]) if given_dict else "لا يوجد"
            t_str = " | ".join([f"{k}: {v}" for k, v in taken_dict.items()]) if taken_dict else "لا يوجد"
            
            d_status = "🧊 مجمد" if d in data.get("frozen_drivers", []) else "✅ نشط"

            summary_rows.append({"اسم السائق": d, "الحالة": d_status, "نزل رزق (عطى)": g_str, "أخذ رزق (استلم)": t_str})

        df_sum = pd.DataFrame(summary_rows)
        st.dataframe(df_sum, use_container_width=True)

        # سحب تقرير Excel/CSV
        st.markdown("---")
        csv_data = df_sum.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📊 سحب وتنزيل تقرير Excel",
            data=csv_data,
            file_name=f"driver_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )