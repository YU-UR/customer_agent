from pymilvus import DataType, AnnSearchRequest, RRFRanker

from app.core.client import client


class AsyncMilvusOperator:

    def __init__(self,collection_name):
        self.client = client.async_milvus_client
        self.collection_name = collection_name


    async def create_schema(self):
        schema = self.client.create_schema(auto_id=True, description="这是通用知识库的参数模型")
        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True, description="主键")
        schema.add_field(field_name="dense_vector", datatype=DataType.FLOAT_VECTOR, dim=1536,
                         description="这是密集向量")
        schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR,
                         description="这是稀疏向量")
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=4096, description="这是文本内容")
        return schema

    async def create_collection(self):
        await self.client.create_collection(collection_name=self.collection_name,
                                                                        schema=await self.create_schema(),
                                                                        description="这是通用知识库")
        index_params = self.client.prepare_index_params()
        index_params.add_index(field_name="dense_vector", index_type="FLAT", metric_type="COSINE")
        index_params.add_index(field_name="sparse_vector", index_type="SPARSE_INVERTED_INDEX", metric_type="IP")
        await self.client.create_index(collection_name=self.collection_name, index_params=index_params)

    async def insert_vector(self, data):
        res = await self.client.insert(collection_name=self.collection_name, data=data)
        return res

    async def search_vector(self, question_vector):
        res = await client.async_milvus_client.search(collection_name=self.collection_name, data=question_vector, limit=10,
                                                      output_fields=["text"])
        return res

    async def mix_search_vector(self, dense_vector, sparse_vector):
        await self.client.load_collection(collection_name=self.collection_name)
        req_dense = AnnSearchRequest(
            data=[dense_vector],
            anns_field="dense_vector",
            param={"metric_type": "COSINE"},
            limit=10,
        )
        req_sparse = AnnSearchRequest(
            data=[sparse_vector],
            anns_field="sparse_vector",
            param={"metric_type": "IP"},
            limit=10,
        )
        reqs = [req_dense, req_sparse]
        ranker = RRFRanker(k=10)
        res = await self.client.hybrid_search(collection_name=self.collection_name, reqs=reqs,
                                                             output_fields=["text"],
                                                             ranker=ranker)
        return res
