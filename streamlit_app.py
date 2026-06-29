#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bedenimi Bul - Streamlit arayüzü.

Çalıştırma:
    pip install -r requirements.txt
    streamlit run streamlit_app.py
"""

from pathlib import Path

import streamlit as st

from bedenimi_bul import BODY_TYPES, WIDTH_LABEL, calculate


GENDER_LABELS = {"female": "Kadın", "male": "Erkek"}
GENDER_BY_LABEL = {label: key for key, label in GENDER_LABELS.items()}


st.set_page_config(page_title="Bedenimi Bul", page_icon="📏", layout="wide")

st.markdown(
    """
    <style>
      .main-title {font-size: clamp(34px, 5vw, 64px); font-weight: 850; letter-spacing: -0.05em; margin-bottom: 0.35rem;}
      .result-card {border: 1px solid #e2e8f0; border-radius: 24px; padding: 22px; background: white; box-shadow: 0 18px 40px rgba(15,23,42,.08); min-height: 210px;}
      .eyebrow {font-size: 13px; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: .04em;}
      .size {font-size: 48px; line-height: 1; font-weight: 900; letter-spacing: -.06em; margin: 10px 0;}
      .alt {font-size: 14px; color: #334155; font-weight: 600; margin-bottom: 10px;}
      .pill {display: inline-flex; padding: 6px 10px; border-radius: 999px; background: #ecfdf5; color: #047857; font-size: 12px; font-weight: 800; margin-bottom: 10px;}
      .muted {color: #64748b; font-size: 13px; line-height: 1.55;}
      .guide-card {border: 1px solid #e2e8f0; border-radius: 24px; padding: 18px; background: white; box-shadow: 0 18px 40px rgba(15,23,42,.06); margin-top: 18px;}
      .guide-title {font-size: 16px; font-weight: 850; color: #0f172a; margin-bottom: 8px;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">Bedenimi Bul</div>', unsafe_allow_html=True)

DEFAULT_STATE = {
    "gender": "female",
    "prev_gender": "female",
    "height": "166",
    "weight": "57",
    "body_type": "rectangle",
    "upper_build": "medium",
    "waist_build": "medium",
    "hip_build": "medium",
    "chest": "",
    "waist": "",
    "hip": "",
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value

left, right = st.columns([0.92, 1.55], gap="large")

with left:
    st.subheader("Temel bilgiler")
    selected_gender_label = st.segmented_control(
        "Cinsiyet",
        options=["Kadın", "Erkek"],
        default=GENDER_LABELS[st.session_state.gender],
        label_visibility="collapsed",
    )
    gender = GENDER_BY_LABEL[selected_gender_label]

    if gender != st.session_state.prev_gender:
        st.session_state.gender = gender
        st.session_state.prev_gender = gender
        st.session_state.height = "166" if gender == "female" else "178"
        st.session_state.weight = "57" if gender == "female" else "78"
        st.session_state.body_type = BODY_TYPES[gender][0]["key"]
        st.session_state.chest = ""
        st.session_state.waist = ""
        st.session_state.hip = ""
        st.rerun()

    col_h, col_w = st.columns(2)
    with col_h:
        height = st.text_input("Boy (cm)", key="height")
    with col_w:
        weight = st.text_input("Kilo (kg)", key="weight")

    st.markdown("### Vücut tipi")
    st.caption("En yakın vücut tipini seçin.")
    body_options = BODY_TYPES[gender]
    body_keys = [item["key"] for item in body_options]
    if st.session_state.body_type not in body_keys:
        st.session_state.body_type = body_keys[0]
    body_label_by_key = {item["key"]: item["label"] for item in body_options}
    body_type = st.radio(
        "Vücut tipi",
        options=body_keys,
        format_func=lambda key: body_label_by_key[key],
        horizontal=True,
        key="body_type",
        label_visibility="collapsed",
    )

    st.markdown("### Vücut yapısı")
    st.caption("Ölçü girmediğiniz durumda beden puanlamasını iyileştirmek için kullanılır.")
    width_keys = ["narrow", "medium", "wide"]

    st.markdown("**Göğüs / Üst yapı**")
    upper_build = st.radio(
        "Göğüs / Üst yapı",
        width_keys,
        format_func=lambda key: WIDTH_LABEL[key],
        horizontal=True,
        key="upper_build",
        label_visibility="collapsed",
    )

    st.markdown("**Bel genişliği**")
    waist_build = st.radio(
        "Bel genişliği",
        width_keys,
        format_func=lambda key: WIDTH_LABEL[key],
        horizontal=True,
        key="waist_build",
        label_visibility="collapsed",
    )

    if gender == "female":
        st.markdown("**Kalça / Basen genişliği**")
        hip_build = st.radio(
            "Kalça / Basen genişliği",
            width_keys,
            format_func=lambda key: WIDTH_LABEL[key],
            horizontal=True,
            key="hip_build",
            label_visibility="collapsed",
        )
    else:
        if "hip_build" not in st.session_state:
            st.session_state.hip_build = "medium"

        hip_build = st.session_state.hip_build
        st.session_state.hip = ""

    with st.expander("Opsiyonel mezura ölçüleri", expanded=True):
        st.caption("Girerseniz öneri daha güçlü şekilde bu ölçülere dayanır.")
        if gender == "female":
            c1, c2, c3 = st.columns(3)
            with c1:
                chest = st.text_input("Göğüs", placeholder="cm", key="chest")
            with c2:
                waist = st.text_input("Bel", placeholder="cm", key="waist")
            with c3:
                hip = st.text_input("Basen", placeholder="cm", key="hip")
        else:
            c1, c2 = st.columns(2)
            with c1:
                chest = st.text_input("Göğüs", placeholder="cm", key="chest")
            with c2:
                waist = st.text_input("Bel", placeholder="cm", key="waist")
            hip = ""

result = calculate(
    gender=gender,
    height=height,
    weight=weight,
    body_type=body_type,
    upper_build=upper_build,
    waist_build=waist_build,
    hip_build=hip_build,
    chest=chest,
    waist=waist,
    hip=hip,
    include_debug=False,
)

with right:
    r1, r2 = st.columns(2)
    with r1:
        st.markdown(
            f"""
            <div class="result-card">
              <div class="eyebrow">Üst beden önerisi</div>
              <div class="size">{result['topMain']}</div>
              <div class="alt">{result['topAlt']}</div>
              <div class="pill">{result['topConfidence']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with r2:
        st.markdown(
            f"""
            <div class="result-card">
              <div class="eyebrow">Alt beden önerisi</div>
              <div class="size">{result['bottomMain']}</div>
              <div class="alt">{result['bottomAlt']}</div>
              <div class="pill">{result['bottomConfidence']}</div>
            </div>
            """,
            unsafe_allow_html=True, 
        )

    bodytype_image = Path(__file__).with_name("bodytype.png")
    if bodytype_image.exists():
        st.markdown(
            '<div class="guide-card"><div class="guide-title">Vücut tipi kılavuzu</div>',
            unsafe_allow_html=True,
        )
        st.image(str(bodytype_image), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Vücut tipi kılavuzu görseli bulunamadı. Lütfen bodytype.png dosyasını uygulama dosyasıyla aynı klasöre ekleyin.")

    st.caption("Bu demo, beden öneri akışını test etmek için hazırlanmıştır.")
