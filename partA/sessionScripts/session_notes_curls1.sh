#!/usr/bin/env bash
set -euo pipefail

BASE_URL="http://localhost:4567"

curl -sS "$BASE_URL/todos"
curl -sS "$BASE_URL/todos"
curl -sS "$BASE_URL/todos?id=1"
curl -sS "$BASE_URL/todos?id=4"
curl -sS "$BASE_URL/todos?asdfajksdlf&id=2"
curl -sS "$BASE_URL/todos?id>2"
curl -sS "$BASE_URL/todos?doneStatus=false"
curl -sS "$BASE_URL/todos?description="
curl -sS -I "$BASE_URL/todos"
curl -sS -X POST "$BASE_URL/todos"
curl -sS -X POST "$BASE_URL/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"test1"}'
curl -sS "$BASE_URL/todos"
curl -sS -X POST "$BASE_URL/todos" \
  -H "Content-Type: application/xml" \
  -d '<todo><title>pineapple</title></todo>'
curl -sS -X POST "$BASE_URL/todos" \
  -H "Content-Type: application/xml" \
  -d '<todo></todo>'
curl -sS -X POST "$BASE_URL/todos" \
  -H "Content-Type: application/xml" \
  -d '<title>pineapple</title>'
curl -sS -X POST "$BASE_URL/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"test3","description":"testing 3"}'
curl -sS -X POST "$BASE_URL/todos" \
  -H "Content-Type: application/xml" \
  -d '<todo><title>test3</title><description>testing 3</description></todo>'
curl -sS -X POST "$BASE_URL/todos" \
  -H "Content-Type: application/json" \
  -d '{"id":"999","title":"test-id","description":"test"}'
curl -sS -X POST "$BASE_URL/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"test & symbols"}'
curl -sS -X POST "$BASE_URL/todos"
curl -sS -X POST "$BASE_URL/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"valid-after-empty"}'
curl -sS -X POST "$BASE_URL/todos" \
  -H "Content-Type: application/xml" \
  -d '<todo></todo>'
curl -sS -X POST "$BASE_URL/todos" \
  -H "Content-Type: application/xml" \
  -d '<todo><title>valid-after-empty-xml</title></todo>'
curl -sS -X POST "$BASE_URL/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"test","description":"testing","invalidField":"test"}'
curl -sS -X POST "$BASE_URL/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"test","description":"testing","doneStatus":false}'
curl -sS -X POST "$BASE_URL/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"newtest","description":"newtest","doneStatus":true,"categories":[{"id":"1"}],"tasksof":[{"id":"1"}]}'
curl -sS -X POST "$BASE_URL/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"newtest","description":"newtest","doneStatus":true,"categories":"invalid"}'
curl -sS "$BASE_URL/todos/1"
curl -sS "$BASE_URL/todos?id=3"
curl -sS "$BASE_URL/todos/3"
curl -sS -I "$BASE_URL/todos/1"
curl -sS -I "$BASE_URL/todos/9999"
curl -sS -X PUT "$BASE_URL/todos/1" \
  -H "Content-Type: application/xml" \
  -d '<todo></todo>'

curl -sS -X PUT "$BASE_URL/todos/3" \
  -H "Content-Type: application/json" \
  -d '{"title":"valid","description":"testing"}'

curl -sS -X PUT "$BASE_URL/todos/1" \
  -H "Content-Type: application/json" \
  -d '{"description":"no-title"}'

curl -sS -X PUT "$BASE_URL/todos/1" \
  -H "Content-Type: application/json" \
  -d '{"title":"bad-doneStatus","doneStatus":"no"}'

curl -sS -X PUT "$BASE_URL/todos/1" \
  -H "Content-Type: application/json" \
  -d '{"title":"bad-field","asdf":"x"}'

curl -sS -X PUT "$BASE_URL/todos/1" \
  -H "Content-Type: application/json" \
  -d '{"id":"123","title":"id-field"}'
curl -sS -X PUT "$BASE_URL/todos/1" \
  -H "Content-Type: application/json" \
  -d '{"title":"valid","description":"updated","doneStatus":true}'
curl -sS -X POST "$BASE_URL/todos/15" \
  -H "Content-Type: application/json" \
  -d '{"title":"newtest","description":"newtest","doneStatus":true}'
curl -sS -X POST "$BASE_URL/todos/\""
curl -sS -X POST "$BASE_URL/todos/%5C%22"
curl -sS "$BASE_URL/todos/2?id=3"
curl -sS "$BASE_URL/todos?id=2&id=5&id=6"
curl -sS -X DELETE "$BASE_URL/todos/2"
curl -sS -X DELETE "$BASE_URL/todos/2"
curl -sS -X DELETE "$BASE_URL/todos/asdf"
curl -sS -X DELETE "$BASE_URL/todos/"
curl -sS -X DELETE "$BASE_URL/todos"
curl -sS "$BASE_URL/todos/"
curl -sS -X POST "$BASE_URL/todos/"
curl -sS -X PUT "$BASE_URL/todos/"
curl -sS -I "$BASE_URL/todos/"
