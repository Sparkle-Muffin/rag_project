import streamlit as st
from common.bielik_api import call_model_stream, call_model_non_stream
from common.prompt_generation import create_prompt_with_history
import json
from datetime import datetime

# Initialize session state early to avoid KeyError
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_start" not in st.session_state:
    st.session_state.session_start = datetime.now().strftime("%Y%m%d_%H%M%S")

# Load the system prompts
with open("common/prompts/rag_system_prompt.txt", "r") as f:
    rag_system_prompt = f.read()

with open("common/prompts/normal_chat_system_prompt.txt", "r") as f:
    normal_chat_system_prompt = f.read()

with open("common/prompts/expansion_system_prompt.txt", "r") as f:
    expansion_system_prompt = f.read()


# # RAG Project - Interactive Chat Interface
# 
# This Streamlit application provides an interactive interface for the RAG (Retrieval-Augmented Generation) system.
# Users can ask questions and receive answers based on the knowledge base, with configurable retrieval parameters.
# 
# ## Features:
# - Interactive chat interface with streaming responses
# - Configurable database chunk retrieval (1-100 chunks)
# - Adjustable model context size (1-50 chunks)
# - Real-time streaming of model responses
# - Persistent chat history within the session
# - Toggle between RAG mode and normal chat mode
# - Query/Prompt Expansion for improved search results
# - Chat memory functionality for context-aware conversations
# 
# ## How it works:
# 1. User inputs a question in the chat interface
# 2. System retrieves relevant document chunks using hybrid search (vector + BM25) [RAG mode only]
# 3. Retrieved context is combined with the system prompt and conversation history [RAG mode only]
# 4. Bielik model generates a response using the enhanced context and chat memory
# 5. Response is streamed back to the user in real-time

st.title("RAG Project")

# Add mode switch in the sidebar
with st.sidebar:
    st.header("Tryb pracy")
    chat_mode = st.radio(
        "Wybierz tryb:",
        ["Tryb RAG", "Tryb zwykłego chatu"],
        index=0,
        help="Tryb RAG: używa bazy wiedzy do generowania odpowiedzi\nTryb zwykłego chatu: odpowiada bez kontekstu z bazy"
    )
    
    # Settings section - grayed out in normal chat mode
    st.header("Ustawienia")
    
    if chat_mode == "Tryb RAG":
        # Enable settings in RAG mode
        db_chunks_number = st.number_input(
            "Liczba chunków pobieranych z bazy danych",
            min_value=1,
            max_value=100,
            value=20,
            step=1,
            help="Wybierz liczbę chunków pobieranych z bazy danych (1-100)"
        )
        model_context_chunks_number = st.number_input(
            "Liczba chunków przekazywanych do modelu",
            min_value=1,
            max_value=50,
            value=10,
            step=1,
            help="Wybierz liczbę chunków przekazywanych do modelu (1-10)"
        )
        
        # Query expansion switch
        st.subheader("Rozszerzanie zapytań")
        use_query_expansion = st.checkbox(
            "Użyj rozszerzania zapytań",
            value=False,
            help="Rozszerza pytanie użytkownika przed wyszukiwaniem w bazie danych dla lepszych wyników"
        )
        
        if use_query_expansion:
            st.info("🔍 Zapytanie zostanie rozszerzone przed wyszukiwaniem w bazie")
    else:
        # Disable settings in normal chat mode
        st.info("Ustawienia są dostępne tylko w trybie RAG")
        db_chunks_number = None  # No context retrieval in normal chat mode
        model_context_chunks_number = None  # No context in normal chat mode
        use_query_expansion = False  # Default value
    
    # Chat memory management
    st.header("Zarządzanie czatem")
    
    # Memory length control
    max_memory_length = st.number_input(
        "Maksymalna długość pamięci czatu",
        min_value=1,
        max_value=50,
        value=10,
        step=1,
        help="Liczba ostatnich wiadomości zachowanych w pamięci (1-50)"
    )
    
    # Clear chat button
    if st.button("🗑️ Wyczyść historię czatu", type="secondary"):
        st.session_state.messages = []
        st.rerun()
    
    # Show current memory status
    if "messages" in st.session_state:
        current_memory_length = len(st.session_state.messages)
        st.info(f"📝 Aktualna długość pamięci: {current_memory_length}/{max_memory_length}")
        
        if current_memory_length > max_memory_length:
            st.warning("⚠️ Pamięć czatu przekroczyła limit! Najstarsze wiadomości zostaną usunięte.")
    
    # Show conversation history in sidebar (collapsible)
    if st.session_state.messages:
        with st.expander("📚 Historia rozmowy", expanded=False):
            for i, message in enumerate(st.session_state.messages):
                role_icon = "👤" if message["role"] == "user" else "🤖"
                role_text = "Użytkownik" if message["role"] == "user" else "Asystent"
                st.markdown(f"**{role_icon} {role_text}:**")
                st.markdown(f"*{message['content'][:100]}{'...' if len(message['content']) > 100 else ''}*")
                if i < len(st.session_state.messages) - 1:
                    st.divider()
        
        # Export/Import functionality
        st.subheader("📤 Eksport/Import")
        
        # Export chat history
        if st.button("💾 Eksportuj historię czatu"):
            chat_data = {
                "timestamp": st.session_state.get("session_start", "unknown"),
                "messages": st.session_state.messages,
                "chat_mode": chat_mode,
                "settings": {
                    "db_chunks_number": db_chunks_number,
                    "model_context_chunks_number": model_context_chunks_number,
                    "use_query_expansion": use_query_expansion
                }
            }
            
            # Create JSON string for download
            json_str = json.dumps(chat_data, ensure_ascii=False, indent=2)
            
            # Create download button
            st.download_button(
                label="📥 Pobierz plik JSON",
                data=json_str,
                file_name=f"chat_history_{st.session_state.get('session_start', 'unknown')}.json",
                mime="application/json"
            )
        
        # Import chat history
        uploaded_file = st.file_uploader("📁 Importuj historię czatu", type=['json'])
        if uploaded_file is not None:
            try:
                chat_data = json.load(uploaded_file)
                if "messages" in chat_data:
                    st.session_state.messages = chat_data["messages"]
                    st.success("✅ Historia czatu została zaimportowana!")
                    st.rerun()
                else:
                    st.error("❌ Nieprawidłowy format pliku - brak wiadomości")
            except Exception as e:
                st.error(f"❌ Błąd podczas importowania: {str(e)}")


# Manage memory length - remove oldest messages if exceeding limit
if len(st.session_state.messages) > max_memory_length:
    # Keep only the most recent messages
    st.session_state.messages = st.session_state.messages[-max_memory_length:]

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Main chat input and processing loop
if user_prompt := st.chat_input("Zadaj pytanie:"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Process user input and generate response
    with st.chat_message("assistant"):
        # Create a placeholder for streaming
        message_placeholder = st.empty()
        full_response = ""
        
        # Show that we're waiting for the model
        message_placeholder.markdown("🤔 Myślę...")
        
        try:
            # Get conversation history (excluding the current user message)
            conversation_history = st.session_state.messages[:-1]  # Exclude current user message
            
            if chat_mode == "Tryb RAG":
                # RAG mode: use context retrieval with chat memory
                if use_query_expansion:
                    # Expand the query first
                    message_placeholder.markdown("🔍 Rozszerzam zapytanie...")
                    expanded_user_prompt = call_model_non_stream(
                        system_prompt=expansion_system_prompt,
                        user_prompt=user_prompt
                    )
                    
                    search_query = expanded_user_prompt
                    message_placeholder.markdown(f"🔍 Rozszerzone zapytanie: {search_query}")
                else:
                    # Use original query without expansion
                    search_query = user_prompt
                
                # Create prompt with history and context
                message_placeholder.markdown("📚 Wyszukuję w bazie danych i przygotowuję kontekst...")
                system_prompt = create_prompt_with_history(
                    system_prompt=rag_system_prompt,
                    user_prompt=search_query,
                    conversation_history=conversation_history,
                    db_chunks_number=db_chunks_number,
                    model_context_chunks_number=model_context_chunks_number
                )
                
                # Debug output (can be removed in production)
                print("----------------------------------------------------------------")
                print(f"User prompt:\n\n{user_prompt}")
                print("----------------------------------------------------------------")
                print(f"System prompt with history:\n\n{system_prompt}")
                print("----------------------------------------------------------------")
                print(f"Search query:\n\n{search_query}")
                print("----------------------------------------------------------------")
            else:
                # Normal chat mode: use normal system prompt with chat memory
                system_prompt = create_prompt_with_history(
                    system_prompt=normal_chat_system_prompt,
                    user_prompt=user_prompt,
                    conversation_history=conversation_history
                )
            
            # Stream response chunks and display them in real-time
            message_placeholder.markdown("🤖 Generuję odpowiedź...")
            for chunk in call_model_stream(system_prompt, user_prompt):
                if chunk:
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
            
            # Show the final response without the cursor
            message_placeholder.markdown(full_response)
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            message_placeholder.markdown(error_msg)
            st.error(f"Exception occurred: {e}")
            full_response = error_msg
        
    # Store the complete response in session state for chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Manage memory length after adding new message
    if len(st.session_state.messages) > max_memory_length:
        st.session_state.messages = st.session_state.messages[-max_memory_length:]
