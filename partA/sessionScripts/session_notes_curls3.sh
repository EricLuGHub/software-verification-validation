#!/usr/bin/env bash
set -euo pipefail

BASE_URL="http://localhost:4567"

curl -sS "$BASE_URL/projects"
curl -sS -I "$BASE_URL/projects"

curl -sS -X POST "$BASE_URL/projects"

curl -sS -X POST "$BASE_URL/projects" \
  -H "Content-Type: application/json" \
  -d '{"id":"123","title":"with-id"}'

curl -sS -X POST "$BASE_URL/projects" \
  -H "Content-Type: application/json" \
  -d '{"asdf":"nope"}'

curl -sS -X POST "$BASE_URL/projects" \
  -H "Content-Type: application/json" \
  -d '{"id":"123","asdf":"nope"}'

curl -sS -X POST "$BASE_URL/projects" \
  -H "Content-Type: application/json" \
  -d '{"title":"proj-full","completed":false,"active":true,"description":"desc"}'

curl -sS -X PUT "$BASE_URL/projects"
curl -sS -X PATCH "$BASE_URL/projects"
curl -sS -X DELETE "$BASE_URL/projects"
curl -sS -i -X OPTIONS "$BASE_URL/projects"

curl -sS -i -X OPTIONS "$BASE_URL/projects/1"

curl -sS "$BASE_URL/projects/1"
curl -sS "$BASE_URL/projects/3"

curl -sS -I "$BASE_URL/projects/1"

curl -sS -X POST "$BASE_URL/projects/1" \
  -H "Content-Type: application/json" \
  -d '{"title":"updated-title"}'

curl -sS -X POST "$BASE_URL/projects/3" \
  -H "Content-Type: application/json" \
  -d '{"title":"nope"}'

curl -sS -X POST "$BASE_URL/projects/1" \
  -H "Content-Type: application/json" \
  -d '{"id":"asdf"}'

curl -sS -X POST "$BASE_URL/projects/1" \
  -H "Content-Type: application/json" \
  -d '{"id":"5"}'

curl -sS -X POST "$BASE_URL/projects/1" \
  -H "Content-Type: application/json" \
  -d '{"id":3}'

curl -sS -X PUT "$BASE_URL/projects/1" \
  -H "Content-Type: application/json" \
  -d '{"title":"put-only"}'

curl -sS -X POST "$BASE_URL/projects/1" \
  -H "Content-Type: application/json" \
  -d '{"title":"post-only"}'

curl -sS -X PUT "$BASE_URL/projects/1" \
  -H "Content-Type: application/json" \
  -d '{"title":12}'

curl -sS -X POST "$BASE_URL/projects/1" \
  -H "Content-Type: application/json" \
  -d '{"title":12}'

curl -sS -X DELETE "$BASE_URL/projects/1"
curl -sS -X DELETE "$BASE_URL/projects/4"

curl -sS -X PATCH "$BASE_URL/projects/1"

curl -sS "$BASE_URL/projects/1/tasks"
curl -sS "$BASE_URL/projects/999/tasks"

curl -sS -I "$BASE_URL/projects/1/tasks"

curl -sS -X PUT "$BASE_URL/projects/1/tasks"
curl -sS -X PATCH "$BASE_URL/projects/1/tasks"
curl -sS -X DELETE "$BASE_URL/projects/1/tasks"

curl -sS -i -X OPTIONS "$BASE_URL/projects/1/tasks"

TODO1_ID=$(curl -sS -X POST "$BASE_URL/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"proj3-task-1"}' | python3 - <<'PY'
import sys, json, re
raw = sys.stdin.read().strip()
try:
    print(json.loads(raw)["id"])
except Exception:
    m = re.search(r'"id"\s*:\s*"?(\d+)"?', raw)
    print(m.group(1) if m else "")
PY
)

TODO2_ID=$(curl -sS -X POST "$BASE_URL/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"proj3-task-2"}' | python3 - <<'PY'
import sys, json, re
raw = sys.stdin.read().strip()
try:
    print(json.loads(raw)["id"])
except Exception:
    m = re.search(r'"id"\s*:\s*"?(\d+)"?', raw)
    print(m.group(1) if m else "")
PY
)

if [[ -z "$TODO1_ID" ]]; then
  TODO1_ID="1"
fi
if [[ -z "$TODO2_ID" ]]; then
  TODO2_ID="2"
fi

curl -sS -X POST "$BASE_URL/projects/1/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title":"just-title"}'

curl -sS -X POST "$BASE_URL/projects/1/tasks" \
  -H "Content-Type: application/json" \
  -d "{\"id\":\"${TODO1_ID}\"}"

curl -sS -X POST "$BASE_URL/projects/1/tasks" \
  -H "Content-Type: application/json" \
  -d "{\"id\":\"${TODO1_ID}\"}"

curl -sS -X POST "$BASE_URL/projects/1/tasks" \
  -H "Content-Type: application/json" \
  -d "{\"id\":\"${TODO1_ID}\",\"description\":\"extra\"}"

curl -sS -X POST "$BASE_URL/projects/1/tasks" \
  -H "Content-Type: application/json" \
  -d '{"description":"no-title"}'

curl -sS -X PUT "$BASE_URL/projects/1/tasks"
curl -sS -X PATCH "$BASE_URL/projects/1/tasks"
curl -sS -X DELETE "$BASE_URL/projects/1/tasks"

curl -sS -i -X OPTIONS "$BASE_URL/projects/1/tasks"

curl -sS -i -X OPTIONS "$BASE_URL/projects/1/tasks/${TODO1_ID}"

curl -sS "$BASE_URL/projects/1/tasks/${TODO1_ID}"
curl -sS -X POST "$BASE_URL/projects/1/tasks/${TODO1_ID}"
curl -sS -I "$BASE_URL/projects/1/tasks/${TODO1_ID}"

curl -sS -X PUT "$BASE_URL/projects/1/tasks/${TODO1_ID}"
curl -sS -X PATCH "$BASE_URL/projects/1/tasks/${TODO1_ID}"

curl -sS -X DELETE "$BASE_URL/projects/1/tasks/${TODO1_ID}"
curl -sS -X DELETE "$BASE_URL/projects/6/tasks/3"

curl -sS -X POST "$BASE_URL/projects/1/tasks" \
  -H "Content-Type: application/json" \
  -d "{\"id\":${TODO1_ID}}"

curl -sS -X POST "$BASE_URL/projects/1/tasks" \
  -H "Content-Type: application/json" \
  -d "{\"id\":\"${TODO1_ID}\"}"

curl -sS -i -X OPTIONS "$BASE_URL/projects/1/categories"

curl -sS "$BASE_URL/projects/1/categories"
curl -sS "$BASE_URL/projects/999/categories"

NEW_CAT_ID=$(curl -sS -X POST "$BASE_URL/categories" \
  -H "Content-Type: application/json" \
  -d '{"title":"proj3-cat"}' | python3 - <<'PY'
import sys, json, re
raw = sys.stdin.read().strip()
try:
    print(json.loads(raw)["id"])
except Exception:
    m = re.search(r'"id"\s*:\s*"?(\d+)"?', raw)
    print(m.group(1) if m else "")
PY
)

if [[ -z "$NEW_CAT_ID" ]]; then
  NEW_CAT_ID="1"
fi

curl -sS -X POST "$BASE_URL/projects/1/categories" \
  -H "Content-Type: application/json" \
  -d "{\"id\":\"${NEW_CAT_ID}\"}"

curl -sS -X POST "$BASE_URL/projects/1/categories" \
  -H "Content-Type: application/json" \
  -d '{"id":999999}'

curl -sS -I "$BASE_URL/projects/1/categories"

curl -sS -X PUT "$BASE_URL/projects/1/categories"
curl -sS -X PATCH "$BASE_URL/projects/1/categories"

curl -sS -i -X OPTIONS "$BASE_URL/projects/1/categories/${NEW_CAT_ID}"

curl -sS "$BASE_URL/projects/1/categories/${NEW_CAT_ID}"
curl -sS -X POST "$BASE_URL/projects/1/categories/${NEW_CAT_ID}"
curl -sS -I "$BASE_URL/projects/1/categories/${NEW_CAT_ID}"

curl -sS -X PUT "$BASE_URL/projects/1/categories/${NEW_CAT_ID}"
curl -sS -X PATCH "$BASE_URL/projects/1/categories/${NEW_CAT_ID}"

curl -sS -X DELETE "$BASE_URL/projects/1/categories/${NEW_CAT_ID}"
curl -sS -X DELETE "$BASE_URL/projects/1/categories/1"
