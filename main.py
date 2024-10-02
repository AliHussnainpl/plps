import streamlit as st
import httpx
import time
import json

st.title("PLPS Chatbot Demo")


# API URLs
LOGIN_API_URL = "http://plpschatbot.server1.purelogics.net/api/login/"
CHAT_API_URL = "http://plpschatbot.server1.purelogics.net/api/chat/"

# User credentials for login
USERNAME = "ali"  # Replace with actual username
PASSWORD = "ali"  # Replace with actual password


def get_jwt_token():
    """Retrieve JWT token by calling the login API."""
    payload = json.dumps({
        "username": USERNAME,
        "password": PASSWORD
    })
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = httpx.post(LOGIN_API_URL, headers=headers, data=payload)
        response.raise_for_status()
        return response.json().get("access", None)  # Assuming the token is in the "access" field
    except httpx.RequestError as exc:
        st.error(f"An error occurred while trying to login: {exc}")
    except httpx.HTTPStatusError as exc:
        st.error(f"HTTP error occurred: {exc.response.status_code}")
    return None


# Chat interface
st.header("Chat with the AI using PL Data")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input and sending chat messages
if prompt := st.chat_input("What is your question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Get JWT token by calling the login API
        jwt_token = get_jwt_token()

        if jwt_token:
            # POST request with JWT token
            headers = {"Authorization": f"Bearer {jwt_token}"}
            data = {"message": prompt}

            try:
                response = httpx.post(CHAT_API_URL, headers=headers, json=data, timeout=120)
                response.raise_for_status()  # Raise error if the response contains an HTTP error status

                full_response = response.json().get("response", "No response from server.")
                message_placeholder.markdown(full_response)
            except httpx.RequestError as exc:
                print(f"Exception: {exc}")
                message_placeholder.markdown(f"Sorry for inconvenience.Something wrong at our end.We are checking")
            except httpx.HTTPStatusError as exc:
                print(f"Exception: {exc}")
                message_placeholder.markdown(f"Sorry for inconvenience.Something wrong at our end.We are checking")
        else:
            message_placeholder.markdown("Sorry for inconvenience.Something wrong at our end.We are checking")

    st.session_state.messages.append({"role": "assistant", "content": full_response})
