# Payment Archiving - Quick Start Guide

## What Changed
Payment records can now be archived instead of permanently deleted, following the same pattern as Trainee, Event, and Match archiving.

## How to Use

### Archive a Payment
1. Go to **Admin → Payments**
2. Find the payment you want to archive
3. Click the **Archive** button (amber icon with archive box)
4. Confirm the action in the dialog

### View Archived Payments
1. Go to **Admin → Payments**
2. Click the **Archived** button in the header
3. Browse, search, and filter archived payments
4. Use the same search/filter options as active payments

### Restore an Archived Payment
1. Go to **Admin → Payments → Archived**
2. Find the payment you want to restore
3. Click the **Restore** button (amber checkmark icon)
4. Payment reappears in the active payments list

## Key Differences from Delete
| Feature | Archive | Delete |
|---------|---------|--------|
| Reversible | ✅ Yes | ❌ No |
| Data intact | ✅ Yes | ❌ No |
| Trainee payments | ✅ Still visible | ❌ Removed |
| Recommended for | Historical records | System cleanup |

## UI Indicators
- **Archived Payments**: Shown with reduced opacity
- **Archive Button**: Amber color (active list)
- **Restore Button**: Amber color (archived list)

## Database Changes
- New field: `Payment.archived` (BooleanField, default=False)
- New index: `archived, -payment_date` (for performance)
- Migration: `0017_payment_archived.py`

## API/View Endpoints
```
GET  /admin/payments/                          # Active payments
GET  /admin/payments/archived/                 # Archived payments
POST /admin/payments/<id>/archive/             # Archive action
POST /admin/payments/<id>/restore/             # Restore action
GET  /admin/payments/partial/                  # HTMX updates (active)
GET  /admin/payments/archived/partial/         # HTMX updates (archived)
```

## Migration Required
Run migrations before using:
```bash
python manage.py migrate
```

## Known Limitations
- Delete functionality is replaced with archive
- Hard delete via admin panel removed for payments
- Archived payments still count in reports (filter as needed)

## Troubleshooting

### Payment doesn't appear after archiving
✅ Check the **Archived** tab instead of active list

### Archive button doesn't work
✅ Ensure you're on a payment list page (not edit view)
✅ Check browser console for HTMX errors

### Can't find archived payment to restore
✅ Use the search/filter on archived list
✅ Check status and type filters

## See Also
- PAYMENT_ARCHIVING_IMPLEMENTATION.md (full technical details)
- Trainee archiving (similar pattern)
- Event archiving (similar pattern)
