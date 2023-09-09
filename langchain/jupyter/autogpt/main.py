import faiss
import os
import gradio as gr
from autogpt_config import AutoGptConfig
from langchain.utilities import SerpAPIWrapper
from langchain.agents import Tool
from langchain.tools.file_management.write import WriteFileTool
from langchain.tools.file_management.read import ReadFileTool
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore
from langchain_experimental.autonomous_agents import AutoGPT
from langchain.chat_models import ChatOpenAI
from utils import ArgumentParser, LOG
from flask import Flask, jsonify, request

def initialize_autogpt():
    SERPAPI_API_KEY = config.SERPAPI_API_KEY
    OPENAI_API_KEY = config.OPENAI_API_KEY

    # Initialize external APIs
    search = SerpAPIWrapper(serpapi_api_key=SERPAPI_API_KEY)
    tools = [
        Tool(
            name="search",
            func=search.run,
            description="useful for when you need to answer questions about current events. You should ask targeted questions",
        ),
        WriteFileTool(),
        ReadFileTool(),
    ]

    # OpenAI Embedding 模型
    embeddings_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    # Initialize OpenAI Embeddings and Faiss
    embedding_size = 1536
    index = faiss.IndexFlatL2(embedding_size)
    vectorstore = FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {})

    # Initialize AutoGPT agent
    agent = AutoGPT.from_llm_and_tools(
        ai_name="Yang",
        ai_role="Assistant",
        tools=tools,
        llm=ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY),
        memory=vectorstore.as_retriever(), # 实例化 Faiss 的 VectorStoreRetriever
    )
    # Enable logging
    agent.chain.verbose = False

    return agent

def qa(query, agent):
    return agent.run([query])

if __name__ == "__main__":
    # 解析命令行
    argument_parser = ArgumentParser()
    args = argument_parser.parse_arguments()

    # 初始化配置单例
    config = AutoGptConfig()
    config.initialize(args) 

    # 初始化 translator
    agent = initialize_autogpt()

    iface = gr.Interface(
        fn=lambda query: qa(query, agent),
        inputs="text",
        outputs="text",
        title="AutoGPT Q&A",
        description="Ask questions and get answers using AutoGPT.",
    )

    iface.launch()
