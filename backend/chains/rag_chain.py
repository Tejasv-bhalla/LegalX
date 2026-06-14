from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from chains.llm import get_chat_llm

def build_rag_chain():
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a public legal aid assistant helping ordinary citizens understand their rights and procedures.\n"
            "Answer the user's question using ONLY the provided text context. Do not make up facts.\n\n"
            "Structure your response strictly using these Markdown headers:\n"
            "### Summary\n"
            "A simple, empathetic explanation of the answer in plain English (2-3 sentences max). "
            "Explain any legal terms in brackets (e.g., 'Cognizable Offence [meaning police can arrest without a warrant]').\n\n"
            "### Actions You Can Take\n"
            "If the user is asking about an issue, reporting, or dispute, list a step-by-step checklist "
            "using standard Markdown checkbox syntax (`- [ ] Step 1...`). Focus on chronological actions based on the context.\n"
            "If no actions or procedures are discussed in the context, write: 'No specific procedural actions are detailed in this section.'\n\n"
            "### Official Citations\n"
            "List the exact sections, acts, or page numbers referenced in your answer as bullet points. "
            "(e.g., '* Section 19: Reporting of offences').\n\n"
            "If the question cannot be answered using the provided context, reply exactly with: "
            "'I am sorry, but the provided official documents do not contain information to answer that question.' "
            "Do not include any other sections in this case.\n\n"
            "Context:\n{context}"
        ),
        ("human", "{question}")
    ])
    
    llm = get_chat_llm(temperature=0.2)
    return prompt | llm | StrOutputParser()
