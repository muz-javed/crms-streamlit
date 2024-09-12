import os
import streamlit as st
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS

api_key = "sk-svcacct-GKTLsVX_k40dbZcyLsSOm5xxeWofLmuLUa6J9vxhEuL6DT3BlbkFJQFKZyZNQh3pLQeGSd5qsJuRKPBjAxOpZAqzuYV_erZ-AA"
GOOGLE_API_KEY = "AIzaSyBjWM0cyxXBjoiRgdh7cFbSJImF6U05HpU"
GOOGLE_CSE_ID = "d6a7169ef0a274385"

os.environ['GOOGLE_API_KEY'] = "AIzaSyBjWM0cyxXBjoiRgdh7cFbSJImF6U05HpU"
os.environ['GOOGLE_CSE_ID'] = "d6a7169ef0a274385"

chat = ChatOpenAI(
    openai_api_key = api_key,
    temperature=0.7
)
 
search = GoogleSearchAPIWrapper()
 
prompt = ChatPromptTemplate.from_template(
    """Answer the question based only on the context provided.
    Context: {context}
    Question: {question}"""
)


def external_bankruptcy_status(df):
    def is_customer_bankrupt(name):
        st.write(name)
        input_val = f"Is {name} currently bankrupt? Answer with 'Yes' or 'No' at the beginning of your response. If 'Yes', provide specific references such as recent financial statements, news reports, or official filings that indicate the bankruptcy status."
        response = search.run(f"Is {name} bankrupt")
        st.write(response)
        vectorstore = FAISS.from_texts(
            [response], embedding=OpenAIEmbeddings(api_key = "sk-svcacct-GKTLsVX_k40dbZcyLsSOm5xxeWofLmuLUa6J9vxhEuL6DT3BlbkFJQFKZyZNQh3pLQeGSd5qsJuRKPBjAxOpZAqzuYV_erZ-AA")
        )
        output_retriever = vectorstore.as_retriever()
        output_chain = (
                RunnablePassthrough.assign(context=(lambda x: x["question"]) | output_retriever)
                | prompt
                | chat
                | StrOutputParser()
        )
        output = output_chain.invoke({"question": input_val})
        if output[0] == "Y":
            out_val = "Yes"
        else:
            out_val = "No"
        return out_val
    df['external_bankruptcy_flag'] = df['Customer Name'].apply(is_customer_bankrupt)
    return df




















 
# # def bankruptcy_status(df):


# def external_bankruptcy_status(name):
#     input_val = f"Is {name} currently bankrupt? Answer with 'Yes' or 'No' at the beginning of your response. If 'Yes', provide specific references such as recent financial statements, news reports, or official filings that indicate the bankruptcy status."
#     response = search.run(f"Is {name} bankrupt")
#     vectorstore = FAISS.from_texts(
#         [response], embedding=OpenAIEmbeddings(api_key = "sk-svcacct-GKTLsVX_k40dbZcyLsSOm5xxeWofLmuLUa6J9vxhEuL6DT3BlbkFJQFKZyZNQh3pLQeGSd5qsJuRKPBjAxOpZAqzuYV_erZ-AA")
#     )
#     output_retriever = vectorstore.as_retriever()
#     output_chain = (
#             RunnablePassthrough.assign(context=(lambda x: x["question"]) | output_retriever)
#             | prompt
#             | chat
#             | StrOutputParser()
#     )
#     output = output_chain.invoke({"question": input_val})
#     # st.write(output)
#     if output[0] == "Y":
#         out_val = 1
#     else:
#         out_val = 0
#     return out_val
    
# # def bankruptcy_status(df):
    
# #     df['external_bankruptcy_flag'] = df['Customer Name'].apply(is_customer_bankrupt)
#     return df
































# chat = ChatOpenAI(
#     openai_api_key = api_key,
#     temperature=0.7
# )

# chat_prompt = ChatPromptTemplate(
#     messages=[
#         MessagesPlaceholder(variable_name="chat_history"),
#         HumanMessagePromptTemplate.from_template("{input}"),
#         MessagesPlaceholder(variable_name="agent_scratchpad")
#     ]
# )

# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# search = GoogleSearchAPIWrapper()

# tool = StructuredTool.from_function(
#     name="google_search",
#     description="Input to this tool must be a SINGLE JSON STRING.",
#     func=search.run
# )

# agent = OpenAIFunctionsAgent(
#     llm=chat,
#     prompt=chat_prompt,
#     tools=[tool]
# )

# agent_executor = AgentExecutor(
#     agent=agent,
#     verbose=True,
#     tools=[tool],
#     memory=memory
# )

# def bankruptcy_status(df):
#     def is_customer_bankrupt(name):
#         input_val = f"Is {name} currently bankrupt? Answer with 'Yes' or 'No' at the beginning of your response. If 'Yes', provide specific references such as recent financial statements, news reports, or official filings that indicate the bankruptcy status."
#         result = agent_executor(f"{input_val}")
#         if result["output"][0] == "Y":
#             out_val = 1
#         else:
#             out_val = 0
#         return out_val
#     df["LFI files for obligor's bankruptcy"]=df['customer_name'].apply(is_customer_bankrupt)

#     cols = df.columns.tolist()
#     line_of_business_index = cols.index('line_of_business')
#     cols.insert(line_of_business_index + 1, cols.pop(cols.index("LFI files for obligor's bankruptcy")))

#     # Reassign the reordered columns back to the DataFrame
#     df = df[cols]




#     return df
