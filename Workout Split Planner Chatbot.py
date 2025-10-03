# --- Imports ---
import streamlit as st
from google import genai  # Make sure google-genai is installed

# --- 1. Page Configuration ---
st.set_page_config(page_title="💪 Workout Split Planner Chatbot", layout="centered")
st.title("💪 Workout Split Planner Chatbot")
st.caption("Plan your workout split with help from Google's Gemini model")

# --- 2. Sidebar Settings ---
with st.sidebar:
    st.subheader("Settings")

    # Input API Key
    google_api_key = st.text_input("Google AI API Key", type="password")

    # Reset conversation button
    reset_button = st.button("Reset Conversation", help="Clear all messages and start fresh")

    # Workout preferences
    st.subheader("Workout Preferences")
    goal = st.selectbox("Goal", ["Bulking (Hypertrophy)", "Strength", "Cutting (Fat Loss)", "General Fitness"])
    days = st.slider("Days per Week", 2, 6, 4)
    experience = st.selectbox("Experience Level", ["Beginner", "Intermediate", "Advanced"])
    split_style = st.selectbox("Split Style", ["Push-Pull-Legs", "Upper/Lower", "Full Body", "Bro Split", "AI Suggests"])
    include_nutrition = st.checkbox("Include Nutrition Tips", value=True)

# --- 3. API Key Validation ---
if not google_api_key:
    st.info("Please add your Google AI API key in the sidebar to start chatting.", icon="🗝️")
    st.stop()

if ("genai_client" not in st.session_state) or (getattr(st.session_state, "_last_key", None) != google_api_key):
    try:
        st.session_state.genai_client = genai.Client(api_key=google_api_key)
        st.session_state._last_key = google_api_key
        # Reset chat if key changed
        st.session_state.pop("chat", None)
        st.session_state.pop("messages", None)
    except Exception as e:
        st.error(f"Invalid API Key: {e}")
        st.stop()

# --- 4. Reset Conversation ---
if reset_button:
    st.session_state.pop("chat", None)
    st.session_state.pop("messages", None)
    st.experimental_rerun()

# --- 5. Chat Initialization ---
if "chat" not in st.session_state:
    st.session_state.chat = st.session_state.genai_client.chats.create(model="gemini-2.5-flash")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 6. Display Past Messages ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 7. Handle User Input ---
prompt = st.chat_input("Tell me what kind of workout split you want...")

if prompt:
    prompt = prompt.strip()  # Clean input

    # Add workout context automatically
    system_context = f"""
You are a professional fitness coach.
Generate a structured {split_style} workout split plan.
- Goal: {goal}
- Days per week: {days}
- Experience: {experience}
- Include nutrition tips: {include_nutrition}
Make the plan motivating, structured per day, with sets/reps, warm-up & cooldown.
"""
    full_prompt = system_context + "\nUser additional request: " + prompt

    # 1. Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Send to Gemini with spinner
    with st.spinner("Generating workout plan..."):
        try:
            response = st.session_state.chat.send_message(full_prompt)
            answer = response.text if hasattr(response, "text") else str(response)
        except Exception as e:
            answer = f"⚠️ An error occurred while generating the plan: {e}"

    # 3. Show assistant response
    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})