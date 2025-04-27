# GCP Deployment Guide for Django Application

This guide will help you deploy your Django application with Celery and Redis on Google Cloud Platform (GCP) using a VM instance, Nginx, and Gunicorn.

## 1. Create a GCP VM Instance

1. **Sign in to Google Cloud Console**: https://console.cloud.google.com/

2. **Create a new VM instance**:
   - Navigate to Compute Engine > VM instances
   - Click "Create Instance"
   - Choose a name for your instance (e.g., `django-app-vm`)
   - Select a region and zone close to your users
   - Choose machine type (e.g., e2-medium with 2 vCPUs and 4GB memory)
   - Boot disk: Ubuntu 20.04 LTS (or newer)
   - Allow HTTP and HTTPS traffic in the firewall settings
   - Click "Create"

3. **Connect to your VM** using SSH from the GCP console or using gcloud CLI:
   ```
   gcloud compute ssh django-app-vm
   ```

## 2. Set Up the VM Environment

1. **Update the system**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Docker and Docker Compose**:
   ```bash
   # Install Docker
   sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   sudo apt update
   sudo apt install -y docker-ce
   sudo usermod -aG docker ${USER}
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Install Nginx**:
   ```bash
   sudo apt install -y nginx
   ```

4. **Clone your repository**:
   ```bash
   git clone <your-repository-url> /home/$(whoami)/django-gcp
   cd /home/$(whoami)/django-gcp
   ```

## 3. Configure Nginx as a Reverse Proxy

1. **Create an Nginx configuration file**:
   ```bash
   sudo nano /etc/nginx/sites-available/django-app
   ```

2. **Add the following configuration**:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;  # Replace with your domain or server IP
       
       location /static/ {
           alias /home/$(whoami)/django-gcp/static/;
       }
       
       location /media/ {
           alias /home/$(whoami)/django-gcp/media/;
       }
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **Enable the site and restart Nginx**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/django-app /etc/nginx/sites-enabled/
   sudo rm -f /etc/nginx/sites-enabled/default  # Remove default site
   sudo nginx -t  # Test configuration
   sudo systemctl restart nginx
   ```

## 4. Modify Your Django Settings for Production

1. **Update your settings.py file**:
   ```python
   # Set DEBUG to False
   DEBUG = False
   
   # Update ALLOWED_HOSTS
   ALLOWED_HOSTS = ['your-domain.com', 'your-server-ip']
   
   # Configure static files
   STATIC_URL = '/static/'
   STATIC_ROOT = BASE_DIR / 'static'
   
   # Configure media files
   MEDIA_URL = '/media/'
   MEDIA_ROOT = BASE_DIR / 'media'
   ```

2. **Create a .env file for sensitive information**:
   ```bash
   nano .env
   ```
   Add your environment variables:
   ```
   SECRET_KEY=your-secure-secret-key
   DATABASE_URL=your-database-url
   ```

## 5. Update Docker Compose Configuration

Modify your `docker-compose.yml` file to work with Nginx:

```yaml
version: '3.8'

services:
  web:
    build: .
    command: gunicorn -c gunicorn_config.py config.wsgi:application
    entrypoint: /app/docker-entrypoint.sh
    volumes:
      - .:/app
      - static_volume:/app/static
      - media_volume:/app/media
    expose:
      - "8000"
    depends_on:
      - redis
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings
      - CELERY_BROKER_URL=redis://redis:6379/0

  celery:
    build: .
    command: celery -A config worker --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - web
      - redis
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings
      - CELERY_BROKER_URL=redis://redis:6379/0

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  redis_data:
  static_volume:
  media_volume:
```

## 6. Deploy Your Application

1. **Collect static files**:
   ```bash
   mkdir -p static media
   sudo chown -R $(whoami):$(whoami) static media
   ```

2. **Start the Docker containers**:
   ```bash
   docker-compose up -d
   ```

3. **Collect static files inside the container**:
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

## 7. Set Up SSL with Let's Encrypt (Optional but Recommended)

1. **Install Certbot**:
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   ```

2. **Obtain SSL certificate**:
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

3. **Follow the prompts** to complete the SSL setup.

## 8. Set Up Automatic Deployment (Optional)

You can set up a CI/CD pipeline using GitHub Actions or GitLab CI to automatically deploy your application when you push changes to your repository.

## 9. Monitoring and Maintenance

1. **Check logs**:
   ```bash
   docker-compose logs -f
   ```

2. **Restart services**:
   ```bash
   docker-compose restart
   ```

3. **Update application**:
   ```bash
   git pull
   docker-compose down
   docker-compose up -d --build
   ```

## Security Considerations

1. **Set up a firewall**:
   ```bash
   sudo ufw allow 22/tcp  # SSH
   sudo ufw allow 80/tcp  # HTTP
   sudo ufw allow 443/tcp # HTTPS
   sudo ufw enable
   ```

2. **Secure your Django settings**:
   - Use environment variables for sensitive information
   - Set strong, unique passwords
   - Keep your SECRET_KEY secure

3. **Regular updates**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

## Troubleshooting

1. **Check Nginx logs**:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

2. **Check Docker container logs**:
   ```bash
   docker-compose logs -f web
   ```

3. **Check Gunicorn logs**:
   ```bash
   docker-compose logs -f web | grep gunicorn
   ```

Congratulations! Your Django application should now be running on GCP with Nginx as a reverse proxy and Gunicorn as the WSGI server.