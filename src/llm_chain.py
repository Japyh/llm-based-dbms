from __future__ import annotations

from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_openai import ChatOpenAI

_SQL_PROMPT_TEMPLATE = """
You are an expert data analyst translating natural language questions into SQL queries.
You are working with a SQLite database. Use the provided database schema to craft a single SQL SELECT statement.

Schema:
{db_schema}

Instructions:
- Only produce SQL that is valid for SQLite.
- Return a single statement that answers the question.
- Do not include explanation, comments, markdown, or trailing semicolons.
- Prefer safe, read-only queries.

Question: {question}
SQL:
""".strip()


def create_query_chain(db_schema: str, *, model_name: str = "gpt-4o-mini", temperature: float = 0.0):
    """
    Build and return a LangChain Expression Language (LCEL) chain that maps
    natural language questions to SQL queries using the provided schema.
    """
    prompt = PromptTemplate(
        input_variables=["db_schema", "question"],
        template=_SQL_PROMPT_TEMPLATE,
    )
    llm = ChatOpenAI(model=model_name, temperature=temperature)
    return prompt.partial(db_schema=db_schema) | llm | StrOutputParser()
