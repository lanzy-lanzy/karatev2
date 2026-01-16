# Trainee Archiving - Visual Implementation Guide

## Navigation Menu Structure

### Sidebar Layout (Now with Archived Trainees!)

```
┌─────────────────────────────────┐
│    ADMIN DASHBOARD              │
├─────────────────────────────────┤
│                                 │
│  🏠 Dashboard                    │
│                                 │
│  👥 User Management              │
│                                 │
│  👤 Trainee Management           │
│     └─ ✓ Archived Trainees  ⬅️ NEW!
│                                 │
│  📅 Event Management             │
│     └─ ✓ Archived Events         │
│                                 │
│  🛡️  Matchmaking                 │
│     └─ ✓ Archived Matchmaking    │
│                                 │
│  💰 Payments                     │
│                                 │
│  📊 Reports                      │
│                                 │
│  ⚡ Belt Promotion               │
│                                 │
└─────────────────────────────────┘
```

## User Interface - Active Trainees

### Page: Trainee Management

```
┌─────────────────────────────────────────────────────────┐
│  All Trainees  [Add New Trainee]                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Search: [Search box.............]                     │
│  Status: [Active ▼]  Belt: [All Belts ▼]              │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Name           | Belt    | Status    | Actions        │
│  ─────────────────────────────────────────────────     │
│  John Smith     | Blue    | Active    | ✏️  🗑️         │
│  Jane Doe       | Brown   | Active    | ✏️  🗑️  ⬅️ Archive │
│  Mike Johnson   | Yellow  | Active    | ✏️  🗑️         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## User Interface - Archived Trainees

### Page: Archived Trainees

```
┌─────────────────────────────────────────────────────────┐
│  Archived Trainees  [Back to Active Trainees]           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Search: [Search box.............]                     │
│  Status: [All Status ▼]  Belt: [All Belts ▼]          │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Name           | Belt    | Status    | Actions        │
│  ─────────────────────────────────────────────────     │
│  ⚫ David Lee      | Green   | Active    | ↩️  ⬅️ Restore │
│  ⚫ Sarah White    | Orange  | Inactive  | ↩️            │
│                                                         │
│  (Reduced opacity showing archived status)             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Action Flow Diagrams

### Archive Flow

```
Active Trainee List
        │
        │ Click "Archive" (Red button)
        ▼
    Confirm Dialog
    "Are you sure you want to archive [Name]?
     You can restore this trainee later."
        │
        │ Yes
        ▼
    Set archived=True in DB
        │
        ▼
    Remove from active list
        │
        ▼
    Toast: "Trainee [Name] has been archived."
        │
        ▼
    Show updated list (without archived trainee)
```

### Restore Flow

```
Archived Trainee List
        │
        │ Click "Restore" (Green button)
        ▼
    Confirm Dialog
    "Are you sure you want to restore [Name]?"
        │
        │ Yes
        ▼
    Set archived=False in DB
        │
        ▼
    Remove from archived list
        │
        ▼
    Toast: "Trainee [Name] has been restored."
        │
        ▼
    Show updated list (without restored trainee)
```

## Button Styling

### Archive Button (Red)
```
Active Trainees List
│
├─ Edit Button (Blue)
│  └─ 📝 Pencil icon
│
└─ Archive Button (Red)
   └─ 🗑️  Delete/trash icon
      Confirmation: "Archive [Name]?"
```

### Restore Button (Green)
```
Archived Trainees List
│
└─ Restore Button (Green)
   └─ ↩️ Arrow/undo icon
      Confirmation: "Restore [Name]?"
```

## Search & Filter Flow

### Active Trainees

```
Search by:                Filter by:
├─ First Name           ├─ Status
├─ Last Name            │  ├─ Active
├─ Username             │  ├─ Inactive
├─ Belt Rank            │  └─ Suspended
└─ Status               │
                        └─ Belt Rank
                           ├─ White
                           ├─ Yellow
                           ├─ Orange
                           ├─ Green
                           ├─ Blue
                           ├─ Brown
                           └─ Black

Same filters work in Archived Trainees list!
```

## HTMX Update Cycle

```
User Types in Search
         │
         ▼
    HTMX sends GET request
    (300ms debounce)
         │
         ▼
    Django view processes
    - Filters archived=False/True
    - Applies search/filters
    - Builds context
         │
         ▼
    Renders partial template
    (list_partial.html / archived_partial.html)
         │
         ▼
    Returns HTML fragment
    + Toast message
         │
         ▼
    HTMX swaps innerHTML
         │
         ▼
    Toast appears (2 sec)
         │
         ▼
    Updated list visible
    (No page reload!)
```

## Mobile View

### Trainee Card (Active)

```
┌──────────────────────────────┐
│ 👤 John Smith    [Active ●]   │
│    john@email.com             │
├──────────────────────────────┤
│ Belt: Blue   Age: 25   Weight │
│              Middleweight     │
├──────────────────────────────┤
│ [📝 Edit] [🗑️  Archive]        │
└──────────────────────────────┘
```

### Trainee Card (Archived)

```
┌──────────────────────────────┐
│ ⚫ David Lee     [Active ●]    │
│    david@email.com            │
│ (reduced opacity)             │
├──────────────────────────────┤
│ Belt: Green  Age: 30   Weight │
│              Middleweight     │
├──────────────────────────────┤
│ [↩️  Restore]                  │
└──────────────────────────────┘
```

## State Transitions

### Trainee Record States

```
                    Database Record
                          │
                          │ archived field
                    ┌─────┴─────┐
                    │           │
                 FALSE         TRUE
                    │           │
                    ▼           ▼
                ┌────────┐  ┌─────────┐
                │ Active │  │ Archived│
                │Trainee │  │ Trainee │
                └───┬────┘  └────┬────┘
                    │            │
              [Archive]      [Restore]
                    │            │
                    └────┬───────┘
                         │
                   (User Action)
```

## Data Preservation

```
Active Trainee Archived
        │
        ├─ User Profile → PRESERVED
        ├─ Event Registrations → PRESERVED
        ├─ Match History → PRESERVED
        ├─ Payment Records → PRESERVED
        ├─ Points/Leaderboard → PRESERVED
        ├─ Belt Rank Progress → PRESERVED
        └─ Notifications → PRESERVED

All related data remains intact!
Can be restored anytime.
```

## URL Structure

```
Admin Routes:

/admin/trainees/
├─ GET  → List active trainees
├─ POST /add/ → Create new trainee
├─ POST /<id>/edit/ → Edit trainee
├─ DELETE /<id>/ → Archive trainee ⬅️ Modified
│
└─ /archived/
   ├─ GET → List archived trainees ⬅️ NEW
   ├─ GET /partial/ → HTMX partial ⬅️ NEW
   └─ POST /<id>/restore/ → Restore trainee ⬅️ NEW
```

## Comparison View

### Side-by-Side: Active vs Archived

```
ACTIVE TRAINEES              ARCHIVED TRAINEES
═══════════════════════════════════════════════

Name: John Smith       ↔     Name: David Lee
Status: Active         ↔     Status: Active (but archived)
Belt: Blue             ↔     Belt: Green
Age: 25                ↔     Age: 30
Opacity: 100%          ↔     Opacity: 75%

Actions:               ↔     Actions:
├─ Edit (Blue)        ↔     └─ Restore (Green)
└─ Archive (Red)      
```

## Complete User Journey

```
Step 1: View Active Trainees
        └─ Go to Trainee Management
           └─ See list of active trainees
              └─ Can search, filter, edit

Step 2: Archive a Trainee
        └─ Click Archive button (Red)
           └─ Confirm action
              └─ Trainee disappears from list
                 └─ Toast: "archived"

Step 3: View Archived Trainees
        └─ Click "Archived Trainees" in sidebar
           └─ See only archived trainees
              └─ Can search and filter

Step 4: Restore a Trainee
        └─ Click Restore button (Green)
           └─ Confirm action
              └─ Trainee disappears from archived
                 └─ Toast: "restored"

Step 5: Return to Active Trainees
        └─ Click "Trainee Management" in sidebar
           └─ See restored trainee in active list
              └─ Back to normal
```

## Quick Reference

| Action | Location | Button | Color | Icon | Result |
|--------|----------|--------|-------|------|--------|
| Archive | Active List | Delete/Trash | Red | 🗑️ | Moves to Archived |
| Restore | Archived List | Restore | Green | ↩️ | Moves to Active |
| Search | Both Lists | Input | Gray | 🔍 | Filters list |
| Edit | Active List | Edit | Blue | ✏️ | Opens form |

---

**Implementation Complete!** 🎉

All visual elements match Event Management and Matchmaking patterns.
