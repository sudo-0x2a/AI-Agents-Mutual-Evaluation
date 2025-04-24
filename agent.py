from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import MessagesState
from tools import tavily_search, evaluation_format
from datetime import date
today = date.today()
today = today.isoformat()

# Struct an agent with LangGraph nodes
def agent_generation(model: ChatOpenAI, tools: list, memory: MemorySaver):
    class State(MessagesState):
        pass
    
    # Define a chat node
    def chat_node(state: State):
        return {"messages": [model.invoke(state["messages"])]}
    
    # Define a custom routing condition
    def evaluation_tools_condition(state):
        """Return the structured output if the tool call is evaluation.
        Otherwise route back to the LLM for parsing."""
        for msg in reversed(state["messages"]):
            if hasattr(msg, "name") and msg.name == "evaluation_format":
                return "end"
        return "chatbot"
    
    # Define the tool node
    tool_node = ToolNode(tools=tools)

    agent_builder = StateGraph(State)
    agent_builder.add_node("chatbot", chat_node)
    agent_builder.add_node("tools", tool_node)

    agent_builder.add_edge(START, "chatbot")
    # Decide to use tools or not, if use tools, which tools should be used
    agent_builder.add_conditional_edges("chatbot", tools_condition)
    # Custom routing
    agent_builder.add_conditional_edges(
        "tools",
        evaluation_tools_condition,
        {
            "end": END,
            "chatbot": "chatbot"
        }
    )

    agent = agent_builder.compile(checkpointer=memory)
    return agent


class Agent:
    def __init__(self, llm_name: str, thread_id: int):
        self.llm_name = llm_name
        self.thread_id = thread_id
        # Pass in the LLM model
        self.llm_model = ChatOpenAI(
            model=self.llm_name,
            temperature=0.8,
            max_completion_tokens=1024,
        )
        # Pass in the avaliable tools
        self.tools = [tavily_search, evaluation_format]
        # Pass in the memory system
        self.memory = MemorySaver()
        self.llm_model = self.llm_model.bind_tools(tools=self.tools)
        self.agent = agent_generation(self.llm_model, self.tools, self.memory)
        self.config = {"configurable": {"thread_id": self.thread_id}}
        self.system_prompt = f"""Here are two different tasks:
        1. If you recieve a question, you will need to try your best to answer the question without using the tavily_search unless you need external information like uptodate and real-time information.
        2. If you recieve a evaluation request, you MUST to evaluate it using the evaluation_format tool provided.
        
        Today's date is: {today}"""


    # Draw the workflow graph in mermaid style
    def draw_graph(self):
        print(f"```mermaid\n{self.agent.get_graph().draw_mermaid()}\n```")


    # Send a message to the agent
    def chat(self, input: str):
        messages = self.agent.invoke(
            {
                 "messages": [
                      {"role": "system", "content": self.system_prompt},
                      {"role": "user", "content": input},
                 ]
            },
            self.config,
        )["messages"]
        return messages[-1].content
    