# ==========================
# 폼 위젯 : 입력값 검증
# 
# 여러 입력을 한번에 제출할 수 있다.
# 폼 제출시 입력값을 검증하고 처리하기 편하다.
# 블록 안의 위젯들은 값이 바뀌어도 즉시 재실행되지 않고, "제출 버튼"을
# 누르는 순간에만 한번에 재실행된다. --> 성능 사용성을 모두 개선
# ==========================

import streamlit as st

st.title('회원 가입 (검증포함)')

# 'signup_form': 폼 이름은 폼을 구분하는 고유한 이름(key), 폼이 여러개면 서로 다른 이름을 주어야 한다.
with st.form('signup_form_v2'):
    name= st.text_input('이름')
    email = st.text_input('이메일')
    age = st.number_input('나이', min_value=0, max_value=120, value=20) # 기본값 20
    agree = st.checkbox('이용약관에 동의합니다.')

    # 일반 버튼 위젯이 아니고 form 안에서만 쓸 수 있는 버튼 위젯을 사용해야 한다.
    submited = st.form_submit_button('가입하기')

# 가입 버튼을 누르면 -> 폼 제출 시점의 최종값을 그대로 가지고 있다. (with밖에서 해도 된다.)
if submited:
    if not name:
        st.error('이름을 입력해주세요')
    elif '@' not in email:
        st.error('유효한 이메일 주소가 아닙니다.')
    elif not agree:
        st.error('이용약관에 동의해야 가입할 수 있습니다.')
    else:
        st.success(f'{name}님, 가입이 완료되었습니다. (이메일: {email}, 나이:{age})')

