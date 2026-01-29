import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all AI agents using GitHub Models API."""
    
    def __init__(
        self,
        name: str,
        githubToken: str,
        modelName: str = "gpt-4o-mini",
        temperature: float = 0.3,
        maxTokens: int = 4000
    ):
        self.name = name
        self.modelName = modelName
        self.temperature = temperature
        self.maxTokens = maxTokens
        
        if not githubToken:
            raise ValueError("GITHUB_TOKEN is required.")
        
        self._initGitHubModels(githubToken)
    
    def _initGitHubModels(self, githubToken: str):
        """Initialize GitHub Models client."""
        try:
            from utils.githubModels import GitHubModelsClient
            self.client = GitHubModelsClient(
                githubToken=githubToken,
                model=self.modelName
            )
            logger.info(f"Agent '{self.name}' initialized with {self.modelName}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize GitHub Models: {e}")
    
    def generate(self, prompt: str, systemPrompt: str = None) -> str:
        """
        Generate a response using GitHub Models API.
        
        Args:
            prompt: The user prompt
            systemPrompt: Optional system prompt for context
        
        Returns:
            Generated text response
        """
        try:
            return self.client.generate(
                prompt=prompt,
                systemPrompt=systemPrompt,
                temperature=self.temperature,
                maxTokens=self.maxTokens
            )
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """Execute the agent's main task."""
        pass
    
    @property
    def systemPrompt(self) -> str:
        """Return the agent's system prompt."""
        return ""
