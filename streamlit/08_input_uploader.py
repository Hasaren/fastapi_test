# ===============================
#  - 입력 위젯 (텍스트 입력, 파일 업로더 등)
# ===============================

import streamlit as st
import pandas as pd

string1 = st.text_input(
    '좋아하는 포켓몬은??',
    placeholder='피카츄',
    max_chars=32
)

if string1:
    st.text(f'Your starting poketmon is {string1}')

# 2. 비밀번호 입력 : 싫어하는 음식 받기 (입력 내용을 숨긴다.)
string2 = st.text_input(
    '싫어하는 음식은?',
    placeholder='싫어하는 음식을 작성',
    max_chars=32,
    type='password'
)

if string2:
    st.text(f'Your answer is {string2}')

st.divider()
# 3. 파일 업로더 : csv 파일만 업로드 가능하게

file = st.file_uploader(
    'Choose a file',
    type='csv',
    accept_multiple_files=False #파일 여러개 선택 불가(false)
)

if file is not None:
    df = pd.read_csv(file)
    st.write(df)