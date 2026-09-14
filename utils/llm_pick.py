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