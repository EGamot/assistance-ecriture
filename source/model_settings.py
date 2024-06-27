from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
azure_ad_token = os.getenv('TOKEN_OPENAI_GPT4')

llm_4 = AzureChatOpenAI(
    deployment_name="poc-aar-sgdy-gpt4-turbo",
    temperature=0,
    openai_api_version="2024-02-15-preview",
    azure_endpoint="https://poc-aar-sgdy.openai.azure.com/",
    openai_api_key=azure_ad_token
    ) #gitleaks:allow