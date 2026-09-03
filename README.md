# vdblsrv

An asynchronous vector database server with a clean and minimal REST API for similarity search, embeddings storage, and metadata querying.
Designed for AI, retrieval-augmented generation (RAG), semantic search, and realtime recommendation systems.

Built on FAISS engine ( Facebook AI Similarity Search - see https://faiss.ai )


## Features

    Asynchronous server for maximum throughput

    REST API for easy integration with any language

    VDBL - SQL-like language

    Fast vector similarity search

    Collections & metadata filtering

    Batch insert

    Load/Save persistance

    LLightweight & container-friendly


## Installation

Clone the repository:

```
git clone https://github.com/xxx/vdblsrv.git

```

Run the server

```
python3 vdblsrv

```


## Quick Start

Create a collection

```
vdbl> CREATE COLLECTION mycoll1 ( vector[ 4 ] );

```

Insert vectors

```
vdbl> INSERT INTO mycoll1 VALUES ( 1.0, 0.1, 0.2, 0.3 );
vdbl> INSERT INTO mycoll1 VALUES ( 0.1, 0.2, 1.3, 0.4 );
```

Search

```
vdbl> SEARCH FROM mycoll1 USING ( 1.0, 0.0, 0.0, 0.0 ) TOP 1;

{
    'id': '8dcb71f9-8390-49f9-8d6a-ddaed096ead0', 
    'result': {
        'status': 'ok', 
        'result': [{
            'id': '7e1a4e07-9772-46e8-a174-e238c6c83477', 
            'score': 1.0, 
            'metadata': {'list': '[1.0, 0.1, 0.2, 0.3]'}
        }]
    }
}
```


## API Reference

Status

```
GET /api/v1

response = {
    "status": "ok",
    "waiting": 0,
    "done": 0
}
```

Get results

```
GET /api/v1/<uuid>

response = {
    'id': 'b1e6c57d-3499-4c43-8c47-d9beb4a29e02', 
    'result': {
        'status': 'ok',
        'result': <...>
    }
}

```

Send command

```
POST /api/v1

{
    'statement': 'INSERT INTO mycoll1 VALUES ( 0.1, 0.2, 1.3, 0.4 );',
    'timeout': 10
}

response = {

    status': 'ok', 
    'data': {
        'statement': 'INSERT INTO mycoll1 VALUES ( 0.1, 0.2, 1.3, 0.4 );', 
        'id': '6fefcb3a-2c90-48f2-ac60-dd4e7ae1779f'
    }
}

```

Send commands

```
POST /api/v1/batch

{
    'statements': [
        'INSERT INTO mycoll1 VALUES ( 1.0, 0.1, 0.2, 0.3 );',
        'INSERT INTO mycoll1 VALUES ( 0.1, 0.2, 1.3, 0.4 );',
    ],
    'timeout': 10
}

response = {

    status': 'ok', 
    'data': {
        'statements': [
            'INSERT INTO mycoll1 VALUES ( 1.0, 0.1, 0.2, 0.3 );',
            'INSERT INTO mycoll1 VALUES ( 0.1, 0.2, 1.3, 0.4 );',
        ]
        'ids': [ 
            '6fefcb3a-2c90-48f2-ac60-dd4e7ae1779f', 
            '8eefcb3a-2c90-48f2-ac60-dd4e7ae1770a' 
        ]
    }

}

```


## VDBL Reference

### Definition language

```
CREATE COLLECTION <NAME>_( VECTOR [ <VSIZE> ] )
    [ USING <INDEXTYPE> ] 
    [ NLIST <NLIST> ]
    [ NPROBE <NPROBE> ]
    [ M <MNUMBER> ]
    [ EFC <EF_CONSTRUCTION> ]
    [ EFS <EF_SEARCH> ]
    [ METRIC <METRIC> ]
    ;

DROP COLLECTION <NAME>;

, where:

    <NAME> - collection name
    <VSIZE> - size of the vector
    <INDEXTYPE> - default FLAT, HNSW, IVF_FLAT, IVF_HNSW
    <NLIST> - default 256, number of index clusters (partitions)
    <NPROBE> - default 16, number of index centroids ( IVF )
    <MNUMBER> - default 32, number of links ( HNSW )
    <EF_CONSTRUCTION> - default 200, index-building parameter
    <EF_SEARCH> - default 64, search paramater
    <METRIC> - default INNER, L1, L2, LP
```

### Manipulation language

```
INSERT INTO <NAME> VALUES ( <VECTOR> )
                   [ META { <ATTRS> } ] ;

DELETE FROM <NAME> BY UUID <UUID> ;

TRAIN <NAME> VALUES ( <VECTOR> ) ;

, where:

    <NAME> - collection name
    <VECTOR> - float point numbers
    <UUID> - vector identifier
    <ATTRS> - vector attributes

```

### Query language

```
SEARCH FROM <NAME> USING (<VECTOR>) TOP <TOPK> ;

META SEARCH FROM <NAME> LIKE <STRING> ;

, where:

    <NAME> - collection name
    <VECTOR> - float point numbers
    <STRING> - string to search
    <TOPK> - number of relevant items

```

### Persistence language

```
STORE COLLECTION <NAME> ;

RESTORE COLLECTION <NAME> ;

, where:

    <NAME> - collection name

```


## Configuration

    Server address/port, default: 0.0.0.0:9091

    Database folder, default: .

    Log file, default: vdblsrv.log

    Log level, default: 10

  
## Future Development

    Add user authentication

    Add set operations

    Add PQ (Product Quantization) Index

    Add advanced metrics

    Improve error handling

    Improve performance ( FAISS GPU support )


## License

MIT License - free for commercial and personal use.


## Inspired by

pgvector - Open-source vector similarity search for Postgres


## Troubleshooting

If something does not work, try running these commands:

```
# apt install python3
$ pip install faiss_cpu numpy asyncio lark
```

