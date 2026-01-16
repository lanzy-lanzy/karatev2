# Trainee Archiving - Quick Start

## What Was Changed

Trainee management now uses **soft archiving** instead of permanent deletion - just like event management.

## Key Features

✅ Archive trainees (soft delete)  
✅ View archived trainees separately  
✅ Restore archived trainees  
✅ Search & filter archived trainees  
✅ All data preserved  

## How It Works

### Archive a Trainee
1. Go to **Admin → Trainees**
2. Find the trainee you want to remove
3. Click the **Archive** button (red delete icon)
4. Confirm the action
5. Trainee is moved to archived list

### View Archived Trainees
1. Go to **Admin → Trainees**
2. Click **Archived Trainees** link (or navigate to `/admin/trainees/archived/`)
3. Browse archived trainees
4. Use search and filters

### Restore a Trainee
1. Go to **Admin → Archived Trainees**
2. Find the trainee
3. Click **Restore** button (green arrow icon)
4. Confirm
5. Trainee returns to active list

## Code Files Modified

**Models:**
- `core/models.py` - Added `archived` field to Trainee

**Views:**
- `core/views/admin.py` - Updated 3 views, added 3 new views
- `core/views/__init__.py` - Exported new views

**Routes:**
- `core/urls.py` - Added 3 new URLs

**Templates:**
- `templates/admin/trainees/list_partial.html` - Updated button text
- `templates/admin/trainees/archived.html` - NEW
- `templates/admin/trainees/archived_partial.html` - NEW

**Database:**
- `core/migrations/0017_trainee_archived.py` - NEW

## Implementation Details

### Views
- `trainee_list()` - Filters `archived=False`
- `trainee_delete()` - Archives instead of deletes
- `archived_trainees_list()` - Lists archived trainees
- `archived_trainees_list_partial()` - HTMX partial
- `trainee_restore()` - Restores archived trainee

### Database Index
Creates index on `(archived, -joined_date)` for performance

### Features
- HTMX dynamic updates
- Toast notifications
- Search by name/belt/status
- Filter by status and belt
- Mobile-friendly
- Consistent with event archiving

## URLs

**Active Trainees:**
- `/admin/trainees/` - List active trainees
- `/admin/trainees/<id>/delete/` - Archive trainee

**Archived Trainees:**
- `/admin/trainees/archived/` - List archived trainees
- `/admin/trainees/<id>/restore/` - Restore trainee

## Testing

```python
# Archive a trainee
trainee.archived = True
trainee.save()

# Restore a trainee
trainee.archived = False
trainee.save()

# Query active trainees
active = Trainee.objects.filter(archived=False)

# Query archived trainees
archived = Trainee.objects.filter(archived=True)
```

## Next Steps

Run migrations:
```bash
python manage.py migrate
```

## Similar Implementation

This follows the exact same pattern as event archiving:
- Same field structure
- Same view patterns
- Same URL naming conventions
- Same template layouts

See `TRAINEE_ARCHIVING_IMPLEMENTATION.md` for full details.
