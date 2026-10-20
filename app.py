import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="كابتن الجروب 🚖 | نظام الكروات والميزان",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. تصميم الواجهة العصرية
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

    div[data-testid="stForm"], div.stExpander {
        background: #ffffff;
        padding: 16px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        margin-bottom: 12px;
    }

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

    button[kind="primary"] {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: #ffffff !important;
    }

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
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        padding: 8px 8px !important;
        border-radius: 10px !important;
        color: #475569 !important;
    }

    button[aria-selected="true"] {
        background-color: #ffffff !important;
        color: #d97706 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06) !important;
    }

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

DATA_FILE = "groups_accounts_data.json"

DEFAULT_PRICES = {
    "كروة كاملة": 10000,
    "نفر": 2500,
    "نفرين": 5000,
    "حوض": 15000,
    "بريد": 5000,
    "بريد كامل": 10000,
    "كروة مرجع": 12000,
    "أخرى (إدخال يدوي ✍️)": 0
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "groups" not in data: data["groups"] = {}
                return data
        except Exception:
            pass
    return {
        "groups": {
            "الجروب الرئيسي": {
                "phone": "07711111111",
                "pin": "1111",
                "drivers": [],
                "trips": [],
                "supervisors": [],
                "prices": DEFAULT_PRICES,
                "archives": [],
                "chat": []
            }
        }
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

if "success_msg" in st.session_state:
    st.success(st.session_state.pop("success_msg"))

if "reset_step" not in st.session_state:
    st.session_state.reset_step = 1
    st.session_state.reset_phone = ""
    st.session_state.otp_code = ""

# ---------------- 🔒 شاشة تسجيل الدخول أو التسجيل أو استعادة الرمز ----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_name = None
    st.session_state.current_group = None

if not st.session_state.authenticated:
    st.markdown("""
        <div style="text-align: center; padding: 15px 0 10px 0;">
            <div style="font-size: 3.8rem; line-height: 1;">🚖</div>
            <h2 style="color: #d97706; margin-top: 8px; font-weight: 800;">كابتن الجروب</h2>
            <p style="color: #64748b; font-size: 0.9rem;">نظام إدارة وميزان كروات التكسي المستقل</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab_auth1, tab_auth2, tab_auth3 = st.tabs(["🔑 تسجيل الدخول", "✨ حساب جروب جديد", "🔄 استعادة الرمز"])
    
    # 1. تسجيل الدخول
    with tab_auth1:
        with st.form("login_form"):
            st.markdown("##### تسجيل الدخول لحساب الجروب أو المشرفين")
            l_phone = st.text_input("📞 رقم الموبايل:")
            l_pin = st.text_input("🔑 الرمز السري (PIN):", type="password")
            sub_l = st.form_submit_button("دخول للنظام 🚀", type="primary")
            
            if sub_l:
                l_phone = l_phone.strip()
                l_pin = l_pin.strip()
                
                found_g = None
                found_sup = None
                for g_name, g_info in data["groups"].items():
                    if str(g_info.get("phone")) == l_phone and str(g_info.get("pin")) == l_pin:
                        found_g = g_name
                        break
                    for sup in g_info.get("supervisors", []):
                        if str(sup.get("phone")) == l_phone and str(sup.get("pin")) == l_pin:
                            found_g = g_name
                            found_sup = sup
                            break
                    if found_g:
                        break
                        
                if found_g:
                    g_info = data["groups"][found_g]
                    if found_sup and found_sup.get("frozen", False):
                        st.error("⚠️ حسابك كمشرف مجمد حالياً من قبل مسؤول الجروب!")
                    else:
                        st.session_state.authenticated = True
                        st.session_state.user_name = found_sup["name"] if found_sup else f"مسؤول {found_g}"
                        st.session_state.current_group = found_g
                        st.success(f"✅ تم تسجيل الدخول بنجاح إلى جروب: {found_g}")
                        st.rerun()
                else:
                    st.error("❌ رقم الموبايل أو الرمز السري غير صحيح!")

    # 2. إنشاء حساب جروب جديد
    with tab_auth2:
        with st.form("register_form"):
            st.markdown("##### تسجيل حساب جروب جديد بالنظام")
            r_gname = st.text_input("اسم الجروب (مثلاً: جروب الكرادة / شركة الأمان):")
            r_phone = st.text_input("رقم موبايل المسؤول (للدخول والاستعادة):")
            r_pin = st.text_input("اختر رمزاً سرياً (PIN) لا يقل عن 4 أرقام:", type="password")
            sub_r = st.form_submit_button("إنشاء الجروب وانطلاق 🚀", type="primary")
            
            if sub_r:
                r_gname = r_gname.strip()
                r_phone = r_phone.strip()
                r_pin = r_pin.strip()
                
                if not r_gname or not r_phone or len(r_pin) < 4:
                    st.error("يرجى ملء كافة الحقول والتأكد أن الرمز لا يقل عن 4 أرقام!")
                elif r_gname in data["groups"]:
                    st.error("اسم الجروب هذا مستخدم مسبقاً، اختر اسماً آخر!")
                else:
                    phone_exists = any(str(g.get("phone")) == r_phone for g in data["groups"].values())
                    if phone_exists:
                        st.error("رقم الهاتف هذا مسجل مسبقاً بحساب جروب آخر!")
                    else:
                        data["groups"][r_gname] = {
                            "phone": r_phone,
                            "pin": r_pin,
                            "drivers": [],
                            "trips": [],
                            "supervisors": [],
                            "prices": DEFAULT_PRICES,
                            "archives": [],
                            "chat": []
                        }
                        save_data(data)
                        st.session_state.authenticated = True
                        st.session_state.user_name = f"مسؤول {r_gname}"
                        st.session_state.current_group = r_gname
                        st.session_state["success_msg"] = f"🎉 تم إنشاء حساب جروب ({r_gname}) بنجاح!"
                        st.rerun()

    # 3. استعادة الرمز
    with tab_auth3:
        st.markdown("##### 🔄 استعادة وتغيير الرمز السري عبر رقم الموبايل")
        
        if st.session_state.reset_step == 1:
            with st.form("step1_form"):
                rec_phone = st.text_input("📞 أدخل رقم الموبايل المسجل في حسابك:")
                sub_send_otp = st.form_submit_button("إرسال رمز التحقق إلى الرقم 📩", type="primary")
                
                if sub_send_otp:
                    rec_phone = rec_phone.strip()
                    exists = False
                    for g_info in data["groups"].values():
                        if str(g_info.get("phone")) == rec_phone:
                            exists = True
                            break
                        for sup in g_info.get("supervisors", []):
                            if str(sup.get("phone")) == rec_phone:
                                exists = True
                                break
                        if exists: break
                            
                    if exists:
                        generated_otp = str(random.randint(1000, 9999))
                        st.session_state.reset_phone = rec_phone
                        st.session_state.otp_code = generated_otp
                        st.session_state.reset_step = 2
                        st.rerun()
                    else:
                        st.error("❌ رقم الموبايل هذا غير مسجل في النظام نهائياً!")

        elif st.session_state.reset_step == 2:
            st.info(f"تم إرسال رمز التحقق (OTP) إلى الرقم: **{st.session_state.reset_phone}**")
            st.markdown(f"""
                <div style="background-color: #fef3c7; border: 2px dashed #d97706; padding: 12px; border-radius: 12px; text-align: center; margin-bottom: 15px;">
                    <span style="font-size: 0.9rem; color: #92400e; font-weight: 700;">رمز التحقق الوارد (OTP):</span><br>
                    <span style="font-size: 1.8rem; font-weight: 800; color: #b45309; letter-spacing: 4px;">{st.session_state.otp_code}</span>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("step2_form"):
                entered_otp = st.text_input("🔢 أدخل رمز التحقق الظاهري أعلاه:")
                new_pin_input = st.text_input("🔑 أدخل الرمز السري (PIN) الجديد:", type="password")
                sub_verify = st.form_submit_button("تحقق وتغيير الرمز السري 🔒", type="primary")
                
                if sub_verify:
                    entered_otp = entered_otp.strip()
                    new_pin_input = new_pin_input.strip()
                    
                    if entered_otp != st.session_state.otp_code:
                        st.error("❌ رمز التحقق غير صحيح!")
                    elif len(new_pin_input) < 4:
                        st.error("❌ الرمز السري الجديد يجب ألا يقل عن 4 أرقام!")
                    else:
                        target_phone = st.session_state.reset_phone
                        for g_info in data["groups"].values():
                            if str(g_info.get("phone")) == target_phone:
                                g_info["pin"] = new_pin_input
                                break
                            for sup in g_info.get("supervisors", []):
                                if str(sup.get("phone")) == target_phone:
                                    sup["pin"] = new_pin_input
                                    break
                        save_data(data)
                        
                        st.session_state.reset_step = 1
                        st.session_state.reset_phone = ""
                        st.session_state.otp_code = ""
                        st.session_state["success_msg"] = "🎉 تم تغيير الرمز السري بنجاح! يمكنك الآن تسجيل الدخول برمزك الجديد."
                        st.rerun()
                        
            if st.button("🔙 إلغاء والعودة للخلف"):
                st.session_state.reset_step = 1
                st.rerun()
    st.stop()

# ---------------- التطبيق المستقل الخاص بالجروب الحالي فقط ----------------

current_g_name = st.session_state.current_group
group_data = data["groups"][current_g_name]

if "prices" not in group_data: group_data["prices"] = DEFAULT_PRICES
if "supervisors" not in group_data: group_data["supervisors"] = []
if "archives" not in group_data: group_data["archives"] = []
if "chat" not in group_data: group_data["chat"] = []

st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 5px 0 12px 0;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 2.2rem;">🚖</span>
            <div>
                <h2 style="margin: 0; font-size: 1.25rem; color: #d97706;">{current_g_name}</h2>
                <span style="font-size: 0.75rem; color: #64748b;">نظامك الخاص والمستقل لإدارة الكروات والرزق</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

col_info1, col_info2 = st.columns([2, 1])
with col_info1:
    st.caption(f"المستخدم: **{st.session_state.user_name}** | الجروب: **{current_g_name}**")
with col_info2:
    if st.button("خروج 🚪"):
        st.session_state.authenticated = False
        st.session_state.user_name = None
        st.session_state.current_group = None
        st.rerun()

active_drivers_count = len([d for d in group_data["drivers"] if not d.get("frozen", False)])
today_str = datetime.now().strftime("%Y-%m-%d")
today_trips_count = len([t for t in group_data["trips"] if str(t.get("time", "")).startswith(today_str)])
total_trips_count = len(group_data["trips"])

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

tabs = st.tabs(["📝 تسجيل رزق", "🚘 الأعضاء والسواق", "👑 إدارة المشرفين", "📋 سجل الكروات", "📊 الميزان والمالية", "💬 محادثة الجروب"])
tab1, tab2, tab3, tab4, tab5, tab6 = tabs[0], tabs[1], tabs[2], tabs[3], tabs[4], tabs[5]

# --- 1. تسجيل رزق ---
with tab1:
    st.subheader("📝 تسجيل طلب / رزق جديد")
    active_drivers = [d["name"] for d in group_data["drivers"] if not d.get("frozen", False)]
    if not active_drivers:
        st.warning("لا يوجد سواق نشطون في هذا الجروب حالياً! (يرجى إضافة سواق من تبويب الأعضاء والسواق).")
    else:
        with st.form("add_trip_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                giver = st.selectbox("السائق المعطي (صاحب الكروة):", active_drivers, key="giver")
            with col2:
                receiver = st.selectbox("السائق المستلم:", active_drivers, key="receiver")
                
            resq_type = st.selectbox("نوع الرزق / الكروة:", list(group_data["prices"].keys()))
            
            manual_custom_type = ""
            if "أخرى" in resq_type:
                manual_custom_type = st.text_input("✍️ اكتب نوع الرزق اليدوي / التفاصيل الخاصة:")
                
            default_price = group_data["prices"].get(resq_type, 0)
            trip_price = st.number_input("سعر الكروة (دينار عراقي):", value=int(default_price), step=500)
            notes = st.text_input("ملاحظات إضافية أو حقل فارغ مخصص للتفاصيل:")
            
            submit_trip = st.form_submit_button("➕ تسجيل الرزق الآن", type="primary")
            if submit_trip:
                if giver == receiver:
                    st.error("⚠️ لا يمكن أن يكون السائق المعطي هو نفسه المستلم!")
                else:
                    final_type = f"{resq_type} - {manual_custom_type}" if manual_custom_type else resq_type
                    new_trip = {
                        "id": len(group_data["trips"]) + 1,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "giver": giver,
                        "receiver": receiver,
                        "type": final_type,
                        "price": float(trip_price),
                        "notes": notes,
                        "added_by": st.session_state.user_name
                    }
                    group_data["trips"].append(new_trip)
                    save_data(data)
                    st.session_state["success_msg"] = f"✅ تم تسجيل الكروة بنجاح!"
                    st.rerun()

# --- 2. الأعضاء والسواق ---
with tab2:
    st.subheader("🚘 إدارة الأعضاء والسواق")
    with st.form("add_d_form", clear_on_submit=True):
        st.markdown("##### إضافة سائق جديد للجروب")
        d_name = st.text_input("اسم السائق الكامل *:")
        d_phone = st.text_input("رقم الهاتف:")
        d_car = st.text_input("نوع وموديل السيارة:")
        d_address = st.text_input("عنوان السكن:")
        sub_d = st.form_submit_button("إضافة السائق ➕")
        if sub_d:
            d_name = d_name.strip()
            if not d_name:
                st.error("يرجى إدخال اسم السائق!")
            elif d_name in [d["name"] for d in group_data["drivers"]]:
                st.error("السائق موجود بالفعل!")
            else:
                group_data["drivers"].append({"name": d_name, "phone": d_phone, "car": d_car, "address": d_address, "frozen": False})
                save_data(data)
                st.session_state["success_msg"] = f"✅ تم إضافة السائق ({d_name}) بنجاح!"
                st.rerun()

    st.markdown("---")
    st.subheader("📋 قائمة سواق الجروب")
    if group_data["drivers"]:
        df_d = pd.DataFrame(group_data["drivers"])
        df_d["الحالة"] = df_d["frozen"].apply(lambda x: "🧊 مجمد" if x else "✅ نشط")
        st.dataframe(df_d[["name", "الحالة", "phone", "car", "address"]].rename(columns={"name": "الاسم", "phone": "الهاتف", "car": "السيارة", "address": "السكن"}), use_container_width=True)
        
        sel_drv_del = st.selectbox("اختر سائق لإدارته (تجميد أو طرد):", [d["name"] for d in group_data["drivers"]])
        d_obj = next((d for d in group_data["drivers"] if d["name"] == sel_drv_del), None)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if d_obj and st.button("🧊 تجميد / فك تجميد السائق"):
                d_obj["frozen"] = not d_obj.get("frozen", False)
                save_data(data)
                st.session_state["success_msg"] = "✅ تم تحديث حالة السائق بنجاح!"
                st.rerun()
        with col_btn2:
            if st.button("🗑️ طرد / حذف السائق نهائياً"):
                group_data["drivers"] = [d for d in group_data["drivers"] if d["name"] != sel_drv_del]
                save_data(data)
                st.session_state["success_msg"] = "🗑️ تم طرد وحذف السائق بنجاح!"
                st.rerun()
    else:
        st.info("لا توجد سواق مضافون حتى الآن.")

# --- 3. إدارة المشرفين ---
with tab3:
    st.subheader("👑 إدارة المشرفين وصلاحيات الدخول")
    with st.form("add_sup_form", clear_on_submit=True):
        st.markdown("##### إضافة مشرف جديد برقم هاتف ورمز سري")
        s_name = st.text_input("اسم المشرف *:")
        s_phone = st.text_input("رقم موبايل المشرف (لتسجيل الدخول والاستعادة) *:")
        s_pin = st.text_input("الرمز السري الخاص به (PIN) *:", type="password")
        sub_s = st.form_submit_button("إضافة وتوثيق المشرف ➕")
        if sub_s:
            s_name = s_name.strip()
            s_phone = s_phone.strip()
            s_pin = s_pin.strip()
            if not s_name or not s_phone or not s_pin:
                st.error("يرجى ملء كافة حقول المشرف بدقة!")
            else:
                phone_taken = (s_phone == str(group_data["phone"])) or any(str(sup.get("phone")) == s_phone for sup in group_data["supervisors"])
                if phone_taken:
                    st.error("رقم الهاتف هذا مسجل مسبقاً لمشرف أو مسؤول آخر!")
                else:
                    group_data["supervisors"].append({"name": s_name, "phone": s_phone, "pin": s_pin, "frozen": False})
                    save_data(data)
                    st.session_state["success_msg"] = f"✅ تم إضافة المشرف ({s_name}) بنجاح!"
                    st.rerun()

    st.markdown("---")
    st.subheader("📋 قائمة المشرفين المسجلين بالجروب")
    if group_data["supervisors"]:
        df_sup = pd.DataFrame(group_data["supervisors"])
        df_sup["الحالة"] = df_sup["frozen"].apply(lambda x: "🧊 مجمد" if x else "✅ نشط")
        st.dataframe(df_sup[["name", "phone", "الحالة"]].rename(columns={"name": "اسم المشرف", "phone": "رقم الهاتف"}), use_container_width=True)
        
        sel_s = st.selectbox("اختر المشرف لإدارته:", [s["name"] for s in group_data["supervisors"]])
        s_obj = next((s for s in group_data["supervisors"] if s["name"] == sel_s), None)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if s_obj and st.button("🧊 تجميد / فك تجميد المشرف"):
                s_obj["frozen"] = not s_obj.get("frozen", False)
                save_data(data)
                st.session_state["success_msg"] = "✅ تم تحديث حالة المشرف بنجاح!"
                st.rerun()
        with col_s2:
            if s_obj and st.button("🗑️ طرد / حذف المشرف نهائياً"):
                group_data["supervisors"] = [s for s in group_data["supervisors"] if s["name"] != sel_s]
                save_data(data)
                st.session_state["success_msg"] = "🗑️ تم طرد وحذف المشرف بنجاح!"
                st.rerun()
    else:
        st.info("لا توجد مشرفون فرعيون مضافون حالياً.")

# --- 4. سجل الكروات ---
with tab4:
    st.subheader("📜 سجل الكروات التفصيلي")
    if not group_data["trips"]:
        st.info("لا توجد كروات مسجلة لهذا الجروب.")
    else:
        df_trips = pd.DataFrame(group_data["trips"]).rename(columns={
            "id": "ت", "time": "الوقت", "giver": "المعطي", 
            "receiver": "المستلم", "type": "النوع", "price": "السعر (د.ع)", "notes": "ملاحظات", "added_by": "سجل بواسطة"
        })
        st.dataframe(df_trips, use_container_width=True)
        
        sel_tid = st.selectbox("اختر رقم الكروة للحذف:", [t["id"] for t in group_data["trips"]])
        if st.button("حذف الكروة المحددة"):
            group_data["trips"] = [t for t in group_data["trips"] if t["id"] != sel_tid]
            save_data(data)
            st.session_state["success_msg"] = "❌ تم حذف الكروة بنجاح!"
            st.rerun()

# --- 5. الميزان والمالية ---
with tab5:
    st.subheader("📊 ميزان العدالة وحسابات الفلوس")
    if group_data["drivers"]:
        balances = {d["name"]: {"given_count": 0, "received_count": 0, "given_money": 0.0, "received_money": 0.0} for d in group_data["drivers"]}
        for t in group_data["trips"]:
            price = float(t.get("price", 0))
            if t.get("giver") in balances:
                balances[t["giver"]]["given_count"] += 1
                balances[t["giver"]]["given_money"] += price
            if t.get("receiver") in balances:
                balances[t["receiver"]]["received_count"] += 1
                balances[t["receiver"]]["received_money"] += price
                
        summary_data = []
        for d in group_data["drivers"]:
            b = balances[d["name"]]
            summary_data.append({
                "اسم السائق": d["name"],
                "الحالة": "🧊 مجمد" if d.get("frozen", False) else "✅ نشط",
                "أنطى (كروات)": b["given_count"],
                "أخذ (كروات)": b["received_count"],
                "صافي الكروات": b["given_count"] - b["received_count"],
                "الصافي الفعلي (د.ع)": f"{(b['given_money'] - b['received_money']):,}"
            })
            
        df_sum = pd.DataFrame(summary_data)
        st.dataframe(df_sum, use_container_width=True)
        
        wa_text = f"🚖 *تقرير ميزان {current_g_name}* 🚖\n"
        wa_text += f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d')}\n"
        wa_text += "-----------------------------------\n"
        for item in summary_data:
            wa_text += f"👤 *{item['اسم السائق']}*: كروات ({item['صافي الكروات']}) | الصافي: ({item['الصافي الفعلي (د.ع)']} د.ع)\n"
        wa_text += "-----------------------------------\n"
        st.text_area("نص الواتساب للجروب:", wa_text, height=140)
        st.download_button("📥 تحميل ميزان الجروب (Excel)", df_sum.to_csv(index=False, encoding='utf-8-sig'), "ميزان_الجروب.csv", "text/csv")
    else:
        st.info("لا توجد بيانات سواق لعرض الميزان.")

# --- 6. محادثة الجروب ---
with tab6:
    st.subheader(f"💬 محادثة جروب {current_g_name}")
    st.caption("نافذة محادثة خاصة بمسؤول الجروب والمشرفين التابعين له.")
    
    chat_box = st.container(height=320)
    with chat_box:
        if group_data["chat"]:
            for msg in group_data["chat"]:
                st.markdown(f"**💬 {msg['sender']}** ({msg['time']}):<br>{msg['text']}", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("لا توجد رسائل دردشة في هذا الجروب حتى الآن.")
            
    with st.form("group_chat_form", clear_on_submit=True):
        group_msg_text = st.text_input("اكتب رسالة للزملاء في الجروب:")
        sub_g_chat = st.form_submit_button("إرسال رسالة 📨", type="primary")
        if sub_g_chat:
            group_msg_text = group_msg_text.strip()
            if group_msg_text:
                group_data["chat"].append({
                    "sender": st.session_state.user_name,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "text": group_msg_text
                })
                save_data(data)
                st.rerun()
