import os
import asyncio
import logging
from typing import Optional, Dict, Any
import aiohttp
from backend.config import settings

logger = logging.getLogger(__name__)


class LLMEngine:
    """LLM Engine for handling different language models"""

    def __init__(self):
        self.local_models = {}
        self.remote_endpoints = {}
        self._load_models()

    def _load_models(self):
        """Load available models"""
        # Local models
        if os.path.exists(settings.LOCAL_LLM_PATH):
            for model_dir in os.listdir(settings.LOCAL_LLM_PATH):
                model_path = os.path.join(settings.LOCAL_LLM_PATH, model_dir)
                if os.path.isdir(model_path):
                    self.local_models[model_dir] = {"path": model_path, "type": "local"}

        # Remote endpoints
        if settings.REMOTE_LLM_ENDPOINT:
            self.remote_endpoints["remote"] = {"url": settings.REMOTE_LLM_ENDPOINT, "type": "remote"}

        # OpenAI
        if settings.OPENAI_API_KEY:
            self.remote_endpoints["openai"] = {"api_key": settings.OPENAI_API_KEY, "type": "openai"}

    async def generate(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        """Generate text using specified model"""
        try:
            if not model:
                model = self._get_default_model()

            if model in self.local_models:
                return await self._generate_local(prompt, model, **kwargs)
            elif model in self.remote_endpoints:
                return await self._generate_remote(prompt, model, **kwargs)
            else:
                # Fallback to mock response
                return await self._generate_mock(prompt, model)

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return f"Error generating response: {str(e)}"

    async def _generate_local(self, prompt: str, model: str, **kwargs) -> str:
        """Generate using local model"""
        model_info = self.local_models[model]
        model_path = model_info["path"]

        # Check for llama.cpp binary
        bin_path = os.path.join(model_path, "main")
        model_file = os.path.join(model_path, "model.gguf")

        if not os.path.exists(bin_path) or not os.path.exists(model_file):
            return await self._generate_mock(prompt, model)

        try:
            # Run llama.cpp process
            proc = await asyncio.create_subprocess_exec(
                bin_path, "-m", model_file, "-p", prompt, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await proc.communicate()

            if proc.returncode == 0:
                return stdout.decode("utf-8").strip()
            else:
                logger.error(f"Local model error: {stderr.decode()}")
                return await self._generate_mock(prompt, model)

        except Exception as e:
            logger.error(f"Local model execution error: {e}")
            return await self._generate_mock(prompt, model)

    async def _generate_remote(self, prompt: str, model: str, **kwargs) -> str:
        """Generate using remote endpoint"""
        endpoint_info = self.remote_endpoints[model]

        if endpoint_info["type"] == "openai":
            return await self._generate_openai(prompt, **kwargs)
        else:
            return await self._generate_http(prompt, endpoint_info["url"], **kwargs)

    async def _generate_openai(self, prompt: str, **kwargs) -> str:
        """Generate using OpenAI API"""
        try:
            import openai

            client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

            response = await client.chat.completions.create(
                model=kwargs.get("model", "gpt-3.5-turbo"),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
            )

            content = response.choices[0].message.content
            return content if content else "No response generated"

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return await self._generate_mock(prompt, "openai")

    async def _generate_http(self, prompt: str, url: str, **kwargs) -> str:
        """Generate using HTTP endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"prompt": prompt, **kwargs}

                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "No response")
                    else:
                        logger.error(f"HTTP endpoint error: {response.status}")
                        return await self._generate_mock(prompt, "http")

        except Exception as e:
            logger.error(f"HTTP generation error: {e}")
            return await self._generate_mock(prompt, "http")

    async def _generate_mock(self, prompt: str, model: str) -> str:
        """Generate mock response for testing"""
        return f"Mock response from {model}: {prompt[:50]}..."

    def _get_default_model(self) -> str:
        """Get default model"""
        if self.local_models:
            return list(self.local_models.keys())[0]
        elif self.remote_endpoints:
            return list(self.remote_endpoints.keys())[0]
        else:
            return "mock"

    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models"""
        return {
            "local": list(self.local_models.keys()),
            "remote": list(self.remote_endpoints.keys()),
            "default": self._get_default_model(),
        }

    def health_check(self) -> Dict[str, Any]:
        """Health check for LLM engine"""
        return {
            "status": "healthy",
            "local_models": len(self.local_models),
            "remote_endpoints": len(self.remote_endpoints),
            "default_model": self._get_default_model(),
        }
