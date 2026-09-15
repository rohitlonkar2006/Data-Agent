from langchain_groq import ChatGroq

def pick_llm(level:str):
    """
    Picks the appropriate LLM based on the level of the question
    
    Args:
        level(str) : the level of the question, can be "easy","medium", or "hard".
    
    Returns:
        str: the name of the LLM to be used.
    """
    if level.lower == "low":
        llm = ChatGroq(model = "llama-3.1-8b-instant", temperature = 0)
        
    elif level.lower == "medium":
        llm = ChatGroq(model = "openai/gtp-oss-120b", temperature = 0)    
    elif level.lower == "high":
        llm = ChatGroq(model = "openai/gpt-oss-120b", temperature = 0)
    else:
        raise ValueError(f"Unsupported level: {level}")
    
    return llm

llm_obj = pick_llm("low")
llm_obj.invoke("Who is modi")