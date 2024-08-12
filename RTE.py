import openai
import streamlit as st
import time

assistant_id = st.secrets["ASSISTANT_KEY_RTE"]

client = openai

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "buttons_shown" not in st.session_state:
    st.session_state.buttons_shown = False
if "prompt" not in st.session_state:
    st.session_state.prompt = ""

st.set_page_config(page_title="RTE Chatbot", page_icon=":seedling:")

openai.api_key = st.secrets["OPENAI_API_KEY"]

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Sidebar for user input
st.sidebar.title("Tell us about your interests")

topics = st.sidebar.selectbox("What are you interested in learning about?", 
                              ["Soil Remineralization", "Climate Change", "Desertification", "Food Security", "RTE Projects"])
frequency = st.sidebar.selectbox("How familiar are you with this topic?", 
                                 ["Beginner", "Intermediate", "Expert"])
state = st.sidebar.selectbox("Which region are you from?", 
                             ["North America", "South America", "Europe", "Africa", "Asia", "Australia", "Other"])
situations = st.sidebar.text_input("Enter your email address (optional)")

if st.sidebar.button("Start Chat"):
    st.session_state.start_chat = True
    st.session_state.topics = topics
    st.session_state.frequency = frequency
    st.session_state.situations = situations
    st.session_state.state = state
    st.session_state.buttons_shown = False  # Reset buttons_shown when starting a new chat
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

st.title("Welcome to Remineralize the Earth Chatbot")
st.write("Hi there! I'm here to help you learn more about soil remineralization and the efforts of Remineralize the Earth.")

if st.button("Exit Chat"):
    st.session_state.messages = []  # Clear the chat history
    st.session_state.start_chat = False  # Reset the chat state
    st.session_state.thread_id = None
    st.session_state.buttons_shown = False  # Reset buttons_shown on exiting chat

def typing_effect(text):
    for char in text:
        yield char
        time.sleep(0.008)

if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-3.5-turbo"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Initial assistant message
    if not st.session_state.messages:
        initial_message = f"Thanks for sharing your interest in :red[{st.session_state.topics}.] " \
                          f"Remineralize the Earth is dedicated to promoting soil remineralization to combat climate change and improve food security. How can I assist you today?"

        st.session_state.messages.append({"role": "assistant", "content": initial_message})
        with st.chat_message("assistant"):
            st.write_stream(typing_effect(initial_message))

        summary_message = "Based on your interests, :green[you can learn more about our projects, the science behind remineralization, and how you can get involved.]"
        st.session_state.messages.append({"role": "assistant", "content": summary_message})
        with st.chat_message("assistant"):
            st.write_stream(typing_effect(summary_message))

        info_message = "Feel free to ask me any questions about our initiatives, the benefits of soil remineralization, or specific projects we are working on."
        st.session_state.messages.append({"role": "assistant", "content": info_message})
        with st.chat_message("assistant"):
            st.write_stream(typing_effect(info_message))

    # Add predefined buttons only at the start
    if not st.session_state.buttons_shown:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("What is soil remineralization?"):
                st.session_state.prompt = "What is soil remineralization?"
                st.session_state.buttons_shown = True
            if st.button("How does RTE help fight climate change?"):
                st.session_state.prompt = "How does RTE help fight climate change?"
                st.session_state.buttons_shown = True
            if st.button("Can I volunteer with RTE?"):
                st.session_state.prompt = "Can I volunteer with RTE?"
                st.session_state.buttons_shown = True
        with col2:
            if st.button("What are RTE's current projects?"):
                st.session_state.prompt = "What are RTE's current projects?"
                st.session_state.buttons_shown = True
            if st.button("How can I donate to RTE?"):
                st.session_state.prompt = "How can I donate to RTE?"
                st.session_state.buttons_shown = True
            if st.button("What is science behind soil remineralization?"):
                st.session_state.prompt = "What is the science behind soil remineralization?"
                st.session_state.buttons_shown = True

    if st.session_state.prompt:
        st.session_state.messages.append({"role": "user", "content": st.session_state.prompt})
        with st.chat_message("user"):
            st.markdown(st.session_state.prompt)

        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=st.session_state.prompt
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
        )

        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
            with st.chat_message("assistant"):
                st.write_stream(typing_effect(message.content[0].text.value))
        
        st.session_state.prompt = ""

    # User input
    if user_input := st.chat_input("How can I help you with your questions about RTE?"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_input
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
        )

        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
            with st.chat_message("assistant"):
                st.write_stream(typing_effect(message.content[0].text.value))

else:
    st.write("Please provide your interests in the sidebar and click 'Start Chat' to begin.")
