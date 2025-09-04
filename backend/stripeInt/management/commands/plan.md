# Django Invoicing Management Commands

## Primary Command Structure

### Set Term (Main Command)
```bash
python manage.py set_term 2024-03-01 --weeks 10 [options]
```

**Arguments:**
- `start_date` (positional, required): First billing date in YYYY-MM-DD format

**Options:**
- `--weeks` (required): Number of weeks the term runs for
- `--strategies`: Comma-separated list of billing strategies to trigger (default: all)
  - Options: `weekly`, `fortnightly`, `half_termly`, `termly`
- `--dry-run`: Preview what would be scheduled without actually creating tasks
- `--force`: Overwrite existing term schedules if they exist

## Usage Examples

### Schedule All Billing Strategies
```bash
python manage.py set_term 2024-03-01 --weeks 10
```

### Schedule Specific Strategies Only
```bash
python manage.py set_term 2024-03-01 --weeks 10 --strategies weekly,fortnightly
```

### Preview Changes
```bash
python manage.py set_term 2024-03-01 --weeks 10 --dry-run
```

### Force Overwrite Existing Term
```bash
python manage.py set_term 2024-03-01 --weeks 10 --force
```
