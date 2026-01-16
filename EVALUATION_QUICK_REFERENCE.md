# Trainee Evaluation System - Quick Reference Card

## URLs at a Glance

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/admin/evaluations/` | GET | List all evaluations |
| `/admin/evaluations/partial/` | GET | HTMX partial (live filter) |
| `/admin/evaluations/add/` | GET/POST | Create new evaluation |
| `/admin/evaluations/<id>/edit/` | GET/POST | Edit existing evaluation |
| `/admin/evaluations/<id>/delete/` | GET/POST | Delete (archive) evaluation |
| `/admin/evaluations/<trainee_id>/trainee/` | GET | View trainee's history |

## Models Overview

### TraineeEvaluation
```python
trainee                  # FK to Trainee
evaluator               # FK to User (admin)
technique               # 1-5 rating
speed                   # 1-5 rating
strength                # 1-5 rating
flexibility             # 1-5 rating
discipline              # 1-5 rating
spirit                  # 1-5 rating
overall_rating          # 1-5 rating
comments                # Text feedback
strengths               # Text field
areas_for_improvement   # Text field
recommendations         # Text field
status                  # pending/completed/archived
evaluated_at            # Auto timestamp
next_evaluation_date    # Optional date
archived                # Boolean flag
```

## Views Quick Guide

### evaluation_list
- **Purpose**: Display all evaluations with filters
- **GET Params**: search, status_filter, rating_filter
- **Returns**: list.html (full page) or list_partial.html (HTMX)

### evaluation_list_partial
- **Purpose**: HTMX partial for filtering
- **GET Params**: search, status_filter, rating_filter
- **Returns**: list_partial.html (HTML fragment)

### evaluation_add
- **Purpose**: Create new evaluation
- **GET**: Shows empty form
- **POST**: Creates evaluation + redirects
- **Requires**: Trainee ID, ratings (auto-defaults to 3)

### evaluation_edit
- **Purpose**: Modify existing evaluation
- **GET**: Shows pre-filled form
- **POST**: Updates evaluation + redirects
- **Preserves**: Trainee (can't change)

### evaluation_delete
- **Purpose**: Archive evaluation
- **GET**: Shows confirmation dialog
- **POST**: Sets archived=True + redirects

### trainee_evaluations
- **Purpose**: Show trainee's evaluation history
- **Returns**: trainee_detail.html with timeline
- **Includes**: Statistics + all evaluations

## Templates Quick Reference

| Template | Purpose | Key Elements |
|----------|---------|--------------|
| list.html | Main page | Filters, list container, "New" button |
| list_partial.html | HTMX partial | Evaluation cards, action buttons |
| form.html | Create/Edit | Form fields, rating dropdowns, text areas |
| confirm_delete.html | Confirmation | Warning message, Delete/Cancel buttons |
| trainee_detail.html | History view | Info card, stats, timeline of evals |

## Rating Scale

| Score | Label | Color | Meaning |
|-------|-------|-------|---------|
| 1 | Poor | 🔴 Red | Needs improvement |
| 2 | Fair | 🟠 Orange | Below average |
| 3 | Good | 🟡 Yellow | Meets expectations |
| 4 | Very Good | 🔵 Blue | Above average |
| 5 | Excellent | 🟢 Green | Outstanding |

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Focus search | Click search box |
| Filter by status | Select dropdown |
| Filter by rating | Select dropdown |
| Submit form | Tab to button + Enter |
| Cancel form | Click Cancel link |

## Form Fields Reference

### Required Fields
- Trainee (select dropdown)

### Auto-Set Fields
- Evaluator (current user)
- Status (completed)
- Evaluated_at (current datetime)

### Optional Fields
- Next evaluation date

### Default Values
- All ratings: 3 (Good)
- Comments: empty
- Strengths: empty
- Areas: empty
- Recommendations: empty

## Admin Panel Operations

### In Django Admin (`/admin/`)
1. Look for "TraineeEvaluation" model
2. Click to see all evaluations
3. Filter, search, or click to edit
4. Full CRUD available

### In Custom Interface (`/admin/evaluations/`)
1. See list with search/filters
2. Click "New Evaluation"
3. Fill form and submit
4. View history for trainee

## File Structure
```
admin/
└── evaluations/
    ├── list.html
    ├── list_partial.html
    ├── form.html
    ├── confirm_delete.html
    └── trainee_detail.html
```

## Database Query Examples

### Get all evaluations
```python
TraineeEvaluation.objects.all()
```

### Get trainee's evaluations
```python
trainee.evaluations.all()
```

### Get evaluations by rating
```python
TraineeEvaluation.objects.filter(overall_rating=5)
```

### Get archived evaluations
```python
TraineeEvaluation.objects.filter(archived=True)
```

### Get evaluations by admin
```python
TraineeEvaluation.objects.filter(evaluator=user)
```

## Common Workflows

### Create Evaluation
1. Go to `/admin/evaluations/`
2. Click "New Evaluation"
3. Select trainee
4. Set 6 ratings + overall
5. Add text feedback
6. Click "Create Evaluation"

### View Trainee History
1. Go to `/admin/evaluations/`
2. Search or find trainee
3. Click "View All" button
4. See timeline of evaluations

### Edit Evaluation
1. Click "Edit" button
2. Change ratings/comments
3. Click "Update Evaluation"

### Delete Evaluation
1. Click "Delete" button
2. Confirm in modal
3. Evaluation archived

### Filter Evaluations
1. Go to `/admin/evaluations/`
2. Use search box (name)
3. Use status filter (pending/completed)
4. Use rating filter (1-5)
5. Results update via HTMX

## Permissions

| User Type | Create | View | Edit | Delete |
|-----------|--------|------|------|--------|
| Admin | ✅ | ✅ | ✅ | ✅ |
| Trainee | ❌ | ❌ | ❌ | ❌ |
| Judge | ❌ | ❌ | ❌ | ❌ |
| Anonymous | ❌ | ❌ | ❌ | ❌ |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Link not in sidebar | Run migration, restart server |
| Can't create evaluation | Check trainee is active |
| Form won't submit | Verify all fields filled |
| Filters not working | Clear cache, refresh page |
| Date picker not working | Check browser compatibility |

## Performance Tips

- Search filters results in real-time (HTMX)
- Indexes on trainee + date for fast queries
- Soft delete preserves history
- Pagination recommended for 100+ evaluations

## Security Notes

- Only admins can access evaluations
- All forms CSRF protected
- Soft delete prevents data loss
- User tracked as evaluator
- Inputs validated/escaped

## Integration Points

### Links With
- Trainee (foreign key)
- User/Admin (evaluator)
- Events (potential future)
- Training Plans (potential future)

### Can Link To
- Belt promotions (future)
- Progress reports (future)
- Training recommendations (future)

## HTMX Endpoints

| Endpoint | Trigger | Updates |
|----------|---------|---------|
| `/admin/evaluations/partial/` | Search input | #evaluations-list |
| `/admin/evaluations/partial/` | Status filter | #evaluations-list |
| `/admin/evaluations/partial/` | Rating filter | #evaluations-list |

## Migration Info

**File**: `core/migrations/0021_traineeevaluation.py`

**Run**:
```bash
python manage.py migrate
```

**Rollback**:
```bash
python manage.py migrate core 0020
```

---

## Sidebar Navigation

```
▼ Evaluations (NEW)
   → List all evaluations
   → Search & filter
   → Create new
   → View trainee history
```

## Quick Stats

- 1 new model
- 6 new views
- 5 new templates
- 6 new URLs
- 260+ lines of Python
- 450+ lines of HTML
- 1 migration
- ~2,000 total lines

---

**Ready to go! Start with EVALUATION_QUICK_START.md for detailed guide.**
