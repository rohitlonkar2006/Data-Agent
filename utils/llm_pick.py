from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

def pick_llm(level:str):
    """
    Picks the appropriate LLM based on the level of the question
    
    Args:
        level(str) : the reasoning level, can be "low", "medium", or "high".
    
    Returns:
        ChatGroq: the LLM configured for the requested reasoning level.
    """
    if level.lower() == "low":
        llm = ChatGroq(model = "openai/gpt-oss-20b", temperature = 0, reasoning_effort = "low")
    elif level.lower() == "medium":
        llm = ChatGroq(model = "openai/gpt-oss-120b", temperature = 0, reasoning_effort = "medium")
    elif level.lower() == "high":
        llm = ChatGroq(model = "openai/gpt-oss-120b", temperature = 0, reasoning_effort = "high")
    else:
        raise ValueError(f"Unsupported level: {level}")
    
    return llm

if __name__ == "__main__":
    llm_obj = pick_llm("low")
    print(llm_obj.invoke("Who is modi"))