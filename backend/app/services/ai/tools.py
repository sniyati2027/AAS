from typing import List, Dict, Any
from google.ai.generativelanguage_v1beta.types import content


def get_chat_tools() -> List[content.Tool]:
    """Get list of tools available to the AI chat assistant."""
    
    get_user_info = content.FunctionDeclaration(
        name="get_user_info",
        description="Get information about a user by email or ID",
        parameters=content.Schema(
            type=content.Type.OBJECT,
            properties={
                "user_identifier": content.Schema(
                    type=content.Type.STRING,
                    description="User email or ID"
                )
            },
            required=["user_identifier"]
        )
    )
    
    get_system_stats = content.FunctionDeclaration(
        name="get_system_stats",
        description="Get current system statistics and metrics",
        parameters=content.Schema(
            type=content.Type.OBJECT,
            properties={
                "metric_type": content.Schema(
                    type=content.Type.STRING,
                    description="Type of metrics: 'performance', 'usage', 'errors', or 'all'",
                    enum=["performance", "usage", "errors", "all"]
                )
            }
        )
    )
    
    search_audit_logs = content.FunctionDeclaration(
        name="search_audit_logs",
        description="Search audit logs for specific actions or users",
        parameters=content.Schema(
            type=content.Type.OBJECT,
            properties={
                "query": content.Schema(
                    type=content.Type.STRING,
                    description="Search query"
                ),
                "limit": content.Schema(
                    type=content.Type.INTEGER,
                    description="Maximum number of results (default: 10)"
                )
            },
            required=["query"]
        )
    )
    
    create_policy = content.FunctionDeclaration(
        name="create_policy",
        description="Create a new access control policy",
        parameters=content.Schema(
            type=content.Type.OBJECT,
            properties={
                "name": content.Schema(
                    type=content.Type.STRING,
                    description="Policy name"
                ),
                "description": content.Schema(
                    type=content.Type.STRING,
                    description="Policy description"
                ),
                "rule": content.Schema(
                    type=content.Type.STRING,
                    description="Natural language rule"
                )
            },
            required=["name", "rule"]
        )
    )
    
    return [content.Tool(function_declarations=[
        get_user_info,
        get_system_stats,
        search_audit_logs,
        create_policy,
    ])]


async def execute_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool function and return results."""
    
    if tool_name == "get_user_info":
        return {
            "user_identifier": args.get("user_identifier"),
            "status": "active",
            "role": "DEVELOPER",
            "last_login": "2026-03-14T10:30:00Z",
            "message": "User information retrieved successfully"
        }
    
    elif tool_name == "get_system_stats":
        metric_type = args.get("metric_type", "all")
        return {
            "metric_type": metric_type,
            "timestamp": "2026-03-15T12:00:00Z",
            "performance": {
                "avg_response_time_ms": 245,
                "p95_response_time_ms": 680,
                "cpu_usage_percent": 45,
                "memory_usage_percent": 62
            },
            "usage": {
                "active_users": 127,
                "api_requests_today": 15432,
                "database_queries": 8921
            },
            "errors": {
                "error_rate_percent": 0.8,
                "total_errors_today": 23
            }
        }
    
    elif tool_name == "search_audit_logs":
        query = args.get("query", "")
        limit = args.get("limit", 10)
        return {
            "query": query,
            "total_found": 3,
            "results": [
                {
                    "timestamp": "2026-03-15T11:45:00Z",
                    "action": "user.approve",
                    "user": "admin@atlasuniversity.edu.in",
                    "details": f"Matched query: {query}"
                },
                {
                    "timestamp": "2026-03-15T10:30:00Z",
                    "action": "policy.create",
                    "user": "developer@atlasuniversity.edu.in",
                    "details": f"Related to: {query}"
                }
            ]
        }
    
    elif tool_name == "create_policy":
        return {
            "policy_id": 12345,
            "name": args.get("name"),
            "status": "created",
            "message": "Policy created successfully and will be translated to DSL"
        }
    
    else:
        return {"error": f"Unknown tool: {tool_name}"}
