# VDBL Transformer

from lark import Transformer
import vdbl_nodes
import vdbl_constants as C


class ASTBuilder(Transformer):
    def NAME(self, t): return str(t)
    def NUMBER(self, t): return float(t)

    def STRING(self, t):
        s = str(t)
        return s[1:-1]  # strip quotes

    def vector(self, items):
        return [float(x) for x in items]

    def attributes(self, items):
        ret = {}
        for i in range(0, len(items), 2):
            ret[ items[ i ] ] = items[ i + 1 ]
        return ret

    def create_collection(self, items):
        name = items[0]
        dim = int(items[1])
        index_type = items[2]
        if index_type is None:
            index_type = C.DEFAULT_INDEX
        nlist = items[3]
        if nlist is None:
            nlist = C.DEFAULT_NLIST
        else:
            nlist = int(nlist)
        nprobe = items[4]
        if nprobe is None:
            nprobe = C.DEFAULT_NPROBE
        else:
            nprobe = int(nlist)
        M = items[5]
        if M is None:
            M = C.DEFAULT_M
        else:
            M = int(M)
        ef_construction = items[6]
        if ef_construction is None:
            ef_construction = C.DEFAULT_JEFC
        else:
            ef_construction = int(ef_construction)
        ef_search = items[7]
        if ef_search is None:
            ef_search = C.DEFAULT_JEFS
        else:
            ef_search = int(ef_search)
        return vdbl_nodes.CreateCollection(
            name,
            dim,
            index_type,
            nlist,
            nprobe,
            M,
            ef_construction,
            ef_search)

    def drop_collection(self, items):
        name = items[0]
        return vdbl_nodes.DropCollection(name)

    def store_collection(self, items):
        name = items[0]
        return vdbl_nodes.StoreCollection(name)

    def restore_collection(self, items):
        name = items[0]
        return vdbl_nodes.RestoreCollection(name)

    def insert_stmt(self, items):
        name = items[0]
        vector = items[1]
        meta = items[2]
        if meta is None:
            meta = { 'list' : str(vector) } # default
        return vdbl_nodes.Insert(name, vector, meta)

    def delete_stmt(self, items):
        collection = items[0]
        rec_id = items[1]
        return vdbl_nodes.Delete(collection, rec_id)

    def search_stmt(self, items):
        name = items[0]
        using = items[1]
        top = int(items[2])
        return vdbl_nodes.Search(name, using, top)

    def search_meta_stmt(self, items):
        collection = items[0]
        like = items[1]
        return vdbl_nodes.SearchMeta(collection, like)

    def train_stmt(self, items):
        name = items[0]
        vector = items[1]
        return vdbl_nodes.Train(name, vector)

    def statement(self, items):
        return items[0]
