from langchain.utilities import SerpAPIWrapper

from langchain.agents import Tool, AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import RetrievalQA


def create_agent(docsearch):
  llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

  # SEARCH TOOL
  search = SerpAPIWrapper()

  search_tool = Tool(
    name="search_tool",
    description="If db is not able to answer, this tool will be used. It will search the web for an answer.",
    func=search.run,
  )

  retriever = retriever = docsearch.as_retriever(search_type="mmr", search_kwargs={"k": 5, "fetch_k": 15})
  vector_store = RetrievalQA.from_chain_type(
      llm=llm, chain_type="stuff", retriever=retriever
  )

  vector_store_tool = Tool(
      name="Main recipes store",
      description="""Useful to try and see if a recipe is available in the database.
      The language of the answer will be the same as the question.
      Respond with all the data available in the recipe.
      """,
      func=vector_store.run,
      # return_direct=True
  )


  # AGENT
  tools = [
    vector_store_tool,
    search_tool,
  ]

  # tools = load_tools(["serpapi"], llm=llm)

  memory = ConversationBufferMemory(memory_key="chat_history")


  agent = initialize_agent(
    llm=llm,
    tools=tools,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
  )

  return agent
