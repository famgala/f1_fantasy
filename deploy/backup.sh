#!/bin/bash

# F1 Fantasy Test Stack Backup Script
# Creates backups of SQLite database, application files, and configuration

set -e

# Configuration
APP_DIR="/opt/f1fantasy"
DATA_DIR="/opt/f1fantasy/data"
BACKUP_DIR="/backup/f1fantasy"
DB_FILE="$DATA_DIR/f1fantasy_test.db"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

echo "🗄️ F1 Fantasy Test Stack Backup Script"
echo "======================================="

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "📅 Creating backup for $DATE"

# SQLite database backup
echo "💾 Backing up SQLite database..."
if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" "$BACKUP_DIR/database_$DATE.db"
    gzip "$BACKUP_DIR/database_$DATE.db"
    echo "  ✅ Database backup completed"
else
    echo "  ⚠️ Database file not found: $DB_FILE"
fi

# Application files backup
echo "📁 Backing up application files..."
tar -czf "$BACKUP_DIR/app_files_$DATE.tar.gz" \
    -C /opt \
    --exclude="f1fantasy/venv" \
    --exclude="f1fantasy/__pycache__" \
    --exclude="f1fantasy/.git" \
    --exclude="f1fantasy/htmlcov" \
    --exclude="f1fantasy/.pytest_cache" \
    --exclude="f1fantasy/data/*.db" \
    f1fantasy/

# Configuration backup
echo "⚙️ Backing up configuration..."
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" \
    /etc/systemd/system/f1fantasy.service \
    "$APP_DIR/.env" 2>/dev/null || true

# Log files backup
echo "📊 Backing up logs..."
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" \
    /var/log/f1fantasy/ 2>/dev/null || true

# Clean old backups
echo "🧹 Cleaning old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "*.db.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

# Show backup summary
echo ""
echo "✅ Backup completed successfully!"
echo "📁 Backup location: $BACKUP_DIR"
echo "📊 Backup files created:"
ls -lh "$BACKUP_DIR"/*_$DATE.*

echo ""
echo "💡 To restore from backup:"
echo "  Database: gunzip -c database_$DATE.db.gz > $DB_FILE"
echo "  Files: tar -xzf app_files_$DATE.tar.gz -C /opt/"
echo "  Stop service first: sudo systemctl stop f1fantasy" 