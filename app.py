import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# 1. إعدادات الصفحة الأساسية مع أيقونة التكسي
st.set_page_config(
    page_title="كابتن الجروب 🚖 | نظام الكروات",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. تصميم الواجهة العصرية (Modern CSS Styling)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');
    
    html, body, [class*="css"], .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Tajawal', 'Segoe UI', sans-serif;
        background-color: #f8fafc;
    }
    
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* عناوين الواجهة */
    h1, h2, h3, h4 {
        font-family: 'Tajawal', sans-serif !important;
        font-weight: 700 !important;
        color: #0f172a;
    }

    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
        max-width: 100% !important;
    }

    /* تصميم البطاقات والنماذج Modern Card Styling */
    div[data-testid="stForm"], div.stExpander {
        background: #ffffff;
        padding: 16px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        margin-bottom: 12px;
    }

    /* أزرار التطبيق العصرية */
    .stButton>button, div[data-testid="stForm"] button {
        width: 100% !important;
        border-radius: 12px !important;
        font-size: 1.02rem !important;
        font-weight: 700 !important;
        font-family: 'Tajawal', sans-serif !important;
        padding: 10px 14px !important;
        transition: all 0.2s ease-in-out;
        border: none !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
    }

    /* زر التسجيل الرئيسي باللون الذهبي التكسي */
    button[kind="primary"] {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: #ffffff !important;
    }
    
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%) !important;
        box-shadow: 0 4px 12px rgba(217, 119, 6, 0.3) !important;
    }

    /* التبويبات العلويّة Tabs */
    div[data-baseweb="tab-list"] {
        gap: 6px !important;
        flex-wrap: wrap !important;
        background-color: #e2e8f0;
        padding: 5px;
        border-radius: 14px;
        margin-bottom: 15px;
    }
    
    button[data-baseweb="tab"] {
        font-family: 'Tajawal', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        padding: 8px 12px !important;
        border-radius: 10px !important;
        color: #475569 !important;
    }

    button[aria-selected="true"] {
        background-color: #ffffff !important;
        color: #d97706 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06) !important;
    }

    /* شارات الإحصائيات (KPI Cards) */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 10px 14px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02);
    }
    .metric-val {
        font-size: 1.3rem;
        font-weight: 800;
        color: #d97706;
    }
    .metric-lbl {
        font-size: 0.78rem;
        color: #64748b;
        font-weight: 600;
    }

    #MainMenu, header, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "drivers_data.json"

DEFAULT_PRICES = {
    "كروة كاملة": 10000,
    "نفر": 2500,
    "نفرين": 5000,
    "حوض": 15000,
    "بريد": 5000,
    "بريد كامل": 10000,
    "كروة مرجع": 12000
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "drivers" not in data: data["drivers"] = []
                if "trips" not in data: data["trips"] = []
                if "supervisors" not in data: data["supervisors"] = []
                if "manager_pin" not in data: data["manager_pin"] = "1234"
                if "prices" not in data: data["prices"] = DEFAULT_PRICES
                if "archives" not in data: data["archives"] = []
                
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
                
                for t in data["trips"]:
                    if "price" not in t:
                        t["price"] = data["prices"].get(t.get("type", ""), 0)
                return data
        except Exception:
            pass
    return {
        "drivers": [],
        "trips": [],
        "supervisors": [],
        "manager_pin": "1234",
        "prices": DEFAULT_PRICES,
        "archives": []
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# ---------------- 🔒 شاشة تسجيل الدخول العصرية ----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.user_name = None

if not st.session_state.authenticated:
    st.markdown("""
        <div style="text-align: center; padding: 20px 0 10px 0;">
            <div style="font-size: 4rem; line-height: 1;">🚖</div>
            <h2 style="color: #d97706; margin-top: 10px; font-weight: 800;">كابتن الجروب</h2>
            <p style="color: #64748b; font-size: 0.95rem;">النظام الذكي لإدارة وميزان كروات التكسي</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.markdown("##### 🔒 تسجيل الدخول بالنظام")
        pin_entry = st.text_input("🔑 أدخل الرمز السري (PIN):", type="password")
        submit_login = st.form_submit_button("دخول للنظام 🚀", type="primary")
        
        if submit_login:
            if pin_entry == str(data.get("manager_pin", "1234")):
                st.session_state.authenticated = True
                st.session_state.role = "manager"
                st.session_state.user_name = "المدير العام"
                st.success("🔓 مرحباً بك يا مديرنا العام!")
                st.rerun()
            else:
                supervisor = next((s for s in data.get("supervisors", []) if str(s.get("pin")) == pin_entry), None)
                if supervisor:
                    if supervisor.get("frozen", False):
                        st.error("⚠️ حساب هذا المشرف مجمد حالياً بقرار من المدير العام!")
                    else:
                        st.session_state.authenticated = True
                        st.session_state.role = "supervisor"
                        st.session_state.user_name = supervisor["name"]
                        st.success(f"✅ مرحباً بك المشرف: {supervisor['name']}")
                        st.rerun()
                else:
                    st.error("❌ الرمز السري خاطئ أو غير مصرح له بالدخول!")
    st.stop()

# ---------------- بداية التطبيق الرئيسي ----------------
if "success_msg" in st.session_state:
    st.success(st.session_state.pop("success_msg"))

# هيدر التطبيق وشعار التكسي
st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 5px 0 12px 0;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 2.2rem;">🚖</span>
            <div>
                <h2 style="margin: 0; font-size: 1.25rem; color: #d97706;">كابتن الجروب</h2>
                <span style="font-size: 0.75rem; color: #64748b;">نظام متابعة الكروات</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

col_info1, col_info2 = st.columns([2, 1])
with col_info1:
    role_badge = "👑 المدير العام" if st.session_state.role == "manager" else f"👤 المشرف: {st.session_state.user_name}"
    st.caption(f"الحساب الحالي: **{role_badge}**")
with col_info2:
    if st.button("خروج 🚪"):
        st.session_state.authenticated = False
        st.session_state.role = None
        st.session_state.user_name = None
        st.rerun()

# 📊 شريط إحصائيات سريع السواح والكروات
active_drivers_count = len([d for d in data["drivers"] if not d.get("frozen", False)])
today_str = datetime.now().strftime("%Y-%m-%d")
today_trips_count = len([t for t in data["trips"] if str(t.get("time", "")).startswith(today_str)])
total_trips_count = len(data["trips"])

st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 15px;">
        <div class="metric-card">
            <div class="metric-val">{active_drivers_count}</div>
            <div class="metric-lbl">سائق نشط 🚖</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">{today_trips_count}</div>
            <div class="metric-lbl">كروات اليوم 📈</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">{total_trips_count}</div>
            <div class="metric-lbl">مجموع الكروات 📋</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------------- التبويبات الرئيسية ----------------
tab_titles = ["📝 تسجيل رزق", "👥 الأعضاء والمشرفين", "📋 سجل الكروات", "📊 الميزان والمالية"]
if st.session_state.role == "manager":
    tab_titles.append("⚙️ إعدادات المدير")

tabs = st.tabs(tab_titles)
tab1, tab2, tab3, tab4 = tabs[0], tabs[1], tabs[2], tabs[3]
tab5 = tabs[4] if st.session_state.role == "manager" else None

# --- التبويب الأول: تسجيل رزق جديد ---
with tab1:
    st.subheader("📝 تسجيل طلب / رزق جديد")
    active_drivers = [d["name"] for d in data["drivers"] if not d.get("frozen", False)]
    
    if not active_drivers:
        st.warning("لا يوجد سواق نشطون حالياً! (يرجى إضافة سواق من تبويب إدارة الأعضاء).")
    else:
        with st.form("add_trip_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                giver = st.selectbox("السائق المعطي (صاحب الكروة):", active_drivers, key="giver")
            with col2:
                receiver = st.selectbox("السائق المستلم:", active_drivers, key="receiver")
                
            resq_type = st.selectbox("نوع الرزق / الكروة:", list(data["prices"].keys()))
            default_price = data["prices"].get(resq_type, 0)
            trip_price = st.number_input("سعر الكروة (دينار عراقي):", value=int(default_price), step=500)
            notes = st.text_input("ملاحظات إضافية (اختياري):")
            
            submit_trip = st.form_submit_button("➕ تسجيل الرزق الآن", type="primary")
            
            if submit_trip:
                if giver == receiver:
                    st.error("⚠️ لا يمكن أن يكون السائق المعطي هو نفسه المستلم!")
                else:
                    new_trip = {
                        "id": len(data["trips"]) + 1,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "giver": giver,
                        "receiver": receiver,
                        "type": resq_type,
                        "price": float(trip_price),
                        "notes": notes,
                        "added_by": st.session_state.user_name
                    }
                    data["trips"].append(new_trip)
                    save_data(data)
                    st.session_state["success_msg"] = f"✅ تم تسجيل كروة ({resq_type}) بقيمة {trip_price:,} د.ع بنجاح!"
                    st.rerun()

# --- التبويب الثاني: إدارة الأعضاء والمشرفين جنبًا إلى جنب ---
with tab2:
    st.subheader("👥 إدارة الأعضاء والمشرفين")

    if st.session_state.role == "manager":
        col_sup, col_drv = st.columns(2)

        # العمود الأول: إدارة المشرفين
        with col_sup:
            st.markdown("### 👑 1. إدارة المشرفين")
            with st.form("add_supervisor_form", clear_on_submit=True):
                sup_name = st.text_input("اسم المشرف الجديد *:")
                sup_pin = st.text_input("الرمز السري المخصص له (PIN) *:", type="password")
                submit_sup = st.form_submit_button("إضافة المشرف وإصدار الرمز ➕")
                if submit_sup:
                    sup_name = sup_name.strip()
                    sup_pin = sup_pin.strip()
                    existing_pins = [str(s.get("pin")) for s in data["supervisors"]] + [str(data.get("manager_pin"))]
                    if not sup_name or not sup_pin:
                        st.error("يرجى كتابة اسم المشرف والرمز السري!")
                    elif sup_pin in existing_pins:
                        st.error("هذا الرمز السري مستخدم مسبقاً! اختر رمزاً آخر.")
                    else:
                        data["supervisors"].append({"name": sup_name, "pin": sup_pin, "frozen": False})
                        save_data(data)
                        st.session_state["success_msg"] = f"✅ تم إضافة المشرف ({sup_name}) برمز [{sup_pin}] بنجاح!"
                        st.rerun()

            st.markdown("---")
            st.markdown("#### ⚙️ إجراءات المشرفين:")
            if data["supervisors"]:
                sup_names = [s["name"] for s in data["supervisors"]]
                selected_sup_name = st.selectbox("اختر المشرف:", sup_names, key="sel_sup_manage")
                sup_obj = next((s for s in data["supervisors"] if s["name"] == selected_sup_name), None)

                if sup_obj:
                    col_s1, col_s2 = st.columns(2)
                    with col_s1:
                        if sup_obj.get("frozen", False):
                            st.warning("⚠️ المشرف مجمد حالياً")
                            if st.button("🔥 فك تجميد المشرف"):
                                sup_obj["frozen"] = False
                                save_data(data)
                                st.session_state["success_msg"] = "✅ تم فك تجميد المشرف بنجاح!"
                                st.rerun()
                        else:
                            st.info("✅ المشرف نشط")
                            if st.button("🧊 تجميد المشرف"):
                                sup_obj["frozen"] = True
                                save_data(data)
                                st.session_state["success_msg"] = "🧊 تم تجميد المشرف بنجاح!"
                                st.rerun()
                    with col_s2:
                        if st.button("🗑️ طرد / حذف المشرف"):
                            data["supervisors"] = [s for s in data["supervisors"] if s["name"] != selected_sup_name]
                            save_data(data)
                            st.session_state["success_msg"] = "🗑️ تم طرد وحذف المشرف نهائياً!"
                            st.rerun()

                st.markdown("---")
                st.markdown("#### 📋 قائمة المشرفين:")
                df_sup = pd.DataFrame(data["supervisors"])
                df_sup["الحالة"] = df_sup["frozen"].apply(lambda x: "🧊 مجمد" if x else "✅ نشط")
                df_sup = df_sup.rename(columns={"name": "الاسم", "pin": "الرمز (PIN)"})
                st.dataframe(df_sup[["الاسم", "الرمز (PIN)", "الحالة"]], use_container_width=True)
            else:
                st.info("لا يوجد مشرفون مضافون حالياً.")

        # العمود الثاني: إدارة الاعضاء والسواق
        with col_drv:
            st.markdown("### 🚘 2. إضافة سائق جديد")
            with st.form("add_driver_form", clear_on_submit=True):
                new_name = st.text_input("اسم السائق الكامل *:")
                new_phone = st.text_input("رقم الهاتف:")
                new_car = st.text_input("نوع وموديل السيارة:")
                new_address = st.text_input("عنوان السكن:")
                submit_add = st.form_submit_button("إضافة السائق ➕")

                if submit_add:
                    new_name = new_name.strip()
                    if not new_name:
                        st.error("يرجى إدخال اسم السائق!")
                    elif new_name in [d["name"] for d in data["drivers"]]:
                        st.error("السائق موجود بالفعل!")
                    else:
                        data["drivers"].append({"name": new_name, "phone": new_phone, "car": new_car, "address": new_address, "frozen": False})
                        save_data(data)
                        st.session_state["success_msg"] = f"✅ تم إضافة السائق ({new_name}) بنجاح!"
                        st.rerun()

            st.markdown("---")
            st.markdown("#### ⚙️ إجراءات وعقوبة السواق:")
            if data["drivers"]:
                selected_d = st.selectbox("اختر السائق:", [d["name"] for d in data["drivers"]], key="sel_drv_manage")
                driver_obj = next((d for d in data["drivers"] if d["name"] == selected_d), None)

                if driver_obj:
                    col_f1, col_f2 = st.columns(2)
                    with col_f1:
                        if driver_obj.get("frozen", False):
                            st.warning("⚠️ السائق مجمد حالياً")
                            if st.button("🔥 فك التجميد"):
                                driver_obj["frozen"] = False
                                save_data(data)
                                st.session_state["success_msg"] = "✅ تم فك تجميد السائق بنجاح!"
                                st.rerun()
                        else:
                            st.info("✅ السائق نشط")
                            if st.button("🧊 تجميد السائق"):
                                driver_obj["frozen"] = True
                                save_data(data)
                                st.session_state["success_msg"] = "🧊 تم تجميد السائق بنجاح!"
                                st.rerun()
                    with col_f2:
                        if st.button("🗑️ حذف السائق نهائياً"):
                            data["drivers"] = [d for d in data["drivers"] if d["name"] != selected_d]
                            save_data(data)
                            st.session_state["success_msg"] = "🗑️ تم حذف السائق نهائياً!"
                            st.rerun()

    else:
        # واجهة المشرف
        st.markdown("### 🚘 إضافة سائق جديد")
        with st.form("add_driver_form_sup", clear_on_submit=True):
            new_name = st.text_input("اسم السائق الكامل *:")
            new_phone = st.text_input("رقم الهاتف:")
            new_car = st.text_input("نوع وموديل السيارة:")
            new_address = st.text_input("عنوان السكن:")
            submit_add = st.form_submit_button("إضافة السائق ➕")

            if submit_add:
                new_name = new_name.strip()
                if not new_name:
                    st.error("يرجى إدخال اسم السائق!")
                elif new_name in [d["name"] for d in data["drivers"]]:
                    st.error("السائق موجود بالفعل!")
                else:
                    data["drivers"].append({"name": new_name, "phone": new_phone, "car": new_car, "address": new_address, "frozen": False})
                    save_data(data)
                    st.session_state["success_msg"] = f"✅ تم إضافة السائق ({new_name}) بنجاح!"
                    st.rerun()

        st.markdown("---")
        st.markdown("#### ⚙️ عقوبة تجميد السائق:")
        if data["drivers"]:
            selected_d = st.selectbox("اختر السائق:", [d["name"] for d in data["drivers"]], key="sel_drv_manage_sup")
            driver_obj = next((d for d in data["drivers"] if d["name"] == selected_d), None)

            if driver_obj:
                if driver_obj.get("frozen", False):
                    st.warning("⚠️ السائق مجمد حالياً")
                    if st.button("🔥 فك تجميد السائق"):
                        driver_obj["frozen"] = False
                        save_data(data)
                        st.session_state["success_msg"] = "✅ تم فك تجميد السائق بنجاح!"
                        st.rerun()
                else:
                    st.info("✅ السائق نشط")
                    if st.button("🧊 تجميد السائق (عقوبة)"):
                        driver_obj["frozen"] = True
                        save_data(data)
                        st.session_state["success_msg"] = "🧊 تم تجميد السائق بنجاح!"
                        st.rerun()

    st.markdown("---")
    st.subheader("📋 دليل جميع سواق الجروب")
    if data["drivers"]:
        df_show = pd.DataFrame(data["drivers"])
        df_show["الحالة"] = df_show["frozen"].apply(lambda x: "🧊 مجمد" if x else "✅ نشط")
        df_show = df_show.rename(columns={"name": "الاسم", "phone": "الهاتف", "car": "السيارة", "address": "السكن"})
        st.dataframe(df_show[["الاسم", "الحالة", "الهاتف", "السيارة", "السكن"]], use_container_width=True)

# --- التبويب الثالث: سجل الكروات التفصيلي ---
with tab3:
    st.subheader("📜 سجل الكروات التفصيلي والفلترة")
    if not data["trips"]:
        st.info("لا توجد كروات مسجلة حتى الآن.")
    else:
        col_flt1, col_flt2 = st.columns(2)
        with col_flt1:
            filter_driver = st.selectbox("🔍 فلترة حسب السائق:", ["الكل"] + [d["name"] for d in data["drivers"]])
        with col_flt2:
            filter_date = st.selectbox("📅 فلترة حسب التاريخ:", ["الكل", "اليوم فقط"])

        filtered_trips = data["trips"].copy()

        if filter_driver != "الكل":
            filtered_trips = [t for t in filtered_trips if t.get("giver") == filter_driver or t.get("receiver") == filter_driver]

        if filter_date == "اليوم فقط":
            filtered_trips = [t for t in filtered_trips if str(t.get("time", "")).startswith(today_str)]

        if not filtered_trips:
            st.warning("لا توجد كروات تطابق الفلتر المحدد!")
        else:
            df_trips_display = pd.DataFrame(filtered_trips).rename(columns={
                "id": "ت", "time": "الوقت", "giver": "المعطي", 
                "receiver": "المستلم", "type": "النوع", "price": "السعر (د.ع)", "notes": "ملاحظات", "added_by": "سجل بواسطة"
            })
            st.dataframe(df_trips_display, use_container_width=True)

        st.markdown("---")
        selected_trip_id = st.selectbox("اختر رقم الكروة للحذف:", [t["id"] for t in data["trips"]])
        if st.button("حذف الكروة المحددة"):
            data["trips"] = [t for t in data["trips"] if t["id"] != selected_trip_id]
            save_data(data)
            st.session_state["success_msg"] = f"❌ تم حذف الكروة رقم {selected_trip_id} بنجاح!"
            st.rerun()

# --- التبويب الرابع: الميزان وحسابات الفلوس ---
with tab4:
    st.subheader("📊 ميزان العدالة وحسابات الفلوس")
    if data["drivers"]:
        balances = {d["name"]: {"given_count": 0, "received_count": 0, "given_money": 0.0, "received_money": 0.0} for d in data["drivers"]}
        
        for t in data["trips"]:
            price = float(t.get("price", 0))
            if t.get("giver") in balances:
                balances[t["giver"]]["given_count"] += 1
                balances[t["giver"]]["given_money"] += price
            if t.get("receiver") in balances:
                balances[t["receiver"]]["received_count"] += 1
                balances[t["receiver"]]["received_money"] += price
                
        summary_data = []
        for d in data["drivers"]:
            b = balances[d["name"]]
            count_net = b["given_count"] - b["received_count"]
            money_net = b["given_money"] - b["received_money"]
            
            summary_data.append({
                "اسم السائق": d["name"],
                "الحالة": "🧊 مجمد" if d.get("frozen", False) else "✅ نشط",
                "أنطى (كروات)": b["given_count"],
                "أخذ (كروات)": b["received_count"],
                "صافي الكروات": count_net,
                "أنطى (د.ع)": f"{b['given_money']:,}",
                "أخذ (د.ع)": f"{b['received_money']:,}",
                "الصافي الفعلي (د.ع)": f"{money_net:,}"
            })
            
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📲 مشاركة الميزان بجروب الواتساب")
        
        wa_text = "🚖 *تقرير ميزان كروات الجروب* 🚖\n"
        wa_text += f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}\n"
        wa_text += "-----------------------------------\n"
        for item in summary_data:
            wa_text += f"👤 *{item['اسم السائق']}*: كروات ({item['صافي الكروات']}) | الصافي المالي: ({item['الصافي الفعلي (د.ع)']} د.ع)\n"
        wa_text += "-----------------------------------\n"
        wa_text += "تحيات إدارة كابتن الجروب 🌹"
        
        st.text_area("انسخ هذا النص وارقعه بجروب الواتساب مباشرة:", wa_text, height=150)
        
        st.markdown("---")
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            st.download_button("📥 تحميل الميزان (Excel)", df_summary.to_csv(index=False, encoding='utf-8-sig'), "ميزان_الجروب.csv", "text/csv")
        with col_ex2:
            if data["trips"]:
                st.download_button("📥 تحميل السجل التفصيلي", pd.DataFrame(data["trips"]).to_csv(index=False, encoding='utf-8-sig'), "سجل_الكروات.csv", "text/csv")

# --- التبويب الخامس: إعدادات المدير العام ---
if tab5 and st.session_state.role == "manager":
    with tab5:
        st.subheader("⚙️ إعدادات وتعديلات المدير العام")
        
        with st.expander("🔑 1. تغيير الرمز السري للمدير العام"):
            with st.form("change_pin_form"):
                new_m_pin = st.text_input("أدخل الرمز السري الجديد للمدير:", type="password")
                submit_pin = st.form_submit_button("تحديث الرمز السري 🔒")
                if submit_pin:
                    new_m_pin = new_m_pin.strip()
                    if len(new_m_pin) < 4:
                        st.error("الرمز السري يجب أن يتكون من 4 أرقام على الأقل!")
                    else:
                        data["manager_pin"] = new_m_pin
                        save_data(data)
                        st.session_state["success_msg"] = f"✅ تم تغيير رمز المدير العام إلى [{new_m_pin}] بنجاح!"
                        st.rerun()

        with st.expander("💰 2. تعديل أسعار الكروات الإفتراضية"):
            st.info("تعديل السعر هنا سيغير السعر التلقائي عند تسجيل كروة جديدة.")
            with st.form("prices_form"):
                updated_prices = {}
                for p_name, p_val in data["prices"].items():
                    updated_prices[p_name] = st.number_input(f"سعر ({p_name}):", value=int(p_val), step=500)
                submit_prices = st.form_submit_button("حفظ الأسعار الجديدة 💾")
                if submit_prices:
                    data["prices"] = updated_prices
                    save_data(data)
                    st.session_state["success_msg"] = "✅ تم تحديث قائمة أسعار الكروات بنجاح!"
                    st.rerun()

        with st.expander("🔄 3. تصفير الحسابات وبداية شهر/فترة جديدة (اختياري)"):
            st.warning("⚠️ التصفير سيقوم بنقل جميع الكروات الحالية للأرشيف وتصفير ميزان السواق لبدء دوره جديدة.")
            archive_name = st.text_input("اسم/تاريخ الدورة الأرشيفية (مثلاً: أرباح شهر تشرين الأول):")
            confirm_check = st.checkbox("أقرّ بأسفل هذا الخيار وأرغب بتصفير الحسابات الآن.")
            
            if st.button("🚨 تصفير الحسابات ونقل الكروات للأرشيف", type="primary"):
                if not confirm_check:
                    st.error("يرجى التأشير على مربع الإقرار والتأكيد أولاً!")
                else:
                    archive_entry = {
                        "archive_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "title": archive_name if archive_name else f"أرشيف {datetime.now().strftime('%Y-%m-%d')}",
                        "trips": data["trips"]
                    }
                    data["archives"].append(archive_entry)
                    data["trips"] = []
                    save_data(data)
                    st.session_state["success_msg"] = "🎉 تم تصفير الميزان ونقل كافة البيانات السابقة إلى الأرشيف بنجاح!"
                    st.rerun()

            if data["archives"]:
                st.markdown("---")
                st.markdown("#### 📜 الأرشيف والدورات السابقة:")
                arch_titles = [a["title"] for a in data["archives"]]
                sel_arch = st.selectbox("عرض كروات أرشيف سابق:", arch_titles)
                arch_obj = next((a for a in data["archives"] if a["title"] == sel_arch), None)
                if arch_obj and arch_obj["trips"]:
                    st.dataframe(pd.DataFrame(arch_obj["trips"]), use_container_width=True)

        with st.expander("💾 4. حفظ واسترجاع نسخة احتياطية من البيانات"):
            st.download_button(
                label="📥 تنزيل نسخة احتياطية للبيانات (JSON Backup)",
                data=json.dumps(data, ensure_ascii=False, indent=2),
                file_name=f"drivers_backup_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
