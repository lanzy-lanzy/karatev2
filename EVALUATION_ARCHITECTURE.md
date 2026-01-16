# Trainee Evaluation System - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    ADMIN INTERFACE                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Sidebar    │  │   Dashboard  │  │   Admin UI   │     │
│  │              │  │              │  │              │     │
│  │ Evaluations  │  │   Metrics    │  │   Tables     │     │
│  │ (NEW LINK)   │  │   Charts     │  │   Forms      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│       │                                      │              │
└───────┼──────────────────────────────────────┼──────────────┘
        │                                      │
        ▼                                      ▼
    ┌─────────────────────────────────────────────┐
    │      EVALUATION VIEWS & ENDPOINTS          │
    ├─────────────────────────────────────────────┤
    │                                             │
    │  GET  /admin/evaluations/                  │
    │    └─ evaluation_list()                    │
    │       Returns: list.html + filters        │
    │                                             │
    │  GET  /admin/evaluations/partial/          │
    │    └─ evaluation_list_partial()            │
    │       Returns: HTMX partial list           │
    │                                             │
    │  GET/POST /admin/evaluations/add/          │
    │    └─ evaluation_add()                     │
    │       Returns: form.html                   │
    │                                             │
    │  GET/POST /admin/evaluations/<id>/edit/    │
    │    └─ evaluation_edit()                    │
    │       Returns: form.html (pre-filled)     │
    │                                             │
    │  GET/POST /admin/evaluations/<id>/delete/  │
    │    └─ evaluation_delete()                  │
    │       Returns: confirm_delete.html         │
    │                                             │
    │  GET /admin/evaluations/<id>/trainee/      │
    │    └─ trainee_evaluations()                │
    │       Returns: trainee_detail.html         │
    │                                             │
    └─────────────────────────────────────────────┘
            │
            ▼
    ┌─────────────────────────────────────────────┐
    │         DATABASE - MODELS LAYER             │
    ├─────────────────────────────────────────────┤
    │                                             │
    │  TraineeEvaluation                         │
    │  ├── id (Primary Key)                      │
    │  ├── trainee (FK ──┐                       │
    │  ├── evaluator (FK─┼──┐                   │
    │  ├── technique (1-5)                       │
    │  ├── speed (1-5)                          │
    │  ├── strength (1-5)                       │
    │  ├── flexibility (1-5)                    │
    │  ├── discipline (1-5)                     │
    │  ├── spirit (1-5)                         │
    │  ├── overall_rating (1-5)                │
    │  ├── comments (Text)                      │
    │  ├── strengths (Text)                     │
    │  ├── areas_for_improvement (Text)        │
    │  ├── recommendations (Text)               │
    │  ├── status                               │
    │  ├── evaluated_at                         │
    │  ├── next_evaluation_date                │
    │  ├── archived                             │
    │  └── Index on [trainee, -evaluated_at]   │
    │      Index on [archived, -evaluated_at]  │
    │                                             │
    └─────────────────────────────────────────────┘
            │                       │
            ▼                       ▼
        ┌─────────┐            ┌─────────┐
        │ Trainee │            │  User   │
        └─────────┘            └─────────┘
```

## Data Flow

### Create Evaluation
```
User Form Submit (POST)
    │
    ├─ validate trainee_id
    ├─ validate ratings (1-5)
    ├─ create TraineeEvaluation object
    ├─ set evaluator = current_user
    ├─ set status = 'completed'
    │
    ▼
Database Insert
    │
    ▼
Redirect to /admin/evaluations/
    │
    ▼
List Updated
```

### Read Evaluations
```
GET /admin/evaluations/
    │
    ├─ fetch all TraineeEvaluations
    ├─ apply search filter
    ├─ apply status filter
    ├─ apply rating filter
    ├─ order by -evaluated_at
    │
    ▼
Return list.html with context
    │
    ▼
Render Template
    │
    ├─ show filter form
    ├─ display evaluation cards
    ├─ show HTMX endpoints
    │
    ▼
User Sees List
```

### Update Evaluation
```
GET /admin/evaluations/<id>/edit/
    │
    ├─ fetch TraineeEvaluation
    ├─ pre-fill form with current values
    │
    ▼
User Modifies Form
    │
    ▼
POST /admin/evaluations/<id>/edit/
    │
    ├─ fetch existing evaluation
    ├─ update fields
    ├─ save to database
    │
    ▼
Redirect to list
```

### Delete (Archive) Evaluation
```
GET /admin/evaluations/<id>/delete/
    │
    ├─ fetch evaluation
    │
    ▼
Show Confirmation Modal
    │
    ▼
User Confirms
    │
    ▼
POST /admin/evaluations/<id>/delete/
    │
    ├─ set archived = True
    ├─ save to database
    │
    ▼
Redirect to list
```

## Template Hierarchy

```
base.html (Main Layout)
    │
    ├── Header (Navigation)
    │   ├── Logo
    │   ├── Notifications
    │   └── User Menu
    │
    ├── Sidebar (Navigation)
    │   ├── Dashboard Link
    │   ├── Trainees Link
    │   ├── Events Link
    │   ├── Matchmaking Link
    │   ├── Payments Link
    │   ├── Reports Link
    │   ├── Belt Promotion Link
    │   └── Evaluations Link (NEW)
    │
    └── Content Area
        │
        ├── admin/evaluations/list.html
        │   ├── Filter Form
        │   ├── #evaluations-list (HTMX target)
        │   │   └─ admin/evaluations/list_partial.html
        │   │       └── Evaluation Cards (repeated)
        │   └── Action Buttons
        │
        ├── admin/evaluations/form.html
        │   ├── Trainee Selection
        │   ├── Rating Fields (6)
        │   ├── Overall Rating
        │   ├── Assessment Fields
        │   ├── Date Field
        │   └── Submit/Cancel Buttons
        │
        ├── admin/evaluations/confirm_delete.html
        │   ├── Warning Message
        │   └── Confirm/Cancel Buttons
        │
        └── admin/evaluations/trainee_detail.html
            ├── Trainee Info Card
            ├── Statistics Cards
            └── Evaluation Timeline
                └── Individual Evaluation Cards
```

## CRUD Operations

### CREATE
```
Flow: evaluation_add view
┌────────────────────────────────────┐
│ GET /admin/evaluations/add/        │
├────────────────────────────────────┤
│ 1. Fetch active trainees            │
│ 2. Render form.html                 │
└────────────────────────────────────┘
                │
                ▼
    ┌─────────────────────────┐
    │ User fills out form      │
    │ - Select trainee        │
    │ - Rate 6 criteria       │
    │ - Add feedback text     │
    │ - Set next eval date    │
    └─────────────────────────┘
                │
                ▼
    ┌──────────────────────────────┐
    │ POST /admin/evaluations/add/  │
    ├──────────────────────────────┤
    │ 1. Validate trainee_id        │
    │ 2. Create evaluation object   │
    │ 3. Set evaluator = user       │
    │ 4. Set status = completed     │
    │ 5. Save to database           │
    │ 6. Redirect to list           │
    └──────────────────────────────┘
```

### READ
```
Flow: evaluation_list view
┌──────────────────────────────────────┐
│ GET /admin/evaluations/              │
├──────────────────────────────────────┤
│ 1. Query all non-archived evaluations│
│ 2. Apply filters:                    │
│    - search (trainee name)           │
│    - status_filter                   │
│    - rating_filter                   │
│ 3. Order by -evaluated_at            │
│ 4. Paginate results                  │
│ 5. Render list.html or partial       │
└──────────────────────────────────────┘

Flow: trainee_evaluations view
┌──────────────────────────────────────┐
│ GET /admin/evaluations/<id>/trainee/ │
├──────────────────────────────────────┤
│ 1. Fetch trainee by id               │
│ 2. Query evaluations for trainee     │
│ 3. Calculate statistics              │
│ 4. Order by -evaluated_at            │
│ 5. Render trainee_detail.html        │
└──────────────────────────────────────┘
```

### UPDATE
```
Flow: evaluation_edit view
┌──────────────────────────────────────┐
│ GET /admin/evaluations/<id>/edit/    │
├──────────────────────────────────────┤
│ 1. Fetch evaluation by id            │
│ 2. Pre-fill form with current data   │
│ 3. Render form.html                  │
└──────────────────────────────────────┘
                │
                ▼
    ┌─────────────────────────┐
    │ User modifies fields     │
    └─────────────────────────┘
                │
                ▼
    ┌──────────────────────────────┐
    │ POST /admin/evaluations/      │
    │   <id>/edit/                  │
    ├──────────────────────────────┤
    │ 1. Fetch evaluation          │
    │ 2. Update fields             │
    │ 3. Validate new data         │
    │ 4. Save to database          │
    │ 5. Redirect to list          │
    └──────────────────────────────┘
```

### DELETE (Archive)
```
Flow: evaluation_delete view
┌──────────────────────────────────────┐
│ GET /admin/evaluations/<id>/delete/  │
├──────────────────────────────────────┤
│ 1. Fetch evaluation by id            │
│ 2. Render confirm_delete.html        │
└──────────────────────────────────────┘
                │
                ▼
    ┌──────────────────────────┐
    │ User confirms deletion    │
    └──────────────────────────┘
                │
                ▼
    ┌──────────────────────────────┐
    │ POST /admin/evaluations/      │
    │   <id>/delete/               │
    ├──────────────────────────────┤
    │ 1. Fetch evaluation          │
    │ 2. Set archived = True       │
    │ 3. Save to database          │
    │ 4. Redirect to list          │
    └──────────────────────────────┘
```

## HTMX Integration

```
User Action (Search/Filter)
    │
    ▼
Browser Sends AJAX via HTMX
    POST /admin/evaluations/partial/
    Params: search, status_filter, rating_filter
    │
    ▼
Server Processes Request
    1. Query evaluations with filters
    2. Render list_partial.html
    │
    ▼
Return HTML Fragment
    │
    ▼
HTMX Swaps into #evaluations-list
    (No page reload)
    │
    ▼
User Sees Updated List
```

## Rating System

```
┌─────────────────────────────────────┐
│ Rating Scale (1-5 for each)         │
├─────────────────────────────────────┤
│                                     │
│ 1 = Poor       🔴 (Red)             │
│ 2 = Fair       🟠 (Orange)          │
│ 3 = Good       🟡 (Yellow)          │
│ 4 = Very Good  🔵 (Blue)            │
│ 5 = Excellent  🟢 (Green)           │
│                                     │
├─────────────────────────────────────┤
│ Criteria Evaluated:                 │
├─────────────────────────────────────┤
│                                     │
│ 1. Technique      (Form proficiency) │
│ 2. Speed          (Reaction time)    │
│ 3. Strength       (Physical power)   │
│ 4. Flexibility    (Range of motion)  │
│ 5. Discipline     (Focus)            │
│ 6. Spirit         (Determination)    │
│                                     │
│ + Overall Rating                    │
│                                     │
└─────────────────────────────────────┘
```

## User Roles & Permissions

```
┌──────────────────────────────────────┐
│ Permission Model                     │
├──────────────────────────────────────┤
│                                      │
│ Admin User (@admin_required)         │
│ ├─ Create Evaluation    ✅           │
│ ├─ View Evaluations     ✅           │
│ ├─ Edit Evaluations     ✅           │
│ ├─ Delete Evaluations   ✅           │
│ └─ View History         ✅           │
│                                      │
│ Non-Admin User                       │
│ └─ No Access                         │
│    (Redirected to login)             │
│                                      │
└──────────────────────────────────────┘
```

## Database Queries

### Optimized Queries Used

```python
# List view
evaluations = TraineeEvaluation.objects.select_related(
    'trainee__profile__user',  # Avoid N+1 for trainee
    'evaluator'                # Avoid N+1 for evaluator
).filter(archived=False)

# Single evaluation
evaluation = TraineeEvaluation.objects.select_related(
    'trainee__profile__user',
    'evaluator'
).get(id=evaluation_id)

# Trainee history
evaluations = TraineeEvaluation.objects.filter(
    trainee=trainee,
    archived=False
).order_by('-evaluated_at')
```

### Index Strategy

```
Table: core_traineeevaluation

Index 1: [trainee_id, -evaluated_at]
         ├─ Used by: trainee_evaluations view
         ├─ Improves: Filtering by trainee
         └─ Query time: ~1-5ms

Index 2: [archived, -evaluated_at]
         ├─ Used by: evaluation_list view
         ├─ Improves: Filtering non-archived
         └─ Query time: ~1-10ms
```

## Performance Considerations

```
┌──────────────────────────────┐
│ Optimization Strategies      │
├──────────────────────────────┤
│                              │
│ 1. Database Indexes          │
│    └─ Fast filtering         │
│                              │
│ 2. select_related()          │
│    └─ Avoid N+1 queries      │
│                              │
│ 3. HTMX Partial Updates      │
│    └─ Reduce data transfer   │
│                              │
│ 4. Soft Delete (archived)    │
│    └─ No cascading deletes   │
│                              │
│ 5. Pagination (optional)     │
│    └─ Limit result sets      │
│                              │
└──────────────────────────────┘
```

## Error Handling

```
┌──────────────────────────────┐
│ Error Cases Handled          │
├──────────────────────────────┤
│                              │
│ 1. Missing Trainee           │
│    └─ Validation error       │
│                              │
│ 2. Invalid Rating (not 1-5)  │
│    └─ Defaults to 3 (Good)   │
│                              │
│ 3. Non-existent Evaluation   │
│    └─ 404 error              │
│                              │
│ 4. Invalid Form Data         │
│    └─ Re-render form         │
│                              │
│ 5. Unauthorized Access       │
│    └─ Redirect to login      │
│                              │
└──────────────────────────────┘
```
