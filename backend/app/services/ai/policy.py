from typing import Dict, Any
from app.services.ai.gemini import gemini_client


class PolicyService:
    """Service for translating natural language policies to executable DSL."""

    TRANSLATION_PROMPT = """You are a policy translation engine. Convert the natural language policy into a structured logical DSL.

Rules:
- Use operators: AND, OR, NOT
- Use comparisons: ==, !=, <, >, <=, >=
- Use functions: contains(), startsWith(), endsWith()
- Variables: user.role, user.department, resource.type, resource.owner, time.hour

Example:
Natural: "Allow managers to access reports during business hours"
DSL: (user.role == "manager") AND (resource.type == "report") AND (time.hour >= 9 AND time.hour <= 17)

Natural language policy:
{policy}

Respond with ONLY the DSL, no explanation."""

    async def translate_policy(self, natural_language: str) -> str:
        """Translate natural language policy to DSL."""
        if not gemini_client.is_available():
            return "# Set GEMINI_API_KEY for natural-language translation. Fallback:\nuser.role == 'ADMIN'"

        prompt = self.TRANSLATION_PROMPT.format(policy=natural_language)
        dsl = await gemini_client.generate_text(
            prompt=prompt,
            temperature=0.2,
        )
        return dsl.strip()

    async def validate_policy(self, dsl: str) -> Dict[str, Any]:
        """Validate a policy DSL (basic syntax check)."""
        try:
            # Basic validation - check for common operators and syntax
            valid_operators = ["AND", "OR", "NOT", "==", "!=", "<", ">", "<=", ">="]
            valid_functions = ["contains", "startsWith", "endsWith"]
            
            has_operator = any(op in dsl for op in valid_operators)
            has_valid_syntax = "(" in dsl and ")" in dsl
            
            return {
                "valid": has_operator and has_valid_syntax,
                "errors": [] if (has_operator and has_valid_syntax) else ["Invalid DSL syntax"],
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)],
            }


policy_service = PolicyService()
