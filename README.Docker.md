# Docker Deployment Guide

This guide explains how to run PDF-Insight using Docker.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 1.29 or higher)

## Quick Start

### Production Deployment

1. **Build and start the container:**
   ```bash
   docker-compose up -d
   ```

2. **Access the application:**
   Open your browser and navigate to `http://localhost:8011`

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the container:**
   ```bash
   docker-compose down
   ```

### Development Mode

For development with hot reload:

```bash
docker-compose -f docker-compose.dev.yml up
```

This mounts your source code as volumes, so changes are reflected immediately.

## Docker Commands

### Build the image
```bash
docker-compose build
```

### Start the service
```bash
docker-compose up -d
```

### Stop the service
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f pdf-insight
```

### Restart the service
```bash
docker-compose restart
```

### Execute commands inside the container
```bash
docker-compose exec pdf-insight bash
```

### Remove all data (caution!)
```bash
docker-compose down -v
```

## Data Persistence

The following directories are mounted as volumes to persist data:

- `./data` - PDF files (pending, processed, images, text)
- `./logs` - Application logs
- `./chroma_db` - ChromaDB vector database
- `./pdf_metadata.db` - SQLite database

All data is preserved even if you stop or remove the container.

## Configuration

### Port Configuration

To change the port, edit `docker-compose.yml`:

```yaml
ports:
  - "8080:8011"  # Change 8080 to your desired port
```

### Environment Variables

You can add environment variables in `docker-compose.yml`:

```yaml
environment:
  - PYTHONUNBUFFERED=1
  - LOG_LEVEL=INFO
```

## Health Check

The container includes a health check that runs every 30 seconds. Check status:

```bash
docker-compose ps
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs

# Rebuild image
docker-compose build --no-cache
docker-compose up -d
```

### Permission issues
```bash
# Fix permissions on data directories
sudo chown -R $USER:$USER data logs chroma_db
```

### Port already in use
```bash
# Find process using port 8011
sudo lsof -i :8011

# Change port in docker-compose.yml
```

### Clear all data and restart
```bash
docker-compose down -v
rm -rf data/processed/* data/images/* data/text/* logs/* chroma_db/*
rm pdf_metadata.db
docker-compose up -d
```

## Building for Production

### Optimize image size
```bash
docker build -t pdf-insight:latest .
```

### Multi-stage build (advanced)
For a smaller production image, you can create a multi-stage Dockerfile.

## Docker Hub Deployment

### Tag and push
```bash
docker tag pdf-insight:latest yourusername/pdf-insight:latest
docker push yourusername/pdf-insight:latest
```

### Pull and run
```bash
docker pull yourusername/pdf-insight:latest
docker run -d -p 8011:8011 -v $(pwd)/data:/app/data yourusername/pdf-insight:latest
```

## Advanced Usage

### Run with custom database location
```bash
docker run -d \
  -p 8011:8011 \
  -v /path/to/data:/app/data \
  -v /path/to/custom.db:/app/pdf_metadata.db \
  pdf-insight:latest
```

### Run tests in container
```bash
docker-compose exec pdf-insight python3 -m pytest
```

### Access Python shell
```bash
docker-compose exec pdf-insight python3
```

## Security Considerations

1. **Don't expose unnecessary ports**
2. **Use secrets for sensitive data** (not environment variables)
3. **Run as non-root user** (can be configured in Dockerfile)
4. **Keep base image updated**
5. **Scan for vulnerabilities:**
   ```bash
   docker scan pdf-insight:latest
   ```

## Performance Tuning

### Adjust container resources
```yaml
services:
  pdf-insight:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Use production ASGI server
For high-traffic deployments, consider using Gunicorn with Uvicorn workers (modify CMD in Dockerfile).
