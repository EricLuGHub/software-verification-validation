#!/usr/bin/env bash
set -euo pipefail

BASE_URL="http://localhost:4567"

curl -sS "$BASE_URL/todos/1/tasksof"
curl -sS "$BASE_URL/todos/2/tasksof"

curl -sS "$BASE_URL/todos/3/tasksof"
curl -sS "$BASE_URL/todos/asdf/tasksof"

curl -sS -I "$BASE_URL/todos/1/tasksof"
curl -sS -I "$BASE_URL/todos/3/tasksof"

curl -sS -X POST "$BASE_URL/todos/1/tasksof" \
  -H "Content-Type: application/json" \
  -d '{"id":9999}'

curl -sS -X POST "$BASE_URL/todos/3/tasksof" \
  -H "Content-Type: application/json" \
  -d '{"id":9999}'

curl -sS -X POST "$BASE_URL/todos/1/tasksof" \
  -H "Content-Type: application/json" \
  -d '{"id":1}'

curl -sS -X POST "$BASE_URL/todos/3/tasksof" \
  -H "Content-Type: application/json" \
  -d '{"id":1}'

if [[ -z "$NEW_PROJECT_ID" ]]; then
  NEW_PROJECT_ID="1"
fi

curl -sS -X POST "$BASE_URL/todos/2/tasksof" \
  -H "Content-Type: application/json" \
  -d "{\"id\":${NEW_PROJECT_ID}}"

curl -sS -X POST "$BASE_URL/todos/2/tasksof" \
  -H "Content-Type: application/json" \
  -d "{\"id\":\"${NEW_PROJECT_ID}\"}"

curl -sS -X DELETE "$BASE_URL/todos/2/tasksof"

curl -sS -X DELETE "$BASE_URL/todos/2/tasksof" \
  -H "Content-Type: application/json" \
  -d "{\"id\":\"${NEW_PROJECT_ID}\"}"

curl -sS -i -X OPTIONS "$BASE_URL/todos/2/tasksof"
curl -sS -X PUT "$BASE_URL/todos/2/tasksof"
curl -sS -X PATCH "$BASE_URL/todos/2/tasksof"

curl -sS -X POST "$BASE_URL/todos/1/tasksof" \
  -H "Content-Type: application/json" \
  -d '{"id":"1"}'

curl -sS -X DELETE "$BASE_URL/todos/1/tasksof/2"
curl -sS -X DELETE "$BASE_URL/todos/1/tasksof/1"
curl -sS -X DELETE "$BASE_URL/todos/1/tasksof/1"

curl -sS "$BASE_URL/todos/1/tasksof/1"
curl -sS -X POST "$BASE_URL/todos/1/tasksof/1"
curl -sS -I "$BASE_URL/todos/1/tasksof/1"

curl -sS -X PUT "$BASE_URL/todos/1/tasksof/1"
curl -sS -X PATCH "$BASE_URL/todos/1/tasksof/1"
curl -sS -i -X OPTIONS "$BASE_URL/todos/1/tasksof/1"

curl -sS -i -X OPTIONS "$BASE_URL/todos/1/categories"
curl -sS "$BASE_URL/todos/1/categories"
curl -sS "$BASE_URL/todos/999/categories"

curl -sS "$BASE_URL/todos/999/categories"

curl -sS -I "$BASE_URL/todos/1/categories"
curl -sS -I "$BASE_URL/todos/2/categories"

curl -sS -i -X OPTIONS "$BASE_URL/todos/1/categories/1"
curl -sS "$BASE_URL/todos/1/categories/1"
curl -sS -X POST "$BASE_URL/todos/1/categories/1"
curl -sS -I "$BASE_URL/todos/1/categories/1"

curl -sS -X PUT "$BASE_URL/todos/1/categories/1"
curl -sS -X PATCH "$BASE_URL/todos/1/categories/1"

curl -sS -X DELETE "$BASE_URL/todos/1/categories/2"
curl -sS -X POST "$BASE_URL/todos/1/categories" \
  -H "Content-Type: application/json" \
  -d '{"id":"1"}'
curl -sS -X DELETE "$BASE_URL/todos/1/categories/1"

curl -sS -i -X OPTIONS "$BASE_URL/todos/1/tasksof"
curl -sS -X PUT "$BASE_URL/todos/1/tasksof"
curl -sS -X PATCH "$BASE_URL/todos/1/tasksof"
