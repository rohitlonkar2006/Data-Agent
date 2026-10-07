import os
import sys

import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage

ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from agents.etl_analyst import etl_analyst
from agents.sql_analyst import final_graph
from models.schema import RouterSchema
from utils.llm_pick import pick_llm


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


def route_user_request(user_question: str):
    if not user_question.strip():
        raise ValueError("Please enter a question or task before submitting.")

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
    st.set_page_config(page_title="Data Agent", page_icon="🧠", layout="centered")
    st.title("Data Agent")
    st.caption("Ask a SQL question or request an ETL workflow in plain English.")

    if not os.getenv("GROQ_API_KEY"):
        st.warning(
            "GROQ_API_KEY is not set. Add it to your environment or .env file before using the app."
        )

    with st.form("query_form"):
        user_question = st.text_area(
            "Your request",
            value="",
            height=160,
            placeholder="Example: How many rides were completed last month? or Extract data from https://pokeapi.co/api/v2/pokemon and save it in data/extract",
        )
        submitted = st.form_submit_button("Run agent")

    if submitted:
        try:
            with st.spinner("Routing and processing your request..."):
                response = route_user_request(user_question)

            st.success(f"Handled as: {response['route'].upper()}")
            st.markdown("### Final answer")
            st.write(response["final_answer"])

            if response["route"] == "sql":
                result = response["result"]
                with st.expander("Generated SQL"):
                    st.code(result.get("generated_sql_query", ""), language="sql")

                with st.expander("Safety review"):
                    st.write(result.get("comments", ""))

                with st.expander("SQL execution result"):
                    st.code(result.get("sql_query_execution_result", ""))

            else:
                with st.expander("ETL workflow details"):
                    st.json(response["result"])

        except Exception as exc:
            st.error(f"The request could not be processed: {exc}")


if __name__ == "__main__":
    main()
