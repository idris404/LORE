import os
from functools import lru_cache
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

GROQ_MODEL_DEFAULT = "llama-3.3-70b-versatile"


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    return ChatGroq(
        model=os.getenv("GROQ_MODEL", GROQ_MODEL_DEFAULT),
        api_key=os.getenv("GROQ_API_KEY", ""),
        temperature=0.3,
        max_tokens=2048,
    )


async def complete(system_prompt: str, user_prompt: str) -> str:
    llm = get_llm()
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]
    response = await llm.ainvoke(messages)
    return response.content


async def summarize_paper(title: str, abstract: str) -> str:
    system = (
        "You are a research assistant. Summarize academic papers concisely in 2-3 sentences, "
        "highlighting key contributions and practical implications."
    )
    user = f"Title: {title}\n\nAbstract: {abstract}"
    return await complete(system, user)
