"""
Валидация конфигурации с использованием Pydantic
"""

from typing import Optional, Dict, Any, List, Tuple
from pydantic import BaseModel, validator, Field
import logging

logger = logging.getLogger(__name__)


class GenerationConfig(BaseModel):
    """Конфигурация генерации"""
    max_tokens: int = Field(default=4096, ge=1, le=32768)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    top_k: int = Field(default=40, ge=1, le=100)
    repetition_penalty: float = Field(default=1.1, ge=1.0, le=2.0)


class ModelConfig(BaseModel):
    """Конфигурация модели"""
    provider: str = Field(..., description="Провайдер модели")
    model_name: str = Field(..., description="Имя модели")
    device: str = Field(default="cuda", description="Устройство")
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    model_path: Optional[str] = None
    
    @validator('provider')
    def validate_provider(cls, v):
        allowed = ['ollama', 'lmstudio', 'local_transformers']
        if v not in allowed:
            raise ValueError(f'Неподдерживаемый провайдер: {v}. Допустимые: {allowed}')
        return v
    
    @validator('device')
    def validate_device(cls, v):
        allowed = ['cuda', 'cpu', 'mps']
        if v not in allowed:
            raise ValueError(f'Неподдерживаемое устройство: {v}. Допустимые: {allowed}')
        return v


class AgentConfig(BaseModel):
    """Конфигурация агента"""
    system_prompt: str = Field(default="Ты опытный AI-ассистент для программирования.")
    history_path: str = Field(default="./history")
    max_context_length: int = Field(default=8192, ge=1024, le=32768)
    save_history: bool = Field(default=True)
    load_project_context: bool = Field(default=True)
    project_root: str = Field(default=".")


class OllamaConfig(BaseModel):
    """Конфигурация Ollama"""
    base_url: str = Field(default="http://localhost:11434")
    timeout: int = Field(default=300, ge=1, le=3600)


class LMStudioConfig(BaseModel):
    """Конфигурация LM Studio"""
    base_url: str = Field(default="http://localhost:1234")
    timeout: int = Field(default=300, ge=1, le=3600)


class MCPConfig(BaseModel):
    """Конфигурация MCP"""
    enabled: bool = Field(default=True)
    max_iterations: int = Field(default=5, ge=1, le=20)


class GPUConfig(BaseModel):
    """Конфигурация GPU"""
    use_gpu: bool = Field(default=True)
    max_memory: int = Field(default=24, ge=1, le=128)
    use_4bit: bool = Field(default=False)
    use_8bit: bool = Field(default=False)
    use_flash_attention: bool = Field(default=True)


class UIConfig(BaseModel):
    """Конфигурация UI"""
    cli_theme: str = Field(default="dark")
    mode: str = Field(default="both")
    web_host: str = Field(default="127.0.0.1")
    web_port: int = Field(default=8000, ge=1024, le=65535)


class AppConfig(BaseModel):
    """Полная конфигурация приложения"""
    model: ModelConfig
    agent: AgentConfig = Field(default_factory=AgentConfig)
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    lmstudio: LMStudioConfig = Field(default_factory=LMStudioConfig)
    mcp: MCPConfig = Field(default_factory=MCPConfig)
    gpu: GPUConfig = Field(default_factory=GPUConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AppConfig':
        """
        Создать конфигурацию из словаря
        
        Args:
            config_dict: Словарь с конфигурацией
        
        Returns:
            Валидированная конфигурация
        """
        try:
            return cls(**config_dict)
        except Exception as e:
            logger.error(f"Ошибка валидации конфигурации: {e}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать конфигурацию в словарь"""
        return self.dict(exclude_none=True)


def validate_config(config_dict: Dict[str, Any]) -> Tuple[bool, Optional[AppConfig], Optional[str]]:
    """
    Валидация конфигурации
    
    Args:
        config_dict: Словарь с конфигурацией
    
    Returns:
        Кортеж (успех, конфигурация или None, сообщение об ошибке или None)
    """
    try:
        config = AppConfig.from_dict(config_dict)
        return True, config, None
    except Exception as e:
        error_msg = f"Ошибка валидации конфигурации: {str(e)}"
        logger.error(error_msg)
        return False, None, error_msg

