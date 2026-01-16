# Archiving Pattern Comparison: Events vs Trainees

## Overview
Both Event and Trainee models now implement the same soft-delete archiving pattern.

## Side-by-Side Comparison

### Model Fields

| Aspect | Events | Trainees |
|--------|--------|----------|
| Archive Field | `archived: BooleanField(default=False)` | `archived: BooleanField(default=False)` |
| Index Fields | `(archived, -event_date)` | `(archived, -joined_date)` |
| Meta Ordering | `['-event_date']` | `['profile__user__first_name', 'profile__user__last_name']` |

### Views

| Functionality | Events | Trainees |
|--------------|--------|----------|
| List Active | `event_list()` | `trainee_list()` |
| List Partial | `event_list_partial()` | `trainee_list_partial()` |
| Archive | `event_archive()` | `trainee_delete()` * |
| List Archived | `archived_events_list()` | `archived_trainees_list()` |
| Archived Partial | `archived_events_list_partial()` | `archived_trainees_list_partial()` |
| Restore | `event_restore()` | `trainee_restore()` |

\* `trainee_delete()` now archives instead of deletes (for consistency with button labels)

### URL Patterns

| Pattern | Events | Trainees |
|---------|--------|----------|
| List Active | `/admin/events/` | `/admin/trainees/` |
| List Archived | `/admin/events/archived/` | `/admin/trainees/archived/` |
| Archive Partial | `/admin/events/archived/partial/` | `/admin/trainees/archived/partial/` |
| Archive Action | `/admin/events/<id>/archive/` | `/admin/trainees/<id>/delete/` |
| Restore Action | `/admin/events/<id>/restore/` | `/admin/trainees/<id>/restore/` |

### Templates

| Template | Events | Trainees |
|----------|--------|----------|
| List Page | `events/list.html` | `trainees/list.html` |
| List Partial | `events/list_partial.html` | `trainees/list_partial.html` |
| Archived Page | `events/archived.html` | `trainees/archived.html` |
| Archived Partial | `events/archived_partial.html` | `trainees/archived_partial.html` |

## Functionality Comparison

### Active List Features
```
✓ Search
✓ Filter (by status/belt for trainees, by status for events)
✓ HTMX dynamic updates
✓ Delete/Archive action
✓ Edit action (events show detail, trainees show edit form)
✓ Toast notifications
✓ Mobile-friendly
```

### Archived List Features
```
✓ Search
✓ Filter (same as active)
✓ HTMX dynamic updates
✓ Restore action only
✓ Toast notifications
✓ Mobile-friendly
✓ Reduced opacity styling
✓ Back button to active list
```

## Code Structure Similarity

### View Pattern - Archive
```python
# Events
@admin_required
def event_archive(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.archived = True
        event.save()
        # ... handle HTMX response
        
# Trainees
@admin_required
def trainee_delete(request, trainee_id):
    trainee = get_object_or_404(Trainee, id=trainee_id, archived=False)
    if request.method == 'DELETE' or request.method == 'POST':
        trainee.archived = True
        trainee.save()
        # ... handle HTMX response
```

### View Pattern - Restore
```python
# Events
@admin_required
def event_restore(request, event_id):
    event = get_object_or_404(Event, id=event_id, archived=True)
    if request.method == 'POST':
        event.archived = False
        event.save()
        # ... handle HTMX response

# Trainees
@admin_required
def trainee_restore(request, trainee_id):
    trainee = get_object_or_404(Trainee, id=trainee_id, archived=True)
    if request.method == 'POST':
        trainee.archived = False
        trainee.save()
        # ... handle HTMX response
```

### List Filter Pattern
```python
# Events
events = Event.objects.filter(archived=False)  # or archived=True

# Trainees
trainees = Trainee.objects.filter(archived=False)  # or archived=True
```

## Consistency Benefits

1. **Uniform User Experience**: Same archiving workflow across the app
2. **Predictable Code**: Developers know exactly where to find views and templates
3. **Easy to Extend**: Same pattern can be applied to Judges, Matches, etc.
4. **Maintainability**: Changes to archiving logic only need to be made once
5. **Documentation**: Clear pattern for future feature development

## Other Models Using Archiving

| Model | Archive Method | Status |
|-------|---|--------|
| Event | Soft Archive | ✅ Implemented |
| Match | Soft Archive | ✅ Implemented |
| Trainee | Soft Archive | ✅ Implemented |
| Judge | Hard Delete | ❌ Could be updated |
| Payment | Hard Delete | ❌ Could be updated |

## Future Standardization

Consider applying this pattern to:
- Judge management
- Payment records
- Event registrations
- Registrations (new member signups)

All would benefit from the same archiving approach.

## Migration Status

| Model | Migration | Status |
|-------|-----------|--------|
| Event | `0010_event_archived.py` | ✅ Applied |
| Match | `0011_match_archived.py` | ✅ Applied |
| Trainee | `0017_trainee_archived.py` | ✅ Created |

## Performance Notes

Both models have optimized indexes:
- Speeds up filtering by `archived` status
- Supports sorting by date field
- Enables efficient queries in list views
- Supports combined filters (e.g., `archived=False, status='active'`)

## Data Integrity

- No foreign key constraints prevent archival
- Archived records remain linked to other models
- Restoration preserves all relationships
- No cascade deletes occur
- Complete audit trail maintained
