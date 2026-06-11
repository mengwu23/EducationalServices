"""企业业务办理助手的依赖注入。"""

from typing import Optional

from fastapi import Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db

from .llm_client import OperationLlmClient
from .orchestrator import OperationOrchestrator


def _get_llm_client() -> OperationLlmClient:
    """获取 LLM 客户端（单例模式）。"""
    return OperationLlmClient()


def get_orchestrator(
    db: Session = Depends(get_db),
    llm_client: OperationLlmClient = Depends(_get_llm_client),
) -> OperationOrchestrator:
    """获取编排器实例。"""
    return OperationOrchestrator(db, llm_client)
