from django.urls import path
from . import views
from .views import admin as admin_views
from .views import admin_registrations as admin_reg_views
from .views import admin_judges as admin_judges_views
from .views import trainee as trainee_views
from .views import judge as judge_views
from .views import leaderboard as leaderboard_views
from .views import notifications as notification_views
from .views import attendance as attendance_views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    # Admin URLs
    path("admin/dashboard/", admin_views.dashboard_view, name="admin_dashboard"),
    # Registration Management URLs
    path(
        "admin/registrations/",
        admin_reg_views.registration_list,
        name="admin_registrations",
    ),
    path(
        "admin/registrations/<int:registration_id>/",
        admin_reg_views.registration_detail,
        name="admin_registration_detail",
    ),
    path(
        "admin/registrations/<int:registration_id>/approve/",
        admin_reg_views.registration_approve,
        name="admin_registration_approve",
    ),
    path(
        "admin/registrations/<int:registration_id>/reject/",
        admin_reg_views.registration_reject,
        name="admin_registration_reject",
    ),
    # Judge Management URLs
    path("admin/judges/", admin_judges_views.judge_list, name="admin_judges"),
    path(
        "admin/judges/partial/",
        admin_judges_views.judge_list_partial,
        name="admin_judge_list_partial",
    ),
    path(
        "admin/judges/archived/",
        admin_judges_views.archived_judges_list,
        name="admin_archived_judges",
    ),
    path(
        "admin/judges/archived/partial/",
        admin_judges_views.archived_judges_list_partial,
        name="admin_archived_judges_partial",
    ),
    path("admin/judges/add/", admin_judges_views.judge_add, name="admin_judge_add"),
    path(
        "admin/judges/<int:judge_id>/edit/",
        admin_judges_views.judge_edit,
        name="admin_judge_edit",
    ),
    path(
        "admin/judges/<int:judge_id>/deactivate/",
        admin_judges_views.judge_deactivate,
        name="admin_judge_deactivate",
    ),
    path(
        "admin/judges/<int:judge_id>/restore/",
        admin_judges_views.judge_restore,
        name="admin_judge_restore",
    ),
    # Trainee Management URLs (Requirements: 3.1-3.6)
    path("admin/trainees/", admin_views.trainee_list, name="admin_trainees"),
    path(
        "admin/trainees/partial/",
        admin_views.trainee_list_partial,
        name="admin_trainee_list_partial",
    ),
    path(
        "admin/trainees/archived/",
        admin_views.archived_trainees_list,
        name="admin_archived_trainees",
    ),
    path(
        "admin/trainees/archived/partial/",
        admin_views.archived_trainees_list_partial,
        name="admin_archived_trainees_partial",
    ),
    path("admin/trainees/add/", admin_views.trainee_add, name="admin_trainee_add"),
    path(
        "admin/trainees/<int:trainee_id>/edit/",
        admin_views.trainee_edit,
        name="admin_trainee_edit",
    ),
    path(
        "admin/trainees/<int:trainee_id>/delete/",
        admin_views.trainee_delete,
        name="admin_trainee_delete",
    ),
    path(
        "admin/trainees/<int:trainee_id>/restore/",
        admin_views.trainee_restore,
        name="admin_trainee_restore",
    ),
    path(
        "admin/trainees/export/",
        admin_views.trainee_export,
        name="admin_trainee_export",
    ),
    # Event Management URLs (Requirements: 4.1-4.5)
    path("admin/events/", admin_views.event_list, name="admin_events"),
    path(
        "admin/events/partial/",
        admin_views.event_list_partial,
        name="admin_event_list_partial",
    ),
    path(
        "admin/events/archived/",
        admin_views.archived_events_list,
        name="admin_archived_events",
    ),
    path(
        "admin/events/archived/partial/",
        admin_views.archived_events_list_partial,
        name="admin_archived_events_partial",
    ),
    path("admin/events/add/", admin_views.event_add, name="admin_event_add"),
    path(
        "admin/events/<int:event_id>/",
        admin_views.event_detail,
        name="admin_event_detail",
    ),
    path(
        "admin/events/<int:event_id>/edit/",
        admin_views.event_edit,
        name="admin_event_edit",
    ),
    path(
        "admin/events/<int:event_id>/archive/",
        admin_views.event_archive,
        name="admin_event_archive",
    ),
    path(
        "admin/events/<int:event_id>/restore/",
        admin_views.event_restore,
        name="admin_event_restore",
    ),
    path(
        "admin/events/<int:event_id>/status/",
        admin_views.event_status_update,
        name="admin_event_status_update",
    ),
    path("admin/events/export/", admin_views.event_export, name="admin_event_export"),
    # Matchmaking Management URLs (Requirements: 5.1-5.6)
    path("admin/matchmaking/", admin_views.matchmaking_list, name="admin_matchmaking"),
    path(
        "admin/matchmaking/partial/",
        admin_views.matchmaking_list_partial,
        name="admin_matchmaking_list_partial",
    ),
    path(
        "admin/matchmaking/archived/",
        admin_views.archived_matchmaking_list,
        name="admin_archived_matchmaking",
    ),
    path(
        "admin/matchmaking/archived/partial/",
        admin_views.archived_matchmaking_list_partial,
        name="admin_archived_matchmaking_partial",
    ),
    path("admin/matchmaking/add/", admin_views.match_add, name="admin_match_add"),
    path(
        "admin/matchmaking/<int:match_id>/edit/",
        admin_views.match_edit,
        name="admin_match_edit",
    ),
    path(
        "admin/matchmaking/<int:match_id>/archive/",
        admin_views.match_archive,
        name="admin_match_archive",
    ),
    path(
        "admin/matchmaking/<int:match_id>/restore/",
        admin_views.match_restore,
        name="admin_match_restore",
    ),
    path(
        "admin/matchmaking/<int:match_id>/delete/",
        admin_views.match_delete,
        name="admin_match_delete",
    ),
    path(
        "admin/matchmaking/auto/",
        admin_views.auto_matchmaking,
        name="admin_auto_matchmaking",
    ),
    path(
        "admin/matchmaking/auto/confirm/",
        admin_views.auto_matchmaking_confirm,
        name="admin_auto_matchmaking_confirm",
    ),
    path(
        "admin/matchmaking/monitor/",
        admin_views.match_monitor,
        name="admin_match_monitor",
    ),
    path(
        "admin/matchmaking/monitor/export/pdf/",
        admin_views.match_monitor_export_pdf,
        name="admin_match_monitor_export_pdf",
    ),
    path(
        "admin/matchmaking/<int:match_id>/detail/",
        admin_views.match_detail,
        name="admin_match_detail",
    ),
    path(
        "admin/matchmaking/<int:match_id>/export/pdf/",
        admin_views.match_export_pdf,
        name="admin_match_export_pdf",
    ),
    path(
        "admin/matchmaking/<int:match_id>/close/",
        admin_views.match_close,
        name="admin_match_close",
    ),
    # Payment Management URLs (Requirements: 6.1-6.5)
    path("admin/payments/", admin_views.payment_list, name="admin_payments"),
    path(
        "admin/payments/partial/",
        admin_views.payment_list_partial,
        name="admin_payment_list_partial",
    ),
    path(
        "admin/payments/archived/",
        admin_views.archived_payments_list,
        name="admin_archived_payments",
    ),
    path(
        "admin/payments/archived/partial/",
        admin_views.archived_payments_list_partial,
        name="admin_archived_payments_partial",
    ),
    path("admin/payments/add/", admin_views.payment_add, name="admin_payment_add"),
    path(
        "admin/payments/<int:payment_id>/edit/",
        admin_views.payment_edit,
        name="admin_payment_edit",
    ),
    path(
        "admin/payments/<int:payment_id>/delete/",
        admin_views.payment_delete,
        name="admin_payment_delete",
    ),
    path(
        "admin/payments/<int:payment_id>/archive/",
        admin_views.payment_archive,
        name="admin_payment_archive",
    ),
    path(
        "admin/payments/<int:payment_id>/restore/",
        admin_views.payment_restore,
        name="admin_payment_restore",
    ),
    path(
        "admin/payments/<int:payment_id>/complete/",
        admin_views.payment_mark_completed,
        name="admin_payment_complete",
    ),
    # Reports URLs (Requirements: 7.1-7.4)
    path("admin/reports/", admin_views.reports_view, name="admin_reports"),
    path(
        "admin/reports/export/", admin_views.reports_export, name="admin_reports_export"
    ),
    # Extended Reports URLs
    path(
        "admin/reports/belt-promotion/",
        admin_views.belt_promotion_report,
        name="admin_belt_promotion_report",
    ),
    path(
        "admin/reports/skill-progression/",
        admin_views.skill_progression_report,
        name="admin_skill_progression_report",
    ),
    path(
        "admin/reports/tournament-participation/",
        admin_views.tournament_participation_report,
        name="admin_tournament_participation_report",
    ),
    path(
        "admin/reports/performance-evaluation/",
        admin_views.performance_evaluation_report,
        name="admin_performance_evaluation_report",
    ),
    path(
        "admin/reports/competition-results/",
        admin_views.competition_results_report,
        name="admin_competition_results_report",
    ),
    path(
        "admin/reports/trainee-milestones/",
        admin_views.trainee_milestones_report,
        name="admin_trainee_milestones_report",
    ),
    # Belt Rank Promotion URLs
    path(
        "admin/belt-promotion/",
        admin_views.belt_rank_promotion_list,
        name="admin_belt_promotion",
    ),
    path(
        "admin/belt-promotion/partial/",
        admin_views.belt_rank_promotion_list_partial,
        name="admin_belt_promotion_list_partial",
    ),
    path(
        "admin/belt-promotion/<int:trainee_id>/promote/",
        admin_views.belt_rank_promote,
        name="admin_belt_rank_promote",
    ),
    path(
        "admin/belt-promotion/history/",
        admin_views.belt_rank_promotion_history,
        name="admin_belt_promotion_history",
    ),
    # Evaluation URLs
    path("admin/evaluations/", admin_views.evaluation_list, name="admin_evaluations"),
    path(
        "admin/evaluations/partial/",
        admin_views.evaluation_list_partial,
        name="admin_evaluation_list_partial",
    ),
    path(
        "admin/evaluations/add/",
        admin_views.evaluation_add,
        name="admin_evaluation_add",
    ),
    path(
        "admin/evaluations/<int:evaluation_id>/edit/",
        admin_views.evaluation_edit,
        name="admin_evaluation_edit",
    ),
    path(
        "admin/evaluations/<int:evaluation_id>/delete/",
        admin_views.evaluation_delete,
        name="admin_evaluation_delete",
    ),
    path(
        "admin/evaluations/<int:trainee_id>/trainee/",
        admin_views.trainee_evaluations,
        name="admin_trainee_evaluations",
    ),
    # Admin Leaderboard URLs
    path("admin/leaderboard/", admin_views.leaderboard_view, name="admin_leaderboard"),
    # Attendance Management URLs
    path(
        "admin/attendance/",
        attendance_views.attendance_dashboard,
        name="attendance_dashboard",
    ),
    path(
        "admin/attendance/sessions/",
        attendance_views.session_list,
        name="session_list",
    ),
    path(
        "admin/attendance/sessions/bulk-delete/",
        attendance_views.session_bulk_delete,
        name="session_bulk_delete",
    ),
    path(
        "admin/attendance/sessions/create/",
        attendance_views.session_create,
        name="session_create",
    ),
    path(
        "admin/attendance/sessions/<int:session_id>/edit/",
        attendance_views.session_edit,
        name="session_edit",
    ),
    path(
        "admin/attendance/sessions/<int:session_id>/delete/",
        attendance_views.session_delete,
        name="session_delete",
    ),
    path(
        "admin/attendance/sessions/<int:session_id>/attendance/",
        attendance_views.session_attendance,
        name="session_attendance",
    ),
    path(
        "admin/attendance/sessions/<int:session_id>/bulk-present/",
        attendance_views.bulk_mark_present,
        name="bulk_mark_present",
    ),
    path(
        "admin/attendance/quick-session/",
        attendance_views.quick_session_create,
        name="quick_session_create",
    ),
    path(
        "admin/attendance/events/<int:event_id>/",
        attendance_views.event_attendance,
        name="event_attendance",
    ),
    path(
        "admin/attendance/trainees/<int:trainee_id>/history/",
        attendance_views.trainee_attendance_history,
        name="trainee_attendance_history",
    ),
    path(
        "admin/attendance/export/",
        attendance_views.session_attendance_export,
        name="session_attendance_export",
    ),
    # Trainee URLs (Requirements: 8.1-8.3, 9.1-9.4, 10.1-10.3, 11.1-11.3)
    path("trainee/dashboard/", trainee_views.dashboard_view, name="trainee_dashboard"),
    path("trainee/profile/", trainee_views.profile_view, name="trainee_profile"),
    path(
        "trainee/profile/edit/", trainee_views.profile_edit, name="trainee_profile_edit"
    ),
    path("trainee/events/", trainee_views.events_view, name="trainee_events"),
    path(
        "trainee/events/<int:event_id>/register/",
        trainee_views.event_register,
        name="trainee_event_register",
    ),
    path(
        "trainee/events/<int:event_id>/unregister/",
        trainee_views.event_unregister,
        name="trainee_event_unregister",
    ),
    path("trainee/matches/", trainee_views.matches_view, name="trainee_matches"),
    path("trainee/payments/", trainee_views.payments_view, name="trainee_payments"),
    path(
        "trainee/achievements/add/",
        trainee_views.achievement_add,
        name="trainee_achievement_add",
    ),
    # Judge URLs (Requirements: 12.1-12.3, 13.1-13.3, 14.1-14.4)
    path("judge/dashboard/", judge_views.dashboard_view, name="judge_dashboard"),
    path("judge/events/", judge_views.events_view, name="judge_events"),
    path("judge/matches/", judge_views.matches_view, name="judge_matches"),
    path("judge/results/", judge_views.results_view, name="judge_results"),
    path(
        "judge/results/<int:match_id>/",
        judge_views.result_entry,
        name="judge_result_entry",
    ),
    path("judge/profile/edit/", judge_views.profile_edit, name="judge_profile_edit"),
    # Leaderboard and Belt Rank URLs
    path(
        "leaderboard/all-time/",
        leaderboard_views.leaderboard_all_time,
        name="leaderboard_all_time",
    ),
    path(
        "leaderboard/yearly/",
        leaderboard_views.leaderboard_yearly,
        name="leaderboard_yearly",
    ),
    path(
        "leaderboard/monthly/",
        leaderboard_views.leaderboard_monthly,
        name="leaderboard_monthly",
    ),
    path(
        "leaderboard/by-belt/",
        leaderboard_views.leaderboard_by_belt,
        name="leaderboard_by_belt",
    ),
    path(
        "trainee/<int:trainee_id>/points/",
        leaderboard_views.trainee_profile_points,
        name="trainee_profile_points",
    ),
    path(
        "belt-rank/progress/",
        leaderboard_views.belt_rank_progress,
        name="belt_rank_progress",
    ),
    # Notification URLs
    path(
        "notifications/", notification_views.notification_list, name="notification_list"
    ),
    path(
        "notifications/<int:notification_id>/mark-as-read/",
        notification_views.mark_as_read,
        name="mark_notification_read",
    ),
    path(
        "notifications/mark-all-as-read/",
        notification_views.mark_all_as_read,
        name="mark_all_notifications_read",
    ),
    path(
        "notifications/unread-count/",
        notification_views.get_unread_count,
        name="unread_count",
    ),
    path(
        "notifications/recent/",
        notification_views.get_recent_notifications,
        name="recent_notifications",
    ),
]
