# CISA KEV Monitor

A real-time monitoring system for CISA Known Exploited Vulnerabilities (KEV) catalog. This web application provides up-to-date vulnerability information, search functionality, and comprehensive monitoring capabilities.

## 🚀 Features

- **Real-time Data Sync**: Automatically synchronizes with CISA KEV API
- **Advanced Search**: Filter vulnerabilities by CVE, vendor, product, and date
- **Comprehensive Dashboard**: View vulnerability statistics and trends
- **REST API**: Full API access with OpenAPI documentation
- **Responsive Design**: Mobile-friendly interface with modern UI
- **Docker Support**: Easy deployment with Docker Compose

## 🛠 Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **PostgreSQL**: Primary database for vulnerability data
- **Redis**: Caching and session storage
- **SQLAlchemy**: ORM with async support
- **Pydantic**: Data validation and serialization

### Frontend
- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **React Query**: Data fetching and caching

## 📦 Installation

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mkway/cisa-kev-monitor.git
   cd cisa-kev-monitor
   ```

2. **Start the services**
   ```bash
   docker-compose up -d
   ```

3. **Initialize the database**
   ```bash
   # Access backend container
   docker exec -it cisa-kev-backend bash
   
   # Run database initialization
   python -m app.cli init-db
   
   # Sync CISA KEV data
   python -m app.cli sync-data
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start PostgreSQL and Redis**
   ```bash
   docker-compose up -d postgres redis
   ```

5. **Run database migrations**
   ```bash
   python -m app.cli init-db
   ```

6. **Start development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

## 🎯 Usage

### API Endpoints

#### Vulnerabilities
- `GET /api/vulnerabilities/` - List vulnerabilities with pagination
- `GET /api/vulnerabilities/{cve}` - Get specific vulnerability
- `POST /api/vulnerabilities/search` - Advanced search
- `GET /api/vulnerabilities/stats/overview` - Get statistics

#### Synchronization
- `GET /api/sync/status` - Check sync status
- `POST /api/sync/manual` - Trigger manual sync

#### Vendors
- `GET /api/vulnerabilities/vendors/` - List vendors

### CLI Commands

```bash
# Database operations
python -m app.cli init-db          # Initialize database
python -m app.cli reset-db         # Reset database

# Data synchronization
python -m app.cli sync-data        # Sync CISA KEV data
python -m app.cli check-updates    # Check for updates

# Development utilities
python -m app.cli dev-seed         # Seed test data
```

### Automation Scripts

The project includes automation scripts for development workflow:

```bash
# Project initialization
./scripts/dev_workflow.sh init

# Daily workflow
./scripts/dev_workflow.sh start-day
./scripts/dev_workflow.sh end-day

# Development environment
./scripts/dev_workflow.sh start-dev
./scripts/dev_workflow.sh stop-dev

# Project status
./scripts/dev_workflow.sh status
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/cisa_kev
REDIS_URL=redis://localhost:6379
CISA_KEV_API_URL=https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
ALLOWED_HOSTS=["http://localhost:3000"]
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 Database Schema

### Main Tables
- **vulnerabilities**: Core vulnerability data from CISA KEV
- **vendors**: Software/hardware vendors
- **products**: Vulnerable products
- **sync_logs**: Data synchronization history

### Key Fields
- **CVE ID**: Common Vulnerabilities and Exposures identifier
- **CVSS Score**: Common Vulnerability Scoring System score
- **Known Exploited**: Whether vulnerability is actively exploited
- **Date Added**: When vulnerability was added to KEV catalog
- **Due Date**: Remediation deadline for federal agencies

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Integration tests
npm run test:e2e
```

## 📈 Monitoring

### Health Checks
- Database connectivity: `/api/health/db`
- Redis connectivity: `/api/health/redis`
- External API: `/api/health/external`

### Logs
- Application logs: `backend/logs/app.log`
- Access logs: `backend/logs/access.log`
- Sync logs: Database table `sync_logs`

## 🚀 Deployment

### Production Deployment

1. **Update environment files**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Build and deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Initialize production database**
   ```bash
   docker exec -it cisa-kev-backend python -m app.cli init-db
   docker exec -it cisa-kev-backend python -m app.cli sync-data
   ```

### SSL Configuration
Configure reverse proxy (nginx) for HTTPS:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:3000;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

## 📝 API Documentation

- **OpenAPI Spec**: Available at `/docs` (Swagger UI)
- **ReDoc**: Available at `/redoc`
- **OpenAPI JSON**: Available at `/openapi.json`

### Example API Usage

```javascript
// Fetch vulnerabilities
const response = await fetch('/api/vulnerabilities/?page=1&per_page=10');
const data = await response.json();

// Search vulnerabilities
const searchResponse = await fetch('/api/vulnerabilities/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'Microsoft',
    dateFrom: '2024-01-01',
    dateTo: '2024-12-31'
  })
});
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Commit changes**: `git commit -m "Add new feature"`
4. **Push to branch**: `git push origin feature/new-feature`
5. **Create Pull Request**

### Development Guidelines
- Follow Python PEP 8 style guide
- Use TypeScript strict mode
- Write unit tests for new features
- Update documentation for API changes

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check PostgreSQL container
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

#### CORS Errors
```bash
# Check CORS settings in backend/app/core/config.py
# Ensure frontend URL is in ALLOWED_HOSTS
```

#### Build Failures
```bash
# Clean build cache
docker-compose down -v
docker-compose build --no-cache
```

#### External Access Issues
For WSL/local development with external access:
1. Update `ALLOWED_HOSTS` with your IP address
2. Configure firewall rules
3. Update frontend `NEXT_PUBLIC_API_URL`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [CISA](https://www.cisa.gov/) for providing the KEV catalog
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [Next.js](https://nextjs.org/) for the React framework
- Open source community for all the amazing tools and libraries

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Mkway/cisa-kev-monitor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Mkway/cisa-kev-monitor/discussions)
- **Email**: mkway1004@gmail.com

---

**🔒 Security Notice**: This tool is designed for defensive security purposes only. It helps security teams monitor and respond to known vulnerabilities. Please use responsibly and in accordance with your organization's security policies.