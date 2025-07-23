# +
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Document,
    Settings)

from llama_index.core.node_parser import (
    SentenceSplitter,
    SentenceWindowNodeParser
)

DEFAULT_CHUNK_SIZE = 70
DEFAULT_CHUNK_OVERLAP = 25
Settings.embed_model = None
Settings.llm = None
# -

from dataclasses import dataclass
from typing import Dict

from wtpsplit import SaT



@dataclass        
class TextNode:
    """
    Simulate a similar structure to llama index nodes
    """
    metadata: Dict[str, int]
    text: str = ""

    def dict(self):
        return {'metadata':self.metadata,
               'text':self.text}

    def class_name(self):
        return 'TextNode'

class Chunker_SaT:
    """
    Split the input documents into nodes (=chunks), each corresponding to one sentence 
        using the wtpslit splitter: works for all languages. window size parameter controls the number of consecutive 
    sentences that should compose the chunk
    """
    
    def __init__(self,
                 documents_list,
                 language,
                 window_size = 1):

        # Ensure a list of document texts is provided
        if documents_list is None or not isinstance(documents_list, list):
            raise Exception("You must provide a list of texts.")
        
        # Create a list of Document objects from the list of texts
        self.documents = documents_list
        
        # initialize splitter
        self.sat_sm = SaT("sat-1l-sm", style_or_domain="ud", language=language)
        self.nodes = self.chunk_documents(window_size = window_size)  

    
    def chunk_documents(self, window_size: int):
        """
        Split the input documents into sentences.
        Each chunk will have the document index from the input list as metadata.
        """
        nodes = []
        for idx, document in enumerate(self.documents):
            doc_texts = self.sat_sm.split(document)
            if window_size>1:
                doc_texts = [''.join(doc_texts[i:i + window_size]) for i in range(0, len(doc_texts), window_size)]
            for t in doc_texts:
                node = TextNode(text = t.strip(), metadata = {"document_id": idx})
                nodes.append(node)
        return nodes
# -


