import pandas as pd
import streamlit as st
import datetime

st.set_page_config(page_title="Doc Karate - ACWR Tracker", page_icon="🥋", layout="wide")

st.title("🥋 Doc Karate - Athlete Workload & ACWR System")
st.markdown("نظام تخصيص ومتابعة الأحمال التدريبية الحادة والمزمنة (Acute:Chronic Workload Ratio)")

# Sidebar for data input
st.sidebar.header("➕ إضافة سجل تدريب جديد")
input_date = st.sidebar.date_input("التاريخ", datetime.date.today())

st.sidebar.subheader("التدريب الأساسي (Sport)")
sport_train = st.sidebar.number_input("مدة التدريب الأساسي (دقائق)", min_value=0.0, value=90.0, step=10.0)
sport_load = st.sidebar.number_input("معدل الشدة RPE (1-10)", min_value=0.0, max_value=10.0, value=8.0, step=0.5)

st.sidebar.subheader("تدريب اللياقة البدنية (Fitness)")
fitness_train = st.sidebar.number_input("مدة تدريب اللياقة (دقائق)", min_value=0.0, value=0.0, step=10.0)
fitness_load = st.sidebar.number_input("معدل الشدة RPE (1-10)", min_value=0.0, max_value=10.0, value=0.0, step=0.5)

# Initialize session state for database
if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame(columns=[
        'التاريخ', 'Sport training', 'Sport load', 'Fitness training', 'fitness load', 'Daily load', 'Acute load', 'chronic load', 'ACWR'
    ])

if st.sidebar.button("حساب وإضافة السجل"):
    daily_load = (sport_train * sport_load) + (fitness_train * fitness_load)
    
    new_row = {
        'التاريخ': pd.to_datetime(input_date),
        'Sport training': sport_train,
        'Sport load': sport_load,
        'Fitness training': fitness_train,
        'fitness load': fitness_load,
        'Daily load': daily_load,
        'Acute load': 0.0,
        'chronic load': 0.0,
        'ACWR': 0.0
    }
    
    st.session_state['data'] = pd.concat([st.session_state['data'], pd.DataFrame([new_row])], ignore_index=True)
    
    # Recalculate ACWR metrics
    df = st.session_state['data'].sort_values('التاريخ').reset_index(drop=True)
    df['Acute load'] = df['Daily load'].rolling(window=7, min_periods=1).mean()
    df['chronic load'] = df['Daily load'].rolling(window=28, min_periods=1).mean()
    df['ACWR'] = df['Acute load'] / df['chronic load']
    df['ACWR'] = df['ACWR'].fillna(0)
    st.session_state['data'] = df
    st.success("تمت إضافة السجل وحساب المؤشرات بنجاح!")

# Main Dashboard View
st.subheader("📊 لوحة متابعة الأحمال (Dashboard)")

if not st.session_state['data'].empty:
    current_df = st.session_state['data']
    
    # Display table with formatting
    st.dataframe(current_df.style.format({
        'Daily load': '{:.1f}',
        'Acute load': '{:.2f}',
        'chronic load': '{:.2f}',
        'ACWR': '{:.3f}'
    }), use_container_width=True)
    
    # Charts
    st.subheader("📈 منحنى الحمل التدريبي والنسبة")
    st.line_chart(current_df.set_index('التاريخ')[['Acute load', 'chronic load']])
    
    st.subheader("📉 مؤشر الـ ACWR")
    st.line_chart(current_df.set_index('التاريخ')['ACWR'])
else:
    st.info("لا توجد بيانات مسجلة حتى الآن. استخدم الشريط الجانبي لإدخال أول سجل تدريبي.")
