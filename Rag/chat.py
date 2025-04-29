# chat.py
import streamlit as st
import logging
from core.assistant import get_client, build_system_prompt, get_response, get_relevant_past_conversations
from utils.redis_handler import save_chat_history , load_chat_history , log_model_usage
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
import uuid
from utils.rate import is_user_rate_limited

logging.basicConfig(level=logging.INFO)


cookies = EncryptedCookieManager(
    prefix="aichatbot_",
    password="yd22r-su32r-@ecr#t-p#s$$()d"
)

if not cookies.ready():
    st.stop()

# Always generate new user_id per browser (optional: per session)
if "user_id" not in st.session_state:
    # Check if cookie exists
    user_id_cookie = cookies.get("user_id")

    if user_id_cookie is None:
        user_id = str(uuid.uuid4())
        cookies["user_id"] = user_id
        cookies.save()
    else:
        user_id = user_id_cookie

    st.session_state["user_id"] = user_id

def user():
    return st.session_state["user_id"]

user_id = user()


def load_once():
    if "loaded_once" not in st.session_state:
        st.session_state.loaded_once = True
        
    # ⬇️ Inject custom CSS from a file (optional)
    with open("static/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown('''<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">''',unsafe_allow_html=True)


load_once()

st.markdown(
    """
    <div class="fixed top-0 left-0 w-full flex justify-between items-center px-9 py-5 shadow-md bg-white header-ai">
        <!-- Avatar & Name -->
        <div class="avatar-logo flex items-center gap-4">
            <div class="relative">
                <img class="w-10 h-10 rounded-full" src="https://i.pinimg.com/736x/f6/47/fc/f647fcf81f2256fc881e2ee2075f0cf4.jpg" alt="">
                <span class="top-0 left-7 absolute w-3.5 h-3.5 bg-green-400 border-2 border-white dark:border-gray-800 rounded-full"></span>
            </div>
            <div class="font-medium">
                <div class="text-base font-semibold text-black">Paula</div>
                <div class="text-sm text-gray-400">Live</div>
            </div>
        </div>
        <!-- Contact Icons -->
        <div class="flex items-center gap-6">
            <!-- Phone Button -->
            <a href="tel:+447771401976" class="no-line">
                <button class="itt-phh item flex items-center justify-center border border-[#63AAC4] rounded-full w-12 h-12 text-[#63AAC4] text-2xl sm:text-xl md:text-lg lg:text-2xl hover:text-white transition duration-200">
                    <i class="fas fa-phone"></i>
                </button>
            </a>
            <!-- WhatsApp Button -->
            <!-- Close Button -->
            <button class="itt-phh item flex items-center justify-center border border-[#63AAC4] rounded-full w-12 h-12 text-[#63AAC4] text-2xl sm:text-xl md:text-lg lg:text-2xl hover:text-white transition duration-200" ">
                <i class="fas fa-times"></i>
            </button>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown("""
    <div class="made-by">By chatting, you agree to our privacy policy. Made by <a href="https://nexgeno.in/?utm_source=rajeshwebsite&utm_medium=ai_chatbot&utm_campaign=website" target="_blank" class="no-line"><b>Nexgeno.</b></a></div>
""", unsafe_allow_html=True)
   


def show_modal_error():
    modal_html = """
    <style>
        /* Full-screen overlay to block background */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8); /* Semi-transparent black */
            z-index: 1000; /* Ensure it's on top */
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .st-emotion-cache-1690izd {

            background: rgb(33 33 33 / 0%);
            
        }
        

        /* Modal container */
        .modal {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            width: 90%;
            max-width: 400px;
            z-index: 1001; /* Above the overlay */
        }

        .modal h2 {
            font-size: 20px;
            margin-bottom: 10px;
        }

        .modal p {
            font-size: 14px;
            color: #747171;
            margin-bottom: 20px;
        }

        /* Buttons */
        .modal button {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            border-radius: 24px;
            font-size: 16px;
            font-weight: bold;
            border: none;
            cursor: pointer;
            transition: 0.3s;
        }

        .login-btn {
            background: #b8d0d8;
            color: #000000;
        }

        .signup-btn {
            background: #333;
            color: white;
            border: 1px solid #555;
        }

        .logout-btn {
            background: none;
            color: white;
            text-decoration: underline;
        }

        .login-btn:hover {
            background: #ccc;
        }

        .signup-btn:hover {
            background: #444;
        }
        .login-btn a {
        text-decoration: none;  /* Removes underline */
        color: inherit;         /* Inherits the text color from the parent (button) */
        }

        .logout-btn:hover {
            color: #ccc;
        }
    </style>

    <!-- Overlay and modal -->
    <div class="modal-overlay">
        <div class="modal">
            <h2>Thanks for trying Nexbuddy</h2>
            <p>It seems you’ve fully utilized your current access to Buddy, our AI-powered assistant <b>Try After 24 Hours</b> .</p>
           <a href="https://wa.me/9819555545?text=Hello%2C%20I%20would%20like%20to%20inquire%20about%20Nexgeno's%20sAI Buddy!"> <button class="login-btn">   Contact Nexgeno </button> </a>
           
    </div>
    """
    st.markdown(modal_html, unsafe_allow_html=True)
    



if "chat_input" not in st.session_state:
    st.session_state.chat_input = False

def disable_callback():
    st.session_state.chat_input = True


def ai():
    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = load_chat_history(user_id)


    # Display previous chat history
    chat_container = st.container()
    for chat in st.session_state.chat_history:
        chat_container.chat_message(chat["role"]).write(chat["message"])

    # Handle new user input
    if prompt := st.chat_input("Ask Paula",
        disabled=st.session_state.chat_input,
        on_submit=disable_callback,key='askbuddy'):
        
        # Rate limit check
        if is_user_rate_limited(user_id):
            show_modal_error()
            return

        try:
            save_chat_history(user_id, prompt, role="user")
        except Exception as e:
            logging.error("Error saving user chat history:", exc_info=e)

        st.session_state.chat_history.append({"role": "user", "message": prompt})
        chat_container.chat_message("user").write(prompt)

        # Contextual memory for system prompt
        past_convo = get_relevant_past_conversations(user_id, prompt)
        past_convo_text = "\n".join([f"{msg['role'].capitalize()}: {msg['message']}" for msg in past_convo])
        system_msg = build_system_prompt(prompt, past_convo_text)

        is_team = any(kw in prompt.lower() for kw in ["team", "staff", "photo"])
        client = get_client(is_team)
        model = "deepseek/deepseek-chat:free" if is_team else "llama3-70b-8192"
        log_model_usage(user_id, model)

        # Assistant message with placeholder animation
        placeholder = st.empty()
        msg_box = placeholder.chat_message("assistant")
        msg_area = msg_box.markdown(
            """<div class="chat-bubble">
                <div class="typing">
                    <div class="dot"></div><div class="dot"></div><div class="dot"></div>
                </div>
            </div>""", unsafe_allow_html=True
        )

        full_response = ""
        try:
            stream = get_response(system_msg, prompt, model, client)
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    msg_area.markdown(full_response)
        except Exception as e:
            logging.error("Error with primary model:", exc_info=e)
            st.warning("⚠️ Switching to fallback model...")
            try:
                client = get_client(False)
                model = "meta-llama/llama-4-scout-17b-16e-instruct"
                log_model_usage(user_id, model)
                stream = get_response(system_msg, prompt, model, client)
                full_response = ""
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        msg_area.markdown(full_response)
            except Exception as fallback_e:
                logging.error("Fallback model request failed:", exc_info=fallback_e)
                st.warning("⚠️ Switching to Groq (final fallback)...")
                try:
                    import openai
                    groq_client = openai.OpenAI(
                        base_url="https://api.groq.com/openai/v1",
                        api_key='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'
                    )
                    
                    modelname = "mixtral-8x7b-32768"
                    log_model_usage(user_id, modelname)

                    stream = groq_client.chat.completions.create(
                        model=modelname,  # or groq-supported model
                        messages=[
                            {"role": "system", "content": system_msg},
                            {"role": "user", "content": prompt}
                        ],
                        stream=True
                    )

                    full_response = ""
                    for chunk in stream:
                        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            full_response += content
                            msg_area.markdown(full_response)

                except Exception as groq_error:
                    logging.error("Groq fallback failed:", exc_info=groq_error)
                    st.toast("⚠️ All servers are Bussy Try Again After.")
                    full_response = "⚠️ All servers are Bussy Try Again After."
                    


        # Response length limitation
        max_length = 10000
        if len(full_response) > max_length:
            full_response = full_response[:max_length] + "\n\nFor More Information [Visit Website](https://rajeshdeshmukh.co.uk/)"

        # Save final assistant message
        st.session_state.chat_history.append({"role": "assistant", "message": full_response})
        try:
            save_chat_history(user_id, full_response, role="assistant")
        except Exception as e:
            logging.error("Error saving assistant response to chat history:", exc_info=e)

        # Disable input until user reruns
        st.session_state.chat_input = False
        st.rerun()

    # Show the welcome message only when there's no chat yet
    hide_text = "display: none;" if st.session_state.chat_input or st.session_state.chat_history else "display: block;"
    st.markdown(f"""
        <style>
            .name {{
                {hide_text}
            }}
        </style>
        <div class="name">What can I help with?</div>
    """, unsafe_allow_html=True)





ai()