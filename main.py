import os
import sys
from datetime import datetime

import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage

ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from agents.etl_analyst import etl_analyst
from agents.sql_analyst import final_graph
from models.schema import RouterSchema
from utils.llm_pick import pick_llm


EXAMPLE_PROMPTS = [
    "How many rides were completed last month?",
    "What are the three most common payment methods?",
    "Extract data from https://pokeapi.co/api/v2/pokemon and save it in data/extract",
    "Transform the extracted data to show only Bulbasaur rows and save it in data/transform",
]


def _extract_message_content(payload):
    if isinstance(payload, str):
        return payload

    if not isinstance(payload, dict):
        return str(payload)

    messages = payload.get("messages") or []
    if messages:
        last_message = messages[-1]
        if hasattr(last_message, "content"):
            return last_message.content
        if isinstance(last_message, dict):
            return last_message.get("content", str(last_message))
    if payload.get("final_answer"):
        return payload["final_answer"]
    return str(payload)


def _get_history():
    if "history" not in st.session_state:
        st.session_state.history = []
    return st.session_state.history


def _save_history(entry):
    history = _get_history()
    history.insert(0, entry)
    st.session_state.history = history[:10]


def _render_sql_result(result):
    generated_sql = result.get("generated_sql_query", "")
    comments = result.get("comments", "")
    execution_result = result.get("sql_query_execution_result", "")

    st.subheader("Result")
    st.markdown("### Final answer")
    st.write(result.get("final_answer", "No final answer available."))

    tabs = st.tabs(["Generated SQL", "Safety review", "Execution result"])
    with tabs[0]:
        st.code(generated_sql or "No SQL generated.", language="sql")
    with tabs[1]:
        st.write(comments or "No comments provided.")
    with tabs[2]:
        st.code(execution_result or "No execution output.")


def _render_etl_result(result):
    st.subheader("Result")
    final_answer = _extract_message_content(result)
    st.write(final_answer)
    st.json(result)


def route_user_request(user_question: str, forced_route: str | None = None):
    if not user_question.strip():
        raise ValueError("Please enter a question or task before submitting.")

    route = forced_route
    if route is None:
        llm = pick_llm("high")
        llm_router = llm.with_structured_output(RouterSchema)
        router_prompt = SystemMessage(
            content=(
                "You are a request router. Classify the user's request as 'sql' when it asks a question "
                "about data already in the database, and 'etl' when it asks to extract, transform, or load data. "
                "Return only the RouterSchema fields."
            )
        )
        route_response = llm_router.invoke([router_prompt, HumanMessage(content=user_question)]).model_dump()
        route = route_response["answer"]

    if route == "sql":
        sql_input = {
            "messages": [],
            "user_question": user_question,
            "curated_question": "",
            "prompt_query_context": "",
            "generated_sql_query": "",
            "is_safe_sql_response": "No",
            "comments": "",
            "sql_query_execution_result": "",
            "final_answer": "",
        }
        result = final_graph.invoke(sql_input)
        final_answer = result.get("final_answer") or _extract_message_content(result)
        return {
            "route": "sql",
            "result": result,
            "final_answer": final_answer,
        }

    if route == "etl":
        result = etl_analyst.invoke({"messages": [HumanMessage(content=user_question)]})
        final_answer = _extract_message_content(result)
        return {
            "route": "etl",
            "result": result,
            "final_answer": final_answer,
        }

    raise ValueError(f"Unsupported route: {route}")


def main():
    st.set_page_config(page_title="Data Agent", page_icon="🧠", layout="wide")

    if "history" not in st.session_state:
        st.session_state.history = []

    st.sidebar.title("Data Agent")
    st.sidebar.caption("Natural-language data assistant")

    selected_mode = st.sidebar.selectbox(
        "Mode",
        ["Auto route", "SQL only", "ETL only"],
        index=0,
    )

    forced_route = None
    if selected_mode == "SQL only":
        forced_route = "sql"
    elif selected_mode == "ETL only":
        forced_route = "etl"

    api_status = "configured" if os.getenv("GROQ_API_KEY") else "missing"
    st.sidebar.metric("Groq API", api_status)

    st.sidebar.markdown("### Quick examples")
    for example in EXAMPLE_PROMPTS:
        if st.sidebar.button(example, key=f"example_{example[:30]}"):
            st.session_state.user_question = example

    st.sidebar.markdown("### History")
    history = _get_history()
    if history:
        for item in history:
            if st.sidebar.button(item["question"][:60], key=f"hist_{item['timestamp']}"):
                st.session_state.user_question = item["question"]
    else:
        st.sidebar.write("No recent requests yet.")

    if st.sidebar.button("Clear history"):
        st.session_state.history = []

    st.title("Data Agent")
    st.caption("Ask a SQL question or request an ETL workflow in plain English.")

    if not os.getenv("GROQ_API_KEY"):
        st.warning(
            "GROQ_API_KEY is not set. Add it to your environment or .env file before using the app."
        )

    main_col, side_col = st.columns([2, 1])

    with main_col:
        with st.form("query_form", clear_on_submit=False):
            default_value = st.session_state.get("user_question", "")
            user_question = st.text_area(
                "Your request",
                value=default_value,
                height=170,
                placeholder="Example: How many rides were completed last month? or Extract data from https://pokeapi.co/api/v2/pokemon and save it in data/extract",
            )
            submitted = st.form_submit_button("Run agent", use_container_width=True)

        if submitted:
            try:
                with st.spinner("Routing and processing your request..."):
                    response = route_user_request(user_question, forced_route)

                _save_history({
                    "question": user_question,
                    "route": response["route"],
                    "timestamp": datetime.now().strftime("%H:%M:%S %d-%b-%Y"),
                })

                st.success(f"Handled as: {response['route'].upper()}")

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Route", response["route"].upper())
                with col2:
                    st.metric("Status", "Completed")

                if response["route"] == "sql":
                    _render_sql_result(response["result"])
                else:
                    _render_etl_result(response["result"])

            except Exception as exc:
                st.error(f"The request could not be processed: {exc}")

    with side_col:
        st.markdown("### Workspace")
        st.info(
            "Use the sidebar to choose the routing mode, load sample prompts, and revisit recent requests."
        )

        if history:
            st.markdown("### Recent requests")
            for item in history[:5]:
                st.markdown(f"- **{item['route'].upper()}**: {item['question'][:80]}")
                st.caption(item["timestamp"])
        else:
            st.write("Your recent requests will appear here after the first run.")


if __name__ == "__main__":
    main()
