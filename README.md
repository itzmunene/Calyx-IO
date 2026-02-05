# 🌸 Calyx.io Backend API

**Zero-budget flower identification system** using trait elimination and vector similarity search.

## 📋 Project Overview

Calyx.io is a proof-of-concept flower identification API that combines:
- **Trait-based elimination** (color, petal count, size)
- **Vector similarity search** (image embeddings)
- **Smart caching** (7-day cache for repeated queries)

### Tech Stack
- **API**: FastAPI (Python 3.11)
- **Database**: Supabase (PostgreSQL + pgvector)
- **Vision**: HuggingFace CLIP model
- **Hosting**: Render (free tier)

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- Supabase account (free tier)
- HuggingFace account (free tier)
- Render account (free tier)
- Git

### 2. Local Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/calyx-backend.git
cd calyx-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# - Get SUPABASE_URL and SUPABASE_KEY from Supabase dashboard
# - Get HF_TOKEN from https://huggingface.co/settings/tokens
```

### 3. Database Setup

**Step 1: Create Supabase Project**
1. Go to https://supabase.com
2. Create new project (choose free tier)
3. Wait for setup to complete (~2 minutes)

**Step 2: Enable pgvector Extension**
1. Go to SQL Editor in Supabase dashboard
2. Run: `CREATE EXTENSION vector;`

**Step 3: Run Schema**
1. Copy contents of `database/schema.sql`
2. Paste and run in SQL Editor
3. Verify tables created successfully

**Step 4: Seed Data**
1. Copy contents of `database/seed_data.sql`
2. Paste and run in SQL Editor
3. Verify 100 species inserted

### 4. Run Locally

```bash
# Start the API server
uvicorn main:app --reload --port 8000

# Test the API
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": 1234567890,
  "database": "connected",
  "model": "loaded"
}
```

---

## 📡 API Endpoints

### Health Check
```
GET /health
```

### Root Info
```
GET /
```
Returns API info and flower count.

### Identify Flower
```
POST /api/v1/identify
```
**Body**: `multipart/form-data` with `image` file

**Response**:
```json
{
  "species_id": "uuid",
  "scientific_name": "Rosa rubiginosa",
  "common_names": ["Rose", "Sweet Briar"],
  "confidence": 0.87,
  "primary_image_url": "https://...",
  "method": "trait_elimination",
  "traits_extracted": {
    "color_primary": ["pink"],
    "petal_count": 5,
    "flower_size": "medium"
  },
  "alternatives": [...],
  "response_time_ms": 245
}
```

### Search Flowers (Text)
```
GET /api/v1/search?q=rose&limit=20
```

### Get Species Details
```
GET /api/v1/species/{species_id}
```

### Submit Feedback
```
POST /api/v1/feedback
```
**Body**:
```json
{
  "identification_id": "uuid",
  "is_correct": true,
  "correct_species_id": "uuid",
  "notes": "Actually a different variety"
}
```

### Get Stats
```
GET /api/v1/stats
```

---

## 🚢 Deployment (Render)

### Method 1: GitHub Auto-Deploy

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/calyx-backend.git
   git push -u origin main
   ```

2. **Connect to Render**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`

3. **Set Environment Variables**
   - Go to Environment tab
   - Add:
     - `SUPABASE_URL`
     - `SUPABASE_KEY`
     - `HF_TOKEN`

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (~5 minutes)
   - Your API will be live at `https://your-app.onrender.com`

### Method 2: Manual Deploy

```bash
# Install Render CLI
npm install -g render-cli

# Login
render login

# Deploy
render deploy
```

---

## 🧪 Testing

### Test with cURL

```bash
# Health check
curl https://your-app.onrender.com/health

# Identify flower
curl -X POST https://your-app.onrender.com/api/v1/identify \
  -F "image=@path/to/flower.jpg"

# Search
curl "https://your-app.onrender.com/api/v1/search?q=rose"
```

### Test with Python

```python
import requests

# Identify flower
with open('flower.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/identify',
        files={'image': f}
    )
    
print(response.json())
```

---

## 📊 Architecture

```
┌─────────────┐
│   iOS App   │
└──────┬──────┘
       │
       │ HTTPS
       ▼
┌─────────────────┐
│   FastAPI       │ ◄─── Render (Free Tier)
│   (main.py)     │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    │         │          │          │
    ▼         ▼          ▼          ▼
┌────────┐ ┌─────┐  ┌──────┐  ┌─────────┐
│Supabase│ │CLIP │  │Cache │  │ pgvector│
│(Postgres)│ │ HF  │  │Redis?│  │ Search  │
└────────┘ └─────┘  └──────┘  └─────────┘
```

### Flow:
1. **User uploads image** → iOS app sends to `/api/v1/identify`
2. **Check cache** → If image hash exists, return cached result
3. **Extract traits** → Use CLIP to classify color, petals, size
4. **Trait elimination** → PostgreSQL JSONB query filters candidates
5. **Vector refinement** → If multiple matches, use embedding similarity
6. **Cache result** → Store for 7 days
7. **Return response** → JSON with species info + confidence

---

## 💰 Cost Breakdown (Zero Budget)

| Service | Free Tier | Usage |
|---------|-----------|-------|
| **Supabase** | 500MB DB, 2GB bandwidth | ✅ Sufficient for 100 flowers |
| **Render** | 750 hrs/month | ✅ Sleeps after 15min inactivity |
| **HuggingFace** | 1,000 requests/day | ✅ ~30 requests/day expected |
| **Total** | **$0/month** | Perfect for POC |

### Limitations:
- API sleeps after 15min (first request takes ~30s to wake)
- 1,000 HF API calls/day (fallback to basic extraction after)
- No custom domain (use `yourapp.onrender.com`)

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGc...  # Service role key
HF_TOKEN=hf_xxxxx

# Optional
PYTHON_VERSION=3.11.0
PORT=8000  # Auto-set by Render
```

### Database Config

Edit `database/schema.sql` to customize:
- Traits schema (add new fields)
- Vector dimensions (default 384)
- Cache expiry (default 7 days)

---

## 📁 Project Structure

```
calyx-backend/
├── main.py              # FastAPI application
├── models.py            # Pydantic models
├── database.py          # Supabase client
├── vision.py            # HF CLIP model + fallback
├── requirements.txt     # Python dependencies
├── render.yaml          # Render deployment config
├── .env.example         # Environment template
├── .gitignore          # Git ignore rules
├── database/
│   ├── schema.sql      # Database schema
│   └── seed_data.sql   # 100 flower species
└── README.md           # This file
```

---

## 🐛 Troubleshooting

### "Database connection failed"
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in environment
- Check Supabase project is active
- Ensure pgvector extension is enabled

### "HuggingFace API error"
- Verify `HF_TOKEN` is valid
- Check daily quota (1,000 requests)
- Token from: https://huggingface.co/settings/tokens

### "No matching flowers found"
- Seed data might not be loaded
- Run `seed_data.sql` in Supabase SQL Editor
- Check traits are properly formatted in database

### "Render deployment failed"
- Check build logs in Render dashboard
- Verify `requirements.txt` has all dependencies
- Ensure Python 3.11 is specified

### "API is slow"
- Free tier sleeps after 15min inactivity
- First request after sleep takes ~30s
- Consider upgrading to paid tier for production

---

## 🎯 Next Steps

### Phase 1: Complete POC (Current)
- ✅ Database schema
- ✅ API endpoints
- ✅ Trait extraction
- ✅ Vector search
- ⏳ Deploy to Render
- ⏳ Generate embeddings for all 100 flowers

### Phase 2: Improve Accuracy
- Train custom trait classifier
- Add more species (500+)
- Improve trait extraction
- User feedback loop

### Phase 3: Scale
- Migrate to paid hosting (if needed)
- Add caching layer (Redis)
- Optimize vector search
- CDN for images

---

## 📝 API Documentation

Once deployed, interactive docs available at:
- **Swagger UI**: `https://your-app.onrender.com/docs`
- **ReDoc**: `https://your-app.onrender.com/redoc`

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

- **Supabase** - Database and storage
- **HuggingFace** - CLIP model inference
- **Render** - API hosting
- **GBIF** - Botanical taxonomy data
- **iNaturalist** - Flower images

---

## 📞 Support

- **Issues**: GitHub Issues
- **Email**: support@calyx.io
- **Docs**: https://docs.calyx.io

---

Built with 🌸 by the Calyx team
