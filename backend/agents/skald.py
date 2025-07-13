import logging
from typing import Dict, Any, Optional
from backend.llm.engine import LLMEngine
from backend.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class SkaldAgent(BaseAgent):
    """Skald Agent - Multilingual Assistant and Translator"""

    name = "Skald"
    description = "Multilingual assistant specializing in translation and cultural context"
    capabilities = ["translate", "summarize", "cultural_context", "multilingual_chat"]

    def __init__(self):
        super().__init__()
        self.llm_engine = LLMEngine()
        self.supported_languages = ["en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar", "hi"]

    async def execute(self, task_type: str, payload: Dict[str, Any], model: Optional[str] = None) -> Dict[str, Any]:
        """Execute Skald agent tasks"""
        try:
            if task_type == "translate":
                return await self._translate(payload, model)
            elif task_type == "summarize":
                return await self._summarize(payload, model)
            elif task_type == "cultural_context":
                return await self._cultural_context(payload, model)
            elif task_type == "multilingual_chat":
                return await self._multilingual_chat(payload, model)
            else:
                return {"error": f"Unknown task type: {task_type}"}
        except Exception as e:
            logger.error(f"Skald agent error: {e}")
            return {"error": str(e)}

    async def _translate(self, payload: Dict[str, Any], model: Optional[str] = None) -> Dict[str, Any]:
        """Translate text between languages"""
        text = payload.get("text", "")
        source_lang = payload.get("source_lang", "auto")
        target_lang = payload.get("target_lang", "en")

        if not text:
            return {"error": "No text provided for translation"}

        prompt = f"""
        Translate the following text from {source_lang} to {target_lang}:
        
        Text: {text}
        
        Provide only the translated text without additional commentary.
        """

        result = await self.llm_engine.generate(prompt, model)

        return {"translated_text": result, "source_lang": source_lang, "target_lang": target_lang, "confidence": 0.95}

    async def _summarize(self, payload: Dict[str, Any], model: Optional[str] = None) -> Dict[str, Any]:
        """Summarize text in specified language"""
        text = payload.get("text", "")
        language = payload.get("language", "en")
        max_length = payload.get("max_length", 200)

        if not text:
            return {"error": "No text provided for summarization"}

        prompt = f"""
        Summarize the following text in {language}. Keep the summary under {max_length} characters:
        
        Text: {text}
        
        Summary:
        """

        result = await self.llm_engine.generate(prompt, model)

        return {"summary": result, "language": language, "original_length": len(text), "summary_length": len(result)}

    async def _cultural_context(self, payload: Dict[str, Any], model: Optional[str] = None) -> Dict[str, Any]:
        """Provide cultural context for text"""
        text = payload.get("text", "")
        target_culture = payload.get("target_culture", "general")

        if not text:
            return {"error": "No text provided for cultural analysis"}

        prompt = f"""
        Provide cultural context and insights for the following text, considering {target_culture} perspective:
        
        Text: {text}
        
        Cultural Context:
        """

        result = await self.llm_engine.generate(prompt, model)

        return {
            "cultural_context": result,
            "target_culture": target_culture,
            "insights": "Cultural nuances and context provided",
        }

    async def _multilingual_chat(self, payload: Dict[str, Any], model: Optional[str] = None) -> Dict[str, Any]:
        """Handle multilingual conversation"""
        message = payload.get("message", "")
        user_language = payload.get("user_language", "en")
        conversation_history = payload.get("history", [])

        if not message:
            return {"error": "No message provided"}

        # Build conversation context
        context = ""
        if conversation_history:
            context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-5:]])

        prompt = f"""
        You are Skald, a multilingual assistant. Respond to the user's message in {user_language}.
        
        Previous conversation:
        {context}
        
        User message: {message}
        
        Response in {user_language}:
        """

        result = await self.llm_engine.generate(prompt, model)

        return {"response": result, "language": user_language, "agent": "Skald"}

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities"""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "supported_languages": self.supported_languages,
        }
