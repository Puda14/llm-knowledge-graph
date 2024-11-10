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
