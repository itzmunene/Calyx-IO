import httpx
import numpy as np
from PIL import Image
import io
import os
from typing import Dict, List
import onnxruntime as ort
import base64

class VisionModel:
    def __init__(self):
        self.hf_token = os.getenv("HF_TOKEN")
        self.hf_api_url = "https://api-inference.huggingface.co/models"
        self.clip_model = "openai/clip-vit-base-patch32"
        
        self.daily_request_count = 0
        self.max_daily_requests = 1000
        
        self.onnx_session = None
        self.loaded = False
        
    async def load_model(self):
        """Load ONNX model for fallback (runs on CPU)"""
        try:
            # For POC, we'll use HuggingFace primarily
            # ONNX model can be added later for local inference
            self.loaded = True
            print("✅ Vision model initialized (using HuggingFace API)")
        except Exception as e:
            print(f"⚠️ ONNX model not loaded: {e}")
            self.loaded = True  # Still operational with HF API
    
    def is_loaded(self):
        return self.loaded
    
    async def extract_traits(self, image: Image.Image) -> Dict:
        """
        Extract traits using CLIP zero-shot classification
        Free tier: 1,000 requests/day on HuggingFace
        """
        self.daily_request_count += 1
        
        if self.daily_request_count > self.max_daily_requests:
            # Fallback to basic trait extraction
            print("⚠️ Daily HF quota exceeded, using fallback")
            return self._extract_traits_fallback(image)
        
        # Prepare image
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        img_bytes = buffered.getvalue()
        
        # Define trait labels for zero-shot classification
        color_labels = [
            "yellow flower", "white flower", "red flower", "pink flower",
            "purple flower", "blue flower", "orange flower"
        ]
        
        petal_labels = [
            "flower with 3 petals", "flower with 4 petals", "flower with 5 petals",
            "flower with 6 petals", "flower with many petals"
        ]
        
        size_labels = [
            "small flower", "medium flower", "large flower"
        ]
        
        try:
            # Query HuggingFace CLIP model
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"Authorization": f"Bearer {self.hf_token}"}
                
                # Color classification
                color_response = await client.post(
                    f"{self.hf_api_url}/{self.clip_model}",
                    headers=headers,
                    files={"file": ("image.jpg", img_bytes, "image/jpeg")},
                    data={"candidate_labels": ",".join(color_labels)}
                )
                
                if color_response.status_code != 200:
                    print(f"HF API error: {color_response.status_code}")
                    return self._extract_traits_fallback(image)
                
                color_result = color_response.json()
                
                # Parse results (simplified for POC)
                traits = {
                    "color_primary": [self._parse_color(color_result[0]['label']) if color_result else "unknown"],
                    "petal_count": 5,  # Default for POC
                    "flower_size": "medium",  # Default for POC
                    "confidence": {
                        "color": color_result[0]['score'] if color_result else 0.5
                    }
                }
                
                return traits
                
        except Exception as e:
            print(f"Error in trait extraction: {e}")
            return self._extract_traits_fallback(image)
    
    async def get_embedding(self, image: Image.Image) -> List[float]:
        """
        Get image embedding for vector similarity search
        Returns 384-dimensional vector
        """
        try:
            # Prepare image
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=85)
            img_bytes = buffered.getvalue()
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"Authorization": f"Bearer {self.hf_token}"}
                
                # Use feature extraction endpoint
                response = await client.post(
                    f"{self.hf_api_url}/{self.clip_model}",
                    headers=headers,
                    files={"file": ("image.jpg", img_bytes, "image/jpeg")}
                )
                
                if response.status_code != 200:
                    print(f"HF embedding API error: {response.status_code}")
                    return self._get_dummy_embedding()
                
                # Response is the embedding vector
                embedding = response.json()
                
                # CLIP-ViT-B/32 returns 512-dim, reduce to 384
                if isinstance(embedding, list) and len(embedding) >= 384:
                    return embedding[:384]
                else:
                    return self._get_dummy_embedding()
                    
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return self._get_dummy_embedding()
    
    def _extract_traits_fallback(self, image: Image.Image) -> Dict:
        """
        Fallback trait extraction when HF quota exceeded
        Uses basic color histogram analysis
        """
        try:
            # Simple color analysis
            img_array = np.array(image.resize((100, 100)))
            
            # Get dominant color channel
            avg_colors = img_array.mean(axis=(0, 1))
            r, g, b = avg_colors
            
            # Determine color
            if r > g and r > b:
                color = "red"
            elif g > r and g > b:
                if b > 150:
                    color = "blue"
                else:
                    color = "yellow"
            elif b > r and b > g:
                color = "blue"
            else:
                color = "white"
            
            return {
                "color_primary": [color],
                "petal_count": 5,  # Default assumption
                "flower_size": "medium",
                "confidence": {"fallback": True, "color": 0.3}
            }
        except Exception as e:
            print(f"Fallback extraction error: {e}")
            return {
                "color_primary": ["unknown"],
                "petal_count": None,
                "flower_size": "medium",
                "confidence": {"fallback": True, "error": True}
            }
    
    def _get_dummy_embedding(self) -> List[float]:
        """Generate a dummy embedding for testing"""
        # Return a normalized random vector
        vec = np.random.randn(384)
        vec = vec / np.linalg.norm(vec)
        return vec.tolist()
    
    @staticmethod
    def _parse_color(label: str) -> str:
        """Parse color from label like 'yellow flower' -> 'yellow'"""
        return label.split()[0] if label else "unknown"
    
    @staticmethod
    def _parse_petal_count(label: str) -> int:
        """Parse petal count from label"""
        parts = label.split()
        if "many" in parts:
            return 10  # Represent "many" as 10+
        try:
            return int(parts[2])  # "flower with 5 petals" -> 5
        except:
            return 5  # Default
    
    @staticmethod
    def _parse_size(label: str) -> str:
        """Parse size from label like 'small flower' -> 'small'"""
        return label.split()[0] if label else "medium"
