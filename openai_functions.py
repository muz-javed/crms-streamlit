import os
import streamlit as st
import langchain
import openai
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_core.tools import Tool, StructuredTool
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from langchain.schema import SystemMessage
from langchain.memory import ConversationBufferMemory

api_key = "sk-svcacct-GKTLsVX_k40dbZcyLsSOm5xxeWofLmuLUa6J9vxhEuL6DT3BlbkFJQFKZyZNQh3pLQeGSd5qsJuRKPBjAxOpZAqzuYV_erZ-AA"
GOOGLE_API_KEY = "AIzaSyBjWM0cyxXBjoiRgdh7cFbSJImF6U05HpU"
GOOGLE_CSE_ID = "d6a7169ef0a274385"

import requests

# Replace these with your actual API key and CSE ID
query = 'Python programming'  # Replace with your search query

# Construct the URL for the API request
url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={query}"

# Send the GET request to the API
response = requests.get(url)

# Parse the JSON response
results = response.json()

# Check if the request was successful
if 'items' in results:
    for i, item in enumerate(results['items'], start=1):
        st.write(f"Result {i}:")
        st.write(f"Title: {item['title']}")
        st.write(f"Link: {item['link']}\n")
else:
    st.write("No results found or there was an error with the request.")






# os.environ['GOOGLE_API_KEY'] = "AIzaSyBjWM0cyxXBjoiRgdh7cFbSJImF6U05HpU"
# os.environ['GOOGLE_CSE_ID'] = "d6a7169ef0a274385"

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
