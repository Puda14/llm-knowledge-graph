# llm-knowledge-graph

## Link

|       |  Link                          |
|-------|--------------------------------|
| Neo4j | http://localhost:7474/browser/ |
| Ngrok | http://localhost:4040          |

## Test

### Test Connect MongoDB in Webhook-handler
```python
curl -X POST <ngrok>.ngrok-free.app/github-webhook \
-H "Content-Type: application/json" \
-d '{"user": "test", "pass": "123"}'
```

### Neo4j

Show database
```sh
MATCH (n)-[r]->(m)
RETURN n, r, m
```

Delete database
```sh
MATCH (n)
DETACH DELETE n
```
