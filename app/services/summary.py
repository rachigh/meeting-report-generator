"""
Summary generation service using OpenAI GPT.
"""

import json
import asyncio
from typing import Dict, Any, List
from openai import OpenAI  

from app.core.config import settings
from app.schemas.report import Topic, Decision, ActionItem


class SummaryService:
    """Service for generating meeting summaries using OpenAI GPT."""

    def __init__(self):
        """Initialize the summary service."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_summary(self, transcription: str) -> Dict[str, Any]:
        """
        Generate a structured summary from a meeting transcription.
        
        Args:
            transcription: The meeting transcription text
        
        Returns:
            Dictionary containing summary, topics, decisions, and action items
        """
        try:
            # Create the prompt for structured summary
            prompt = self._create_summary_prompt(transcription)
            
            
            loop = asyncio.get_event_loop()
            
            def _generate():
                return self.client.chat.completions.create(
                    model="gpt-4o-mini",  # Using gpt-4o-mini for cost efficiency
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert meeting analyst. Your task is to analyze meeting transcriptions and extract key information in a structured format."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,  # Lower temperature for more consistent output
                    response_format={"type": "json_object"}
                )
            
            response = await loop.run_in_executor(None, _generate)
            
            # Parse the response
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Validate and structure the response
            return {
                "summary": result.get("summary", ""),
                "topics": self._parse_topics(result.get("topics", [])),
                "decisions": self._parse_decisions(result.get("decisions", [])),
                "action_items": self._parse_action_items(result.get("action_items", []))
            }
        
        except Exception as e:
            raise Exception(f"Summary generation failed: {str(e)}")

    def _create_summary_prompt(self, transcription: str) -> str:
        """Create the prompt for summary generation."""
        return f"""Analyze the following meeting transcription and provide a structured summary in JSON format.

Transcription:
{transcription}

Please provide your analysis in the following JSON structure:
{{
    "summary": "A concise paragraph summarizing the main points of the meeting",
    "topics": [
        {{
            "title": "Topic name",
            "description": "Brief description of what was discussed"
        }}
    ],
    "decisions": [
        {{
            "description": "What was decided",
            "responsible": "Who is responsible (if mentioned)"
        }}
    ],
    "action_items": [
        {{
            "task": "What needs to be done",
            "assignee": "Who should do it (if mentioned)",
            "deadline": "When it should be done (if mentioned)",
            "priority": "high/medium/low (if mentioned)"
        }}
    ]
}}

Instructions:
- Be concise but comprehensive
- Extract all important decisions and action items
- If information is not mentioned in the transcription, use null for that field
- Focus on actionable information
- Identify key topics discussed
"""

    def _parse_topics(self, topics_data: List[Dict]) -> List[Topic]:
        """Parse topics from response data."""
        topics = []
        for topic in topics_data:
            if isinstance(topic, dict) and "title" in topic:
                topics.append(Topic(
                    title=topic["title"],
                    description=topic.get("description")
                ))
        return topics

    def _parse_decisions(self, decisions_data: List[Dict]) -> List[Decision]:
        """Parse decisions from response data."""
        decisions = []
        for decision in decisions_data:
            if isinstance(decision, dict) and "description" in decision:
                decisions.append(Decision(
                    description=decision["description"],
                    responsible=decision.get("responsible")
                ))
        return decisions

    def _parse_action_items(self, action_items_data: List[Dict]) -> List[ActionItem]:
        """Parse action items from response data."""
        action_items = []
        for item in action_items_data:
            if isinstance(item, dict) and "task" in item:
                action_items.append(ActionItem(
                    task=item["task"],
                    assignee=item.get("assignee"),
                    deadline=item.get("deadline"),
                    priority=item.get("priority")
                ))
        return action_items


# Create a singleton instance
summary_service = SummaryService()
