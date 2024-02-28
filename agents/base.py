from langchain.schema import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import create_openai_tools_agent, AgentExecutor

from memory import create_memory
from beans import Message
from logger import logger


class BaseAgent:
    def __init__(self, llm, tools, prompt):
        self.memory = create_memory()
        self.agent = create_openai_tools_agent(llm, tools, prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools)
        self.output_parser = StrOutputParser()

    def respond(self, user_input: Message, history: list[Message]):
        # 历史最后一条消息应该与用户输入一致
        if history[-1]["_id"] != user_input["_id"]:
            logger.info("用户有新的输入，不进行回复")
            return
        history = history[:-1]  # 去掉最后一条消息
        res = self.agent_executor.invoke(
            {
                "user_input": user_input["content"],
                "related_messages": self.get_related_messages(user_input, history),
                "recent_chat_history": self.get_recent_chat_history(
                    user_input, history
                ),
            }
        )
        return res["output"]

    def get_related_messages(self, user_input: Message, history: list[Message]):
        self.memory.clear()
        inputs_buffer = []
        for message in history:
            from_user = message["senderId"] == user_input["senderId"]
            if from_user:
                inputs_buffer.append(message["content"])
            else:
                inputs = "\n".join(inputs_buffer)
                output = message["content"]
                inputs_buffer = []
                self.memory.save_context({"user": inputs}, {"you": output})
        return self.memory.load_memory_variables({"prompt": user_input["content"]})[
            "chat_history"
        ]

    def get_recent_chat_history(self, user_input: Message, history: list[Message]):
        recent_chat_history = []
        for message in history[-10:]:
            from_user = message["senderId"] == user_input["senderId"]
            recent_chat_history.append(
                HumanMessage(message["content"])
                if from_user
                else AIMessage(message["content"])
            )
        return recent_chat_history
