"""
念念 - 语音克隆集成模块
支持 ElevenLabs / Azure Custom Neural Voice
用于将用户上传的语音样本训练为可复用的语音模型
"""
import os
import json
import uuid
import httpx
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class VoiceModel:
    """语音模型"""
    id: str
    name: str
    provider: str  # elevenlabs, azure, local
    status: str  # training, ready, failed
    voice_id: Optional[str] = None  # Provider's voice ID
    sample_urls: List[str] = field(default_factory=list)
    created_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class ElevenLabsVoiceClone:
    """ElevenLabs 语音克隆"""
    
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY", "")
        self.headers = {
            "xi-api-key": self.api_key,
            "Accept": "application/json",
        }
    
    async def create_voice(
        self,
        name: str,
        audio_files: List[bytes],
        description: str = ""
    ) -> VoiceModel:
        """创建语音模型（上传样本 + 训练）"""
        if not self.api_key:
            return VoiceModel(
                id=str(uuid.uuid4()),
                name=name,
                provider="elevenlabs",
                status="failed",
                metadata={"error": "API key not configured"}
            )
        
        async with httpx.AsyncClient(timeout=120) as client:
            # Prepare multipart form data
            files = []
            for i, audio in enumerate(audio_files):
                files.append(
                    ("files", (f"sample_{i}.wav", audio, "audio/wav"))
                )
            
            data = {
                "name": name,
                "description": description or f"念念语音模型 - {name}",
            }
            
            try:
                resp = await client.post(
                    f"{self.BASE_URL}/voices/add",
                    headers=self.headers,
                    data=data,
                    files=files,
                )
                resp.raise_for_status()
                result = resp.json()
                
                return VoiceModel(
                    id=str(uuid.uuid4()),
                    name=name,
                    provider="elevenlabs",
                    status="ready",
                    voice_id=result.get("voice_id"),
                    metadata=result
                )
            except Exception as e:
                return VoiceModel(
                    id=str(uuid.uuid4()),
                    name=name,
                    provider="elevenlabs",
                    status="failed",
                    metadata={"error": str(e)}
                )
    
    async def synthesize(
        self,
        voice_id: str,
        text: str,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
    ) -> Optional[bytes]:
        """使用克隆语音合成音频"""
        if not self.api_key:
            return None
        
        async with httpx.AsyncClient(timeout=60) as client:
            try:
                resp = await client.post(
                    f"{self.BASE_URL}/text-to-speech/{voice_id}",
                    headers={
                        **self.headers,
                        "Content-Type": "application/json",
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_multilingual_v2",
                        "voice_settings": {
                            "stability": stability,
                            "similarity_boost": similarity_boost,
                            "style": style,
                        }
                    }
                )
                resp.raise_for_status()
                return resp.content
            except Exception as e:
                print(f"TTS error: {e}")
                return None
    
    async def get_voices(self) -> List[Dict]:
        """获取所有可用语音"""
        if not self.api_key:
            return []
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/voices",
                    headers=self.headers,
                )
                resp.raise_for_status()
                return resp.json().get("voices", [])
            except Exception:
                return []
    
    async def delete_voice(self, voice_id: str) -> bool:
        """删除语音模型"""
        if not self.api_key:
            return False
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.delete(
                    f"{self.BASE_URL}/voices/{voice_id}",
                    headers=self.headers,
                )
                return resp.status_code == 200
            except Exception:
                return False


class AzureVoiceClone:
    """Azure Custom Neural Voice（预留接口）"""
    
    def __init__(self, api_key: str = "", region: str = "eastus"):
        self.api_key = api_key
        self.region = region
    
    async def create_voice(self, name: str, audio_files: List[bytes]) -> VoiceModel:
        # Azure Custom Neural Voice requires a more complex setup
        # This is a placeholder for future implementation
        return VoiceModel(
            id=str(uuid.uuid4()),
            name=name,
            provider="azure",
            status="failed",
            metadata={"error": "Azure voice clone not yet implemented"}
        )


class VoiceCloneManager:
    """语音克隆管理器"""
    
    def __init__(self):
        self.elevenlabs = ElevenLabsVoiceClone()
        self.azure = AzureVoiceClone()
    
    async def create_voice(
        self,
        name: str,
        audio_files: List[bytes],
        provider: str = "elevenlabs",
        description: str = ""
    ) -> VoiceModel:
        """创建语音模型"""
        if provider == "elevenlabs":
            return await self.elevenlabs.create_voice(name, audio_files, description)
        elif provider == "azure":
            return await self.azure.create_voice(name, audio_files)
        else:
            return VoiceModel(
                id=str(uuid.uuid4()),
                name=name,
                provider=provider,
                status="failed",
                metadata={"error": f"Unknown provider: {provider}"}
            )
    
    async def synthesize(
        self,
        voice_id: str,
        text: str,
        provider: str = "elevenlabs",
        **kwargs
    ) -> Optional[bytes]:
        """合成语音"""
        if provider == "elevenlabs":
            return await self.elevenlabs.synthesize(voice_id, text, **kwargs)
        return None
    
    async def list_voices(self, provider: str = "elevenlabs") -> List[Dict]:
        """列出所有语音"""
        if provider == "elevenlabs":
            return await self.elevenlabs.get_voices()
        return []


# 全局实例
voice_clone_manager = VoiceCloneManager()
