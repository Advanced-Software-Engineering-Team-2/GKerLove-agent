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
        attached_messages = self.get_recent_chat_history(user_input, history)
        related_messages = self.get_related_messages(user_input, history)
        res = self.agent_executor.invoke(
            {
                "user_input": user_input["content"],
                "related_messages": related_messages,
                "recent_chat_history": attached_messages,
            }
        )
        return res["output"]

    def get_related_messages(
        self,
        user_input: Message,
        history: list[Message],
    ):
        """
        获取与用户输入相关的消息历史，用于模型输入
        将聊天记录每window_size条消息作为一个document
        使用vector search获取与用户输入相关的document
        返回k个聊天窗口
        """
        # 如果没有历史消息，返回空字符串
        if len(history) == 0:
            return ""
        message_window = []
        docs = []
        attached_messages = history[-10:]
        for _message in history:
            # 首先检查是否在messages_attached中
            flag = False
            for attached_message in attached_messages:
                if _message["_id"] == attached_message["_id"]:
                    # 在messages_attached中，不需要再加入message_window
                    flag = True
                    break
            if flag:
                continue
            # 不在messages_attached中，加入message_window
            message = _message.copy()
            from_user = message["senderId"] == user_input["senderId"]
            prefix = "user: " if from_user else "you: "
            message["content"] = prefix + message["content"]
            message_window.append(message)
            if len(message_window) == 6:
                # 6条消息为一个窗口，创建一个document
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
        if len(docs) == 0:
            return ""
        db = FAISS.from_documents(
            docs, OpenAIEmbeddings(base_url=config.openai_base_url)
        )
        # 在相似度阈值大于0.5的情况下，返回最相关的一条消息
        retriever = db.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"score_threshold": 0.5, "k": 2},
        )
        releted_docs = retriever.get_relevant_documents(user_input["content"])
        # 如果没有相关的消息，返回空字符串
        if len(releted_docs) == 0:
            return ""
        # 返回相关的消息
        res = "由于聊天记录窗口只能展示部分对话历史，以下是与用户此次发送消息可能相关的一些对话历史片段（user: 后面是用户的信息，you: 是你之前回复的信息，第一行是对话发生的时间），这部分信息可能帮助你做出更好的回答，但注意不要重复你之前的回复：\n"
        for doc in releted_docs:
            res += doc.metadata["timestamp"] + "\n"
            res += doc.page_content + "\n"
        res = res.strip()
        return res

    def get_recent_chat_history(self, user_input: Message, history: list[Message]):
        """
        获取最近的10条消息，作为模型聊天上下文
        """
        recent_chat_history = []
        for message in history[-10:]:
            from_user = message["senderId"] == user_input["senderId"]
            recent_chat_history.append(
                HumanMessage(message["content"])
                if from_user
                else AIMessage(message["content"])
            )
        return recent_chat_history
