

@admin_required
def belt_promotion_report(request):
    """
    Belt promotion history report view with filters.
    """
    from core.models import Trainee
    from core.services.reports import ReportService
    from datetime import date, timedelta

    report_service = ReportService()

    default_end_date = date.today()
    default_start_date = default_end_date - timedelta(days=365)

    trainees = Trainee.objects.filter(archived=False).order_by(
        "profile__user__first_name", "profile__user__last_name"
    )

    if request.method == "POST":
        trainee_id = request.POST.get("trainee_id", "").strip()
        start_date_str = request.POST.get("start_date", "").strip()
        end_date_str = request.POST.get("end_date", "").strip()
        belt_rank = request.POST.get("belt_rank", "").strip()

        try:
            start_date = (
                date.fromisoformat(start_date_str)
                if start_date_str
                else default_start_date
            )
            end_date = (
                date.fromisoformat(end_date_str) if end_date_str else default_end_date
            )
        except ValueError:
            start_date = default_start_date
            end_date = default_end_date

        trainee_id_int = int(trainee_id) if trainee_id else None

        report_data = report_service.belt_promotion_history_report(
            trainee_id=trainee_id_int,
            start_date=start_date,
            end_date=end_date,
            belt_rank=belt_rank if belt_rank else None,
        )

        export_format = request.POST.get("export_format", "").strip()

        if export_format == "pdf":
            pdf_content = report_service.export_pdf(report_data, "belt_promotion_history")
            response = HttpResponse(pdf_content, content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="belt_promotion_history.pdf"'
            return response
        elif export_format == "csv":
            csv_content = report_service.export_csv(report_data, "belt_promotion_history")
            response = HttpResponse(csv_content, content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="belt_promotion_history.csv"'
            return response

    context = {
        "trainees": trainees,
        "default_start_date": default_start_date.isoformat(),
        "default_end_date": default_end_date.isoformat(),
        "belt_choices": Trainee.BELT_CHOICES,
    }

    return render(request, "admin/reports/belt_promotion.html", context)


@admin_required
def skill_progression_report(request):
    """
    Trainee skill progression report view with filters.
    """
    from core.models import Trainee
    from core.services.reports import ReportService
    from datetime import date, timedelta

    report_service = ReportService()

    default_end_date = date.today()
    default_start_date = default_end_date - timedelta(days=90)

    trainees = Trainee.objects.filter(archived=False).order_by(
        "profile__user__first_name", "profile__user__last_name"
    )

    if request.method == "POST":
        trainee_id = request.POST.get("trainee_id", "").strip()
        start_date_str = request.POST.get("start_date", "").strip()
        end_date_str = request.POST.get("end_date", "").strip()
        include_evaluations = request.POST.get("include_evaluations") == "on"
        include_achievements = request.POST.get("include_achievements") == "on"

        try:
            start_date = (
                date.fromisoformat(start_date_str)
                if start_date_str
                else default_start_date
            )
            end_date = (
                date.fromisoformat(end_date_str) if end_date_str else default_end_date
            )
        except ValueError:
            start_date = default_start_date
            end_date = default_end_date

        trainee_id_int = int(trainee_id) if trainee_id else None

        report_data = report_service.trainee_skill_progression_report(
            trainee_id=trainee_id_int,
            start_date=start_date,
            end_date=end_date,
            include_evaluations=include_evaluations,
            include_achievements=include_achievements,
        )

        export_format = request.POST.get("export_format", "").strip()

        if export_format == "pdf":
            pdf_content = report_service.export_pdf(report_data, "trainee_skill_progression")
            response = HttpResponse(pdf_content, content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="skill_progression.pdf"'
            return response
        elif export_format == "csv":
            csv_content = report_service.export_csv(report_data, "trainee_skill_progression")
            response = HttpResponse(csv_content, content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="skill_progression.csv"'
            return response

    context = {
        "trainees": trainees,
        "default_start_date": default_start_date.isoformat(),
        "default_end_date": default_end_date.isoformat(),
    }

    return render(request, "admin/reports/skill_progression.html", context)


@admin_required
def tournament_participation_report(request):
    """
    Tournament participation report view with filters.
    """
    from core.models import Trainee, Event
    from core.services.reports import ReportService
    from datetime import date, timedelta

    report_service = ReportService()

    default_end_date = date.today()
    default_start_date = default_end_date - timedelta(days=180)

    trainees = Trainee.objects.filter(archived=False).order_by(
        "profile__user__first_name", "profile__user__last_name"
    )
    events = Event.objects.filter(archived=False).order_by("-event_date")

    if request.method == "POST":
        trainee_id = request.POST.get("trainee_id", "").strip()
        event_id = request.POST.get("event_id", "").strip()
        start_date_str = request.POST.get("start_date", "").strip()
        end_date_str = request.POST.get("end_date", "").strip()
        status_filter = request.POST.get("status_filter", "").strip()

        try:
            start_date = (
                date.fromisoformat(start_date_str)
                if start_date_str
                else default_start_date
            )
            end_date = (
                date.fromisoformat(end_date_str) if end_date_str else default_end_date
            )
        except ValueError:
            start_date = default_start_date
            end_date = default_end_date

        trainee_id_int = int(trainee_id) if trainee_id else None
        event_id_int = int(event_id) if event_id else None

        report_data = report_service.tournament_participation_report(
            trainee_id=trainee_id_int,
            event_id=event_id_int,
            start_date=start_date,
            end_date=end_date,
            status_filter=status_filter if status_filter else None,
        )

        export_format = request.POST.get("export_format", "").strip()

        if export_format == "pdf":
            pdf_content = report_service.export_pdf(report_data, "tournament_participation")
            response = HttpResponse(pdf_content, content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="tournament_participation.pdf"'
            return response
        elif export_format == "csv":
            csv_content = report_service.export_csv(report_data, "tournament_participation")
            response = HttpResponse(csv_content, content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="tournament_participation.csv"'
            return response

    context = {
        "trainees": trainees,
        "events": events,
        "default_start_date": default_start_date.isoformat(),
        "default_end_date": default_end_date.isoformat(),
        "status_choices": Event.STATUS_CHOICES,
    }

    return render(request, "admin/reports/tournament_participation.html", context)


@admin_required
def performance_evaluation_report(request):
    """
    Performance evaluation report view with filters.
    """
    from core.models import Trainee, TraineeEvaluation
    from core.services.reports import ReportService
    from datetime import date, timedelta

    report_service = ReportService()

    default_end_date = date.today()
    default_start_date = default_end_date - timedelta(days=90)

    trainees = Trainee.objects.filter(archived=False).order_by(
        "profile__user__first_name", "profile__user__last_name"
    )

    if request.method == "POST":
        trainee_id = request.POST.get("trainee_id", "").strip()
        start_date_str = request.POST.get("start_date", "").strip()
        end_date_str = request.POST.get("end_date", "").strip()
        evaluation_status = request.POST.get("evaluation_status", "").strip()
        min_rating = request.POST.get("min_rating", "").strip()

        try:
            start_date = (
                date.fromisoformat(start_date_str)
                if start_date_str
                else default_start_date
            )
            end_date = (
                date.fromisoformat(end_date_str) if end_date_str else default_end_date
            )
        except ValueError:
            start_date = default_start_date
            end_date = default_end_date

        trainee_id_int = int(trainee_id) if trainee_id else None
        min_rating_int = int(min_rating) if min_rating else None

        report_data = report_service.performance_evaluation_report(
            trainee_id=trainee_id_int,
            start_date=start_date,
            end_date=end_date,
            evaluation_status=evaluation_status if evaluation_status else None,
            min_rating=min_rating_int,
        )

        export_format = request.POST.get("export_format", "").strip()

        if export_format == "pdf":
            pdf_content = report_service.export_pdf(report_data, "performance_evaluation")
            response = HttpResponse(pdf_content, content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="performance_evaluation.pdf"'
            return response
        elif export_format == "csv":
            csv_content = report_service.export_csv(report_data, "performance_evaluation")
            response = HttpResponse(csv_content, content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="performance_evaluation.csv"'
            return response

    context = {
        "trainees": trainees,
        "default_start_date": default_start_date.isoformat(),
        "default_end_date": default_end_date.isoformat(),
        "status_choices": TraineeEvaluation.STATUS_CHOICES,
        "rating_choices": TraineeEvaluation.RATING_CHOICES,
    }

    return render(request, "admin/reports/performance_evaluation.html", context)


@admin_required
def competition_results_report(request):
    """
    Competition results report view with filters.
    """
    from core.models import Trainee, Event, Match
    from core.services.reports import ReportService
    from datetime import date, timedelta

    report_service = ReportService()

    default_end_date = date.today()
    default_start_date = default_end_date - timedelta(days=180)

    trainees = Trainee.objects.filter(archived=False).order_by(
        "profile__user__first_name", "profile__user__last_name"
    )
    events = Event.objects.filter(archived=False).order_by("-event_date")

    if request.method == "POST":
        trainee_id = request.POST.get("trainee_id", "").strip()
        event_id = request.POST.get("event_id", "").strip()
        start_date_str = request.POST.get("start_date", "").strip()
        end_date_str = request.POST.get("end_date", "").strip()
        match_type = request.POST.get("match_type", "").strip()

        try:
            start_date = (
                date.fromisoformat(start_date_str)
                if start_date_str
                else default_start_date
            )
            end_date = (
                date.fromisoformat(end_date_str) if end_date_str else default_end_date
            )
        except ValueError:
            start_date = default_start_date
            end_date = default_end_date

        trainee_id_int = int(trainee_id) if trainee_id else None
        event_id_int = int(event_id) if event_id else None

        report_data = report_service.competition_results_report(
            event_id=event_id_int,
            trainee_id=trainee_id_int,
            start_date=start_date,
            end_date=end_date,
            match_type=match_type if match_type else None,
        )

        export_format = request.POST.get("export_format", "").strip()

        if export_format == "pdf":
            pdf_content = report_service.export_pdf(report_data, "competition_results")
            response = HttpResponse(pdf_content, content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="competition_results.pdf"'
            return response
        elif export_format == "csv":
            csv_content = report_service.export_csv(report_data, "competition_results")
            response = HttpResponse(csv_content, content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="competition_results.csv"'
            return response

    context = {
        "trainees": trainees,
        "events": events,
        "default_start_date": default_start_date.isoformat(),
        "default_end_date": default_end_date.isoformat(),
        "match_type_choices": Match.MATCH_TYPE_CHOICES,
    }

    return render(request, "admin/reports/competition_results.html", context)


@admin_required
def trainee_milestones_report(request):
    """
    Trainee milestones report view with filters.
    """
    from core.models import Trainee, TraineeAchievement
    from core.services.reports import ReportService
    from datetime import date, timedelta

    report_service = ReportService()

    default_end_date = date.today()
    default_start_date = default_end_date - timedelta(days=365)

    trainees = Trainee.objects.filter(archived=False).order_by(
        "profile__user__first_name", "profile__user__last_name"
    )

    if request.method == "POST":
        trainee_id = request.POST.get("trainee_id", "").strip()
        start_date_str = request.POST.get("start_date", "").strip()
        end_date_str = request.POST.get("end_date", "").strip()
        achievement_type = request.POST.get("achievement_type", "").strip()

        try:
            start_date = (
                date.fromisoformat(start_date_str)
                if start_date_str
                else default_start_date
            )
            end_date = (
                date.fromisoformat(end_date_str) if end_date_str else default_end_date
            )
        except ValueError:
            start_date = default_start_date
            end_date = default_end_date

        trainee_id_int = int(trainee_id) if trainee_id else None

        report_data = report_service.trainee_milestones_report(
            trainee_id=trainee_id_int,
            start_date=start_date,
            end_date=end_date,
            achievement_type=achievement_type if achievement_type else None,
        )

        export_format = request.POST.get("export_format", "").strip()

        if export_format == "pdf":
            pdf_content = report_service.export_pdf(report_data, "trainee_milestones")
            response = HttpResponse(pdf_content, content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="trainee_milestones.pdf"'
            return response
        elif export_format == "csv":
            csv_content = report_service.export_csv(report_data, "trainee_milestones")
            response = HttpResponse(csv_content, content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="trainee_milestones.csv"'
            return response

    context = {
        "trainees": trainees,
        "default_start_date": default_start_date.isoformat(),
        "default_end_date": default_end_date.isoformat(),
        "achievement_choices": TraineeAchievement.ACHIEVEMENT_TYPES,
    }

    return render(request, "admin/reports/trainee_milestones.html", context)
