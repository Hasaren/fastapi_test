# =============================================
# 07_multiselect_slider.py
# - 입력 위젯 (다중 선택 박스, 숫자 슬라이더 등)
# =============================================

import streamlit as st
from datetime import time

# 다중 선택 박스
st.title('Streamlit 입력 위젯 실습')
st.divider()

st.subheader('1. 다중 선택 박스 퀴즈')

fruits = st.multiselect('Q1. 과일을 모두 선택하세요. (복수 정답 가능):',
                        ['비행기','망고','수박','토마토','바나나'])

correct = {'망고','바나나'} # 세트 자료형 

if set(fruits) == correct:
    st.write('정답입니다.')
else:
    st.write('다시 선택해보세요.')

st.divider()

st.subheader('2. 숫자 슬라이더')

# 0부터 100까지 정수를 슬라이더로 입력 받는다.
score = st.slider('your score is...',0,100)
st.text(f'my score is {score}')

# 추가

if score >= 80:
    st.write('좋은 점수 입니다.')
elif score >=60:
    st.write('조금만 더 연습해 봅시다.')
else:
    st.write('기초부터 복습해 봅시다.')


st.divider()

st.subheader('3. 시간 범위 슬라이더')

start_time, end_time = st.slider(
    'Working time is ...',
    time(0),
    time(23),
    value=(time(9), time(18)),
    format='HH:mm'
)

st.text(f'Working time : {start_time} - {end_time}')

