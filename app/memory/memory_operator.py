import asyncio
from typing import List, Any

from mem0 import AsyncMemory

from app.core.config import settings


class MemoryOperator:
    def __init__(self):
        provider = settings.VECTOR_PROVIDER
        vector_url = settings.MILVUS_URL if provider == "milvus" else settings.redis_url
        vector_config_key = "url" if provider == "milvus" else "redis_url"
        self.config = {
            "llm": {
                "provider": settings.MODEL_PROVIDER,
                "config": {
                    "model": settings.MODEL_NAME,
                    "api_key": settings.OPENAI_API_KEY,
                    "max_tokens": 2000,
                    "temperature": 0.2
                }
            },
            "embedder": {
                "provider": settings.EMBEDDING_PROVIDER,
                "config": {
                    "model": settings.EMBEDDING_MODEL,
                    "openai_base_url": settings.EMBEDDING_BASE_URL,
                    "api_key": settings.EMBEDDING_API_KEY,

                }
            },
            "vector_store": {
                "provider": provider,
                "config": {
                    "collection_name": settings.COLLECTION_NAME,
                    "embedding_model_dims": settings.DIMENSION,
                    vector_config_key: vector_url
                }
            }
        }

        self.memory_operator = None

    async def _init_memory_operator(self):
        if not self.memory_operator:
            self.memory_operator = await AsyncMemory.from_config(config_dict=self.config)
        return self.memory_operator

    async def add_memory(self, messages: List[dict[str, Any]], user_id=None, agent_id=None,
                         run_id=None):
        self.memory_operator = await self._init_memory_operator()
        args = {"messages": messages}
        if user_id:
            args["user_id"] = user_id
        if agent_id:
            args["agent_id"] = agent_id
        if run_id:
            args["run_id"] = run_id
        data = await self.memory_operator.add(**args,
                                              metadata={"type": "user_event"})
        return data

    async def get_memory(self, user_id, agent_id=None,
                         run_id=None):
        self.memory_operator = await self._init_memory_operator()
        args = {"user_id": user_id}
        if agent_id:
            args["agent_id"] = agent_id
        if run_id:
            args["run_id"] = run_id
        data = await self.memory_operator.get_all(**args, filters={"type": "user_event"})
        return data

    async def search_memory(self, query, user_id, agent_id=None,
                            run_id=None):
        self.memory_operator = await self._init_memory_operator()
        args = {"user_id": user_id, "query": query}
        if agent_id:
            args["agent_id"] = agent_id
        if run_id:
            args["run_id"] = run_id
        data = await self.memory_operator.search(**args)
        return data

    async def delete_user_memory(self, user_id, agent_id=None,
                                 run_id=None):
        self.memory_operator = await self._init_memory_operator()
        args = {"user_id": user_id}
        if agent_id:
            args["agent_id"] = agent_id
        if run_id:
            args["run_id"] = run_id
        data = await self.memory_operator.delete_all(**args)
        return data

    async def delete_one_memory(self, memory_id):
        self.memory_operator = await self._init_memory_operator()
        data = await self.memory_operator.delete(memory_id=memory_id)
        return data


