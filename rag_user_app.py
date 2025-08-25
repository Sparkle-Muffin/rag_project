# from openai import OpenAI
import streamlit as st
from common.bielik_api import call_model
from common.prompt_generation import create_prompt


st.title("RAG Project")

# Add input for number of context files in the sidebar
with st.sidebar:
    st.header("Ustawienia")
    db_chunks_number = st.number_input(
        "Liczba chunków pobieranych z bazy danych",
        min_value=1,
        max_value=100,
        value=50,
        step=1,
        help="Wybierz liczbę chunków pobieranych z bazy danych (1-100)"
    )
    model_context_chunks_number = st.number_input(
        "Liczba chunków przekazywanych do modelu",
        min_value=1,
        max_value=10,
        value=5,
        step=1,
        help="Wybierz liczbę chunków przekazywanych do modelu (1-10)"
    )


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Zadaj pytanie:"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Create a placeholder for streaming
        message_placeholder = st.empty()
        full_response = ""
        
        # Show that we're waiting for the model
        message_placeholder.markdown("🤔 Myślę...")
        
        try:
            # Stream the response
            system_prompt, user_prompt = create_prompt(user_prompt=prompt, 
                                                       db_chunks_number=db_chunks_number, 
                                                       model_context_chunks_number=model_context_chunks_number)
            
            print(system_prompt)
            print(user_prompt)
            
            for chunk in call_model(system_prompt, user_prompt):
                if chunk:
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
            
            # Show the final response
            message_placeholder.markdown(full_response)
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            message_placeholder.markdown(error_msg)
            st.error(f"Exception occurred: {e}")
            full_response = error_msg
        
    # Store the complete response in session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})
