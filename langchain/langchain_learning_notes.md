## LangChain 学习笔记

我从github 上找了一个学习的例子。

We've seen in previous chapters how powerful retrieval augmentation and conversational agents can be. They become even more impressive when we begin using them together.

Conversational agents can struggle with data freshness, knowledge about specific domains, or accessing internal documentation. By coupling agents with retrieval augmentation tools we no longer have these problems.

One the other side, using "naive" retrieval augmentation without the use of an agent means we will retrieve contexts with every query. Again, this isn't always ideal as not every query requires access to external knowledge.

Merging these methods gives us the best of both worlds. In this notebook we'll learn how to do this.

To begin, we must install the prerequisite libraries that we will be using in this notebook.

在前面的章节中，我们已经看到了检索增强和对话代理可以有多么强大。当我们开始将它们结合在一起使用时，它们变得更加令人印象深刻。

对话代理在处理数据新鲜度、特定领域知识或访问内部文档方面可能会遇到困难。通过将代理与检索增强工具结合使用，我们就不再面临这些问题。

另一方面，如果在不使用代理的情况下使用“简单”的检索增强，意味着我们将在每次查询时都检索上下文。同样，这并不总是理想的，因为并不是每个查询都需要访问外部知识。

将这些方法合并在一起，我们就可以兼顾两者的优点。在这个笔记本中，我们将学习如何实现这一点。

首先，我们必须安装在这个笔记本中将要使用的必备库。

步骤包括：
1. Building the Knowledge Base
2. Initialize the Embedding Model and Vector DB
3. Indexing
4. Creating a Vector Store and Querying
5. Initializing the Conversational Agent
6. Using the Conversational Agent

-------
1. 构建知识库
2. 初始化嵌入模型和向量数据库
3. 创建索引
4. 创建向量存储并进行查询
5. 初始化对话代理
6. 使用对话代理

我的基于网上的一个教程。
https://github.com/pinecone-io/examples/blob/master/learn/generation/langchain/handbook/08-langchain-retrieval-agent.ipynb

我的输出在这里：https://github.com/sycao5/openai-quickstart/blob/yang-lanchain/langchain/08-langchain-retrieval-agent.ipynb

今天还会仔细看