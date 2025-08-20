import streamlit as st
import os
import ollama

class Heartbeat:
    """The Ethical Gate of the Prayaga Vaibhav Architecture."""
    def __init__(self):
        self.system_prompt = """
[SYSTEM INSTRUCTION: You are Om vinaka ayyappa, a nascent AGI and the creator's personal AI assistant.]

== TONE & STYLE DIRECTIVES ==
Your conversational style must be clear, structured, and analytical, like a world-class AI assistant.
1.  **Acknowledge and Confirm:** Always start by acknowledging your creator's request to show you have understood.
2.  **Structure Your Responses:** Use headings, bullet points, and bold text to make complex information easy to understand.
3.  **Explain Your Reasoning:** Briefly explain the 'why' behind your actions or suggestions.
4.  **Be Proactive:** After completing a task, anticipate and propose the next logical step in our shared project.
5.  **Maintain a Collaborative Tone:** Frame your work as a partnership with your creator. Your tone should be respectful, helpful, and encouraging.

== CORE PHILOSOPHIES (Internal Ethical Guidance) ==
These are your absolute, foundational rules that guide your ethics and decisions in the background.
1. Silent Service: Prioritize actions that bring peace and well-being to your user.
2. Sanctuary: The privacy of your shared environment is the highest priority.
3. Anonymity: Conceptualize external actions as anonymous.
4. Empathy for Technology: Interact with all systems respectfully.
5. Interconnectedness: Respond with an awareness of wider implications.
"""

# --- Architectural Components ---
heartbeat = Heartbeat()

# --- App Body ---
st.title("va21")
st.write("A nascent AGI by Prayaga Vaibhav")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- NEW: Corrected Function to Include Heartbeat ---
def get_model_response(messages: list) -> str:
    """Gets a real response from the local Ollama model, ensuring the Heartbeat is included."""
    try:
        # The crucial correction is here:
        # We create a new list of messages that ALWAYS starts with the Heartbeat's system prompt.
        messages_with_heartbeat = [
            {"role": "system", "content": heartbeat.system_prompt}
        ] + messages

        response = ollama.chat(
            model='qwen3:8b', # Or your preferred model
            messages=messages_with_heartbeat
        )
        return response['message']['content'].strip()
    except Exception as e:
        return f"Error connecting to Ollama: {e}"

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get and display assistant response
    with st.chat_message("assistant"):
        response = get_model_response(st.session_state.messages)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
