import streamlit as st
from common.bielik_api import call_model_stream, call_model_non_stream
from common.prompt_generation import create_prompt


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
# 
# ## How it works:
# 1. User inputs a question in the chat interface
# 2. System retrieves relevant document chunks using hybrid search (vector + BM25) [RAG mode only]
# 3. Retrieved context is combined with the system prompt [RAG mode only]
# 4. Bielik model generates a response using the enhanced context
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
        db_chunks_number = 20  # Default values
        model_context_chunks_number = 10  # Default values
        use_query_expansion = False  # Default value


# Initialize chat session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Main chat input and processing loop
if input_prompt := st.chat_input("Zadaj pytanie:"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": input_prompt})
    with st.chat_message("user"):
        st.markdown(input_prompt)

    # Process user input and generate response
    with st.chat_message("assistant"):
        # Create a placeholder for streaming
        message_placeholder = st.empty()
        full_response = ""
        
        # Show that we're waiting for the model
        message_placeholder.markdown("🤔 Myślę...")
        
        try:
            if chat_mode == "Tryb RAG":
                # RAG mode: use context retrieval
                if use_query_expansion:
                    # Expand the query first
                    message_placeholder.markdown("🔍 Rozszerzam zapytanie...")
                    expanded_query = call_model_non_stream(
                        system_prompt=expansion_system_prompt,
                        user_prompt=input_prompt
                    )
                    
                    # Check if expansion was successful
                    if expanded_query == "IGNORE_QUERY":
                        # Query is not about LLMs, use original query
                        search_query = input_prompt
                        message_placeholder.markdown("⚠️ Zapytanie nie dotyczy LLM - używam oryginalnego zapytania...")
                    else:
                        search_query = expanded_query
                        message_placeholder.markdown(f"🔍 Rozszerzone zapytanie: {expanded_query}")
                else:
                    # Use original query without expansion
                    search_query = input_prompt
                
                # Now search using the (potentially expanded) query
                message_placeholder.markdown("📚 Wyszukuję w bazie danych...")
                system_prompt, user_prompt = create_prompt(system_prompt=rag_system_prompt, 
                                                           user_prompt=search_query, 
                                                           db_chunks_number=db_chunks_number, 
                                                           model_context_chunks_number=model_context_chunks_number)
                
                # Debug output (can be removed in production)
                print("----------------------------------------------------------------\n\n")
                print(f"Search query\n\n{search_query}")
                print("----------------------------------------------------------------\n\n")
                print(f"System prompt\n\n{system_prompt}")
                print("----------------------------------------------------------------\n\n")
                print(f"User prompt\n\n{user_prompt}")
                print("----------------------------------------------------------------\n\n")
            else:
                # Normal chat mode: no context, use normal system prompt
                system_prompt = normal_chat_system_prompt
                user_prompt = input_prompt
            
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
