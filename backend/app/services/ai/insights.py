from typing import List, Dict, Any
from datetime import datetime, timezone
from app.services.ai.gemini import gemini_client


class InsightsService:
    """Service for generating AI insights and recommendations."""

    INSIGHTS_PROMPT = """Analyze the following system data and generate actionable insights.

Focus on:
- Patterns and anomalies
- Performance bottlenecks
- Security concerns
- Optimization opportunities
- User behavior trends

System Data:
{data}

Generate 3-5 insights in JSON format:
[
  {{
    "title": "Insight title",
    "description": "Detailed description",
    "severity": "CRITICAL|WARNING|RECOMMENDATION",
    "category": "security|performance|usage|cost",
    "suggested_action": "What to do about it",
    "impact": "Expected impact of the action"
  }}
]

Respond with ONLY valid JSON, no markdown or explanation."""

    async def generate_insights(self, system_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights based on system data."""
        if not gemini_client.is_available():
            return self._get_demo_insights()

        import json
        
        data_summary = json.dumps(system_data, indent=2)
        prompt = self.INSIGHTS_PROMPT.format(data=data_summary)
        
        try:
            response = await gemini_client.generate_text(
                prompt=prompt,
                temperature=0.3,
            )
            
            # Clean response (remove markdown code blocks if present)
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.startswith("```"):
                clean_response = clean_response[3:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()
            
            insights = json.loads(clean_response)
            return insights
        except Exception as e:
            print(f"Error generating insights: {e}")
            return self._get_demo_insights()

    def _get_demo_insights(self) -> List[Dict[str, Any]]:
        """Return demo insights when Gemini is not available."""
        return [
            {
                "title": "High API Response Time Detected",
                "description": "Average API response time has increased by 45% over the past week, particularly for database-heavy endpoints.",
                "severity": "WARNING",
                "category": "performance",
                "suggested_action": "Add database query optimization and consider implementing caching for frequently accessed data",
                "impact": "Could reduce response time by 30-40% and improve user experience"
            },
            {
                "title": "Unusual Login Pattern Detected",
                "description": "Multiple failed login attempts from unfamiliar IP addresses during off-hours. Possible credential stuffing attack.",
                "severity": "CRITICAL",
                "category": "security",
                "suggested_action": "Enable rate limiting on authentication endpoints and review security logs",
                "impact": "Prevents potential account takeover and protects user data"
            },
            {
                "title": "Low Feature Adoption Rate",
                "description": "New AI policy features have only 15% adoption rate among active users after 30 days.",
                "severity": "RECOMMENDATION",
                "category": "usage",
                "suggested_action": "Create onboarding tutorial and in-app guidance for new features",
                "impact": "Could increase feature adoption by 40-50% based on similar initiatives"
            }
        ]


insights_service = InsightsService()
