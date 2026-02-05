# Calyx 🌸

> AI-powered flower identification and cataloging platform

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Status: Beta](https://img.shields.io/badge/Status-Beta-yellow.svg)]()

Calyx is a modern web application that helps users identify, discover, and catalog flowers using AI-powered image recognition and comprehensive botanical data.

## 🌐 Live Application

**Web App**: [calyx.app](https://calyx.app) *(coming soon)*  
**iOS App**: [Download on App Store](https://apps.apple.com/app/calyx) *(coming soon)*  
**API Docs**: [api.calyx.app/docs](https://api.calyx.app/docs)

---

## ✨ Features

- 🔍 **AI Flower Identification** - Upload a photo, get instant species identification
- 📚 **Comprehensive Database** - 100+ flower species with care instructions
- 🔎 **Smart Search** - Find flowers by common or scientific name
- 💾 **Personal Collections** - Save and organize your favorite flowers
- 📱 **Mobile-First Design** - Responsive interface optimized for all devices
- 🎨 **Interactive UI** - Beautiful botanical-themed design with animated backgrounds

---

## 🏗️ Architecture

### Tech Stack

**Frontend**
- React/Next.js with TypeScript
- TailwindCSS for styling
- Three.js for WebGL shaders
- Deployed on Vercel

**Backend**
- Python FastAPI
- PostgreSQL with pgvector extension
- HuggingFace CLIP model for image analysis
- Deployed on Render

**Database**
- Supabase (PostgreSQL)
- Vector similarity search
- Trait-based filtering

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 15+ with pgvector
- Supabase account (or PostgreSQL instance)
- HuggingFace API token

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/calyx.git
cd calyx
```

#### 2. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your API URL
npm run dev
```

Frontend runs at `http://localhost:3000`

#### 3. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`

#### 4. Database Setup

```bash
# Run schema and seed data
psql -h your-db-host -U your-user -d calyx < database/schema.sql
psql -h your-db-host -U your-user -d calyx < database/seed_data.sql

# Generate embeddings (optional)
python scripts/generate_embeddings.py
```

---

## 📡 API Reference

### Base URL
```
https://api.calyx.app
```

### Key Endpoints

**Identify Flower**
```http
POST /api/v1/identify
Content-Type: multipart/form-data

Body: { image: File }
```

**Search Flowers**
```http
GET /api/v1/search?q={query}
```

**Get Species Details**
```http
GET /api/v1/species/{id}
```

Full API documentation: [api.calyx.app/docs](https://api.calyx.app/docs)

---

## 🗄️ Database Schema

```sql
-- Core tables
species              -- Flower species data
species_traits       -- Searchable traits (color, petals, etc.)
species_media        -- Images and media
identification_cache -- Performance optimization
identification_feedback -- User feedback for ML improvement
```

---

## 🔧 Configuration

### Environment Variables

**Frontend** (`.env.local`)
```env
VITE_API_URL=https://api.calyx.app
```

**Backend** (`.env`)
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
HF_TOKEN=your-huggingface-token
```

---

## 📦 Deployment

### Frontend (Vercel)

```bash
vercel --prod
```

### Backend (Render)

```yaml
# render.yaml included in repo
# Push to main branch for auto-deployment
```

### Database (Supabase)

1. Create new project at [supabase.com](https://supabase.com)
2. Run `schema.sql` in SQL Editor
3. Run `seed_data.sql` to populate data
4. Enable pgvector extension

---

## 🧪 Testing

### Frontend
```bash
npm test
npm run test:e2e
```

### Backend
```bash
pytest
python test_api.py
```

---

## 📚 Documentation

- [API Documentation](./docs/API.md)
- [Database Schema](./docs/DATABASE.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Contributing Guidelines](./CONTRIBUTING.md)

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](./CONTRIBUTING.md) first.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## 🙏 Acknowledgments

- [GBIF](https://www.gbif.org/) - Botanical taxonomy data
- [iNaturalist](https://www.inaturalist.org/) - Flower images
- [HuggingFace](https://huggingface.co/) - CLIP model inference
- [Supabase](https://supabase.com/) - Database and storage
- [Render](https://render.com/) - API hosting

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/calyx/issues)
- **Email**: support@calyx.app
- **Website**: [calyx.app](https://calyx.app)

---

## 🗺️ Roadmap

- [x] MVP with 100 flower species
- [x] AI-powered identification
- [x] Search and filtering
- [ ] User authentication and profiles
- [ ] Community features (comments, sharing)
- [ ] Mobile app (iOS/Android)
- [ ] Image recognition improvements
- [ ] Expand to 1,000+ species
- [ ] Garden planning tools
- [ ] Care reminders and notifications

---

## 📊 Project Status

**Current Version**: 0.1.0 (Beta)  
**API Status**: ✅ Operational  
**Database**: 100 species  
**Uptime**: 99.5%

---

**Built with 🌸 by the Calyx Team**

*Discover. Identify. Catalog.*
