from llama_index.retrievers.bm25 import BM25Retriever
from typing import List, Dict

from rank_bm25 import BM25Okapi

from dataclasses import dataclass

from tools.chunker import TextNode
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


retriever_bge = AutoModelForSequenceClassification.from_pretrained('BAAI/bge-reranker-v2-m3')
tokenizer_bge = AutoTokenizer.from_pretrained('BAAI/bge-reranker-v2-m3')


class Retriever_bm25:
    """
    BM25 retriever that can be used with any knowledge base 
    (both llama index nodes and generic text nodes as defined in chunker)
    """
    def __init__(self,
                 knowledge_base,
                 name='BM25',
                 top_k=3):

        self.name = name
        self.top_k = top_k
        self.knowledge_base = list(knowledge_base.nodes)
        self.set_retriever()

    def set_retriever(self):
        if self.knowledge_base is None or len(self.knowledge_base) == 0:
            print("Error: Knowledge base is empty!")
            self.retriever = None
            return

        if self.name == 'BM25':
            self.corpus = [doc.text for doc in self.knowledge_base]  # Store corpus
            tokenized_docs = [doc.split(" ") for doc in self.corpus]

            if len(self.corpus) == 0:
                print("Error: Corpus is empty! BM25 retriever cannot be initialized.")
                self.retriever = None
                return
            self.retriever = BM25Okapi(tokenized_docs)
            print(f"BM25 retriever initialized with {len(self.corpus)} documents.")
            
        else:
            print("RetrieverModule Error: Select a valid retriever.")
            self.retriever = None

    def retrieve(self, query: str):
        """
        Retrieve top n most similar chunks to the query
        """      
        if self.retriever is None:
            raise ValueError("Retriever is not initialized. Check if knowledge base is empty.")

        text_metadata_dict = {node.dict()['text']: node.dict()['metadata'] for node in self.knowledge_base}
        tokenized_query = query.split(" ")
        # Ensure we're using the same corpus that was used to initialize BM25
        retrieved_docs = self.retriever.get_top_n(tokenized_query, self.corpus, n=self.top_k)

        return [TextNode(text=retrieved_doc.strip(), metadata=text_metadata_dict[retrieved_doc]) for retrieved_doc in retrieved_docs]

