from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL_NAME
import logging
import ast
import json
import re

logger = logging.getLogger(__name__)

class LLMProcessor:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.conversation_history = []

    def _extract_json(self, text):
        """Extract JSON from LLM response, handling various formats."""
        try:
            # Try to find JSON within markdown code blocks
            match = re.search(r'```(?:json)?\n(.*?)\n```', text, re.DOTALL)
            if match:
                text = match.group(1)
            
            # Try direct JSON parsing first
            return json.loads(text)
        except json.JSONDecodeError:
            try:
                # Fallback to literal_eval for non-standard JSON
                return ast.literal_eval(text)
            except (ValueError, SyntaxError):
                logger.error("Could not extract JSON from response")
                return None

    def analyze_depression(self, text):
        try:
            history = "\n".join([f"User: {msg['input']}\nAI: {msg['output']}"
                                 for msg in self.conversation_history[-3:]])  # Keep last 3 exchanges

            prompt = f"""
Analyze this conversation for depression symptoms. Consider the context:
{history}
Latest message: {text}

Respond with ONLY the following JSON structure, without any additional text or formatting:
{{
    "is_depressed": bool,
    "confidence": float,
    "response": str,
    "reason": str
}}
"""

            logger.info(f"Sending prompt to LLM:\n{prompt}")

            response = self.client.chat.completions.create(
                model=GROQ_MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                timeout=10,
                response_format={"type": "json_object"}  # Request JSON response
            )

            raw_response = response.choices[0].message.content.strip()
            logger.info(f"Raw LLM output:\n{raw_response}")

            # Parse the response
            result = self._extract_json(raw_response)
            
            if not result or not isinstance(result, dict):
                logger.error("Invalid response format from LLM")
                result = {
                    "is_depressed": False,
                    "response": "I'm having trouble understanding right now.",
                    "reason": "LLM returned invalid format",
                    "confidence": 0.0
                }

            # Validate required fields
            required_fields = ["is_depressed", "confidence", "response", "reason"]
            if not all(field in result for field in required_fields):
                logger.error("Missing required fields in LLM response")
                result = {
                    "is_depressed": False,
                    "response": "Let's continue our conversation.",
                    "reason": "Incomplete response from AI",
                    "confidence": 0.0
                }

            # Add to conversation history
            self.conversation_history.append({
                "input": text,
                "output": result["response"]
            })

            return result

        except Exception as e:
            logger.exception("LLM analysis failed")
            return {
                "is_depressed": False,
                "response": "Let's continue our conversation.",
                "reason": "Error occurred",
                "confidence": 0.0
            }