from langchain.schema import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS

from beans import Message
from logger import logger
from config import config


class BaseAgent:
    def __init__(self, llm, tools, prompt):
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

    def get_related_messages(
        self, user_input: Message, history: list[Message], window_size=10, k=2
    ):
        """
        获取与用户输入相关的消息历史，用于模型输入
        将聊天记录每window_size条消息作为一个document
        使用vector search获取与用户输入相关的document
        返回k个聊天窗口
        """
        assert window_size > 0, "window_size should be greater than 0"
        assert k > 0, "k should be greater than 0"
        if len(history) == 0:
            return ""
        message_window = []
        docs = []
        for _message in history:
            message = _message.copy()
            from_user = message["senderId"] == user_input["senderId"]
            prefix = "user: " if from_user else "you: "
            message["content"] = prefix + message["content"]
            message_window.append(message)
            if len(message_window) == window_size:
                # window_size条消息为一个窗口
                docs.append(
                    Document(
                        page_content="\n".join(
                            message["content"] for message in message_window
                        ),
                        metadata={
                            "timestamp": message["timestamp"],
                            "type": message["type"],
                        },
                    )
                )
                message_window = []
        if len(message_window) > 0:
            docs.append(
                Document(
                    page_content="\n".join(
                        message["content"] for message in message_window
                    ),
                    metadata={
                        "timestamp": message["timestamp"],
                        "type": message["type"],
                    },
                )
            )
        db = FAISS.from_documents(
            docs, OpenAIEmbeddings(base_url=config.openai_base_url)
        )
        releted_docs = db.similarity_search(user_input["content"], k=k)
        res = ""
        for doc in releted_docs:
            res += doc.metadata["timestamp"] + "\n"
            res += doc.page_content + "\n"
        return res

    def get_recent_chat_history(
        self, user_input: Message, history: list[Message], messages_num=10
    ):
        """
        获取最近的messages_num条消息，用于模型输入
        """
        assert messages_num > 0, "messages_num should be greater than 0"
        recent_chat_history = []
        for message in history[-messages_num:]:
            from_user = message["senderId"] == user_input["senderId"]
            recent_chat_history.append(
                HumanMessage(message["content"])
                if from_user
                else AIMessage(message["content"])
            )
        return recent_chat_history
