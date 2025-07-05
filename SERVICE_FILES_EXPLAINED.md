# Service Files Summary

You have two service files for different use cases:

## 1. `chicken-gate-web.service` (Development/Port 5000)

- **Port**: 5000
- **User**: pi (regular user)
- **Use case**: Development, testing, or when you can't use port 80
- **Access**: `http://chicken-gate:5000`
- **Advantages**:
  - No root privileges needed
  - Safer for development
  - Can run alongside other web servers

## 2. `chicken-gate-web-port80.service` (Production/Port 80)

- **Port**: 80 (standard HTTP port)
- **User**: root (required for port 80)
- **Use case**: Production deployment
- **Access**: `http://chicken-gate` (no port number needed!)
- **Advantages**:
  - Clean URLs without port numbers
  - Better user experience
  - Mobile-friendly bookmarks

## Which Should You Use?

### For Production (Recommended): `chicken-gate-web-port80.service`

- Clean URLs: `http://chicken-gate`
- Best user experience
- Professional appearance

### For Development: `chicken-gate-web.service`

- Port 5000: `http://chicken-gate:5000`
- No root privileges needed
- Good for testing changes

## Installation Commands

### Production (Port 80)

```bash
sudo cp chicken-gate-web-port80.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable chicken-gate-web-port80.service
sudo systemctl start chicken-gate-web-port80.service
```

### Development (Port 5000)

```bash
sudo cp chicken-gate-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable chicken-gate-web.service
sudo systemctl start chicken-gate-web.service
```

## Key Differences in the Service Files

| Feature  | chicken-gate-web.service | chicken-gate-web-port80.service |
| -------- | ------------------------ | ------------------------------- |
| Port     | 5000                     | 80                              |
| User     | pi                       | root                            |
| Security | Higher (non-root)        | Lower (root required)           |
| URL      | http://chicken-gate:5000 | http://chicken-gate             |
| Use Case | Development              | Production                      |
