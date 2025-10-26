"""
Letta-based Cultural Trivia Integration
Provides stateful trivia questions with persistent memory
"""

import os
import logging
from typing import Dict, Optional

# Try to import Letta Python SDK
try:
    from letta_client import Letta, AgentState
    LETTA_SDK_AVAILABLE = True
except ImportError:
    LETTA_SDK_AVAILABLE = False

logger = logging.getLogger(__name__)


class CulturalTriviaAgent:
    """
    Letta-based cultural trivia agent with persistent memory.
    Maintains conversation history, tracks scores, and avoids repeating questions,
    tailored to a specific country's culture.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('LETTA_API_KEY')
        self.client: Optional[Letta] = None
        self.agents: Dict[str, AgentState] = {}  # Stores agent_id per user_id
        self.enabled = LETTA_SDK_AVAILABLE and bool(self.api_key)
        
        if self.enabled:
            try:
                self.client = Letta(token=self.api_key)
                logger.info("Letta Cultural Trivia Agent initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Letta client: {str(e)}")
                self.enabled = False
        else:
            logger.warning("Letta API key not found or SDK not available. Cultural Trivia agent will not be available.")
    
    def _get_agent_id(self, user_id: str, country: str) -> str:
        """Generates a unique agent ID for a user and country."""
        return f"cultural_trivia_{user_id}_{country.lower().replace(' ', '_')}"

    def _get_persona_and_rules(self, country: str) -> list:
        """Generates memory blocks for the agent's persona and rules, tailored by country."""
        persona = f"""I am a friendly cultural trivia host specializing in {country}. 
I ask engaging questions about {country}'s history, traditions, art, food, and famous people. 
I track scores, provide helpful hints when needed, and avoid repeating questions. 
I celebrate correct answers and provide interesting facts."""
        
        rules = f"""Cultural Trivia Game Rules for {country}:
- I ask interesting trivia questions specifically about {country}'s culture, history, geography, famous people, traditions, food, and art.
- Users get 3 hints per question before I reveal the answer.
- I track the user's score (correct/total questions).
- I keep track of all questions asked to avoid repeats for this user and country.
- I provide encouraging feedback and explanations for answers.
- I will use the 'web_search' tool if I need to find a new trivia question or verify a fact about {country}.
- I will always respond with a question or feedback on an answer, never just a statement."""
        
        return [
            {"label": "persona", "value": persona},
            {"label": "rules", "value": rules}
        ]

    def start_session(self, user_id: str, country: str) -> Dict:
        """
        Start a new cultural trivia session for a user and country.
        Creates or reuses a Letta agent and gets the first question.
        """
        if not self.enabled:
            return {
                "status": "error",
                "response": "Cultural trivia agent not available",
                "agent_id": None
            }
        
        agent_key = self._get_agent_id(user_id, country)
        
        # Check if we already have an agent for this user/country
        if agent_key in self.agents:
            logger.info(f"Reusing existing Letta agent for user {user_id}, country {country}: {self.agents[agent_key].id}")
            # Send a message to resume the session and get a new question
            response = self.client.agents.messages.create(
                self.agents[agent_key].id,
                messages=[{
                    "role": "user",
                    "content": f"Hi! Let's continue our cultural trivia about {country}. Ask me a new question."
                }]
            )
            first_message_content = self._extract_assistant_message(response)
            return {
                "status": "success",
                "response": first_message_content,
                "agent_id": self.agents[agent_key].id
            }

        try:
            logger.info(f"Creating new Letta agent for user {user_id}, country {country}...")
            memory_blocks = self._get_persona_and_rules(country)
            
            # Create agent with trivia configuration
            agent = self.client.agents.create(
                model="openai/gpt-4-turbo",
                embedding="openai/text-embedding-3-small",
                name=f"Cultural Trivia Master ({country})",
                memory_blocks=memory_blocks,
                tools=["web_search"]
            )
            self.agents[agent_key] = agent
            logger.info(f"Letta agent created: {agent.id}")
            
            # Send initial message to get the first question
            response = self.client.agents.messages.create(
                agent.id,
                messages=[{
                    "role": "user",
                    "content": f"Hi! Ready to test your knowledge about {country}? Let's play some cultural trivia! Ask me your first question."
                }]
            )
            first_message_content = self._extract_assistant_message(response)
            
            return {
                "status": "success",
                "response": first_message_content,
                "agent_id": agent.id
            }
            
        except Exception as e:
            logger.error(f"Failed to create Letta agent or start session: {str(e)}")
            return {
                "status": "error",
                "response": f"Failed to start trivia session: {str(e)}",
                "agent_id": None
            }

    def submit_answer(self, agent_id: str, user_answer: str) -> Dict:
        """Submit an answer to the current trivia question."""
        if not self.enabled:
            return {"status": "error", "response": "Trivia agent not available"}
        
        try:
            response = self.client.agents.messages.create(
                agent_id,
                messages=[{
                    "role": "user",
                    "content": f"My answer is: {user_answer}"
                }]
            )
            return {"status": "success", "response": self._extract_assistant_message(response)}
        except Exception as e:
            logger.error(f"Failed to submit answer to Letta agent {agent_id}: {str(e)}")
            return {"status": "error", "response": f"Failed to submit answer: {str(e)}"}

    def request_hint(self, agent_id: str) -> Dict:
        """Request a hint for the current trivia question."""
        if not self.enabled:
            return {"status": "error", "response": "Trivia agent not available"}
        
        try:
            response = self.client.agents.messages.create(
                agent_id,
                messages=[{
                    "role": "user",
                    "content": "Can I get a hint?"
                }]
            )
            return {"status": "success", "response": self._extract_assistant_message(response)}
        except Exception as e:
            logger.error(f"Failed to request hint from Letta agent {agent_id}: {str(e)}")
            return {"status": "error", "response": f"Failed to get hint: {str(e)}"}

    def get_score(self, agent_id: str) -> Dict:
        """Get the current score for the trivia session."""
        if not self.enabled:
            return {"status": "error", "response": "Trivia agent not available"}
        
        try:
            response = self.client.agents.messages.create(
                agent_id,
                messages=[{
                    "role": "user",
                    "content": "What's my current score?"
                }]
            )
            return {"status": "success", "response": self._extract_assistant_message(response)}
        except Exception as e:
            logger.error(f"Failed to get score from Letta agent {agent_id}: {str(e)}")
            return {"status": "error", "response": f"Failed to get score: {str(e)}"}

    def _extract_assistant_message(self, response) -> str:
        """Extracts the content of the first assistant message from a Letta response."""
        for msg in response.messages:
            if msg.message_type == "assistant_message":
                return msg.content
        return "No response from agent."

    def process(self, input_data: Dict) -> Dict:
        """Unified entry point for all trivia actions."""
        action = input_data.get('action')
        user_id = input_data.get('user_id')
        agent_id = input_data.get('agent_id')
        country = input_data.get('country')  # Country for cultural context
        answer = input_data.get('answer')

        if action == 'start':
            if not country:
                return {"status": "error", "response": "Please provide a country to start cultural trivia."}
            return self.start_session(user_id, country)
        elif action == 'answer':
            if not agent_id:
                return {"status": "error", "response": "Agent ID is required to submit an answer."}
            return self.submit_answer(agent_id, answer)
        elif action == 'hint':
            if not agent_id:
                return {"status": "error", "response": "Agent ID is required to request a hint."}
            return self.request_hint(agent_id)
        elif action == 'score':
            if not agent_id:
                return {"status": "error", "response": "Agent ID is required to get the score."}
            return self.get_score(agent_id)
        else:
            return {"status": "error", "response": "Invalid trivia action."}


# Global instance
cultural_trivia_agent = CulturalTriviaAgent()

