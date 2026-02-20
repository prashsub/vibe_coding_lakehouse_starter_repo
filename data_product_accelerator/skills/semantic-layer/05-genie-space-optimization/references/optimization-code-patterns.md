# Optimization Code Patterns

Python implementations for the Genie Space optimization loop. These functions are also available in `scripts/genie_optimizer.py` and `scripts/repeatability_tester.py`.

## Space Discovery

Discover deployed Genie Spaces via the Databricks SDK:

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

spaces = list(w.genie.list_spaces())
for s in spaces:
    print(f"  {s.space_id}  {s.title}")
```

Or via CLI:

```bash
databricks api get /api/2.0/genie/spaces --output json | jq '.spaces[] | {id: .space_id, title: .title}'
```

For domain-specific projects, maintain a mapping:

```python
DOMAIN_SPACES = {
    "cost":        "<space_id>",
    "reliability": "<space_id>",
    "quality":     "<space_id>",
}
```

## run_genie_query

Execute a query against Genie and return SQL + status. Polls until completion with exponential backoff (3s initial, max 10s intervals).

```python
import time
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

def run_genie_query(space_id: str, question: str, max_wait: int = 120) -> dict:
    """Execute a query against Genie and return SQL + status."""
    try:
        resp = w.genie.start_conversation(space_id=space_id, content=question)
        conversation_id = resp.conversation_id
        message_id = resp.message_id

        poll_interval = 3
        start = time.time()
        while time.time() - start < max_wait:
            time.sleep(poll_interval)
            msg = w.genie.get_message(
                space_id=space_id,
                conversation_id=conversation_id,
                message_id=message_id
            )
            status = str(msg.status) if hasattr(msg, 'status') else 'UNKNOWN'
            if any(s in status for s in ['COMPLETED', 'FAILED', 'CANCELLED']):
                break
            poll_interval = min(poll_interval + 1, 10)

        sql = None
        if hasattr(msg, 'attachments') and msg.attachments:
            for att in msg.attachments:
                if hasattr(att, 'query') and att.query:
                    sql = att.query.query if hasattr(att.query, 'query') else str(att.query)
        return {"status": status, "sql": sql}
    except Exception as e:
        return {"status": "ERROR", "sql": None, "error": str(e)}
```

## evaluate_accuracy

Compare generated SQL against expected SQL and check asset routing correctness.

```python
def evaluate_accuracy(result: dict, expected: dict) -> dict:
    """Evaluate if Genie returned correct SQL."""
    generated_sql = (result.get("sql") or "").lower().strip()
    expected_sql = expected.get("expected_sql", "").lower().strip()

    # Check asset routing
    expected_asset = expected.get("expected_asset", "").upper()
    uses_mv = "mv_" in generated_sql or "measure(" in generated_sql
    uses_tvf = "get_" in generated_sql
    actual_asset = "MV" if uses_mv else ("TVF" if uses_tvf else "TABLE")

    return {
        "question": expected["question"],
        "sql_generated": result.get("status") == "COMPLETED" and bool(generated_sql),
        "correct_asset": actual_asset == expected_asset,
        "actual_asset": actual_asset,
        "expected_asset": expected_asset,
    }
```

## test_repeatability

Run each question multiple times and measure SQL consistency across runs.

```python
import hashlib
from collections import Counter

def test_repeatability(space_id: str, question: str, iterations: int = 3) -> dict:
    """Test SQL consistency across multiple runs."""
    hashes = []
    for i in range(iterations):
        sql = run_genie_query(space_id, question).get("sql", "")
        sql_hash = hashlib.md5(sql.lower().encode()).hexdigest()[:8] if sql else "NONE"
        hashes.append(sql_hash)
        time.sleep(12)

    most_common_count = Counter(hashes).most_common(1)[0][1]
    return {
        "question": question,
        "repeatability_pct": (most_common_count / len(hashes)) * 100,
        "unique_variants": len(set(hashes)),
    }
```

## Re-Test Loop

After applying control lever changes, re-run failing questions:

```python
time.sleep(30)  # Wait for propagation

for question in failing_questions:
    result = run_genie_query(space_id, question["question"])
    evaluation = evaluate_accuracy(result, question)
    print(f"  {'PASS' if evaluation['correct_asset'] else 'FAIL'}: {question['question']}")
    time.sleep(12)
```
