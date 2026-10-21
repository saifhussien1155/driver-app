import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="كابتن الجروب 🚖 | نظام الجروبات المتكامل",
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
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        padding: 8px 6px !important;
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
    "كروة مرجع": 12000
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "groups" not in data: data["groups"] = {}
                if "manager_pin" not in data: data["manager_pin"] = "1234"
                if "manager_phone" not in data: data["manager_phone"] = "07700000000"
                return data
        except Exception:
            pass
    return {
        "manager_pin": "1234",
        "manager_phone": "07700000000",
        "groups": {
            "الجروب الرئيسي": {
                "phone": "07711111111",
                "pin": "1111",
                "drivers": [],
                "trips": [],
                "supervisors": [],
                "prices": DEFAULT_PRICES,
                "archives": []
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

# ---------------- 🔒 تسجيل الدخول واستعادة الرمز ----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.user_name = None
    st.session_state.current_group = None

if not st.session_state.authenticated:
    st.markdown("""
        <div style="text-align: center; padding: 15px 0 10px 0;">
            <div style="font-size: 3.8rem; line-height: 1;">🚖</div>
            <h2 style="color: #d97706; margin-top: 8px; font-weight: 800;">كابتن الجروب</h2>
            <p style="color: #64748b; font-size: 0.9rem;">نظام إدارة وميزان كروات التكسي الموثق</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab_auth1, tab_auth2, tab_auth3 = st.tabs(["🔑 تسجيل الدخول", "✨ حساب جديد", "🔄 استعادة الرمز"])
    
    with tab_auth1:
        with st.form("login_form"):
            st.markdown("##### تسجيل الدخول لحسابك القائم")
            l_phone = st.text_input("📞 رقم الموبايل:")
            l_pin = st.text_input("🔑 الرمز السري (PIN):", type="password")
            sub_l = st.form_submit_button("دخول للنظام 🚀", type="primary")
            
            if sub_l:
                l_phone = l_phone.strip()
                l_pin = l_pin.strip()
                
                if l_phone == str(data.get("manager_phone")) and l_pin == str(data.get("manager_pin")):
                    st.session_state.authenticated = True
                    st.session_state.role = "manager"
                    st.session_state.user_name = "المدير العام"
                    st.session_state.current_group = "إدارة عامة"
                    st.success("🔓 أهلاً بك يا مديرنا العام!")
                    st.rerun()
                else:
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
                            st.error("⚠️ حسابك كمشرف مجمد حالياً!")
                        else:
                            st.session_state.authenticated = True
                            st.session_state.role = "supervisor" if found_sup else "group_admin"
                            st.session_state.user_name = found_sup["name"] if found_sup else f"مسؤول {found_g}"
                            st.session_state.current_group = found_g
                            st.success(f"✅ تم تسجيل الدخول بنجاح إلى: {found_g}")
                            st.rerun()
                    else:
                        st.error("❌ رقم الموبايل أو الرمز السري غير صحيح!")

    with tab_auth2:
        with st.form("register_form"):
            st.markdown("##### إنشاء حساب جروب جديد بنفسك")
            r_gname = st.text_input("اسم الجروب الجديد (مثلاً: جروب الكرادة):")
            r_phone = st.text_input("رقم الموبايل (سيكون معتمد لتسجيل الدخول والاستعادة):")
            r_pin = st.text_input("اختر رمزاً سرياً (PIN) لا يقل عن 4 أرقام:", type="password")
            sub_r = st.form_submit_button("تسجيل الحساب وانطلاق 🚀", type="primary")
            
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
                        st.error("رقم الهاتف هذا مسجل مسبقاً بحساب آخر!")
                    else:
                        data["groups"][r_gname] = {
                            "phone": r_phone,
                            "pin": r_pin,
                            "drivers": [],
                            "trips": [],
                            "supervisors": [],
                            "prices": DEFAULT_PRICES,
                            "archives": []
                        }
                        save_data(data)
                        st.session_state.authenticated = True
                        st.session_state.role = "group_admin"
                        st.session_state.user_name = f"مسؤول {r_gname}"
                        st.session_state.current_group = r_gname
                        st.session_state["success_msg"] = f"🎉 تم إنشاء حساب جروب ({r_gname}) بنجاح!"
                        st.rerun()

    with tab_auth3:
        st.markdown("##### 🔄 استعادة وتغيير الرمز السري عبر رقم الموبايل")
        
        if st.session_state.reset_step == 1:
            with st.form("step1_form"):
                rec_phone = st.text_input("📞 أدخل رقم الموبايل المسجل في حسابك:")
                sub_send_otp = st.form_submit_button("إرسال رمز التحقق إلى الرقم 📩", type="primary")
                
                if sub_send_otp:
                    rec_phone = rec_phone.strip()
                    exists = False
                    if rec_phone == str(data.get("manager_phone")):
                        exists = True
                    else:
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
                        if target_phone == str(data.get("manager_phone")):
                            data["manager_pin"] = new_pin_input
                        else:
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

# ---------------- بداية التطبيق ----------------

if st.session_state.role == "manager":
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 5px 0 12px 0;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 2.2rem;">👑</span>
                <div>
                    <h2 style="margin: 0; font-size: 1.25rem; color: #d97706;">لوحة تحكم المدير العام</h2>
                    <span style="font-size: 0.75rem; color: #64748b;">إدارة كافة الجروبات المسجلة</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("خروج 🚪"):
        st.session_state.authenticated = False
        st.session_state.role = None
        st.session_state.user_name = None
        st.session_state.current_group = None
        st.rerun()
        
    st.markdown("---")
    st.subheader("📋 كافة الجروبات المسجلة بالنظام")
    if data["groups"]:
        g_list = [{"اسم الجروب": k, "رقم الموبايل": v["phone"], "الرمز (PIN)": v["pin"], "عدد السواق": len(v["drivers"])} for k, v in data["groups"].items()]
        st.dataframe(pd.DataFrame(g_list), use_container_width=True)
        
        sel_del_g = st.selectbox("اختر جروب للحذف:", ["اختر..."] + list(data["groups"].keys()))
        if sel_del_g != "اختر..." and st.button("🗑️ حذف هذا الجروب"):
            if len(data["groups"]) <= 1:
                st.error("لا يمكن حذف الجروب الوحيد المتبقي!")
            else:
                del data["groups"][sel_del_g]
                save_data(data)
                st.session_state["success_msg"] = "🗑️ تم حذف الجروب بنجاح!"
                st.rerun()
    st.stop()

current_g_name = st.session_state.current_group
group_data = data["groups"][current_g_name]

if "prices" not in group_data: group_data["prices"] = DEFAULT_PRICES
if "supervisors" not in group_data: group_data["supervisors"] = []
if "archives" not in group_data: group_data["archives"] = []

st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 5px 0 12px 0;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 2.2rem;">🚖</span>
            <div>
                <h2 style="margin: 0; font-size: 1.25rem; color: #d97706;">{current_g_name}</h2>
                <span style="font-size: 0.75rem; color: #64748b;">نظام متابعة الكروات والرزق</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

col_info1, col_info2 = st.columns([2, 1])
with col_info1:
    st.caption(f"المستخدم: **{st.session_state.user_name}**")
with col_info2:
    if st.button("خروج 🚪"):
        st.session_state.authenticated = False
        st.session_state.role = None
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
