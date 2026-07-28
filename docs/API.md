# 🌐 Astra API

## Base URL

```
http://localhost:8000
```

---

# Health

## GET /

Returns API status.

Example Response

```json
{
  "status": "online",
  "assistant": "Astra",
  "version": "1.0.0"
}
```

---

# Chat

## POST /chat

Streams AI responses.

Request

```json
{
  "message": "Hello Astra"
}
```

Response

```
Streaming text/plain
```

---

# Browser

## POST /browser/search

Performs AI-assisted web search.

Request

```json
{
  "query": "Best AI internships"
}
```

---

# Future Endpoints

## Memory

POST /memory/save

GET /memory

DELETE /memory/{id}

---

## Files

POST /files/upload

POST /files/analyze

---

## Agents

POST /agent/run

GET /agent/status/{id}