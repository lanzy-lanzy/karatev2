# Payment Archiving Implementation

## Overview
Payment archiving has been implemented following the existing soft-delete pattern used for Trainees, Events, and Matches. This allows payments to be archived (hidden from active view) while maintaining referential integrity and the ability to restore them.

## Changes Made

### 1. Database Model (`core/models.py`)
Added archiving support to the `Payment` model:
- Added `archived = BooleanField(default=False)` field
- Added database index: `models.Index(fields=['archived', '-payment_date'])`
- Meta ordering: `['-payment_date']`

### 2. Database Migration (`core/migrations/0017_payment_archived.py`)
Created migration that:
- Adds the `archived` field to the Payment model
- Adds the composite index for query optimization

### 3. Admin Views (`core/views/admin.py`)
Updated existing views:
- `payment_list()`: Now filters to only show non-archived payments (`archived=False`)
- `payment_list_partial()`: Updated HTMX partial view with archive filter

Added new views:
- `archived_payments_list()`: Display all archived payments with search/filter
- `archived_payments_list_partial()`: HTMX partial for archived payment list updates
- `payment_archive()`: Soft delete a payment (sets `archived=True`)
- `payment_restore()`: Restore an archived payment (sets `archived=False`)

### 4. URL Routes (`core/urls.py`)
Added new endpoints:
- `GET /admin/payments/archived/` → `archived_payments_list` (main page)
- `GET /admin/payments/archived/partial/` → `archived_payments_list_partial` (HTMX)
- `POST /admin/payments/<id>/archive/` → `payment_archive` (archive action)
- `POST /admin/payments/<id>/restore/` → `payment_restore` (restore action)

### 5. Templates

#### Main List (`templates/admin/payments/list.html`)
- Added "Archived" button in the header linking to archived payments view
- Maintains all existing filters (search, status, type)

#### List Partial (`templates/admin/payments/list_partial.html`)
- Replaced "Delete" button with "Archive" button (amber color)
- Archive action sends POST request to `payment_archive` endpoint
- Confirmation dialog: "Archive this payment? It will be moved to the archive but can be restored later."
- Updated mobile and desktop views

#### New Templates
- `archived_list.html`: Main page for viewing archived payments
- `archived_list_partial.html`: HTMX partial for archived list updates
  - Shows archived payments with reduced opacity to indicate archived status
  - Restore button instead of archive button
  - Search and filter capabilities identical to active list

## Features

### Archive Functionality
- **Soft Delete**: Payments are marked as archived but not deleted from database
- **Reversible**: Archived payments can be restored at any time
- **Filtered Views**: Active and archived payments in separate sections
- **HTMX Integration**: Smooth updates without full page reload

### Search and Filtering
Both active and archived payment lists support:
- Search by trainee name (first name, last name, username)
- Filter by payment status (pending, completed, overdue, cancelled)
- Filter by payment type (membership, event, equipment, other)

### UI/UX
- **Archive Button**: Amber-colored icon in active list
- **Restore Button**: Amber-colored icon in archived list
- **Visual Distinction**: Archived payments shown with reduced opacity
- **Confirmation**: Dialog before archiving to prevent accidents

## Database Query Performance
The added index `(archived, -payment_date)` optimizes:
- Filtering payments by archived status
- Ordering results by date within each archived state
- Typical payment list queries

## Backwards Compatibility
- All existing payments have `archived=False` by default
- No data migration required
- Existing payment logic unchanged
- Existing views automatically exclude archived payments

## Testing Checklist
- [ ] Archive a payment from active list
- [ ] View archived payments
- [ ] Search archived payments
- [ ] Filter archived payments by status/type
- [ ] Restore an archived payment
- [ ] Verify restored payment appears in active list
- [ ] Test HTMX updates work smoothly
- [ ] Verify no 404 errors on related trainee pages

## Related Features
Payment archiving works in conjunction with:
- **Trainee Archiving**: When a trainee is archived, their payment records remain but are associated with archived trainee
- **Payment Deletion**: Hard delete functionality still available via `payment_delete` endpoint if needed
- **Payment Reports**: Reports should be updated to exclude archived payments if needed

## Future Enhancements
- Bulk archive/restore actions
- Archive reason/notes field
- Scheduled archiving (auto-archive old payments)
- Archive audit trail
- Integration with data export/backup for archived records
