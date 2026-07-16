import streamlit as st

# code
code='print("hello python")'
code1='printf("hello python")'
code2='<a href=#>네이버</a>'

st.code(code, language='python')
st.code(code1, language='java')
st.code(code2, language='html')

# button
def button_write():
    st.write('button activated')

st.button('Reset', type='primary')
st.button('activate', on_click=button_write)

if st.button('Reset', type='primary', key='btn1'):
    st.write("Reset clicked")

if st.button('Cancel', type='secondary', key='btn2'):
    st.write("Cancel clicked!")

if st.button('Ignore', type='tertiary', key='btn3'):
    st.write("Ignore clicked!")