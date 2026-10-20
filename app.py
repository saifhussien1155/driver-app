import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="كابتن الجروب 🚖 | المنصة المستقلة للرزق والموافقات",
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
                "group_code": "12345",  # رمز دخول الأعضاء للجروب
                "drivers": [],
                "trips": [],             # الكروات المقبولة رسمياً
                "pending_trips": [],     # الكروات بانتظار موافقة المشرف
                "supervisors": [],
                "prices": DEFAULT_PRICES,
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

# ---------------- 🔒 شاشة تسجيل الدخول أو حساب جديد ----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_name = None
    st.session_state.current_group = None
    st.session_state.role_type = None
    st.session_state.user_score = 0
    st.session_state.user_img = "👤"

if not st.session_state.authenticated:
    st.markdown("""
        <div style="text-align: center; padding: 15px 0 10px 0;">
            <div style="font-size: 3.8rem; line-height: 1;">🚖</div>
            <h2 style="color: #d97706; margin-top: 8px; font-weight: 800;">كابتن الجروب</h2>
            <p style="color: #64748b; font-size: 0.9rem;">منصة إدارة الكروات والرزق الموثقة بالأكواد والموافقات</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab_auth1, tab_auth2, tab_auth3 = st.tabs(["🔑 تسجيل الدخول", "✨ إنشاء جروب جديد أو انضمام", "🔄 استعادة الرمز"])
    
    # 1. تسجيل الدخول
    with tab_auth1:
        with st.form("login_form"):
            st.markdown("##### تسجيل الدخول (مسؤول، مشرف، أو عضو)")
            l_phone = st.text_input("📞 رقم الموبايل:")
            l_pin = st.text_input("🔑 الرمز السري (PIN):", type="password")
            sub_l = st.form_submit_button("دخول للنظام 🚀", type="primary")
            
            if sub_l:
                l_phone = l_phone.strip()
                l_pin = l_pin.strip()
                found_g = None
                found_user = None
                role_type = "admin"
                score = 0
                
                for g_name, g_info in data["groups"].items():
                    if str(g_info.get("phone")) == l_phone and str(g_info.get("pin")) == l_pin:
                        found_g = g_name
                        found_user = f"مسؤول {g_name}"
                        role_type = "admin"
                        break
                    for sup in g_info.get("supervisors", []):
                        if str(sup.get("phone")) == l_phone and str(sup.get("pin")) == l_pin:
                            if not sup.get("frozen", False):
                                found_g = g_name
                                found_user = sup["name"]
                                role_type = "supervisor"
                            break
                    for drv in g_info.get("drivers", []):
                        if str(drv.get("phone")) == l_phone and str(drv.get("pin", "")) == l_pin:
                            if not drv.get("frozen", False):
                                found_g = g_name
                                found_user = drv["name"]
                                role_type = "driver"
                                score = drv.get("score", 0)
                            break
                    if found_g: break
                        
                if found_g:
                    st.session_state.authenticated = True
                    st.session_state.user_name = found_user
                    st.session_state.current_group = found_g
                    st.session_state.role_type = role_type
                    st.session_state.user_score = score
                    st.success(f"✅ أهلاً بك ({found_user}) في جروب: {found_g}")
                    st.rerun()
                else:
                    st.error("❌ رقم الموبايل أو الرمز السري غير صحيح!")

    # 2. إنشاء جروب أو الانضمام كعضو برمز الجروب
    with tab_auth2:
        reg_mode = st.radio("اختر نوع الحساب:", ["تأسيس جروب جديد (مسؤول)", "انضمام لعضو/سائق بـ رمز الجروب"])
        
        if reg_mode == "تأسيس جروب جديد (مسؤول)":
            with st.form("new_group_form"):
                st.markdown("##### تأسيس جروب مستقل جديد")
                rg_name = st.text_input("اسم الجروب (مثلاً: جروب المنصور):")
                rg_phone = st.text_input("رقم موبايل المسؤول:")
                rg_pin = st.text_input("الرمز السري (PIN) للمسؤول:", type="password")
                rg_code = st.text_input("رمز انضمام الأعضاء الخاص بالجروب (مثلاً: 9988):")
                sub_rg = st.form_submit_button("تأسيس الجروب الان 🚀", type="primary")
                
                if sub_rg:
                    if not rg_name.strip() or not rg_phone.strip() or len(rg_pin.strip()) < 4 or not rg_code.strip():
                        st.error("يرجى ملء كافة الحقول وتأمين رمز سري لا يقل عن 4 أرقام!")
                    elif rg_name in data["groups"]:
                        st.error("اسم الجروب مستخدم مسبقاً!")
                    else:
                        data["groups"][rg_name] = {
                            "phone": rg_phone.strip(),
                            "pin": rg_pin.strip(),
                            "group_code": rg_code.strip(),
                            "drivers": [],
                            "trips": [],
                            "pending_trips": [],
                            "supervisors": [],
                            "prices": DEFAULT_PRICES,
                            "chat": []
                        }
                        save_data(data)
                        st.session_state.authenticated = True
                        st.session_state.user_name = f"مسؤول {rg_name}"
                        st.session_state.current_group = rg_name
                        st.session_state.role_type = "admin"
                        st.session_state["success_msg"] = "🎉 تم تأسيس الجروب بنجاح!"
                        st.rerun()
        else:
            with st.form("join_member_form"):
                st.markdown("##### انضمام عضو جديد للجروب")
                jn_gname = st.selectbox("اختر اسم الجروب المراد الانضمام إليه:", list(data["groups"].keys()))
                jn_code = st.text_input("رمز انضمام الجروب السري (يطلب من المسؤول):")
                jn_name = st.text_input("اسمك الكامل:")
                jn_phone = st.text_input("رقم هاتفك:")
                jn_pin = st.text_input("اختر رمزاً سرياً خاص بك (PIN):", type="password")
                jn_car = st.text_input("نوع السيارة (اختياري):")
                sub_jn = st.form_submit_button("طلب انضمام لعضوية الجروب ➕", type="primary")
                
                if sub_jn:
                    g_info = data["groups"].get(jn_gname)
                    if jn_code.strip() != str(g_info.get("group_code")):
                        st.error("❌ رمز انضمام الجروب غير صحيح!")
                    elif not jn_name.strip() or not jn_phone.strip() or len(jn_pin.strip()) < 4:
                        st.error("يرجى ملء الحقول وتأمين رمز سري لا يقل عن 4 أرقام!")
                    else:
                        g_info["drivers"].append({
                            "name": jn_name.strip(),
                            "phone": jn_phone.strip(),
                            "pin": jn_pin.strip(),
                            "car": jn_car.strip(),
                            "score": 0,
                            "frozen": False
                        })
                        save_data(data)
                        st.session_state.authenticated = True
                        st.session_state.user_name = jn_name.strip()
                        st.session_state.current_group = jn_gname
                        st.session_state.role_type = "driver"
                        st.session_state.user_score = 0
                        st.session_state["success_msg"] = "🎉 تم التسجيل والانضمام بنجاح!"
                        st.rerun()

    # 3. استعادة الرمز
    with tab_auth3:
        st.markdown("##### 🔄 استعادة الرمز السري")
        with st.form("rec_form"):
            r_ph = st.text_input("رقم هاتفك المسجل:")
            if st.form_submit_button("إرسال رمز التحقق"):
                st.info("تم إرسال رمز التحقق الوهمي (الرمز العام لحسابك هو نفسه أو راجع المسؤول).")
    st.stop()

# ---------------- لوحة تحكم التطبيق المستقل ----------------

current_g_name = st.session_state.current_group
group_data = data["groups"][current_g_name]
user_role = st.session_state.get("role_type", "admin")

if "pending_trips" not in group_data: group_data["pending_trips"] = []
if "group_code" not in group_data: group_data["group_code"] = "12345"

st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 5px 0 12px 0;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 2.2rem;">🚖</span>
            <div>
                <h2 style="margin: 0; font-size: 1.25rem; color: #d97706;">{current_g_name}</h2>
                <span style="font-size: 0.75rem; color: #64748b;">رمز انضمام الجروب: <b>{group_data['group_code']}</b></span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

col_info1, col_info2 = st.columns([2, 1])
with col_info1:
    st.caption(f"المستخدم: **{st.session_state.user_name}** | الصلاحية: **{user_role}**")
with col_info2:
    if st.button("خروج 🚪"):
        st.session_state.authenticated = False
        st.session_state.user_name = None
        st.session_state.current_group = None
        st.rerun()

# تخصيص التبويبات حسب الصلاحية
if user_role == "driver":
    tabs = st.tabs(["👤 صفحتي الشخصية", "📝 تسجيل رزق (بانتظار الموافقة)", "💬 محادثة الجروب"])
    tab1, tab2, tab3 = tabs[0], tabs[1], tabs[2]
    
    # 1. الصفحة الشخصية للعضو
    with tab1:
        st.subheader("👤 ملفي الشخصي وقوة الحساب")
        drv_obj = next((d for d in group_data["drivers"] if d["name"] == st.session_state.user_name), {})
        st.markdown(f"""
            <div style="background: white; padding: 20px; border-radius: 14px; border: 1px solid #e2e8f0; text-align: center;">
                <div style="font-size: 4rem;">🧑‍✈️</div>
                <h3 style="color: #0f172a; margin: 5px 0;">{st.session_state.user_name}</h3>
                <p style="color: #64748b;">رقم الهاتف: {drv_obj.get('phone', 'غير متوفر')}</p>
                <p style="color: #64748b;">نوع السيارة: {drv_obj.get('car', 'غير محدد')}</p>
                <hr style="border: 0; border-top: 1px solid #e2e8f0;">
                <h4 style="color: #d97706;">⭐ قوة الحساب والرزق المسجل: {drv_obj.get('score', 0)} نقطة</h4>
            </div>
        """, unsafe_allow_html=True)

    # 2. تسجيل رزق (يرسل للمشرف للموافقة)
    with tab2:
        st.subheader("📝 تسجيل طلب / رزق جديد (يخضع لموافقة المشرف)")
        active_drivers = [d["name"] for d in group_data["drivers"] if not d.get("frozen", False)]
        if not active_drivers:
            st.warning("لا يوجد سواق نشطون.")
        else:
            with st.form("drv_pend_form", clear_on_submit=True):
                giver = st.selectbox("السائق المعطي:", active_drivers)
                receiver = st.selectbox("السائق المستلم:", active_drivers, index=min(1, len(active_drivers)-1))
                resq_type = st.selectbox("نوع الكروة:", list(group_data["prices"].keys()))
                trip_price = st.number_input("السعر (د.ع):", value=int(group_data["prices"].get(resq_type, 0)), step=500)
                notes = st.text_input("ملاحظات / رابط موقع الخريطة:")
                
                if st.form_submit_button("📤 إرسال طلب الرزق للمشرف للموافقة", type="primary"):
                    if giver == receiver:
                        st.error("⚠️ المعطي والمستلم لا يمكن أن يكونا نفس الشخص!")
                    else:
                        group_data["pending_trips"].append({
                            "id": len(group_data["pending_trips"]) + len(group_data["trips"]) + 1,
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "giver": giver,
                            "receiver": receiver,
                            "type": resq_type,
                            "price": float(trip_price),
                            "notes": notes,
                            "added_by": st.session_state.user_name
                        })
                        save_data(data)
                        st.session_state["success_msg"] = "✅ تم إرسال الطلب بنجاح وهو بانتظار موافقة المشرف!"
                        st.rerun()

    # 3. محادثة الجروب
    with tab3:
        st.subheader("💬 محادثة الجروب")
        c_box = st.container(height=300)
        with c_box:
            for msg in group_data["chat"]:
                st.markdown(f"**💬 {msg['sender']}** ({msg['time']}):<br>{msg['text']}", unsafe_allow_html=True)
                st.markdown("---")
        with st.form("drv_chat_f", clear_on_submit=True):
            txt = st.text_input("اكتب رسالة:")
            if st.form_submit_button("إرسال 📨", type="primary") and txt.strip():
                group_data["chat"].append({
                    "sender": st.session_state.user_name,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "text": txt.strip()
                })
                save_data(data)
                st.rerun()

else:
    # 👑 واجهة المسؤول أو المشرف (مع صلاحية قبول/حذف الطلبات وإدارة الأعضاء)
    tabs = st.tabs(["👑 الموافقات المعلقة ⏳", "📝 تسجيل رزق مباشر", "🚘 الأعضاء والملفات", "📋 سجل الكروات", "📊 الميزان والمالية", "💬 المحادثة"])
    tab1, tab2, tab3, tab4, tab5, tab6 = tabs[0], tabs[1], tabs[2], tabs[3], tabs[4], tabs[5]

    # 1. الموافقات المعلقة
    with tab1:
        st.subheader("⏳ طلبات الرزق المعلقة بانتظار موافقتك")
        if group_data["pending_trips"]:
            for pt in group_data["pending_trips"]:
                with st.expander(f"طلب رقم #{pt['id']} | بواسطة: {pt['added_by']} | المعطي: {pt['giver']} ⬅️ المستلم: {pt['receiver']} ({pt['price']} د.ع)"):
                    st.text(f"النوع: {pt['type']} | الوقت: {pt['time']} | ملاحظات: {pt['notes']}")
                    c_app, c_rej = st.columns(2)
                    with c_app:
                        if st.button(f"✅ قبول الطلب", key=f"app_{pt['id']}"):
                            # نقل الطلب للسجل الرسمي وزيادة نقاط صاحب الطلب
                            group_data["trips"].append(pt)
                            for d in group_data["drivers"]:
                                if d["name"] == pt["added_by"]:
                                    d["score"] = d.get("score", 0) + 10  # زيادة القوة والحساب
                            group_data["pending_trips"] = [x for x in group_data["pending_trips"] if x["id"] != pt["id"]]
                            save_data(data)
                            st.session_state["success_msg"] = "✅ تم قبول الطلب وزيادة قوة حساب العضو بنجاح!"
                            st.rerun()
                    with c_rej:
                        if st.button(f"❌ حذف / رفض الطلب", key=f"rej_{pt['id']}"):
                            group_data["pending_trips"] = [x for x in group_data["pending_trips"] if x["id"] != pt["id"]]
                            save_data(data)
                            st.session_state["success_msg"] = "🗑️ تم رفض وحذف الطلب!"
                            st.rerun()
        else:
            st.info("لا توجد طلبات معلقة بانتظار الموافقة حالياً.")

    # 2. تسجيل رزق مباشر
    with tab2:
        st.subheader("📝 تسجيل رزق مباشر (بصفتك مشرف/مسؤول)")
        active_drivers = [d["name"] for d in group_data["drivers"] if not d.get("frozen", False)]
        if not active_drivers:
            st.warning("يرجى إضافة سواق نشطون أولاً.")
        else:
            with st.form("adm_add_trip", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1: giver = st.selectbox("المعطي:", active_drivers, key="ag")
                with c2: receiver = st.selectbox("المستلم:", active_drivers, key="ar")
                resq_type = st.selectbox("نوع الكروة:", list(group_data["prices"].keys()))
                trip_price = st.number_input("السعر (د.ع):", value=int(group_data["prices"].get(resq_type, 0)), step=500)
                notes = st.text_input("ملاحظات:")
                
                if st.form_submit_button("➕ تسجيل فوري", type="primary"):
                    if giver == receiver:
                        st.error("⚠️ المعطي والمستلم نفس الشخص!")
                    else:
                        group_data["trips"].append({
                            "id": len(group_data["trips"]) + 1,
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "giver": giver, "receiver": receiver, "type": resq_type,
                            "price": float(trip_price), "notes": notes, "added_by": st.session_state.user_name
                        })
                        save_data(data)
                        st.session_state["success_msg"] = "✅ تم التسجيل بنجاح!"
                        st.rerun()

    # 3. الأعضاء والملفات وقوتهم
    with tab3:
        st.subheader("🚘 أعضاء الجروب وصفحاتهم وقوة حساباتهم")
        if group_data["drivers"]:
            df_d = pd.DataFrame(group_data["drivers"])
            df_d["الحالة"] = df_d["frozen"].apply(lambda x: "🧊 مجمد" if x else "✅ نشط")
            st.dataframe(df_d[["name", "الحالة", "score", "phone", "car"]].rename(columns={"name": "الاسم", "score": "نقاط القوة", "phone": "الهاتف", "car": "السيارة"}), use_container_width=True)
            
            sel_d = st.selectbox("اختر عضواً لإدارة حالته:", [d["name"] for d in group_data["drivers"]])
            d_obj = next((d for d in group_data["drivers"] if d["name"] == sel_d), None)
            if d_obj and st.button("🧊 تجميد / فك تجميد العضو"):
                d_obj["frozen"] = not d_obj.get("frozen", False)
                save_data(data)
                st.rerun()
        else:
            st.info("لا توجد أعضاء مسجلين برمز الجروب حتى الآن.")

    # 4. سجل الكروات
    with tab4:
        st.subheader("📜 سجل الكروات المقبولة رسمياً")
        if group_data["trips"]:
            st.dataframe(pd.DataFrame(group_data["trips"]), use_container_width=True)
            sel_t = st.selectbox("رقم الكروة للحذف:", [t["id"] for t in group_data["trips"]])
            if st.button("حذف الكروة المحددة"):
                group_data["trips"] = [t for t in group_data["trips"] if t["id"] != sel_t]
                save_data(data)
                st.rerun()
        else:
            st.info("لا توجد كروات مقبولة.")

    # 5. الميزان والمالية
    with tab5:
        st.subheader("📊 ميزان العدالة وحسابات الفلوس")
        if group_data["drivers"]:
            balances = {d["name"]: {"given": 0, "received": 0, "g_money": 0.0, "r_money": 0.0} for d in group_data["drivers"]}
            for t in group_data["trips"]:
                p = float(t.get("price", 0))
                if t.get("giver") in balances:
                    balances[t["giver"]]["given"] += 1
                    balances[t["giver"]]["g_money"] += p
                if t.get("receiver") in balances:
                    balances[t["receiver"]]["received"] += 1
                    balances[t["receiver"]]["r_money"] += p
            
            summary = []
            for d in group_data["drivers"]:
                b = balances[d["name"]]
                summary.append({
                    "السائق": d["name"],
                    "أنطى": b["given"], "أخذ": b["received"],
                    "الصافي (كروات)": b["given"] - b["received"],
                    "الصافي المالي (د.ع)": f"{(b['g_money'] - b['r_money']):,}"
                })
            df_sum = pd.DataFrame(summary)
            st.dataframe(df_sum, use_container_width=True)
            st.download_button("📥 تحميل الميزان (Excel)", df_sum.to_csv(index=False, encoding='utf-8-sig'), "ميزان.csv", "text/csv")
        else:
            st.info("لا توجد بيانات لعرض الميزان.")

    # 6. المحادثة
    with tab6:
        st.subheader("💬 محادثة الجروب")
        c_box = st.container(height=300)
        with c_box:
            for msg in group_data["chat"]:
                st.markdown(f"**💬 {msg['sender']}** ({msg['time']}):<br>{msg['text']}", unsafe_allow_html=True)
                st.markdown("---")
        with st.form("adm_chat", clear_on_submit=True):
            txt_msg = st.text_input("اكتب رسالة:")
            if st.form_submit_button("إرسال 📨", type="primary") and txt_msg.strip():
                group_data["chat"].append({
                    "sender": st.session_state.user_name,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "text": txt_msg.strip()
                })
                save_data(data)
                st.rerun()
