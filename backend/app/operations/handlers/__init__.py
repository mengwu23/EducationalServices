"""操作处理器注册表。"""

from typing import Dict

from backend.app.operations.base_handler import OperationHandler

_registry: Dict[str, OperationHandler] = {}


def register_handler(handler: OperationHandler) -> None:
    """注册一个操作处理器。"""
    _registry[handler.intent] = handler


def get_handler(intent: str) -> OperationHandler:
    """按意图获取处理器。"""
    handler = _registry.get(intent)
    if handler is None:
        raise ValueError(f"不支持的操作意图: {intent}")
    return handler


def list_intents() -> Dict[str, str]:
    """返回所有已注册的意图及其描述。"""
    return {intent: handler.schema.description for intent, handler in _registry.items()}
