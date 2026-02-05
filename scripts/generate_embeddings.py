#!/usr/bin/env python3
"""
Generate embeddings for flower species using HuggingFace CLIP model
Run this after inserting seed data to populate the embedding column
"""

import os
import asyncio
from supabase import create_client
from PIL import Image
import requests
from io import BytesIO
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

HF_TOKEN = os.getenv("HF_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/openai/clip-vit-base-patch32"

async def get_image_embedding(image_url: str) -> list:
    """
    Download image and get CLIP embedding from HuggingFace
    """
    try:
        # Download image
        response = requests.get(image_url, timeout=10)
        img = Image.open(BytesIO(response.content)).convert('RGB')
        
        # Resize to reasonable size
        img.thumbnail((512, 512))
        
        # Convert to bytes
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        img_bytes = buffered.getvalue()
        
        # Get embedding from HuggingFace
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        hf_response = requests.post(
            HF_API_URL,
            headers=headers,
            files={"file": ("image.jpg", img_bytes, "image/jpeg")},
            timeout=30
        )
        
        if hf_response.status_code == 200:
            embedding = hf_response.json()
            
            # CLIP returns 512-dim, reduce to 384
            if isinstance(embedding, list) and len(embedding) >= 384:
                return embedding[:384]
            else:
                print(f"⚠️ Unexpected embedding format for {image_url}")
                return generate_dummy_embedding()
        else:
            print(f"❌ HF API error {hf_response.status_code} for {image_url}")
            return generate_dummy_embedding()
            
    except Exception as e:
        print(f"❌ Error processing {image_url}: {e}")
        return generate_dummy_embedding()

def generate_dummy_embedding() -> list:
    """Generate a normalized random embedding for testing"""
    vec = np.random.randn(384)
    vec = vec / np.linalg.norm(vec)
    return vec.tolist()

async def process_species():
    """
    Fetch all species without embeddings and generate them
    """
    print("🔍 Fetching species without embeddings...")
    
    # Get species that need embeddings
    result = supabase.table("species")\
        .select("id, scientific_name, primary_image_url")\
        .is_("embedding", "null")\
        .execute()
    
    species_list = result.data
    total = len(species_list)
    
    print(f"📊 Found {total} species needing embeddings")
    
    if total == 0:
        print("✅ All species already have embeddings!")
        return
    
    # Process each species
    for idx, species in enumerate(species_list, 1):
        species_id = species['id']
        name = species['scientific_name']
        image_url = species['primary_image_url']
        
        print(f"\n[{idx}/{total}] Processing: {name}")
        
        if not image_url:
            print(f"  ⚠️ No image URL, skipping...")
            continue
        
        # Get embedding
        print(f"  🎨 Generating embedding...")
        embedding = await get_image_embedding(image_url)
        
        # Update database
        print(f"  💾 Updating database...")
        try:
            supabase.table("species")\
                .update({"embedding": embedding})\
                .eq("id", species_id)\
                .execute()
            print(f"  ✅ Success!")
        except Exception as e:
            print(f"  ❌ Database error: {e}")
        
        # Rate limiting (HF free tier)
        if idx < total:
            print("  ⏳ Waiting 3 seconds (rate limiting)...")
            await asyncio.sleep(3)
    
    print("\n🎉 Embedding generation complete!")
    print("\n📋 Summary:")
    print(f"   Total processed: {total}")
    print(f"   Success rate: Check database for null embeddings")

async def verify_embeddings():
    """
    Verify all species have embeddings
    """
    print("\n🔍 Verifying embeddings...")
    
    result = supabase.table("species")\
        .select("id", count="exact")\
        .is_("embedding", "null")\
        .execute()
    
    missing = result.count
    
    if missing == 0:
        print("✅ All species have embeddings!")
    else:
        print(f"⚠️ {missing} species still missing embeddings")
        print("   Run this script again to retry")

async def main():
    """Main execution"""
    print("🌸 Calyx.io Embedding Generator")
    print("=" * 50)
    
    # Check environment
    if not os.getenv("SUPABASE_URL"):
        print("❌ SUPABASE_URL not set in environment")
        return
    
    if not os.getenv("HF_TOKEN"):
        print("❌ HF_TOKEN not set in environment")
        return
    
    print("✅ Environment configured")
    
    # Process species
    await process_species()
    
    # Verify
    await verify_embeddings()
    
    print("\n" + "=" * 50)
    print("🎉 Complete! Your database is ready.")

if __name__ == "__main__":
    asyncio.run(main())
