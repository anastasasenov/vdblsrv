# FAISS engine
# ( Facebook AI Similarity Search - see https://faiss.ai )
#
#   Insert / delete / search
#   Persist to disk
#
#    Supports index types:
#      - flat
#      - hnsw
#      - ivf_flat
#      - ivf_hnsw
#
# todo: GPU FAISS

import faiss
import numpy as np
import json
import uuid
import os
from typing import List, Dict, Any, Optional #note: python3.8
import vdbl_constants as C

class Vdbf:

    # Contructor
    def __init__(
        self,
        dim: int = 3,
        index_type: str = "flat",   # flat | hnsw | ivf_flat | ivf_hnsw
        nlist: int = 256,
        nprobe: int = 16,
        M: int = 32,
        ef_construction: int = 200,
        ef_search: int = 64,
        metric: str = "inner",
        index_path: Optional[str] = None,
        meta_path: Optional[str] = None,
    ):
        self.dim = dim
        self.index_type = index_type
        self.nprobe = nprobe
        self.index_path = index_path
        self.meta_path = meta_path
        self.metric = faiss.METRIC_INNER_PRODUCT
        self.nlist = nlist
        self.M = M
        self.ef_construction = ef_construction
        self.ef_search = ef_search
        
        if metric == "inner":
            self.metric = faiss.METRIC_INNER_PRODUCT
        elif metric == "l1":
            self.metric = faiss.L1
        elif metric == "l2":
            self.metric = faiss.L2
        elif metric == "lp":
            self.metric = faiss.Lp

        # ID management
        self.next_int_id: int = 0
        self.uuid_to_int: Dict[str, int] = {}
        self.int_to_uuid: Dict[int, str] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}

        self.index = self._create_index(
            dim=dim,
            index_type=index_type,
            nlist=nlist,
            M=M,
            ef_construction=ef_construction,
            ef_search=ef_search,
        )
        return


    # Index creation
    def _create_index(
        self,
        dim: int,
        index_type: str,
        nlist: int,
        M: int,
        ef_construction: int,
        ef_search: int,
    ):
        if index_type == "flat":
            base = faiss.IndexFlatIP(dim)

        elif index_type == "hnsw":
            base = faiss.IndexHNSWFlat(dim, M, self.metric)
            base.hnsw.efConstruction = ef_construction
            base.hnsw.efSearch = ef_search

        elif index_type == "ivf_flat":
            quantizer = faiss.IndexFlatIP(dim)
            base = faiss.IndexIVFFlat(
                quantizer, dim, nlist, self.metric
            )

        elif index_type == "ivf_hnsw":
            quantizer = faiss.IndexHNSWFlat(dim, M, self.metric)
            quantizer.hnsw.efConstruction = ef_construction

            base = faiss.IndexIVFFlat(
                quantizer, dim, nlist, self.metric
            )

        else:
            raise ValueError(f"Unsupported index type: {index_type}")

        return faiss.IndexIDMap2(base)


    # Training (ivf_flat | ivf_hnsw)
    def train(self, vectors: np.ndarray):
        if not self.index.is_trained:
            self.index.train(vectors)


    # Add
    def add(
        self,
        vectors: np.ndarray,
        metadatas: List[Dict[str, Any]],
    ) -> List[str]:
        if vectors.shape[1] != self.dim:
            raise ValueError("Vector dimension mismatch")

        if not self.index.is_trained:
            raise RuntimeError("Index must be trained before add()")

        count = len(vectors)
        int_ids = np.arange(
            self.next_int_id,
            self.next_int_id + count,
            dtype="int64",
        )

        uuids = []
        for int_id, meta in zip(int_ids, metadatas):
            uid = str(uuid.uuid4())
            uuids.append(uid)

            self.uuid_to_int[uid] = int(int_id)
            self.int_to_uuid[int(int_id)] = uid
            self.metadata[uid] = meta

        if hasattr(self.index, C.NPROBE):
            self.index.nprobe = self.nprobe

        self.index.add_with_ids(vectors, int_ids)
        self.next_int_id += count

        return uuids


    # Delete (TRUE FAISS DELETE)
    def delete(self, ids: List[str]) -> int:
        int_ids = []

        for uid in ids:
            int_id = self.uuid_to_int.get(uid)
            if int_id is not None:
                int_ids.append(int_id)

        if not int_ids:
            return 0

        selector = faiss.IDSelectorBatch(
            np.array(int_ids, dtype="int64")
        )

        removed = self.index.remove_ids(selector)

        for int_id in int_ids:
            uid = self.int_to_uuid.pop(int_id, None)
            if uid:
                self.uuid_to_int.pop(uid, None)
                self.metadata.pop(uid, None)

        return int(removed)


    # Search
    def search(
        self,
        query_vector: np.ndarray,
        k: int = 5,
    ) -> List[Dict[str, Any]]:
        if hasattr(self.index, C.NPROBE):
            self.index.nprobe = self.nprobe

        scores, int_ids = self.index.search(query_vector, k)

        results = []
        for score, int_id in zip(scores[0], int_ids[0]):
            if int_id == -1:
                continue

            uid = self.int_to_uuid.get(int(int_id))
            if not uid:
                continue

            results.append({
                C.JID: uid,
                C.JSCORE: float(score),
                C.JMETADATA: self.metadata.get(uid),
            })

        return results


    # Persistence to files
    def save(self):
        if not self.index_path or not self.meta_path:
            raise ValueError("index_path and meta_path are required")

        faiss.write_index(self.index, self.index_path)

        with open(self.meta_path, "w", encoding=C.UTF) as f:
            json.dump(
                {
                    "next_int_id": self.next_int_id,
                    "uuid_to_int": self.uuid_to_int,
                    "int_to_uuid": self.int_to_uuid,
                    C.JDIM: self.dim,
                    C.JINDEX_TYPE: self.index_type,
                    C.JNPROBE: self.nprobe,
                    C.JNLIST: self.nlist,
                    C.JMETRIC: self.metric,
                    C.JM: self.M,
                    C.JEFC: self.ef_construction,
                    C.JEFS: self.ef_search,
                    C.JMETADATA: self.metadata,
                },
                f,
                indent=2,
            )
        return

    def load(self):
        
        self.index = faiss.read_index(self.index_path)

        with open(self.meta_path, "r", encoding=C.UTF) as f:
            data = json.load(f)

        self.next_int_id = data["next_int_id"]
        self.uuid_to_int = {
            k: int(v) for k, v in data["uuid_to_int"].items()
        }
        self.int_to_uuid = {
            int(k): v for k, v in data["int_to_uuid"].items()
        }
        self.dim = int(data[C.JDIM])
        self.index_type = data[C.JINDEX_TYPE]
        self.nprobe = int(data[C.JNPROBE])
        self.nlist = int(data[C.JNLIST])
        self.metric = int(data[C.JMETRIC])
        self.M = int(data[C.JM])
        self.ef_construction = int(data[C.JEFC])
        self.ef_search = int(data[C.JEFS])
        self.metadata = data[C.JMETADATA]
        
        self.index = self._create_index(
            dim=self.dim,
            index_type=self.index_type,
            nlist=self.nlist,
            M=self.M,
            ef_construction=self.ef_construction,
            ef_search=self.ef_search,
        )
        return

