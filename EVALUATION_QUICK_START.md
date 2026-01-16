# Evaluation System - Quick Start Guide

## Setup Steps

### 1. Apply Migration
```bash
python manage.py migrate
```

### 2. Access Evaluations
- **Via Admin Dashboard**: Click "Evaluations" in sidebar
- **Direct URL**: `/admin/evaluations/`

## Create an Evaluation

1. Click **"New Evaluation"** button
2. **Select Trainee**: Choose from dropdown (active trainees only)
3. **Rate Performance** (1-5 scale):
   - Technique
   - Speed
   - Strength
   - Flexibility
   - Discipline
   - Fighting Spirit
   - Overall Rating
4. **Add Feedback**:
   - Comments: General observations
   - Strengths: What they do well
   - Areas for Improvement: What needs work
   - Recommendations: Training guidance
5. **Schedule Next Evaluation**: Set optional date
6. Click **"Create Evaluation"**

## View Evaluations

### All Evaluations
- Go to `/admin/evaluations/`
- Use **Search** to find trainees
- Filter by **Status** (Pending/Completed)
- Filter by **Rating** (1-5 stars)

### Trainee's History
- Click **"View All"** on any evaluation
- See complete evaluation timeline
- View statistics (total, latest, average ratings)

## Edit Evaluation

1. Click **"Edit"** on any evaluation
2. Update ratings or feedback
3. Click **"Update Evaluation"**

## Delete Evaluation

1. Click **"Delete"** 
2. Confirm in popup
3. Evaluation is archived (can be restored)

## Rating Guide

| Rating | Level | Description |
|--------|-------|-------------|
| 1 | Poor | Needs significant improvement |
| 2 | Fair | Below expected level |
| 3 | Good | Meets expectations |
| 4 | Very Good | Exceeds expectations |
| 5 | Excellent | Outstanding performance |

## Sidebar Location

After applying changes:
- Login to admin
- Click **"Evaluations"** in left sidebar
- Under main navigation menu

## Features

✅ Create/Edit evaluations  
✅ Rate 6 performance criteria  
✅ Add detailed feedback  
✅ Search and filter evaluations  
✅ View trainee history  
✅ Archive evaluations  
✅ HTMX live filtering  
✅ Responsive design  

## Admin Panel Integration

Evaluations also available in Django admin:
- Navigate to `/admin/`
- Look for "TraineeEvaluation" section
- Full CRUD operations available

## Common Tasks

### Find all "Excellent" ratings
1. Go to Evaluations
2. Filter by Rating → "Excellent"
3. View results

### View trainee's progress
1. Search trainee by name
2. Click "View All" 
3. See complete evaluation history

### Create bulk evaluations
1. Go to Evaluations
2. Click "New Evaluation"
3. Create evaluation
4. Return to list, repeat

## Data Fields Explained

**Performance Ratings** (1-5 each):
- **Technique**: Karate form and technique proficiency
- **Speed**: Reaction time and movement speed
- **Strength**: Physical power and conditioning
- **Flexibility**: Range of motion and agility
- **Discipline**: Focus, listening, following instructions
- **Spirit**: Drive, determination, fighting spirit

**Assessment Text**:
- **Comments**: Anything relevant to overall performance
- **Strengths**: Positive attributes and skills
- **Areas for Improvement**: Specific things to work on
- **Recommendations**: Suggested training focus areas

**Dates**:
- **Evaluated At**: Automatically set when created
- **Next Evaluation Date**: When to schedule next assessment (optional)

## Tips

- Evaluate regularly (e.g., monthly or after events)
- Include specific examples in comments
- Focus on development, not just criticism
- Set clear next evaluation dates
- Use consistent rating criteria
- Combine with belt promotion tracking

## Need Help?

See `EVALUATION_IMPLEMENTATION.md` for detailed documentation.
