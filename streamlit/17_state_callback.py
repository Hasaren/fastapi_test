# =====================================
# sesstion state
#   - 위젯을 조작할 때마다 일반 파이썬 변수가 초기화 되는 문제를 해결한다.
#   - st.sesstion_state로 재실행 사이의 값을 유지할 수있다.
#   - 콜백 함수와 함께 사용할 수있다.
# =====================================
import streamlit as st

st.title('카운터 (sesstion_state 적용)')

# st.sesstion_state : 브라우저 탭 (세션) 하나에 묶어서 재실행되어도 값이 사라지지 않는
#                     딕셔너리 형태의 특수 저장소
if 'count' not in st.session_state:
    st.session_state.count = 0

def increment():
    """콜백 함수 : 위젯 클릭 시 화면이 다시 그려지기 직전에 자동으로 호출되는 함수"""
    st.session_state.count += 1

def decrement():
    st.session_state.count -= 1

def reset():
    st.session_state.count = 0

col1, col2, col3 = st.columns(3)

with col1:
    st.button('+1', on_click=increment)

with col2:
    st.button('-1', on_click=decrement)

with col3:
    st.button('reset', on_click=reset)

# st.metric : 카드형태로 보여주는 위젯
st.metric('현재 값', st.session_state.count)
# st.write(f'현재 카운트: {st.session_state.count}')