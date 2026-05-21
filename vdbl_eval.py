# VDBL Eval

import numpy as np
import math
import json
import vdbl_nodes
import engine_faiss
import main
import os
import vdbl_constants as C


class WrapperDB:
    def __init__(self):
        self.collections = {}

    def get_index_filepath(self, name):
        filename = C.DB_FILE_PREFIX + name + C.DB_IDX_SUFFIX
        return str( os.path.join( main.DB_FOLDER, filename) )

    def get_meta_filepath(self, name):
        filename = C.DB_FILE_PREFIX + name + C.DB_META_SUFFIX
        return str( os.path.join( main.DB_FOLDER, filename) )

    def create(self, node: vdbl_nodes.CreateCollection):
        db = engine_faiss.Vdbf(
            dim = node.dim,
            index_type = node.index_type.lower(),
            nlist = node.nlist,
            nprobe = node.nprobe,
            M = node.M,
            ef_construction = node.ef_construction,
            ef_search = node.ef_search,
            index_path = self.get_index_filepath( node.name ),
            meta_path = self.get_meta_filepath( node.name ),
        )
        self.collections[node.name] = db
        return 

    def drop(self, node: vdbl_nodes.DropCollection):
        if node.name in self.collections:
            del self.collections[ node.name ]
        return 

    def store(self, node: vdbl_nodes.StoreCollection):
        db = self.collections[node.name]
        db.save()
        return 

    def restore(self, node: vdbl_nodes.RestoreCollection):
        db = engine_faiss.Vdbf(
            index_path = self.get_index_filepath( node.name ),
            meta_path = self.get_meta_filepath( node.name ),
        )
        db.load()
        self.collections[node.name] = db
        return 

    def insert(self, node: vdbl_nodes.Insert):
        db = self.collections[node.collection]
        if len(node.vector) != db.dim:
            raise ValueError("Vector dimension mismatch")
        np_vec = np.array( [ node.vector ] )
        db.add( np_vec, metadatas=[ node.meta ] )
        
    def train(self, node: vdbl_nodes.SearchMeta):
        db = self.collections[node.collection]
        np_vec = np.array( [ node.vector ] )
        np_vec = np_vec.reshape(int(len(node.vector) / db.dim), db.dim)
        db.train( np_vec )
        return str()

    def delete(self, node: vdbl_nodes.Insert):
        db = self.collections[node.collection]
        db.delete( [ node.rec_id ] )

    def search(self, node: vdbl_nodes.Search):
        db = self.collections[node.collection]
        return db.search( np.array( [ node.query_vector ] ), node.top_k )

    def search_meta(self, node: vdbl_nodes.SearchMeta):
        filename = C.DB_FILE_PREFIX + node.collection + C.DB_META_SUFFIX
        f = open(filename)
        txt = f.read()
        ret = json.loads( txt )[ C.JMETADATA ]
        keys = []
        for key in ret:
            if 0 > str( ret[key] ).find( node.like ):
                keys.append(key)
        for key in keys:
            del ret[key]
        return ret


class Evaluator:
    def __init__(self):
        self.db = WrapperDB()

    def eval(self, node):
        if isinstance(node, vdbl_nodes.CreateCollection):
            self.db.create(node)
        if isinstance(node, vdbl_nodes.DropCollection):
            self.db.drop(node)
        if isinstance(node, vdbl_nodes.StoreCollection):
            self.db.store(node)
        if isinstance(node, vdbl_nodes.RestoreCollection):
            self.db.restore(node)
        if isinstance(node, vdbl_nodes.Insert):
            self.db.insert(node)
        if isinstance(node, vdbl_nodes.Delete):
            self.db.delete(node)
        if isinstance(node, vdbl_nodes.Search):
            return self.db.search(node)
        if isinstance(node, vdbl_nodes.SearchMeta):
            return self.db.search_meta(node)
        if isinstance(node, vdbl_nodes.Train):
            return self.db.train(node)

        return str()
