import streamlit as st
from main import app

st.title("AI Travel Planning System")

user_input = st.text_input("Enter your travel request")

if st.button("Plan Trip"):
    if user_input:
        result = app.invoke({
            "messages": [],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0
        })
        st.write(result)
