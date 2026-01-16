# Trainee Evaluation System - Deployment Checklist

## Pre-Deployment

- [ ] Review all code changes
- [ ] Read EVALUATION_SUMMARY.md for overview
- [ ] Read EVALUATION_IMPLEMENTATION.md for technical details
- [ ] Review database schema changes
- [ ] Backup database before migration

## Database

- [ ] Run migration: `python manage.py migrate`
- [ ] Verify migration completed successfully
- [ ] Check TraineeEvaluation table in database
- [ ] Verify indexes created correctly
- [ ] Test database rollback procedure (optional)

## Admin Panel

- [ ] Login to admin (`/admin/`)
- [ ] Verify "TraineeEvaluation" appears in admin models
- [ ] Click on TraineeEvaluation to verify admin panel works
- [ ] Test creating evaluation in admin panel
- [ ] Test filtering/searching in admin panel
- [ ] Test editing evaluation in admin panel
- [ ] Test deleting evaluation in admin panel

## Admin Dashboard

- [ ] Verify "Evaluations" link appears in sidebar
- [ ] Click sidebar link to verify it navigates correctly
- [ ] Check active state styling when on evaluations page
- [ ] Verify sidebar responsive on mobile

## Evaluation List Page

- [ ] Visit `/admin/evaluations/`
- [ ] Verify page loads without errors
- [ ] Test search functionality (type trainee name)
- [ ] Test status filter dropdown
- [ ] Test rating filter dropdown
- [ ] Verify "New Evaluation" button works
- [ ] Test HTMX filtering (changes should not reload page)
- [ ] Verify evaluation cards display correctly
- [ ] Check color-coded ratings (green to red)
- [ ] Test pagination (if evaluations > 20)

## Create Evaluation

- [ ] Click "New Evaluation" button
- [ ] Verify form displays all fields
- [ ] Test trainee dropdown (should show active trainees only)
- [ ] Verify all 6 rating dropdowns work (1-5 scale)
- [ ] Test overall rating field
- [ ] Test comments textarea
- [ ] Test strengths textarea
- [ ] Test areas_for_improvement textarea
- [ ] Test recommendations textarea
- [ ] Test date picker for next_evaluation_date
- [ ] Submit form with complete data
- [ ] Verify success message displays
- [ ] Verify evaluation appears in list
- [ ] Verify evaluator set to current user

## Edit Evaluation

- [ ] Click "Edit" on any evaluation
- [ ] Verify form pre-fills existing data
- [ ] Change a rating value
- [ ] Change some comments
- [ ] Submit form
- [ ] Verify success message
- [ ] Verify changes appear in list

## Delete Evaluation

- [ ] Click "Delete" on an evaluation
- [ ] Verify confirmation modal appears
- [ ] Click "Delete" in confirmation
- [ ] Verify success message
- [ ] Verify evaluation removed from list (archived)
- [ ] Check database confirms archived=true

## Trainee History View

- [ ] Click "View All" on evaluation in list
- [ ] Verify trainee info card displays
- [ ] Check statistics cards (total, latest, average)
- [ ] Verify evaluation timeline displays all evaluations
- [ ] Check evaluation cards show all details
- [ ] Test "Edit" button on evaluation
- [ ] Test "Delete" button on evaluation
- [ ] Check responsive layout on mobile

## Form Validation

- [ ] Try submitting form without selecting trainee
- [ ] Verify error message displays
- [ ] Test form state persistence on error
- [ ] Test special characters in text fields
- [ ] Test long text (1000+ characters)
- [ ] Test date field validation
- [ ] Test numeric field validation (ratings)

## HTMX Integration

- [ ] Open browser network tab
- [ ] Type in search box
- [ ] Verify XHR request sent (not full page request)
- [ ] Verify results update without page reload
- [ ] Change filter dropdown
- [ ] Verify results update via HTMX (no page reload)
- [ ] Combine search + filters
- [ ] Verify both filters apply correctly

## Responsive Design

- [ ] Open on desktop (1920px) - verify layout
- [ ] Open on tablet (768px) - verify layout
- [ ] Open on mobile (375px) - verify layout
- [ ] Test navigation menu on mobile
- [ ] Test form fields on mobile
- [ ] Test evaluation cards stack correctly
- [ ] Test rating grid on mobile (should wrap to 2 columns)
- [ ] Verify buttons are touch-friendly (min 44px)

## Security

- [ ] Verify non-admin cannot access `/admin/evaluations/`
- [ ] Verify non-admin cannot create evaluations
- [ ] Verify CSRF tokens on forms
- [ ] Test XSS with special characters in comments
- [ ] Verify evaluations only show to authorized users
- [ ] Test SQL injection attempts in search (should be escaped)

## Performance

- [ ] Monitor database query count (should be < 10 for list page)
- [ ] Check page load time (should be < 1 second)
- [ ] Monitor HTMX request time (should be < 200ms)
- [ ] Check database connection pool
- [ ] Verify indexes are being used (EXPLAIN ANALYZE)
- [ ] Load test with 100+ evaluations

## Browser Compatibility

- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile Safari (latest)
- [ ] Mobile Chrome (latest)
- [ ] Test forms work in all browsers
- [ ] Test dropdowns in all browsers
- [ ] Test date picker in all browsers

## Documentation

- [ ] Verify EVALUATION_QUICK_START.md is complete
- [ ] Verify EVALUATION_IMPLEMENTATION.md has correct code refs
- [ ] Verify EVALUATION_SUMMARY.md is accurate
- [ ] Check all links in documentation
- [ ] Update README if needed
- [ ] Document any customizations made

## Rollback Plan

- [ ] Have rollback migration ready (if needed)
- [ ] Document rollback steps
- [ ] Test rollback on staging (optional)
- [ ] Keep database backup

## Post-Deployment

- [ ] Monitor error logs for issues
- [ ] Monitor database performance
- [ ] Gather user feedback
- [ ] Check for any reported bugs
- [ ] Update documentation if needed
- [ ] Consider scheduling training for admins

## Final Verification

- [ ] All functionality working as expected
- [ ] No console errors in browser
- [ ] No server errors in logs
- [ ] Database migrations clean
- [ ] Admin sidebar displays correctly
- [ ] Forms validate correctly
- [ ] Filters work as expected
- [ ] HTMX updates smooth
- [ ] Page loads fast
- [ ] Responsive on all devices

## Sign-Off

- [ ] Development complete and tested
- [ ] Code review completed
- [ ] QA testing passed
- [ ] Production deployment approved
- [ ] User training completed
- [ ] Documentation complete
- [ ] Deployment completed successfully
- [ ] Post-deployment monitoring started

---

## Notes

- Keep backups before running migration
- Test thoroughly on staging first
- Have support plan ready
- Document any customizations
- Train admins on new feature

## Contact

For deployment issues:
1. Check error logs
2. Review EVALUATION_IMPLEMENTATION.md
3. Check database migration status
4. Verify all files uploaded correctly
5. Test database connectivity

## Timeline Estimate

- Pre-deployment checks: 15 minutes
- Migration: 5 minutes
- Testing: 1-2 hours
- Deployment: 30 minutes
- Post-deployment monitoring: ongoing
