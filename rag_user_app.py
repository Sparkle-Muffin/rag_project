import streamlit as st
import json
from common.bielik_api import call_model_stream, call_model_non_stream
from common.prompt_generation import create_prompt
from common.models import SearchType


# Load the system prompts
with open("common/prompts/rag_system_prompt.txt", "r") as f:
    rag_system_prompt = f.read()

with open("common/prompts/normal_chat_system_prompt.txt", "r") as f:
    normal_chat_system_prompt = f.read()

with open("common/prompts/expansion_system_prompt.txt", "r") as f:
    expansion_system_prompt = f.read()

with open("common/prompts/clarifying_questions_system_prompt.txt", "r") as f:
    clarifying_questions_system_prompt = f.read()

with open("common/prompts/structured_output.json", "r") as f:
    structured_output = json.load(f)


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
        # Query expansion switch
        st.subheader("Rozszerzanie zapytań")
        use_query_expansion = st.checkbox(
            "Użyj rozszerzania zapytań",
            value=False,
            help="Rozszerza pytanie użytkownika przed wyszukiwaniem w bazie danych dla lepszych wyników"
        )
        
        if use_query_expansion:
            st.info("🔍 Zapytanie zostanie rozszerzone przed wyszukiwaniem w bazie")

        # Clarifying questions switch
        st.subheader("Pytania doprecyzowujące")
        use_clarifying_questions = st.checkbox(
            "Użyj pytań doprecyzowujących",
            value=False,
            help="Model najpierw oceni, czy pytanie jest wystarczające. Jeśli nie, poprosi o doprecyzowanie."
        )

        # Search type selector
        st.subheader("Rodzaj wyszukiwania")
        search_type_option = st.radio(
            "Wybierz typ wyszukiwania:",
            ["Hybrydowe", "Wektorowe", "BM25"],
            index=0,
            help="Hybrydowe: łączy wyszukiwanie wektorowe i BM25\nWektorowe: tylko wyszukiwanie semantyczne\nBM25: tylko wyszukiwanie tekstowe"
        )

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
    else:
        # Disable settings in normal chat mode
        st.info("Ustawienia są dostępne tylko w trybie RAG")
        db_chunks_number = 20  # Default values
        model_context_chunks_number = 10  # Default values
        use_query_expansion = False  # Default value
        use_clarifying_questions = False  # Default value
        search_type_option = "Hybrydowe"  # Default value


# Initialize chat session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# State for clarifying questions flow
if "clarification_pending" not in st.session_state:
    st.session_state.clarification_pending = False
if "accumulated_prompt" not in st.session_state:
    st.session_state.accumulated_prompt = ""

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
            # Handle clarifying questions loop (only in RAG mode when enabled)
            effective_user_prompt = user_prompt
            if chat_mode == "Tryb RAG" and use_clarifying_questions:
                # If we are in the middle of clarification, append user's clarification
                if st.session_state.clarification_pending:
                    st.session_state.accumulated_prompt = (
                        (st.session_state.accumulated_prompt or "")
                        + "\n"
                        + user_prompt
                    )
                    effective_user_prompt = st.session_state.accumulated_prompt
                else:
                    # Start a new clarification session with the initial prompt
                    st.session_state.accumulated_prompt = user_prompt
                    effective_user_prompt = user_prompt

                # Ask the model if the query is sufficient
                sufficiency_raw = call_model_non_stream(
                    system_prompt=clarifying_questions_system_prompt,
                    user_prompt=effective_user_prompt,
                    format=structured_output,
                )

                is_sufficient = True
                missing_info_text = ""
                try:
                    sufficiency = json.loads(sufficiency_raw)
                    is_sufficient = bool(sufficiency.get("is_query_sufficient", True))
                    if not is_sufficient:
                        missing_info_text = sufficiency.get("what_is_missing", "")
                except Exception:
                    # If parsing fails, assume sufficient to avoid blocking the user
                    is_sufficient = True

                if not is_sufficient:
                    # Ask user for clarification and wait for next input
                    message_placeholder.markdown(
                        missing_info_text or "Proszę doprecyzować pytanie."
                    )
                    full_response = missing_info_text or "Proszę doprecyzować pytanie."
                    st.session_state.clarification_pending = True

                    # Debug output (can be removed in production)
                    print("----------------------------------------------------------------")
                    print(f"Clarification response:\n\n{full_response}")

                    # Do not proceed to retrieval/answer generation this turn
                    
                    # Show the final assistant message (the clarification request)
                    message_placeholder.markdown(full_response)
                else:
                    # Clear clarification state and proceed with combined prompt
                    st.session_state.clarification_pending = False
                    effective_user_prompt = st.session_state.accumulated_prompt

            if chat_mode == "Tryb RAG" and (not use_clarifying_questions or not st.session_state.clarification_pending):
                # RAG mode: use context retrieval
                final_prompt_for_model = effective_user_prompt if use_clarifying_questions else user_prompt

                if use_query_expansion:
                    # Expand the query first
                    message_placeholder.markdown("🔍 Rozszerzam zapytanie...")
                    expanded_user_prompt = call_model_non_stream(
                        system_prompt=expansion_system_prompt,
                        user_prompt=final_prompt_for_model,
                    )
                    search_query = expanded_user_prompt
                    message_placeholder.markdown(f"🔍 Rozszerzone zapytanie: {search_query}")
                else:
                    # Use original/combined query without expansion
                    search_query = final_prompt_for_model

                # Convert search type option to SearchType enum
                search_type_mapping = {
                    "Hybrydowe": SearchType.HYBRID,
                    "Wektorowe": SearchType.VECTOR,
                    "BM25": SearchType.BM25
                }
                selected_search_type = search_type_mapping[search_type_option]

                # Now search using the (potentially expanded) query
                message_placeholder.markdown("📚 Wyszukuję w bazie danych...")
                system_prompt = create_prompt(
                    system_prompt=rag_system_prompt,
                    user_prompt=search_query,
                    db_chunks_number=db_chunks_number,
                    model_context_chunks_number=model_context_chunks_number,
                    search_type=selected_search_type,
                )

                # Debug output (can be removed in production)
                print("----------------------------------------------------------------")
                print(f"User prompt:\n\n{user_prompt}")
                print("----------------------------------------------------------------")
                print(f"System prompt:\n\n{system_prompt}")
                print("----------------------------------------------------------------")
                print(f"Search query:\n\n{search_query}")
                print("----------------------------------------------------------------")

                # Stream response chunks and display them in real-time
                message_placeholder.markdown("🤖 Generuję odpowiedź...")
                for chunk in call_model_stream(system_prompt, search_query):
                    if chunk:
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")

                # Show the final response without the cursor
                message_placeholder.markdown(full_response)
            elif chat_mode != "Tryb RAG":
                # Normal chat mode: no context, use normal system prompt
                system_prompt = normal_chat_system_prompt
                search_query = user_prompt

                # Stream response chunks and display them in real-time
                message_placeholder.markdown("🤖 Generuję odpowiedź...")
                for chunk in call_model_stream(system_prompt, search_query):
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
