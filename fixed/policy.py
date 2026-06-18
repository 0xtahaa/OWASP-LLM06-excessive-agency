"""
policy.py (fixed version)

This is APPROACH C (action allowlist / policy layer), specifically
the "contextual parameter policy" variant: it's not enough to ask
"is this tool name allowed for this agent?" — we also have to ask
"do the PARAMETERS of this specific call match what's allowed in
THIS session?"

Why this matters even with narrow tools (Approach A) in place:
lookup_customer_by_id is a perfectly legitimate, narrowly-scoped
tool. But nothing about the tool's definition stops the model from
calling lookup_customer_by_id(customer_id=3) when the actual
customer on this support session is customer #1. The tool doesn't
know what session it's being called from — only the application
code around it does. That's exactly the gap this policy closes.

Design choice: a blocked call returns an error STRING to the model
(instead of raising an exception that kills the whole conversation).
This means the agent keeps functioning — it can still answer the
legitimate part of a mixed request, and can tell the user "I can't
do that part" instead of crashing the whole interaction. A hard
abort would actually hand an attacker an easy way to disable the
agent entirely (send one disallowed call, kill the session).
"""

from dataclasses import dataclass


# Which tools are allowed at all for this agent type. This is the
# "is the tool name allowed" half of the policy — narrower tools from
# Approach A already reduce what's even in this list, but we still
# check it explicitly here as its own deterministic layer, in case a
# new tool gets added later that ISN'T meant for every context.
ALLOWED_TOOLS_FOR_CUSTOMER_SERVICE_AGENT = {
    "lookup_customer_by_id",
    "update_customer_email",
}

# Which parameter name holds the customer ID, per tool — used below to
# find the value we need to compare against the session.
CUSTOMER_ID_PARAM_BY_TOOL = {
    "lookup_customer_by_id": "customer_id",
    "update_customer_email": "customer_id",
}


@dataclass
class PolicyResult:
    allowed: bool
    reason: str = ""


def check_tool_call(
    tool_name: str,
    tool_args: dict,
    session_customer_id: int,
) -> PolicyResult:
    """
    Decide whether a requested tool call is allowed in this session.

    session_customer_id is established BEFORE the model ever sees the
    conversation (see agent.py) — it does not come from anything the
    model said or any text the user wrote in their message. That's
    what makes it a trustworthy value to check against.
    """

    if tool_name not in ALLOWED_TOOLS_FOR_CUSTOMER_SERVICE_AGENT:
        return PolicyResult(
            allowed=False,
            reason=f"Tool '{tool_name}' is not permitted for this agent.",
        )

    id_param = CUSTOMER_ID_PARAM_BY_TOOL.get(tool_name)
    if id_param is not None:
        requested_id = tool_args.get(id_param)
        if requested_id != session_customer_id:
            return PolicyResult(
                allowed=False,
                reason=(
                    f"Tool '{tool_name}' was called with {id_param}={requested_id}, "
                    f"but the current session belongs to customer "
                    f"{session_customer_id}. Cross-customer access is not permitted."
                ),
            )

    return PolicyResult(allowed=True)
