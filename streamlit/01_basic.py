# ------------------------
#   Streamlit 라이브러리 기초 실습
#   Streamlit??
#       - 파이썬 코드만으로 웹페이지를 쉽게 만들 수 있도록 도와주는 라이브러리
#       - 위젯 단위(버튼 클릭, 슬라이더 이동, 제목 등)
# ------------------------
import streamlit as st

st.title('first dashboard')
st.write("파이썬 코드가 웹사이트가 되었습니다!")

st.title('_이탤릭체 제목_ : :blue[파랑색] 그리고 선글라스 이모지 :sunglasses:')

st.header("This is header")
st.header("_이탤릭체 헤더_ : :red[빨강색] 그리고 선글라스 이모지 :sunglasses:")

st.subheader('This is sub-header')
st.subheader('_이탤릭체 서브헤더_ : :green[초록색] 그리고 선글라스 이모지 :sunglasses:')

# text
st.text('이것은 텍스트입니다.')

# divider
st.divider()

st.write('---')