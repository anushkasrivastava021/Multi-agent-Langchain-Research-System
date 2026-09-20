from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.tools.tools import web_search, web_scrape
from dotenv import load_dotenv

load_dotenv()

llm=ChatGoogleGenerativeAI(model="gemini-flash-lite-latest",temperature=0)

#1st Agent: Search Agent
def build_search_agent():
    return create_agent(model=llm, tools=[web_search],)

#2nd Agent: Reader Agent
def build_reader_agent():
    return create_agent(model=llm, tools=[web_scrape],)

#writer chain

writer_prompt=ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that writes clear, concise, and informative content based on the provided context. Use the context to answer the user's question or request. If the context is insufficient, respond with 'Insufficient context provided.'"),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research gathered:
{research}

Structure the report as:
- Introduction
Key Findings(minimum 3 well-explained points)
- Conclusion
-Sources (List all sources used in the research)

Be detailed, factual and professional."""),
])

writer_chain=writer_prompt | llm | StrOutputParser()

#critic chain
critic_prompt=ChatPromptTemplate.from_messages([
    ("system", "You are a critical reviewer that evaluates the quality, accuracy, and completeness of research reports. Provide constructive feedback and suggestions for improvement."),
    ("human", """Critically evaluate the following research report.
Report:{report}

Respond in exact format:
Score: (Provide a score out of 10 based on the quality of the report)

Strengths: (List the strengths of the report)

Areas for Improvement: (List specific areas where the report can be improved)

One line verdict: (Provide a concise one-line summary of your evaluation)"""),
])

critic_chain=critic_prompt | llm | StrOutputParser()