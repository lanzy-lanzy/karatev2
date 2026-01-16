from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q, Avg
from django.http import JsonResponse
from django.core.paginator import Paginator
from ..models import Trainee, Attendance, TrainingSession, Event
from datetime import datetime, date, timedelta


def admin_required(view_func):
    """Decorator to ensure user is admin."""

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if not hasattr(request.user, "profile") or request.user.profile.role != "admin":
            messages.error(request, "You don't have permission to access this page.")
            return redirect("home")
        return view_func(request, *args, **kwargs)

    return wrapper


@admin_required
def attendance_dashboard(request):
    """
    Comprehensive attendance dashboard with statistics and overview.
    """
    today = timezone.now().date()

    # Date range for statistics (last 30 days)
    thirty_days_ago = today - timedelta(days=30)

    # Active Trainees
    active_trainees_count = Trainee.objects.filter(
        status="active", archived=False
    ).count()

    # Today's Sessions
    todays_sessions = TrainingSession.objects.filter(date=today).order_by("start_time")
    todays_sessions_count = todays_sessions.count()

    # Sessions this week
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    weekly_sessions = TrainingSession.objects.filter(
        date__gte=week_start, date__lte=week_end
    ).count()

    # Monthly attendance rate
    monthly_attendance = Attendance.objects.filter(date__gte=thirty_days_ago)
    if monthly_attendance.exists():
        total_records = monthly_attendance.count()
        present_records = monthly_attendance.filter(
            status__in=["present", "late"]
        ).count()
        monthly_rate = (
            int((present_records / total_records) * 100) if total_records > 0 else 0
        )
    else:
        monthly_rate = 0

    # Recent Sessions (last 10)
    recent_sessions = TrainingSession.objects.filter(date__lte=today).order_by(
        "-date", "-start_time"
    )[:10]

    # Add attendance stats to each session
    for session in recent_sessions:
        session.present_count = session.attendance_records.filter(
            status__in=["present", "late"]
        ).count()
        session.absent_count = session.attendance_records.filter(
            status="absent"
        ).count()
        session.excused_count = session.attendance_records.filter(
            status="excused"
        ).count()

    # Upcoming Sessions
    upcoming_sessions = TrainingSession.objects.filter(
        date__gte=today, status__in=["scheduled", "ongoing"]
    ).order_by("date", "start_time")[:5]

    # Upcoming Events with attendance
    upcoming_events = Event.objects.filter(
        event_date__gte=today, status__in=["open", "closed", "ongoing"], archived=False
    ).order_by("event_date")[:5]

    # Top Attendees (last 30 days)
    top_attendees = (
        Trainee.objects.filter(
            status="active",
            archived=False,
            attendance_records__date__gte=thirty_days_ago,
            attendance_records__status__in=["present", "late"],
        )
        .annotate(
            attendance_count=Count(
                "attendance_records",
                filter=Q(
                    attendance_records__date__gte=thirty_days_ago,
                    attendance_records__status__in=["present", "late"],
                ),
            )
        )
        .order_by("-attendance_count")[:5]
    )

    # Low Attendance Trainees (warning)
    # Trainees with less than 50% attendance in last 30 days
    low_attendance_trainees = []
    for trainee in Trainee.objects.filter(status="active", archived=False):
        records = trainee.attendance_records.filter(date__gte=thirty_days_ago)
        if records.exists():
            total = records.count()
            present = records.filter(status__in=["present", "late"]).count()
            rate = (present / total) * 100
            if rate < 50:
                trainee.attendance_rate = int(rate)
                trainee.sessions_attended = present
                trainee.total_sessions = total
                low_attendance_trainees.append(trainee)

    low_attendance_trainees = sorted(
        low_attendance_trainees, key=lambda x: x.attendance_rate
    )[:5]

    # Session type distribution (last 30 days)
    session_types = (
        TrainingSession.objects.filter(date__gte=thirty_days_ago)
        .values("session_type")
        .annotate(count=Count("id"))
    )

    context = {
        "active_trainees_count": active_trainees_count,
        "todays_sessions": todays_sessions,
        "todays_sessions_count": todays_sessions_count,
        "weekly_sessions": weekly_sessions,
        "monthly_rate": monthly_rate,
        "recent_sessions": recent_sessions,
        "upcoming_sessions": upcoming_sessions,
        "upcoming_events": upcoming_events,
        "top_attendees": top_attendees,
        "low_attendance_trainees": low_attendance_trainees,
        "session_types": session_types,
        "today": today,
    }

    return render(request, "admin/attendance/dashboard.html", context)


@admin_required
def session_list(request):
    """
    List all training sessions with filtering and pagination.
    """
    sessions = TrainingSession.objects.all()

    # Filters
    status_filter = request.GET.get("status", "")
    type_filter = request.GET.get("type", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")
    search = request.GET.get("search", "")

    if status_filter:
        sessions = sessions.filter(status=status_filter)
    if type_filter:
        sessions = sessions.filter(session_type=type_filter)
    if date_from:
        sessions = sessions.filter(date__gte=date_from)
    if date_to:
        sessions = sessions.filter(date__lte=date_to)
    if search:
        sessions = sessions.filter(
            Q(title__icontains=search)
            | Q(instructor__icontains=search)
            | Q(location__icontains=search)
        )

    # Pagination
    paginator = Paginator(sessions, 15)
    page = request.GET.get("page", 1)
    sessions = paginator.get_page(page)

    # Add stats
    for session in sessions:
        session.present_count = session.attendance_records.filter(
            status__in=["present", "late"]
        ).count()

    context = {
        "sessions": sessions,
        "status_filter": status_filter,
        "type_filter": type_filter,
        "date_from": date_from,
        "date_to": date_to,
        "search": search,
        "session_types": TrainingSession.SESSION_TYPE_CHOICES,
        "status_choices": TrainingSession.STATUS_CHOICES,
    }

    if request.headers.get("HX-Request"):
        return render(request, "admin/attendance/session_list_partial.html", context)

    return render(request, "admin/attendance/session_list.html", context)


@admin_required
def session_create(request):
    """
    Create a new training session.
    """
    if request.method == "POST":
        title = request.POST.get("title")
        session_type = request.POST.get("session_type", "regular")
        date_str = request.POST.get("date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        location = request.POST.get("location", "Main Dojo")
        instructor = request.POST.get("instructor", "")
        description = request.POST.get("description", "")
        max_capacity = request.POST.get("max_capacity")

        try:
            session_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start = datetime.strptime(start_time, "%H:%M").time()
            end = datetime.strptime(end_time, "%H:%M").time()
        except (ValueError, TypeError):
            messages.error(request, "Invalid date or time format.")
            return redirect("session_create")

        session = TrainingSession.objects.create(
            title=title,
            session_type=session_type,
            date=session_date,
            start_time=start,
            end_time=end,
            location=location,
            instructor=instructor,
            description=description,
            max_capacity=int(max_capacity) if max_capacity else None,
        )

        messages.success(request, f'Session "{title}" created successfully.')
        return redirect("session_attendance", session_id=session.id)

    context = {
        "session_types": TrainingSession.SESSION_TYPE_CHOICES,
        "today": timezone.now().date().isoformat(),
    }
    return render(request, "admin/attendance/session_form.html", context)


@admin_required
def session_edit(request, session_id):
    """
    Edit an existing training session.
    """
    session = get_object_or_404(TrainingSession, id=session_id)

    if request.method == "POST":
        session.title = request.POST.get("title")
        session.session_type = request.POST.get("session_type", "regular")
        date_str = request.POST.get("date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        session.location = request.POST.get("location", "Main Dojo")
        session.instructor = request.POST.get("instructor", "")
        session.description = request.POST.get("description", "")
        session.status = request.POST.get("status", "scheduled")
        max_capacity = request.POST.get("max_capacity")

        try:
            session.date = datetime.strptime(date_str, "%Y-%m-%d").date()
            session.start_time = datetime.strptime(start_time, "%H:%M").time()
            session.end_time = datetime.strptime(end_time, "%H:%M").time()
        except (ValueError, TypeError):
            messages.error(request, "Invalid date or time format.")
            return redirect("session_edit", session_id=session.id)

        session.max_capacity = int(max_capacity) if max_capacity else None
        session.save()

        messages.success(request, f'Session "{session.title}" updated successfully.')
        return redirect("session_list")

    context = {
        "session": session,
        "session_types": TrainingSession.SESSION_TYPE_CHOICES,
        "status_choices": TrainingSession.STATUS_CHOICES,
        "editing": True,
    }
    return render(request, "admin/attendance/session_form.html", context)


@admin_required
def session_delete(request, session_id):
    """
    Delete a training session.
    """
    session = get_object_or_404(TrainingSession, id=session_id)

    if request.method == "POST":
        title = session.title
        session.delete()
        messages.success(request, f'Session "{title}" deleted successfully.')
        return redirect("session_list")

    return render(
        request, "admin/attendance/session_confirm_delete.html", {"session": session}
    )


@admin_required
def session_attendance(request, session_id):
    """
    Mark attendance for a specific training session.
    """
    session = get_object_or_404(TrainingSession, id=session_id)

    if request.method == "POST":
        trainees = Trainee.objects.filter(status="active", archived=False)
        attendance_count = 0

        for trainee in trainees:
            status = request.POST.get(f"status_{trainee.id}")
            notes = request.POST.get(f"notes_{trainee.id}", "")
            check_in_time = request.POST.get(f"check_in_{trainee.id}", "")

            if status:
                check_in = None
                if check_in_time:
                    try:
                        check_in = datetime.strptime(check_in_time, "%H:%M").time()
                    except ValueError:
                        pass

                Attendance.objects.update_or_create(
                    trainee=trainee,
                    session=session,
                    defaults={
                        "date": session.date,
                        "status": status,
                        "notes": notes,
                        "check_in_time": check_in,
                    },
                )
                if status in ["present", "late"]:
                    attendance_count += 1

        # Update session status if it was scheduled
        if session.status == "scheduled":
            session.status = "completed"
            session.save()

        messages.success(
            request,
            f'Attendance marked for "{session.title}" ({attendance_count} present)',
        )
        return redirect("attendance_dashboard")

    # GET - Display attendance form
    trainees = list(
        Trainee.objects.filter(status="active", archived=False).order_by(
            "profile__user__last_name", "profile__user__first_name"
        )
    )

    # Get existing attendance records
    attendance_map = {att.trainee_id: att for att in session.attendance_records.all()}

    # Attach to trainees
    for trainee in trainees:
        trainee.attendance_record = attendance_map.get(trainee.id)

    context = {
        "session": session,
        "trainees": trainees,
        "attendance_map": attendance_map,
    }
    return render(request, "admin/attendance/session_attendance.html", context)


@admin_required
def event_attendance(request, event_id):
    """
    Mark attendance for an event.
    """
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        # Get registered trainees
        registrations = event.registrations.filter(status="registered")
        attendance_count = 0

        for reg in registrations:
            trainee = reg.trainee
            status = request.POST.get(f"status_{trainee.id}")
            notes = request.POST.get(f"notes_{trainee.id}", "")
            check_in_time = request.POST.get(f"check_in_{trainee.id}", "")

            if status:
                check_in = None
                if check_in_time:
                    try:
                        check_in = datetime.strptime(check_in_time, "%H:%M").time()
                    except ValueError:
                        pass

                Attendance.objects.update_or_create(
                    trainee=trainee,
                    event=event,
                    defaults={
                        "date": event.event_date,
                        "status": status,
                        "notes": notes,
                        "check_in_time": check_in,
                    },
                )
                if status in ["present", "late"]:
                    attendance_count += 1

        messages.success(
            request,
            f'Attendance marked for "{event.name}" ({attendance_count} present)',
        )
        return redirect("attendance_dashboard")

    # GET - Display attendance form
    registrations = (
        event.registrations.filter(status="registered")
        .select_related("trainee__profile__user")
        .order_by("trainee__profile__user__last_name")
    )

    trainees = [reg.trainee for reg in registrations]

    # Get existing attendance records
    attendance_map = {att.trainee_id: att for att in event.attendance_records.all()}

    # Attach to trainees
    for trainee in trainees:
        trainee.attendance_record = attendance_map.get(trainee.id)

    context = {
        "event": event,
        "trainees": trainees,
        "attendance_map": attendance_map,
    }
    return render(request, "admin/attendance/event_attendance.html", context)


@admin_required
def trainee_attendance_history(request, trainee_id):
    """
    View attendance history for a specific trainee.
    """
    trainee = get_object_or_404(Trainee, id=trainee_id)

    # Get all attendance records
    records = trainee.attendance_records.select_related("session", "event").order_by(
        "-date"
    )

    # Calculate statistics
    total_records = records.count()
    present_count = records.filter(status__in=["present", "late"]).count()
    absent_count = records.filter(status="absent").count()
    excused_count = records.filter(status="excused").count()

    attendance_rate = (
        int((present_count / total_records) * 100) if total_records > 0 else 0
    )

    # Monthly breakdown
    today = timezone.now().date()
    monthly_stats = []
    for i in range(6):
        month_start = (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(
            days=1
        )

        month_records = records.filter(date__gte=month_start, date__lte=month_end)
        month_total = month_records.count()
        month_present = month_records.filter(status__in=["present", "late"]).count()
        month_rate = int((month_present / month_total) * 100) if month_total > 0 else 0

        monthly_stats.append(
            {
                "month": month_start.strftime("%B %Y"),
                "total": month_total,
                "present": month_present,
                "rate": month_rate,
            }
        )

    # Pagination
    paginator = Paginator(records, 20)
    page = request.GET.get("page", 1)
    records = paginator.get_page(page)

    context = {
        "trainee": trainee,
        "records": records,
        "total_records": total_records,
        "present_count": present_count,
        "absent_count": absent_count,
        "excused_count": excused_count,
        "attendance_rate": attendance_rate,
        "monthly_stats": monthly_stats,
    }
    return render(request, "admin/attendance/trainee_history.html", context)


@admin_required
def quick_session_create(request):
    """
    Quick create session via AJAX/HTMX.
    """
    if request.method == "POST":
        title = request.POST.get("title", "Training Session")
        session_type = request.POST.get("session_type", "regular")
        date_str = request.POST.get("date", timezone.now().date().isoformat())
        start_time = request.POST.get("start_time", "18:00")
        end_time = request.POST.get("end_time", "20:00")

        try:
            session_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start = datetime.strptime(start_time, "%H:%M").time()
            end = datetime.strptime(end_time, "%H:%M").time()
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid date/time"}, status=400)

        session = TrainingSession.objects.create(
            title=title,
            session_type=session_type,
            date=session_date,
            start_time=start,
            end_time=end,
        )

        if request.headers.get("HX-Request"):
            return redirect("session_attendance", session_id=session.id)

        return JsonResponse(
            {
                "id": session.id,
                "title": session.title,
                "redirect": f"/admin/attendance/session/{session.id}/attendance/",
            }
        )

    context = {
        "session_types": TrainingSession.SESSION_TYPE_CHOICES,
        "today": timezone.now().date().isoformat(),
    }
    return render(request, "admin/attendance/quick_session_modal.html", context)


@admin_required
def bulk_mark_present(request, session_id):
    """
    Mark all trainees as present for a session.
    """
    session = get_object_or_404(TrainingSession, id=session_id)
    trainees = Trainee.objects.filter(status="active", archived=False)

    for trainee in trainees:
        Attendance.objects.update_or_create(
            trainee=trainee,
            session=session,
            defaults={
                "date": session.date,
                "status": "present",
            },
        )

    if session.status == "scheduled":
        session.status = "completed"
        session.save()

    messages.success(request, f"All {trainees.count()} trainees marked as present.")

    if request.headers.get("HX-Request"):
        return redirect("session_attendance", session_id=session.id)

    return redirect("attendance_dashboard")


@admin_required
def session_attendance_export(request):
    """
    Export session attendance report as PDF or CSV.

    Query Parameters:
        format: 'pdf' or 'csv' (default: 'pdf')
        session_ids: Comma-separated list of specific session IDs (optional)
        date_from: Start date filter in YYYY-MM-DD format (optional)
        date_to: End date filter in YYYY-MM-DD format (optional)
        sections: Comma-separated list of sections for PDF (header, summary, sessions, details, signature)
    """
    from django.http import HttpResponse
    from core.services.reports import ReportService

    # Get export format
    export_format = request.GET.get("format", "pdf")

    # Parse session IDs if provided
    session_ids_str = request.GET.get("session_ids", "")
    session_ids = None
    if session_ids_str:
        try:
            session_ids = [
                int(sid) for sid in session_ids_str.split(",") if sid.strip()
            ]
        except ValueError:
            session_ids = None

    # Parse date filters
    date_from_str = request.GET.get("date_from", "")
    date_to_str = request.GET.get("date_to", "")

    date_from = None
    date_to = None

    try:
        if date_from_str:
            date_from = datetime.strptime(date_from_str, "%Y-%m-%d").date()
        if date_to_str:
            date_to = datetime.strptime(date_to_str, "%Y-%m-%d").date()
    except ValueError:
        pass

    # Parse sections for PDF
    sections_str = request.GET.get("sections", "")
    sections = None
    if sections_str:
        sections = [s.strip() for s in sections_str.split(",") if s.strip()]

    # Generate report data
    report_service = ReportService()
    report_data = report_service.session_attendance_report(
        session_ids=session_ids,
        date_from=date_from,
        date_to=date_to,
        include_attendance_details=True,
    )

    if export_format == "csv":
        # Generate CSV
        csv_content = report_service.export_csv(report_data, "session_attendance")

        response = HttpResponse(csv_content, content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="session_attendance_report_{date.today().isoformat()}.csv"'
        )
        return response
    else:
        # Generate PDF
        pdf_content = report_service.export_pdf(
            report_data, "session_attendance", sections=sections
        )

        response = HttpResponse(pdf_content, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="session_attendance_report_{date.today().isoformat()}.pdf"'
        )
        return response
