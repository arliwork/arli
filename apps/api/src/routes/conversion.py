"""
API routes for Agent Conversion
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json

from agent_converter import AgentConverter, UniversalAgentPackage

router = APIRouter(prefix="/convert", tags=["conversion"])

converter = AgentConverter()


class ConversionRequest(BaseModel):
    agent_data: Dict[str, Any]
    source_system: Optional[str] = None  # auto-detect if None


class ConversionResponse(BaseModel):
    success: bool
    package: Optional[Dict[str, Any]] = None
    detected_system: Optional[str] = None
    error: Optional[str] = None


class BatchConversionRequest(BaseModel):
    agents: List[Dict[str, Any]]


class BatchConversionResponse(BaseModel):
    success: bool
    converted: int
    failed: int
    packages: List[Dict[str, Any]]
    stats: Dict[str, Any]


@router.post("/agent", response_model=ConversionResponse)
async def convert_agent(request: ConversionRequest):
    """Конвертирует одного агента в Arli формат"""
    try:
        # Detect system
        detected = converter.detect_system(request.agent_data)
        
        # Convert
        package = converter.convert(request.agent_data)
        
        return ConversionResponse(
            success=True,
            package=package.to_dict(),
            detected_system=detected
        )
    except Exception as e:
        return ConversionResponse(
            success=False,
            error=str(e),
            detected_system=converter.detect_system(request.agent_data)
        )


@router.post("/batch", response_model=BatchConversionResponse)
async def convert_batch(request: BatchConversionRequest):
    """Конвертирует несколько агентов"""
    packages = []
    failed = 0
    
    for agent_data in request.agents:
        try:
            package = converter.convert(agent_data)
            packages.append(package.to_dict())
        except Exception:
            failed += 1
    
    return BatchConversionResponse(
        success=True,
        converted=len(packages),
        failed=failed,
        packages=packages,
        stats=converter.get_conversion_stats()
    )


@router.post("/upload")
async def upload_and_convert(file: UploadFile = File(...)):
    """Загружает JSON файл и конвертирует"""
    try:
        content = await file.read()
        agent_data = json.loads(content)
        
        package = converter.convert(agent_data)
        
        return {
            "success": True,
            "filename": file.filename,
            "detected_system": converter.detect_system(agent_data),
            "package": package.to_dict()
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_conversion_stats():
    """Статистика конвертаций"""
    return converter.get_conversion_stats()


@router.get("/supported-systems")
async def get_supported_systems():
    """Список поддерживаемых систем"""
    return {
        "systems": [
            {
                "name": "hermes",
                "description": "Hermes Agent Framework",
                "capabilities": ["fabric", "skills", "trajectory"],
                "conversion_quality": "high"
            },
            {
                "name": "openclaw",
                "description": "OpenClaw Agent System",
                "capabilities": ["modules", "execution_log"],
                "conversion_quality": "medium"
            }
        ],
        "total": 2
    }
