# from openai import OpenAI
import streamlit as st
from common.bielik_api import call_model
from common.prompt_generation import create_prompt


st.title("RAG Project")

# Add input for number of context files
context_files = st.number_input(
    "Wybierz liczbę batchy",
    min_value=1,
    max_value=10,
    value=5,
    step=1,
    help="Wybierz liczbę plików kontekstowych (1-10)"
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
            system_prompt, user_prompt = create_prompt(user_prompt=prompt, context_files=context_files)
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
