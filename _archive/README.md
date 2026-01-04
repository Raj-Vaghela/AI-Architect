# Archive

This folder contains files that are not part of the core application but may be useful for reference or future development.

## Contents

### `project-planning/`
- Original project requirements and planning documents
- Email communications
- Architecture planning PDFs

### `development-notes/`
- Development progress notes and summaries
- Refactoring checklists and completion reports
- Feature implementation guides
- Code review reports

### `backend-test-scripts/`
- Test scripts for backend API endpoints
- Chat testing utilities
- Setup scripts for development environment
- HTML-based chat interface for manual testing

### `data-ingestion-scripts/`
- Scripts for ingesting HuggingFace model data
- Dashboard for data visualization
- Database population utilities
- Model card processing scripts

### `analysis-reports/`
- Database schema analysis
- Data quality reports
- RAG system analysis
- License information preservation notes

## Why These Files Are Archived

These files were moved to keep the main repository clean and focused on the production application code. They contain:
- Historical development artifacts
- One-time data ingestion scripts
- Test utilities (not automated tests)
- Planning and analysis documents

## Using Archived Files

If you need to:
- **Run data ingestion**: See `data-ingestion-scripts/`
- **Understand project history**: See `project-planning/` and `development-notes/`
- **Test the API manually**: See `backend-test-scripts/`
- **Review data quality**: See `analysis-reports/`

## Note

The main application code is in:
- `/backend/` - FastAPI backend
- `/frontend/` - Next.js frontend
- `/README.md` - Main project documentation

