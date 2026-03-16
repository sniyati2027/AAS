from typing import List, Dict, Any, Optional
from app.services.ai.gemini import gemini_client
from app.services.ai.tools import get_chat_tools, execute_tool


class ChatService:
    """Service for AI Manager chat functionality."""

    SYSTEM_INSTRUCTION = """You are the Atlas AI Manager, an intelligent assistant for the Atlas AI Command Center.

Your capabilities:
- Help users understand system status and metrics
- Assist with user management and access control
- Explain policies and create new ones
- Search and analyze audit logs
- Provide insights and recommendations
- Answer questions about the platform

Current context:
- User: {user_email} ({user_role})
- Page: {current_page}

Be helpful, concise, and proactive. Use available tools when needed. If you don't have enough information, ask clarifying questions."""

    async def chat(
        self,
        messages: List[Dict[str, str]],
        user_email: str,
        user_role: str,
        current_page: str = "/",
    ) -> Dict[str, Any]:
        """Process a chat message and return response."""
        
        if not gemini_client.is_available():
            return {
                "role": "assistant",
                "content": "AI Manager is currently unavailable. Please configure the GEMINI_API_KEY to enable AI features.",
                "tool_calls": []
            }

        system_instruction = self.SYSTEM_INSTRUCTION.format(
            user_email=user_email,
            user_role=user_role,
            current_page=current_page,
        )

        try:
            tools = get_chat_tools()
            response = await gemini_client.chat(
                messages=messages,
                system_instruction=system_instruction,
                tools=tools,
            )

            # Execute any function calls
            tool_results = []
            for func_call in response.get("function_calls", []):
                result = await execute_tool(func_call["name"], func_call["args"])
                tool_results.append({
                    "tool": func_call["name"],
                    "result": result
                })

            return {
                "role": "assistant",
                "content": response["content"],
                "tool_calls": tool_results,
            }

        except Exception as e:
            return {
                "role": "assistant",
                "content": f"I encountered an error: {str(e)}. Please try again.",
                "tool_calls": []
            }


chat_service = ChatService()
