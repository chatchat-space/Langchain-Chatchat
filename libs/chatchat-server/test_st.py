import streamlit as st


st.session_state.setdefault("input1", "input 1")
st.session_state.setdefault("input2", "input 2")
st.session_state.setdefault("input3", "input 3")

st.write(st.session_state)

# with st.sidebar:
st.text_input("input 1", key="input1")
select = st.selectbox("select", ["A", "B"])

if select == "A":
    st.text_input("input 2", key="input2")
else:
    st.text_input("input 3", key="input3")
