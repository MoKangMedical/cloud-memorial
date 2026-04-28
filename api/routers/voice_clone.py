"""
念念 - 语音克隆路由
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List, Optional
import os

from ..app_helpers import get_current_user, runtime_config

router = APIRouter(tags=["语音克隆"])

# Lazy import to avoid errors when voice_clone module has issues
_voice_manager = None

def get_voice_manager():
    global _voice_manager
    if _voice_manager is None:
        from ..voice_clone import voice_clone_manager
        _voice_manager = voice_clone_manager
    return _voice_manager


@router.post("/api/voice-clone/create")
async def create_voice_model(
    name: str,
    provider: str = "elevenlabs",
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user)
):
    """创建语音克隆模型"""
    if not files:
        raise HTTPException(status_code=400, detail="请上传至少一个语音样本")
    
    # Read audio files
    audio_files = []
    for f in files:
        content = await f.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail=f"文件 {f.filename} 太大（最大10MB）")
        audio_files.append(content)
    
    manager = get_voice_manager()
    result = await manager.create_voice(
        name=name,
        audio_files=audio_files,
        provider=provider,
        description=f"念念语音模型 - {name}"
    )
    
    return {
        "id": result.id,
        "name": result.name,
        "provider": result.provider,
        "status": result.status,
        "voice_id": result.voice_id,
        "metadata": result.metadata
    }


@router.post("/api/voice-clone/synthesize")
async def synthesize_voice(
    voice_id: str,
    text: str,
    provider: str = "elevenlabs",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    current_user: dict = Depends(get_current_user)
):
    """使用克隆语音合成音频"""
    if not text:
        raise HTTPException(status_code=400, detail="请输入要合成的文字")
    if len(text) > 5000:
        raise HTTPException(status_code=400, detail="文字太长（最大5000字）")
    
    manager = get_voice_manager()
    audio = await manager.synthesize(
        voice_id=voice_id,
        text=text,
        provider=provider,
        stability=stability,
        similarity_boost=similarity_boost
    )
    
    if not audio:
        raise HTTPException(status_code=500, detail="语音合成失败")
    
    from fastapi.responses import Response
    return Response(content=audio, media_type="audio/mpeg")


@router.get("/api/voice-clone/list")
async def list_voice_models(
    provider: str = "elevenlabs",
    current_user: dict = Depends(get_current_user)
):
    """列出所有语音模型"""
    manager = get_voice_manager()
    voices = await manager.list_voices(provider=provider)
    return {"voices": voices}


@router.delete("/api/voice-clone/{voice_id}")
async def delete_voice_model(
    voice_id: str,
    provider: str = "elevenlabs",
    current_user: dict = Depends(get_current_user)
):
    """删除语音模型"""
    if provider == "elevenlabs":
        manager = get_voice_manager()
        success = await manager.elevenlabs.delete_voice(voice_id)
        if not success:
            raise HTTPException(status_code=500, detail="删除失败")
    return {"status": "deleted"}
