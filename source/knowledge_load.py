import json
from pathlib import Path
from typing import List, Optional, Union
from llama_index.core.schema import Document
from langchain.document_loaders.base import BaseLoader

class JSONLoader(BaseLoader):
    def __init__(
        self,
        file_path: Union[str, Path],
        content_key: Optional[str] = None,
        ):
        self.file_path = Path(file_path).resolve()
        self._content_key = content_key
    def load(self) -> List[Document]:
        """Load and return documents from the JSON file."""
        docs = []
        # Load JSON file
        with open(self.file_path, encoding='utf-8') as file:
            data = json.load(file)
        for bloc in data: 
            for question in bloc["content"]["enriched"]:
                metadata_title = bloc["meta"]["title"]
                metadata_category = bloc["meta"]["targets"]["category"] 
                if metadata_category is None:
                    continue
                metadata_url = bloc["meta"]["url"]
                titre = question["question"]
                answers = question["answer"]
                summary = bloc["meta"]['summary']
                docs.append(Document(text = answers, metadata = {"category": metadata_category, "title": metadata_title, "subtitle": titre, "summary": summary, "url": metadata_url}))               
        return docs
    
#load documents
file_path = r"source/enriched_articles_999.json"
loader = JSONLoader(file_path = file_path)
data_sample = loader.load()