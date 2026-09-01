import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from rag import create_vector_store, load_vector_store, retrieve_documents
from tools import get_order_status

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY NOT FOUND ERROR")
    st.stop()

os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY


st.set_page_config(
    page_title="ShopAssist AI",
    page_icon="🛍️",
    layout="wide"
)

st.markdown(
    """
    <style>

    /* Main container */
    .block-container {
        max-width: 1000px;
        padding-top: 2rem;
    }

    /* Header */
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        margin-bottom: 30px;
    }

    /* Suggestion section */
    .suggestion-title {
        font-size: 18px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    /* Sidebar */
    .sidebar-title {
        font-size: 24px;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">🛍️ ShopAssist</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown(
        """
        ### Customer Support

        ShopAssist can help you with:

        - 📦 Order status
        - 🚚 Shipping
        - 🔄 Returns
        - 💰 Refunds
        - 📋 Store policies
        """
    )

    st.markdown("---")
    st.markdown("### 💬 Chat")
    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = [
            {
                "role": "assistant",
                "content":
                    "Hello! 👋 I'm ShopAssist. "
                    "How can I help you today?"
            }
        ]

        st.rerun()

    st.markdown("---")

    st.caption(
        "Powered by Gemini + RAG + Tool Calling"
    )

st.markdown(
    '<div class="main-title">🛍️ ShopAssist AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Your intelligent customer support assistant'
    '</div>',
    unsafe_allow_html=True
)

@st.cache_resource
def create_llm():

    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        temperature=0.1,
        max_tokens=150
    )

@st.cache_resource
def get_vector_store():

    if not os.path.exists("chroma_db"):

        return create_vector_store()

    return load_vector_store()

llm = create_llm()

vector_store = get_vector_store()

llm_with_tools = llm.bind_tools(
    [get_order_status]
)

if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "assistant",
            "content":
                "Hello! 👋 I'm ShopAssist. "
                "How can I help you today?"
        }
    ]

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

st.markdown(
    '<div class="suggestion-title">💡 Try asking</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)


with col1:

    return_question = st.button(
        "📦 Return policy",
        use_container_width=True
    )


with col2:

    order_question = st.button(
        "🚚 Order status",
        use_container_width=True
    )


with col3:

    refund_question = st.button(
        "💰 Refund timing",
        use_container_width=True
    )


# ============================================================
# Customer Input
# ============================================================

question = st.chat_input(
    "Ask about your order, shipping, returns or refunds..."
)

if return_question:
    question = "What is your return policy?"

elif order_question:
    question = "Where is my order ORD001?"

elif refund_question:
    question = "How long does a refund take?"

if question:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("ShopAssist is thinking..."):
                documents = retrieve_documents(vector_store,question)

                if documents:
                    context = "\n\n".join(
                    document.page_content
                    for document in documents
                )
                else:
                    context= ("No relevant information found in the ShopAssist Knowledge Base")

                conversation_history = "" 

                for message in st.session_state.messages: 
                    conversation_history += ( f"{message['role'].upper()}: " 
                    f"{message['content']}\n" 
                )

                prompt = f"""
                You are ShopAssist, an AI customer support assistant.

                You help customers with:

                - Orders
                - Shipping
                - Returns
                - Refunds
                - Store policies
                - Payment Mode

                Use the provided knowledge base when answering policy-related questions.

                Use the order-status tool when the customer asks about a specific order.

                Never invent:

                - Order information
                - Customer information
                - Store policies
                - Refund information

                If you do not have enough information to answer,clearly tell the customer.

                Keep responses helpful and easy to understand.

                Knowledge Base:

                {context}

                Conversation History:

                {conversation_history}

                Customer Question:

                {question}
                """

                response = llm_with_tools.invoke(
                    prompt
                )

                if response.tool_calls:
                    messages = [
                        {
                            "role": "user",
                            "content": prompt
                        },
                        response
                    ]

                    for tool_call in response.tool_calls:

                        if (tool_call["name"]== "get_order_status"):

                            tool_result = (get_order_status.invoke(tool_call["args"])
                            )

                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id":tool_call["id"],
                                    "content":str(tool_result)
                                }
                            )

                    final_response = (llm_with_tools.invoke(messages)
                    )
                    if isinstance(response.content, list):

                            answer = "".join(
                            block.get("text", "")
                            for block in response.content
                            if block.get("type") == "text"
                )

                    else:

                        answer = response.content
                else:

                    if isinstance(response.content, list):

                        answer = "".join(
                        block.get("text", "")
                        for block in response.content
                        if block.get("type") == "text"
                    )

                    else:
                        answer = response.content

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )


        except Exception as e:

            error_message = (
                "Sorry, I encountered a problem while "
                "processing your request. Please try again."
            )

            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message
                }
            )

