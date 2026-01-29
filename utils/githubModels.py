import time
import logging
import requests


logger = logging.getLogger(__name__)


class GitHubModelsClient:
    """Client for GitHub Models API with rate limiting."""

    BASE_URL = "https://models.inference.ai.azure.com"

    def __init__(self, githubToken: str, model: str = "gpt-4o-mini"):
        """
        Initialize GitHub Models client.

        Args:
            githubToken: GitHub Personal Access Token.
            model: Model to use (default: gpt-4o-mini).
        """
        self.githubToken = githubToken
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {githubToken}",
            "Content-Type": "application/json"
        }
        self.maxRetries = 3
        self.baseDelay = 5

    def generate(self, prompt: str, systemPrompt: str = None, maxTokens: int = 4000, temperature: float = 0.3) -> str:
        """
        Generate a response using GitHub Models with retry logic.

        Args:
            prompt: The user prompt.
            systemPrompt: Optional system prompt.
            maxTokens: Maximum tokens in response.
            temperature: Creativity level (0-1).

        Returns:
            Generated text.
        """
        messages = []

        if systemPrompt:
            messages.append({"role": "system", "content": systemPrompt})

        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": maxTokens,
            "temperature": temperature
        }

        for attempt in range(self.maxRetries):
            try:
                response = requests.post(
                    f"{self.BASE_URL}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=120
                )
                response.raise_for_status()

                data = response.json()
                return data["choices"][0]["message"]["content"]

            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    waitTime = self.baseDelay * (attempt + 1) * 2
                    logger.warning(f"Rate limited. Waiting {waitTime}s (attempt {attempt + 1}/{self.maxRetries})")
                    time.sleep(waitTime)
                    continue
                elif response.status_code == 401:
                    raise RuntimeError("Invalid GitHub token.")
                elif response.status_code == 403:
                    raise RuntimeError("GitHub Copilot access required.")
                else:
                    raise RuntimeError(f"API error: {e}")
            except Exception as e:
                logger.error(f"Generation failed: {e}")
                raise

        raise RuntimeError(f"API rate limit exceeded after {self.maxRetries} retries")

    def testConnection(self) -> bool:
        """Test if the API connection works."""
        try:
            response = self.generate("Say 'OK'", maxTokens=10)
            return bool(response)
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
