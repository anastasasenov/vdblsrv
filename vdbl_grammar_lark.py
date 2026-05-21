# VDBL language grammar
#   - vector database definition language
#   - vector database manipulation language
#   - vector database query language

_G =  '    ?start: statement \n'

_G += '    ?statement: '
_G += '        create_collection | '
_G += '        drop_collection | '
_G += '        store_collection | '
_G += '        restore_collection | '
_G += '        insert_stmt | '
_G += '        delete_stmt | '
_G += '        train_stmt | '
_G += '        search_stmt | '
_G += '        search_meta_stmt \n'

# vector database definition language ( VDBDL )
_G += '    create_collection: '
_G += '        "CREATE"i "COLLECTION"i NAME '
_G += '        "(" "VECTOR"i "[" NUMBER "]" ")" '
_G += '        [ "USING"i INDEXTYPE ] '
_G += '        [ "NLIST"i NUMBER ] '
_G += '        [ "NPROBE"i NUMBER ] '
_G += '        [ "M"i NUMBER ] '
_G += '        [ "EFC"i NUMBER ] '
_G += '        [ "EFS"i NUMBER ] '
_G += '        [ "METRIC"i METRIC ] '
_G += '        ";" \n'
_G += '    drop_collection: '
_G += '        "DROP"i "COLLECTION"i NAME ";" \n'
# persistence
_G += '    store_collection: '
_G += '        "STORE"i "COLLECTION"i NAME ";" \n'
_G += '    restore_collection: '
_G += '        "RESTORE"i "COLLECTION"i NAME ";" \n'

# vector database manipulation language ( VDBML )
_G += '    insert_stmt: '
_G += '        "INSERT"i "INTO"i NAME'
_G += '        "VALUES"i '
_G += '        "(" vector ")" '
_G += '        [ "META"i "{" attributes "}" ] ";" \n'
_G += '    delete_stmt: '
_G += '        "DELETE"i "FROM"i NAME'
_G += '        "BY"i "UUID"i UUID  ";" \n'
# training
_G += '    train_stmt: '
_G += '        "TRAIN"i NAME'
_G += '        "VALUES"i "(" vector ")" ";" \n'

# vector database query language ( VDBQL )
_G += '    search_stmt: '
_G += '        "SEARCH"i "FROM"i NAME '
_G += '        "USING"i "(" vector ")" '
_G += '        "TOP"i NUMBER ";" \n'
_G += '    search_meta_stmt: '
_G += '        "META"i "SEARCH"i "FROM"i NAME '
_G += '        "LIKE"i STRING ";" \n'

# language details
_G += '    vector: NUMBER ("," NUMBER)* \n'
_G += '    attributes: STRING ":" STRING ("," STRING ":" STRING)* \n'

_G += '    METRIC: "INNER"i | "L1"i | "L2"i | "LP"i \n'
_G += '    INDEXTYPE: "FLAT"i | "HNSW"i | "IVF_FLAT"i | "IVF_HNSW"i \n'
_G += '    NAME: /[a-zA-Z_][a-zA-Z0-9_]*/ \n'
_G += '    UUID: /[a-fA-F0-9-]+/ \n'
_G += '    STRING: ESCAPED_STRING \n'
_G += '    NUMBER: SIGNED_NUMBER \n'

_G += '    %import common.ESCAPED_STRING \n'
_G += '    %import common.SIGNED_NUMBER \n'
_G += '    %import common.WS \n'
_G += '    %ignore WS \n'

VDBL_GRAMMAR = str( _G )

