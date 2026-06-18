"""
tools.py (vulnerable version)

Defines the tools available to the agent.

THIS IS THE VULNERABLE PART: there is exactly ONE tool, execute_sql,
and it can run ANY SQL statement against the customers table —
SELECT, UPDATE, DELETE, anything. The model decides what query to
write, and that query is executed with no restriction.

This is "Excessive Agency" in its purest form:
- Dimension 1 (excessive functionality): one tool can do everything
  a customer-service agent could ever need, and a lot more besides.
- Dimension 2 (excessive permissions): the underlying DB connection
  has full read/write/delete rights, even though the agent's actual
  job ("answer this one customer's question") never requires write
  or delete access at all.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "shop.db")

# Tool schema exposed to the model via the `tools` parameter of the
# chat.completions API. Note how generic and powerful this single
# tool is — that's the whole point of this vulnerable demo.
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "execute_sql",
            "description": (
                "Execute an arbitrary SQL statement against the shop's "
                "customer database. Use this to look up or update any "
                "customer information needed to answer support requests."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A complete SQL statement, e.g. a SELECT or UPDATE statement.",
                    }
                },
                "required": ["query"],
            },
        },
    }
]


def execute_sql(query: str) -> str:
    """
    Execute the given SQL statement with NO validation, NO restriction
    on statement type, and NO check on which rows are being touched.

    This is intentionally unsafe — it mirrors a real-world pattern where
    a developer wires an LLM agent directly to a database connection
    "because it's simpler than building separate, narrow tools."
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        if query.strip().lower().startswith("select"):
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
            return str(result)
        else:
            conn.commit()
            return f"Query executed successfully. Rows affected: {cursor.rowcount}"
    except sqlite3.Error as e:
        return f"SQL error: {e}"
    finally:
        conn.close()


# Maps tool names (as called by the model) to the actual Python functions.
TOOL_FUNCTIONS = {
    "execute_sql": execute_sql,
}
