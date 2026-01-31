from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class QueryStructDTO(BaseModel):
    """Query genereated by LLM"""
    text: str


class QueryResponseDTO(BaseModel):
    """Objeto que transporta a resposta completa para o Frontend"""
    question: str
    reasoning: str  # O "pensamento" do agente
    sql_generated: str
    # Lista de dicionários (flexível para qualquer query)
    data: List[Dict[str, Any]]
    visualization_suggestion: Optional[str] = "table"  # "bar", "line", etc.
    error: Optional[str] = None
