import asyncio
from openai import AsyncOpenAI
from pymilvus import AsyncMilvusClient

from app.core.config import Settings
from langchain_openai import ChatOpenAI


class Client:

    def __init__(self):
        settings = Settings()
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL
        self.model_name = settings.MODEL_NAME
        self.milvus_uri = settings.MILVUS_URL
        self._async_openai_client = None
        self._chat_client = None
        self._async_milvus_client = None

    @property
    def async_openai_client(self):
        if self._async_openai_client is None:
            self._async_openai_client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._async_openai_client

    @property
    def async_openai_chat(self):
        if self._chat_client is None:
            self._chat_client = ChatOpenAI(base_url=self.base_url, api_key=self.api_key, model=self.model_name)
        return self._chat_client

    @property
    def async_milvus_client(self):
        if self._async_milvus_client is None:
            self._async_milvus_client = AsyncMilvusClient(uri=self.milvus_uri, db_name="default")
        return self._async_milvus_client


client = Client()
