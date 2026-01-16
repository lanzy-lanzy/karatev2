# Trainee Archiving Implementation

## Overview
Implemented a soft-delete archiving system for trainee management, following the same pattern as event archiving.

## Changes Made

### 1. Database Model (core/models.py)
- Added `archived` boolean field to `Trainee` model (default=False)
- Added `Meta` class with:
  - Ordering by first_name and last_name
  - Index on `archived` and `-joined_date` fields for optimized queries

### 2. Views (core/views/admin.py)

#### Modified Views
- **trainee_list()**: Filtered to exclude archived trainees (`filter(archived=False)`)
- **trainee_list_partial()**: Filtered to exclude archived trainees
- **trainee_delete()**: Changed from hard delete to soft archive
  - Now sets `archived=True` instead of deleting records
  - Updated confirmation message from "deleted" to "archived"

#### New Views
- **archived_trainees_list()**: List view for archived trainees
  - Supports search filtering by name, belt rank, status
  - Supports status and belt filters
  - Renders `admin/trainees/archived.html` or `archived_partial.html` for HTMX

- **archived_trainees_list_partial()**: HTMX partial for archived trainees
  - Returns `admin/trainees/archived_partial.html`
  - Includes CSRF token for forms

- **trainee_restore()**: Restore archived trainee
  - Sets `archived=False`
  - Handles both HTMX and regular requests
  - Updates toast notification on successful restore

### 3. Views Export (core/views/__init__.py)
Added exports for new views:
```python
archived_trainees_list,
archived_trainees_list_partial,
trainee_restore,
```

### 4. URL Routes (core/urls.py)
Added new URL patterns:
```python
path('admin/trainees/archived/', admin_views.archived_trainees_list, name='admin_archived_trainees'),
path('admin/trainees/archived/partial/', admin_views.archived_trainees_list_partial, name='admin_archived_trainees_partial'),
path('admin/trainees/<int:trainee_id>/restore/', admin_views.trainee_restore, name='admin_trainee_restore'),
```

### 5. Templates

#### archived.html
- New full-page template for viewing archived trainees
- Mirrors structure of `admin/trainees/list.html`
- Includes search and filtering functionality
- "Back to Active Trainees" button for navigation

#### archived_partial.html
- New partial template for HTMX updates
- Display archived trainees with reduced opacity
- Restore button (green, reverses archiving)
- No delete button (archived data is preserved)
- Same filtering capabilities as active trainees

### 6. Database Migration
- **0017_trainee_archived.py**: Creates migration for:
  - Adding `archived` boolean field
  - Creating database index on `(archived, -joined_date)`
  - Updating model options

## Features

### Soft Delete / Archive
- Trainees are archived instead of permanently deleted
- All related data is preserved (registrations, match history, payments, etc.)
- Data can be restored at any time

### Search & Filtering
Archived trainees can be searched and filtered by:
- Name (first name, last name, username)
- Belt rank (white, yellow, orange, green, blue, brown, black)
- Status (active, inactive, suspended)

### HTMX Integration
- Dynamic list updates without page reloads
- Toast notifications for successful actions
- Smooth transitions and loading states

### Navigation
- "Archived Trainees" link in admin section
- "Back to Active Trainees" button on archived page
- Seamless switching between active and archived views

## User Flow

### Archiving a Trainee
1. Admin views active trainees list
2. Clicks delete button on trainee
3. Confirms archival action
4. Trainee is archived and removed from active list
5. Success toast notification

### Viewing Archived Trainees
1. Admin navigates to "Archived Trainees" section
2. Can search and filter archived trainees
3. Sees trainees with reduced opacity
4. Only restore action available

### Restoring a Trainee
1. Admin views archived trainee
2. Clicks restore button
3. Confirms restoration
4. Trainee is restored to active status
5. Success toast notification

## Benefits

1. **Data Preservation**: No permanent data loss
2. **Audit Trail**: Can track which trainees were archived
3. **Compliance**: Supports data retention policies
4. **Reversibility**: Mistakes can be easily corrected
5. **Clean UI**: Active and archived data separated

## Consistency with Events

This implementation follows the exact same pattern as event archiving:
- Same field name: `archived` (boolean)
- Same soft-delete approach
- Same view structure and naming conventions
- Same template patterns
- Same HTMX integration

## Future Enhancements

Potential improvements:
- Add archival timestamp (archived_at field)
- Add archival reason (archived_reason field)
- Bulk archive/restore actions
- Archive filters in reports
- Email notifications on archival
