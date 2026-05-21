# AST nodes

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

class ASTNode:
    pass

@dataclass
class CreateCollection(ASTNode):
    name: str
    dim: int
    index_type: str                        ### "FLAT" or ...
    nlist: int
    nprobe: int
    M: int
    ef_construction: int
    ef_search: int

@dataclass
class DropCollection(ASTNode):
    name: str

@dataclass
class StoreCollection(ASTNode):
    name: str

@dataclass
class RestoreCollection(ASTNode):
    name: str

@dataclass
class Insert(ASTNode):
    collection: str
    vector: List[float]
    meta: Dict[str, str]

@dataclass
class Search(ASTNode):
    collection: str
    query_vector: Optional[List[float]]
    top_k: int

@dataclass
class SearchMeta(ASTNode):
    collection: str
    like : str

@dataclass
class Delete(ASTNode):
    collection: str
    rec_id : str

@dataclass
class Train(ASTNode):
    collection: str
    vector: List[float]
