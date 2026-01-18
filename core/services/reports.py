"""
Report Service for the BlackCobra Karate Club System.
Handles report generation for membership, financial, and event reports.
Requirements: 7.1, 7.2, 7.3, 7.4
"""

import csv
import io
from datetime import date
from decimal import Decimal
from typing import Any, Dict

from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
)
import os
from django.conf import settings


class ReportService:
    """
    Service class for generating various reports.
    Requirements: 7.1, 7.2, 7.3, 7.4
    """

    def membership_report(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Generate membership statistics report.
        Requirements: 7.1

        Returns:
            dict containing:
            - total_members: Total number of trainees
            - active_members: Number of active trainees
            - inactive_members: Number of inactive trainees
            - suspended_members: Number of suspended trainees
            - new_members: Number of trainees who joined in date range
            - members_by_belt: Breakdown by belt rank
            - members_by_weight_class: Breakdown by weight class
        """
        from core.models import Trainee

        # Get all trainees
        all_trainees = Trainee.objects.all()

        # Basic counts
        total_members = all_trainees.count()
        active_members = all_trainees.filter(status="active").count()
        inactive_members = all_trainees.filter(status="inactive").count()
        suspended_members = all_trainees.filter(status="suspended").count()

        # New members in date range
        new_members = all_trainees.filter(
            joined_date__gte=start_date, joined_date__lte=end_date
        ).count()

        # Members by belt rank with detailed list
        members_by_belt = list(
            all_trainees.values("belt_rank")
            .annotate(count=Count("id"))
            .order_by("belt_rank")
        )

        # Get detailed member list by belt rank with names
        belt_rank_details = {}
        for trainee in all_trainees.select_related("profile__user").order_by(
            "belt_rank", "profile__user__first_name"
        ):
            belt = trainee.belt_rank or "Unknown"
            if belt not in belt_rank_details:
                belt_rank_details[belt] = []
            name = f"{trainee.profile.user.first_name} {trainee.profile.user.last_name}"
            belt_rank_details[belt].append(
                {
                    "name": name,
                    "status": trainee.status,
                    "weight_class": trainee.weight_class or "N/A",
                }
            )

        # Members by weight class
        members_by_weight_class = list(
            all_trainees.values("weight_class")
            .annotate(count=Count("id"))
            .order_by("weight_class")
        )

        return {
            "report_type": "membership",
            "start_date": start_date,
            "end_date": end_date,
            "total_members": total_members,
            "active_members": active_members,
            "inactive_members": inactive_members,
            "suspended_members": suspended_members,
            "new_members": new_members,
            "members_by_belt": members_by_belt,
            "belt_rank_details": belt_rank_details,
            "members_by_weight_class": members_by_weight_class,
        }

    def financial_report(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Generate financial summary report.
        Requirements: 7.2, 7.4

        Returns:
            dict containing:
            - total_revenue: Total completed payments
            - pending_amount: Total pending payments
            - overdue_amount: Total overdue payments
            - payments_by_type: Breakdown by payment type
            - payments_by_month: Monthly breakdown
            - outstanding_balances: List of trainees with pending/overdue payments
        """
        from core.models import Payment
        from django.utils import timezone
        from datetime import datetime

        # Convert dates to datetime for filtering
        start_datetime = timezone.make_aware(
            datetime.combine(start_date, datetime.min.time())
        )
        end_datetime = timezone.make_aware(
            datetime.combine(end_date, datetime.max.time())
        )

        # Get payments in date range
        payments_in_range = Payment.objects.filter(
            payment_date__gte=start_datetime, payment_date__lte=end_datetime
        )

        # Total revenue (completed payments)
        total_revenue = payments_in_range.filter(status="completed").aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

        # Pending amount
        pending_amount = payments_in_range.filter(status="pending").aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

        # Overdue amount
        overdue_amount = payments_in_range.filter(status="overdue").aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

        # Payments by type
        payments_by_type = list(
            payments_in_range.filter(status="completed")
            .values("payment_type")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("payment_type")
        )

        # Payments by month
        payments_by_month = list(
            payments_in_range.filter(status="completed")
            .annotate(month=TruncMonth("payment_date"))
            .values("month")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("month")
        )

        # Outstanding balances (trainees with pending/overdue payments)
        outstanding_balances = list(
            Payment.objects.filter(status__in=["pending", "overdue"])
            .values(
                "trainee__id",
                "trainee__profile__user__first_name",
                "trainee__profile__user__last_name",
            )
            .annotate(total_outstanding=Sum("amount"))
            .order_by("-total_outstanding")[:20]
        )

        return {
            "report_type": "financial",
            "start_date": start_date,
            "end_date": end_date,
            "total_revenue": total_revenue,
            "pending_amount": pending_amount,
            "overdue_amount": overdue_amount,
            "payments_by_type": payments_by_type,
            "payments_by_month": payments_by_month,
            "outstanding_balances": outstanding_balances,
        }

    def event_report(self, event_id: int) -> Dict[str, Any]:
        """
        Generate event participation report.
        Requirements: 7.1, 7.2

        Returns:
            dict containing:
            - event: Event details
            - total_registrations: Number of registrations
            - participants_by_belt: Breakdown by belt rank with trainee names
            - participants_by_weight_class: Breakdown by weight class with trainee names
            - matches_summary: Match statistics
            - all_participants: List of all trainees with their details
        """
        from core.models import Event, EventRegistration, Match, MatchResult

        event = Event.objects.get(id=event_id)

        # Get registrations
        registrations = EventRegistration.objects.filter(
            event=event, status="registered"
        ).select_related("trainee", "trainee__profile", "trainee__profile__user")

        total_registrations = registrations.count()

        # Get all participants with trainee names
        all_participants = []
        for reg in registrations:
            trainee = reg.trainee
            user = trainee.profile.user
            all_participants.append(
                {
                    "id": trainee.id,
                    "name": f"{user.first_name} {user.last_name}".strip()
                    or user.username,
                    "belt_rank": trainee.belt_rank,
                    "weight_class": trainee.weight_class,
                }
            )

        # Participants by belt rank with trainee names
        participants_by_belt = {}
        for participant in all_participants:
            belt = participant["belt_rank"] or "Unknown"
            if belt not in participants_by_belt:
                participants_by_belt[belt] = {"count": 0, "names": []}
            participants_by_belt[belt]["count"] += 1
            participants_by_belt[belt]["names"].append(participant["name"])

        # Convert to list format for template
        participants_by_belt_list = [
            {
                "belt_rank": belt,
                "count": data["count"],
                "names": ", ".join(sorted(data["names"])),
            }
            for belt, data in sorted(participants_by_belt.items())
        ]

        # Participants by weight class with trainee names
        participants_by_weight_class = {}
        for participant in all_participants:
            weight = participant["weight_class"] or "Unknown"
            if weight not in participants_by_weight_class:
                participants_by_weight_class[weight] = {"count": 0, "names": []}
            participants_by_weight_class[weight]["count"] += 1
            participants_by_weight_class[weight]["names"].append(participant["name"])

        # Convert to list format for template
        participants_by_weight_class_list = [
            {
                "weight_class": weight,
                "count": data["count"],
                "names": ", ".join(sorted(data["names"])),
            }
            for weight, data in sorted(participants_by_weight_class.items())
        ]

        # Match statistics
        matches = Match.objects.filter(event=event)
        total_matches = matches.count()
        completed_matches = matches.filter(status="completed").count()
        scheduled_matches = matches.filter(status="scheduled").count()

        return {
            "report_type": "event",
            "event": {
                "id": event.id,
                "name": event.name,
                "event_date": event.event_date,
                "location": event.location,
                "status": event.status,
                "max_participants": event.max_participants,
            },
            "total_registrations": total_registrations,
            "participants_by_belt": participants_by_belt_list,
            "participants_by_weight_class": participants_by_weight_class_list,
            "matches_summary": {
                "total": total_matches,
                "completed": completed_matches,
                "scheduled": scheduled_matches,
            },
            "all_participants": all_participants,
        }

    def export_pdf(
        self, report_data: Dict[str, Any], report_type: str, sections: list = None
    ) -> bytes:
        """
        Export report as PDF.
        Supports: membership, financial, event, trainee_list
        Requirements: 7.3

        Args:
            report_data: The report data dictionary
            report_type: Type of report ('membership', 'financial', 'event', 'trainee_list')
            sections: Optional list of sections to include for trainee_list
                      (valid: 'header', 'summary', 'details', 'signature')

        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch
        )
        styles = getSampleStyleSheet()
        elements = []

        # Title style
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#1a1a1a"),
            spaceAfter=12,
            fontName="Helvetica-Bold",
        )

        if report_type == "membership":
            elements = self._build_membership_pdf(report_data, styles, title_style)
        elif report_type == "financial":
            elements = self._build_financial_pdf(report_data, styles, title_style)
        elif report_type == "event":
            elements = self._build_event_pdf(report_data, styles, title_style)
        elif report_type == "trainee_list":
            elements = self._build_trainee_list_pdf(
                report_data, styles, title_style, sections=sections
            )
        elif report_type == "session_attendance":
            elements = self._build_session_attendance_pdf(
                report_data, styles, title_style, sections=sections
            )
        elif report_type == "belt_promotion_history":
            elements = self._build_belt_promotion_pdf(report_data, styles, title_style)
        elif report_type == "trainee_skill_progression":
            elements = self._build_skill_progression_pdf(
                report_data, styles, title_style
            )
        elif report_type == "tournament_participation":
            elements = self._build_tournament_participation_pdf(
                report_data, styles, title_style
            )
        elif report_type == "performance_evaluation":
            elements = self._build_performance_evaluation_pdf(
                report_data, styles, title_style
            )
        elif report_type == "competition_results":
            elements = self._build_competition_results_pdf(
                report_data, styles, title_style
            )
        elif report_type == "trainee_milestones":
            elements = self._build_trainee_milestones_pdf(
                report_data, styles, title_style
            )

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    def _build_membership_pdf(self, data: dict, styles, title_style) -> list:
        """Build PDF elements for membership report."""
        elements = []

        # Add header with logos and organization name
        logo_path = os.path.join(
            settings.BASE_DIR, "core", "static", "images", "black_cobra_logo.jpg"
        )
        judo_logo_path = os.path.join(
            settings.BASE_DIR, "core", "static", "images", "judo_logo.png"
        )

        # Create header table with left logo, center text, right logo
        header_data = [[None, None, None]]

        # Left logo
        if os.path.exists(logo_path):
            left_logo = Image(logo_path, width=1 * inch, height=1 * inch)
            header_data[0][0] = left_logo

        # Center text
        header_style = ParagraphStyle(
            "OrgHeader",
            parent=styles["Heading2"],
            fontSize=13,
            textColor=colors.black,
            alignment=1,  # Center alignment
            leading=16,
        )
        center_text = Paragraph(
            "BLACK COBRA JUDO<br/>KARATE AIKIDO<br/>ASSOCIATION OF THE<br/>PHILIPPINES",
            header_style,
        )
        header_data[0][1] = center_text

        # Right logo
        if os.path.exists(judo_logo_path):
            right_logo = Image(judo_logo_path, width=1 * inch, height=1 * inch)
            header_data[0][2] = right_logo
        else:
            # Placeholder if judo logo doesn't exist
            header_data[0][2] = Paragraph("Judo<br/>Logo", styles["Normal"])

        header_table = Table(
            header_data, colWidths=[1.2 * inch, 3.6 * inch, 1.2 * inch]
        )
        header_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (0, -1), 0),
                    ("RIGHTPADDING", (-1, 0), (-1, -1), 0),
                ]
            )
        )
        elements.append(header_table)
        elements.append(Spacer(1, 15))

        # Title
        elements.append(Paragraph("Membership Report", title_style))
        elements.append(
            Paragraph(
                f"Period: {data['start_date']} to {data['end_date']}", styles["Normal"]
            )
        )
        elements.append(Spacer(1, 20))

        # Summary table
        summary_data = [
            ["Metric", "Count"],
            ["Total Members", str(data["total_members"])],
            ["Active Members", str(data["active_members"])],
            ["Inactive Members", str(data["inactive_members"])],
            ["Suspended Members", str(data["suspended_members"])],
            ["New Members (Period)", str(data["new_members"])],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        # Belt rank breakdown with trainee names
        if data.get("belt_rank_details"):
            elements.append(
                Paragraph("Members by Belt Rank - Detailed", styles["Heading2"])
            )
            elements.append(Spacer(1, 10))

            for belt_rank in sorted(data["belt_rank_details"].keys()):
                members = data["belt_rank_details"][belt_rank]

                # Belt rank section header
                elements.append(
                    Paragraph(
                        f"{belt_rank.title()} ({len(members)})", styles["Heading3"]
                    )
                )

                # Members list for this belt
                member_data = [["Name", "Status", "Weight Class"]]
                for member in members:
                    member_data.append(
                        [
                            member["name"],
                            member["status"].title(),
                            member["weight_class"],
                        ]
                    )

                member_table = Table(
                    member_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch]
                )
                member_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                            ("ALIGN", (1, 0), (2, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 10),
                            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                            (
                                "ROWBACKGROUNDS",
                                (0, 1),
                                (-1, -1),
                                [colors.white, colors.lightgrey],
                            ),
                        ]
                    )
                )
                elements.append(member_table)
                elements.append(Spacer(1, 10))

        # Add signatory section at the end
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("Prepared By:", styles["Normal"]))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("_" * 40, styles["Normal"]))
        elements.append(Paragraph("INSTRUCTOR", styles["Normal"]))

        return elements

    def _build_financial_pdf(self, data: dict, styles, title_style) -> list:
        """Build PDF elements for financial report."""
        elements = []

        # Add header with logos and organization name
        logo_path = os.path.join(
            settings.BASE_DIR, "core", "static", "images", "black_cobra_logo.jpg"
        )
        judo_logo_path = os.path.join(
            settings.BASE_DIR, "core", "static", "images", "judo_logo.png"
        )

        # Create header table with left logo, center text, right logo
        header_data = [[None, None, None]]

        # Left logo
        if os.path.exists(logo_path):
            left_logo = Image(logo_path, width=1 * inch, height=1 * inch)
            header_data[0][0] = left_logo

        # Center text
        header_style = ParagraphStyle(
            "OrgHeader",
            parent=styles["Heading2"],
            fontSize=13,
            textColor=colors.black,
            alignment=1,  # Center alignment
            leading=16,
        )
        center_text = Paragraph(
            "BLACK COBRA JUDO<br/>KARATE AIKIDO<br/>ASSOCIATION OF THE<br/>PHILIPPINES",
            header_style,
        )
        header_data[0][1] = center_text

        # Right logo
        if os.path.exists(judo_logo_path):
            right_logo = Image(judo_logo_path, width=1 * inch, height=1 * inch)
            header_data[0][2] = right_logo
        else:
            # Placeholder if judo logo doesn't exist
            header_data[0][2] = Paragraph("Judo<br/>Logo", styles["Normal"])

        header_table = Table(
            header_data, colWidths=[1.2 * inch, 3.6 * inch, 1.2 * inch]
        )
        header_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (0, -1), 0),
                    ("RIGHTPADDING", (-1, 0), (-1, -1), 0),
                ]
            )
        )
        elements.append(header_table)
        elements.append(Spacer(1, 15))

        # Title
        elements.append(Paragraph("Financial Report", title_style))
        elements.append(
            Paragraph(
                f"Period: {data['start_date']} to {data['end_date']}", styles["Normal"]
            )
        )
        elements.append(Spacer(1, 20))

        # Summary table
        summary_data = [
            ["Metric", "Amount"],
            ["Total Revenue", f"${data['total_revenue']:.2f}"],
            ["Pending Payments", f"${data['pending_amount']:.2f}"],
            ["Overdue Payments", f"${data['overdue_amount']:.2f}"],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        # Payments by type
        if data["payments_by_type"]:
            elements.append(Paragraph("Revenue by Payment Type", styles["Heading2"]))
            type_data = [["Payment Type", "Count", "Total"]]
            for item in data["payments_by_type"]:
                type_data.append(
                    [
                        item["payment_type"].title(),
                        str(item["count"]),
                        f"${item['total']:.2f}",
                    ]
                )

            type_table = Table(type_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch])
            type_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            elements.append(type_table)
            elements.append(Spacer(1, 20))

        # Outstanding balances
        if data["outstanding_balances"]:
            elements.append(Paragraph("Outstanding Balances", styles["Heading2"]))
            balance_data = [["Trainee", "Outstanding Amount"]]
            for item in data["outstanding_balances"]:
                name = f"{item['trainee__profile__user__first_name']} {item['trainee__profile__user__last_name']}"
                balance_data.append([name, f"${item['total_outstanding']:.2f}"])

            balance_table = Table(balance_data, colWidths=[3 * inch, 2 * inch])
            balance_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            elements.append(balance_table)

        # Add signatory section at the end
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("Prepared By:", styles["Normal"]))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("_" * 40, styles["Normal"]))
        elements.append(Paragraph("INSTRUCTOR", styles["Normal"]))

        return elements

    def _build_event_pdf(self, data: dict, styles, title_style) -> list:
        """Build PDF elements for event report."""
        elements = []

        # Add header with logos and organization name
        logo_path = os.path.join(
            settings.BASE_DIR, "core", "static", "images", "black_cobra_logo.jpg"
        )
        judo_logo_path = os.path.join(
            settings.BASE_DIR, "core", "static", "images", "judo_logo.png"
        )

        # Create header table with left logo, center text, right logo
        header_data = [[None, None, None]]

        # Left logo
        if os.path.exists(logo_path):
            left_logo = Image(logo_path, width=1 * inch, height=1 * inch)
            header_data[0][0] = left_logo

        # Center text
        header_style = ParagraphStyle(
            "OrgHeader",
            parent=styles["Heading2"],
            fontSize=13,
            textColor=colors.black,
            alignment=1,  # Center alignment
            leading=16,
        )
        center_text = Paragraph(
            "BLACK COBRA JUDO<br/>KARATE AIKIDO<br/>ASSOCIATION OF THE<br/>PHILIPPINES",
            header_style,
        )
        header_data[0][1] = center_text

        # Right logo
        if os.path.exists(judo_logo_path):
            right_logo = Image(judo_logo_path, width=1 * inch, height=1 * inch)
            header_data[0][2] = right_logo
        else:
            # Placeholder if judo logo doesn't exist
            header_data[0][2] = Paragraph("Judo<br/>Logo", styles["Normal"])

        header_table = Table(
            header_data, colWidths=[1.2 * inch, 3.6 * inch, 1.2 * inch]
        )
        header_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (0, -1), 0),
                    ("RIGHTPADDING", (-1, 0), (-1, -1), 0),
                ]
            )
        )
        elements.append(header_table)
        elements.append(Spacer(1, 15))

        event = data["event"]

        # Title
        elements.append(Paragraph(f"Event Report: {event['name']}", title_style))
        elements.append(
            Paragraph(
                f"Date: {event['event_date']} | Location: {event['location']}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 20))

        # Summary table
        summary_data = [
            ["Metric", "Value"],
            ["Status", event["status"].title()],
            ["Max Participants", str(event["max_participants"])],
            ["Total Registrations", str(data["total_registrations"])],
            ["Total Matches", str(data["matches_summary"]["total"])],
            ["Completed Matches", str(data["matches_summary"]["completed"])],
            ["Scheduled Matches", str(data["matches_summary"]["scheduled"])],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        # Participants by belt
        if data["participants_by_belt"]:
            elements.append(Paragraph("Participants by Belt Rank", styles["Heading2"]))
            belt_data = [["Belt Rank", "Count", "Trainees"]]
            for item in data["participants_by_belt"]:
                belt_data.append(
                    [
                        item.get("belt_rank", "Unknown").title()
                        if item.get("belt_rank")
                        else "Unknown",
                        str(item["count"]),
                        item.get("names", ""),
                    ]
                )

            belt_table = Table(belt_data, colWidths=[1.5 * inch, 1 * inch, 2.5 * inch])
            belt_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (1, -1), "CENTER"),
                        ("ALIGN", (2, 0), (2, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            elements.append(belt_table)

        # Participants by weight class
        if data["participants_by_weight_class"]:
            elements.append(Spacer(1, 20))
            elements.append(
                Paragraph("Participants by Weight Class", styles["Heading2"])
            )
            weight_data = [["Weight Class", "Count", "Trainees"]]
            for item in data["participants_by_weight_class"]:
                weight_data.append(
                    [
                        item.get("weight_class", "Unknown"),
                        str(item["count"]),
                        item.get("names", ""),
                    ]
                )

            weight_table = Table(
                weight_data, colWidths=[1.5 * inch, 1 * inch, 2.5 * inch]
            )
            weight_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (1, -1), "CENTER"),
                        ("ALIGN", (2, 0), (2, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            elements.append(weight_table)

        # Add signatory section at the end
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("Prepared By:", styles["Normal"]))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("_" * 40, styles["Normal"]))
        elements.append(Paragraph("INSTRUCTOR", styles["Normal"]))

        return elements

    def export_csv(self, report_data: Dict[str, Any], report_type: str) -> str:
        """
        Export report as CSV.
        Supports: membership, financial, event, trainee_list
        Requirements: 7.3

        Args:
            report_data: The report data dictionary
            report_type: Type of report ('membership', 'financial', 'event', 'trainee_list')

        Returns:
            CSV content as string
        """
        output = io.StringIO()

        if report_type == "membership":
            self._build_membership_csv(output, report_data)
        elif report_type == "financial":
            self._build_financial_csv(output, report_data)
        elif report_type == "event":
            self._build_event_csv(output, report_data)
        elif report_type == "trainee_list":
            self._build_trainee_list_csv(output, report_data)
        elif report_type == "session_attendance":
            self._build_session_attendance_csv(output, report_data)
        elif report_type == "belt_promotion_history":
            self._build_belt_promotion_csv(output, report_data)
        elif report_type == "trainee_skill_progression":
            self._build_skill_progression_csv(output, report_data)
        elif report_type == "tournament_participation":
            self._build_tournament_participation_csv(output, report_data)
        elif report_type == "performance_evaluation":
            self._build_performance_evaluation_csv(output, report_data)
        elif report_type == "competition_results":
            self._build_competition_results_csv(output, report_data)
        elif report_type == "trainee_milestones":
            self._build_trainee_milestones_csv(output, report_data)

        return output.getvalue()

    def _build_membership_csv(self, output: io.StringIO, data: dict) -> None:
        """Build CSV content for membership report."""
        writer = csv.writer(output)

        # Header
        writer.writerow(["Membership Report"])
        writer.writerow([f"Period: {data['start_date']} to {data['end_date']}"])
        writer.writerow([])

        # Summary
        writer.writerow(["Summary"])
        writer.writerow(["Metric", "Count"])
        writer.writerow(["Total Members", data["total_members"]])
        writer.writerow(["Active Members", data["active_members"]])
        writer.writerow(["Inactive Members", data["inactive_members"]])
        writer.writerow(["Suspended Members", data["suspended_members"]])
        writer.writerow(["New Members (Period)", data["new_members"]])
        writer.writerow([])

        # Belt breakdown with trainee names
        writer.writerow(["Members by Belt Rank - Detailed"])
        writer.writerow([])

        if data.get("belt_rank_details"):
            for belt_rank in sorted(data["belt_rank_details"].keys()):
                members = data["belt_rank_details"][belt_rank]
                writer.writerow([f"{belt_rank.title()} ({len(members)})"])
                writer.writerow(["Name", "Status", "Weight Class"])
                for member in members:
                    writer.writerow(
                        [
                            member["name"],
                            member["status"].title(),
                            member["weight_class"],
                        ]
                    )
                writer.writerow([])
        else:
            # Fallback to summary if detailed list not available
            writer.writerow(["Belt Rank", "Count"])
            for item in data["members_by_belt"]:
                writer.writerow([item["belt_rank"].title(), item["count"]])
            writer.writerow([])

        # Weight class breakdown
        writer.writerow(["Members by Weight Class"])
        writer.writerow(["Weight Class", "Count"])
        for item in data["members_by_weight_class"]:
            writer.writerow([item["weight_class"], item["count"]])

    def _build_financial_csv(self, output: io.StringIO, data: dict) -> None:
        """Build CSV content for financial report."""
        writer = csv.writer(output)

        # Header
        writer.writerow(["Financial Report"])
        writer.writerow([f"Period: {data['start_date']} to {data['end_date']}"])
        writer.writerow([])

        # Summary
        writer.writerow(["Summary"])
        writer.writerow(["Metric", "Amount"])
        writer.writerow(["Total Revenue", f"${data['total_revenue']:.2f}"])
        writer.writerow(["Pending Payments", f"${data['pending_amount']:.2f}"])
        writer.writerow(["Overdue Payments", f"${data['overdue_amount']:.2f}"])
        writer.writerow([])

        # Payments by type
        writer.writerow(["Revenue by Payment Type"])
        writer.writerow(["Payment Type", "Count", "Total"])
        for item in data["payments_by_type"]:
            writer.writerow(
                [item["payment_type"].title(), item["count"], f"${item['total']:.2f}"]
            )
        writer.writerow([])

        # Outstanding balances
        writer.writerow(["Outstanding Balances"])
        writer.writerow(["Trainee", "Outstanding Amount"])
        for item in data["outstanding_balances"]:
            name = f"{item['trainee__profile__user__first_name']} {item['trainee__profile__user__last_name']}"
            writer.writerow([name, f"${item['total_outstanding']:.2f}"])

    def _build_event_csv(self, output: io.StringIO, data: dict) -> None:
        """Build CSV content for event report."""
        writer = csv.writer(output)
        event = data["event"]

        # Header
        writer.writerow(["Event Report"])
        writer.writerow([f"Event: {event['name']}"])
        writer.writerow([f"Date: {event['event_date']}"])
        writer.writerow([f"Location: {event['location']}"])
        writer.writerow([])

        # Summary
        writer.writerow(["Summary"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Status", event["status"].title()])
        writer.writerow(["Max Participants", event["max_participants"]])
        writer.writerow(["Total Registrations", data["total_registrations"]])
        writer.writerow(["Total Matches", data["matches_summary"]["total"]])
        writer.writerow(["Completed Matches", data["matches_summary"]["completed"]])
        writer.writerow(["Scheduled Matches", data["matches_summary"]["scheduled"]])
        writer.writerow([])

        # Participants by belt
        writer.writerow(["Participants by Belt Rank"])
        writer.writerow(["Belt Rank", "Count", "Trainees"])
        for item in data["participants_by_belt"]:
            belt = (
                item.get("belt_rank", "Unknown").title()
                if item.get("belt_rank")
                else "Unknown"
            )
            names = item.get("names", "")
            writer.writerow([belt, item["count"], names])
        writer.writerow([])

        # Participants by weight class
        writer.writerow(["Participants by Weight Class"])
        writer.writerow(["Weight Class", "Count", "Trainees"])
        for item in data["participants_by_weight_class"]:
            weight = item.get("weight_class", "Unknown")
            names = item.get("names", "")
            writer.writerow([weight, item["count"], names])
        writer.writerow([])

        # All participants detailed list
        if data.get("all_participants"):
            writer.writerow(["All Participants - Detailed List"])
            writer.writerow(["Name", "Belt Rank", "Weight Class"])
            for participant in sorted(
                data["all_participants"], key=lambda x: x["name"]
            ):
                writer.writerow(
                    [
                        participant["name"],
                        participant["belt_rank"] or "Unknown",
                        participant["weight_class"] or "Unknown",
                    ]
                )

    def trainee_report(
        self,
        status_filter: str = None,
        belt_filter: str = None,
        trainee_ids: list = None,
        export_format: str = "by_user",
    ) -> Dict[str, Any]:
        """
        Generate trainee listing report with optional filters.

        Args:
            status_filter: Filter by status (active, inactive, suspended)
            belt_filter: Filter by belt rank
            trainee_ids: List of specific trainee IDs to export
            export_format: 'by_user' (list format) or 'by_belt' (grouped by belt)

        Returns:
            dict containing trainee listing data
        """
        from core.models import Trainee

        trainees = Trainee.objects.select_related("profile__user").filter(
            archived=False
        )

        # Apply specific trainee ID filter if provided
        if trainee_ids:
            trainees = trainees.filter(id__in=trainee_ids)

        # Apply filters
        if status_filter:
            trainees = trainees.filter(status=status_filter)
        if belt_filter:
            trainees = trainees.filter(belt_rank=belt_filter)

        # Order by name
        trainees = trainees.order_by(
            "profile__user__first_name", "profile__user__last_name"
        )

        # Build trainee list with details
        trainee_list = []
        for trainee in trainees:
            user = trainee.profile.user
            trainee_list.append(
                {
                    "id": trainee.id,
                    "name": f"{user.first_name} {user.last_name}".strip()
                    or user.username,
                    "email": user.email,
                    "belt_rank": trainee.belt_rank or "Not Set",
                    "weight_class": trainee.weight_class or "Not Set",
                    "age": trainee.age
                    if hasattr(trainee, "age") and trainee.age is not None
                    else "N/A",
                    "status": trainee.status.title(),
                    "join_date": trainee.joined_date,
                }
            )

        # Group by belt rank if requested
        trainees_by_belt = {}
        if export_format == "by_belt":
            for trainee in trainee_list:
                belt = trainee["belt_rank"]
                if belt not in trainees_by_belt:
                    trainees_by_belt[belt] = []
                trainees_by_belt[belt].append(trainee)

        # Summary statistics
        return {
            "report_type": "trainee_list",
            "export_format": export_format,
            "generated_date": date.today(),
            "total_trainees": len(trainee_list),
            "active_trainees": sum(
                1 for t in trainee_list if "active" in t["status"].lower()
            ),
            "inactive_trainees": sum(
                1 for t in trainee_list if "inactive" in t["status"].lower()
            ),
            "suspended_trainees": sum(
                1 for t in trainee_list if "suspended" in t["status"].lower()
            ),
            "status_filter": status_filter or "All",
            "belt_filter": belt_filter or "All",
            "trainees": trainee_list,
            "trainees_by_belt": trainees_by_belt,
        }

    def _build_trainee_list_pdf(
        self, data: dict, styles, title_style, sections: list = None
    ) -> list:
        """Build PDF elements for trainee list report."""
        export_format = data.get("export_format", "by_user")

        if export_format == "by_belt":
            return self._build_trainee_by_belt_pdf(
                data, styles, title_style, sections=sections
            )
        else:
            return self._build_trainee_by_user_pdf(
                data, styles, title_style, sections=sections
            )

    def _build_trainee_by_user_pdf(
        self, data: dict, styles, title_style, sections: list = None
    ) -> list:
        """Build PDF elements for trainee list organized by user."""
        elements = []

        # Default to all sections if none specified
        if sections is None:
            sections = ["header", "summary", "details", "signature"]

        # Header section
        if "header" in sections:
            elements.append(Paragraph("BlackCobra Karate Club", title_style))
            elements.append(Paragraph("Trainee Management Report", styles["Heading2"]))
            elements.append(
                Paragraph(
                    f"Generated: {data['generated_date'].strftime('%B %d, %Y')} | "
                    f"Status Filter: {data['status_filter']} | Belt Filter: {data['belt_filter']}",
                    styles["Normal"],
                )
            )
            elements.append(Spacer(1, 20))

        # Summary statistics section
        if "summary" in sections:
            summary_data = [
                ["Metric", "Count"],
                ["Total Trainees", str(data["total_trainees"])],
                ["Active", str(data["active_trainees"])],
                ["Inactive", str(data["inactive_trainees"])],
                ["Suspended", str(data["suspended_trainees"])],
            ]

            summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
            summary_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dc2626")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 11),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f3f4f6")),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ]
                )
            )
            elements.append(summary_table)
            elements.append(Spacer(1, 20))

        # Trainee details section
        if "details" in sections:
            if data["trainees"]:
                elements.append(
                    Paragraph("Trainee Details (By User)", styles["Heading3"])
                )
                elements.append(Spacer(1, 10))

                table_data = [
                    [
                        "Name",
                        "Email",
                        "Belt Rank",
                        "Weight Class",
                        "Age",
                        "Status",
                        "Joined",
                    ]
                ]

                for trainee in data["trainees"]:
                    join_date = (
                        trainee["join_date"].strftime("%m/%d/%Y")
                        if trainee["join_date"]
                        else "N/A"
                    )
                    table_data.append(
                        [
                            trainee["name"],
                            trainee["email"],
                            trainee["belt_rank"],
                            trainee["weight_class"],
                            str(trainee["age"]),
                            trainee["status"],
                            join_date,
                        ]
                    )

                # Adjust column widths for 7 columns
                trainee_table = Table(
                    table_data,
                    colWidths=[
                        1.2 * inch,
                        1.3 * inch,
                        1 * inch,
                        1 * inch,
                        0.6 * inch,
                        0.9 * inch,
                        0.8 * inch,
                    ],
                )
                trainee_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("ALIGN", (0, 0), (1, -1), "LEFT"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 9),
                            ("FONTSIZE", (0, 1), (-1, -1), 8),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            (
                                "ROWBACKGROUNDS",
                                (0, 1),
                                (-1, -1),
                                [colors.white, colors.HexColor("#f9fafb")],
                            ),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 5),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                        ]
                    )
                )
                elements.append(trainee_table)
            else:
                elements.append(
                    Paragraph(
                        "No trainees found matching the selected filters.",
                        styles["Normal"],
                    )
                )

        # Signature/Footer section
        if "signature" in sections:
            elements.append(Spacer(1, 40))
            elements.append(Paragraph("_" * 80, styles["Normal"]))
            elements.append(Paragraph("Authorized By:", styles["Normal"]))
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("_" * 40, styles["Normal"]))
            elements.append(Paragraph("Admin Signature", styles["Normal"]))

        return elements

    def _build_trainee_by_belt_pdf(
        self, data: dict, styles, title_style, sections: list = None
    ) -> list:
        """Build PDF elements for trainee list organized by belt rank."""
        elements = []

        # Default to all sections if none specified
        if sections is None:
            sections = ["header", "summary", "details", "signature"]

        # Header section
        if "header" in sections:
            elements.append(Paragraph("BlackCobra Karate Club", title_style))
            elements.append(
                Paragraph(
                    "Trainee Management Report (By Belt Rank)", styles["Heading2"]
                )
            )
            elements.append(
                Paragraph(
                    f"Generated: {data['generated_date'].strftime('%B %d, %Y')} | "
                    f"Status Filter: {data['status_filter']} | Belt Filter: {data['belt_filter']}",
                    styles["Normal"],
                )
            )
            elements.append(Spacer(1, 20))

        # Summary statistics section
        if "summary" in sections:
            summary_data = [
                ["Metric", "Count"],
                ["Total Trainees", str(data["total_trainees"])],
                ["Active", str(data["active_trainees"])],
                ["Inactive", str(data["inactive_trainees"])],
                ["Suspended", str(data["suspended_trainees"])],
            ]

            summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
            summary_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dc2626")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 11),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f3f4f6")),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ]
                )
            )
            elements.append(summary_table)
            elements.append(Spacer(1, 20))

        # Details section - trainees grouped by belt rank
        if "details" in sections:
            # Belt rank order for proper sorting
            belt_order = [
                "white",
                "yellow",
                "orange",
                "green",
                "blue",
                "brown",
                "black",
                "master_degree",
            ]

            # Trainee list grouped by belt rank
            trainees_by_belt = data.get("trainees_by_belt", {})

            if trainees_by_belt:
                elements.append(Paragraph("Trainees by Belt Rank", styles["Heading3"]))
                elements.append(Spacer(1, 10))

                # Sort belts by defined order
                sorted_belts = sorted(
                    trainees_by_belt.keys(),
                    key=lambda x: belt_order.index(x.lower().replace(" ", "_"))
                    if x.lower().replace(" ", "_") in belt_order
                    else len(belt_order),
                )

                for belt_rank in sorted_belts:
                    belt_trainees = trainees_by_belt[belt_rank]

                    # Belt rank heading
                    elements.append(
                        Paragraph(
                            f"{belt_rank.title() if belt_rank != 'master_degree' else 'Master Degree'} Belt ({len(belt_trainees)} trainees)",
                            styles["Heading4"],
                        )
                    )
                    elements.append(Spacer(1, 8))

                    # Create table for this belt rank
                    table_data = [
                        ["Name", "Email", "Weight Class", "Age", "Status", "Joined"]
                    ]

                    for trainee in sorted(belt_trainees, key=lambda x: x["name"]):
                        join_date = (
                            trainee["join_date"].strftime("%m/%d/%Y")
                            if trainee["join_date"]
                            else "N/A"
                        )
                        table_data.append(
                            [
                                trainee["name"],
                                trainee["email"],
                                trainee["weight_class"],
                                str(trainee["age"]),
                                trainee["status"],
                                join_date,
                            ]
                        )

                    belt_table = Table(
                        table_data,
                        colWidths=[
                            1.3 * inch,
                            1.4 * inch,
                            1.1 * inch,
                            0.7 * inch,
                            0.9 * inch,
                            0.8 * inch,
                        ],
                    )
                    belt_table.setStyle(
                        TableStyle(
                            [
                                (
                                    "BACKGROUND",
                                    (0, 0),
                                    (-1, 0),
                                    colors.HexColor("#374151"),
                                ),
                                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                ("ALIGN", (0, 0), (1, -1), "LEFT"),
                                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                                ("FONTSIZE", (0, 0), (-1, 0), 8),
                                ("FONTSIZE", (0, 1), (-1, -1), 7),
                                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                                (
                                    "ROWBACKGROUNDS",
                                    (0, 1),
                                    (-1, -1),
                                    [colors.white, colors.HexColor("#f9fafb")],
                                ),
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                            ]
                        )
                    )
                    elements.append(belt_table)
                    elements.append(Spacer(1, 15))
            else:
                elements.append(
                    Paragraph(
                        "No trainees found matching the selected filters.",
                        styles["Normal"],
                    )
                )

        # Signature/Footer section
        if "signature" in sections:
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("_" * 80, styles["Normal"]))
            elements.append(Paragraph("Authorized By:", styles["Normal"]))
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("_" * 40, styles["Normal"]))
            elements.append(Paragraph("Admin Signature", styles["Normal"]))

        return elements

    def _build_trainee_list_csv(self, output: io.StringIO, data: dict) -> None:
        """Build CSV content for trainee list report."""
        export_format = data.get("export_format", "by_user")

        if export_format == "by_belt":
            self._build_trainee_by_belt_csv(output, data)
        else:
            self._build_trainee_by_user_csv(output, data)

    def _build_trainee_by_user_csv(self, output: io.StringIO, data: dict) -> None:
        """Build CSV content for trainee list organized by user."""
        writer = csv.writer(output)

        # Header
        writer.writerow(["BlackCobra Karate Club - Trainee Management Report"])
        writer.writerow([f"Generated: {data['generated_date'].strftime('%B %d, %Y')}"])
        writer.writerow(
            [
                f"Status Filter: {data['status_filter']} | Belt Filter: {data['belt_filter']}"
            ]
        )
        writer.writerow([])

        # Summary
        writer.writerow(["Summary"])
        writer.writerow(["Metric", "Count"])
        writer.writerow(["Total Trainees", data["total_trainees"]])
        writer.writerow(["Active", data["active_trainees"]])
        writer.writerow(["Inactive", data["inactive_trainees"]])
        writer.writerow(["Suspended", data["suspended_trainees"]])
        writer.writerow([])

        # Detailed list
        writer.writerow(["Trainee Details (By User)"])
        writer.writerow(
            ["Name", "Email", "Belt Rank", "Weight Class", "Age", "Status", "Joined"]
        )
        for trainee in data["trainees"]:
            join_date = (
                trainee["join_date"].strftime("%m/%d/%Y")
                if trainee["join_date"]
                else "N/A"
            )
            writer.writerow(
                [
                    trainee["name"],
                    trainee["email"],
                    trainee["belt_rank"],
                    trainee["weight_class"],
                    str(trainee["age"]),
                    trainee["status"],
                    join_date,
                ]
            )

    def _build_trainee_by_belt_csv(self, output: io.StringIO, data: dict) -> None:
        """Build CSV content for trainee list organized by belt rank."""
        writer = csv.writer(output)

        # Header
        writer.writerow(
            ["BlackCobra Karate Club - Trainee Management Report (By Belt Rank)"]
        )
        writer.writerow([f"Generated: {data['generated_date'].strftime('%B %d, %Y')}"])
        writer.writerow(
            [
                f"Status Filter: {data['status_filter']} | Belt Filter: {data['belt_filter']}"
            ]
        )
        writer.writerow([])

        # Summary
        writer.writerow(["Summary"])
        writer.writerow(["Metric", "Count"])
        writer.writerow(["Total Trainees", data["total_trainees"]])
        writer.writerow(["Active", data["active_trainees"]])
        writer.writerow(["Inactive", data["inactive_trainees"]])
        writer.writerow(["Suspended", data["suspended_trainees"]])
        writer.writerow([])

        # Belt rank order for proper sorting
        belt_order = [
            "white",
            "yellow",
            "orange",
            "green",
            "blue",
            "brown",
            "black",
            "master_degree",
        ]
        trainees_by_belt = data.get("trainees_by_belt", {})

        # Sort belts by defined order
        sorted_belts = sorted(
            trainees_by_belt.keys(),
            key=lambda x: belt_order.index(x.lower().replace(" ", "_"))
            if x.lower().replace(" ", "_") in belt_order
            else len(belt_order),
        )

        # Group by belt rank
        for belt_rank in sorted_belts:
            belt_trainees = trainees_by_belt[belt_rank]

            # Belt rank heading
            belt_label = (
                belt_rank.title() if belt_rank != "master_degree" else "Master Degree"
            )
            writer.writerow([f"{belt_label} Belt ({len(belt_trainees)} trainees)"])
            writer.writerow(
                ["Name", "Email", "Weight Class", "Age", "Status", "Joined"]
            )

            for trainee in sorted(belt_trainees, key=lambda x: x["name"]):
                join_date = (
                    trainee["join_date"].strftime("%m/%d/%Y")
                    if trainee["join_date"]
                    else "N/A"
                )
                writer.writerow(
                    [
                        trainee["name"],
                        trainee["email"],
                        trainee["weight_class"],
                        str(trainee["age"]),
                        trainee["status"],
                        join_date,
                    ]
                )

            writer.writerow([])  # Empty row between belt groups

    def session_attendance_report(
        self,
        session_ids: list = None,
        date_from: date = None,
        date_to: date = None,
        include_attendance_details: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate session attendance report.

        Args:
            session_ids: List of specific session IDs to include
            date_from: Start date filter
            date_to: End date filter
            include_attendance_details: Whether to include individual attendance records

        Returns:
            dict containing session and attendance data
        """
        from core.models import TrainingSession, Attendance, Trainee

        sessions = TrainingSession.objects.all().order_by("-date", "-start_time")

        # Apply filters
        if session_ids:
            sessions = sessions.filter(id__in=session_ids)
        if date_from:
            sessions = sessions.filter(date__gte=date_from)
        if date_to:
            sessions = sessions.filter(date__lte=date_to)

        # Build session data
        sessions_data = []
        total_present = 0
        total_absent = 0
        total_excused = 0
        total_late = 0

        for session in sessions:
            attendance_records = session.attendance_records.select_related(
                "trainee__profile__user"
            ).all()

            present = attendance_records.filter(status="present").count()
            absent = attendance_records.filter(status="absent").count()
            excused = attendance_records.filter(status="excused").count()
            late = attendance_records.filter(status="late").count()
            total = attendance_records.count()

            total_present += present + late
            total_absent += absent
            total_excused += excused
            total_late += late

            session_data = {
                "id": session.id,
                "title": session.title,
                "session_type": session.get_session_type_display(),
                "date": session.date,
                "start_time": session.start_time,
                "end_time": session.end_time,
                "location": session.location,
                "instructor": session.instructor,
                "status": session.get_status_display(),
                "present_count": present + late,
                "absent_count": absent,
                "excused_count": excused,
                "late_count": late,
                "total_marked": total,
                "attendance_rate": int((present + late) / total * 100)
                if total > 0
                else 0,
                "attendance_records": [],
            }

            if include_attendance_details:
                for record in attendance_records.order_by(
                    "trainee__profile__user__last_name"
                ):
                    user = record.trainee.profile.user
                    session_data["attendance_records"].append(
                        {
                            "trainee_name": f"{user.first_name} {user.last_name}".strip()
                            or user.username,
                            "belt_rank": record.trainee.get_belt_rank_display(),
                            "status": record.get_status_display(),
                            "check_in_time": record.check_in_time,
                            "notes": record.notes,
                        }
                    )

            sessions_data.append(session_data)

        # Calculate overall stats
        total_records = total_present + total_absent + total_excused
        overall_rate = (
            int((total_present / total_records) * 100) if total_records > 0 else 0
        )

        return {
            "report_type": "session_attendance",
            "generated_date": date.today(),
            "date_from": date_from,
            "date_to": date_to,
            "total_sessions": len(sessions_data),
            "total_present": total_present,
            "total_absent": total_absent,
            "total_excused": total_excused,
            "total_late": total_late,
            "overall_attendance_rate": overall_rate,
            "sessions": sessions_data,
        }

    def _build_session_attendance_pdf(
        self, data: dict, styles, title_style, sections: list = None
    ) -> list:
        """Build PDF elements for session attendance report."""
        elements = []

        # Default to all sections if none specified
        if sections is None:
            sections = ["header", "summary", "sessions", "details", "signature"]

        # Header section
        if "header" in sections:
            elements.append(Paragraph("BlackCobra Karate Club", title_style))
            elements.append(Paragraph("Session Attendance Report", styles["Heading2"]))

            date_range = ""
            if data.get("date_from") and data.get("date_to"):
                date_range = f" | Period: {data['date_from'].strftime('%B %d, %Y')} to {data['date_to'].strftime('%B %d, %Y')}"
            elif data.get("date_from"):
                date_range = f" | From: {data['date_from'].strftime('%B %d, %Y')}"
            elif data.get("date_to"):
                date_range = f" | To: {data['date_to'].strftime('%B %d, %Y')}"

            elements.append(
                Paragraph(
                    f"Generated: {data['generated_date'].strftime('%B %d, %Y')}{date_range}",
                    styles["Normal"],
                )
            )
            elements.append(Spacer(1, 20))

        # Summary statistics section
        if "summary" in sections:
            elements.append(Paragraph("Summary Statistics", styles["Heading3"]))
            elements.append(Spacer(1, 10))

            summary_data = [
                ["Metric", "Value"],
                ["Total Sessions", str(data["total_sessions"])],
                ["Total Present", str(data["total_present"])],
                ["Total Absent", str(data["total_absent"])],
                ["Total Excused", str(data["total_excused"])],
                ["Total Late", str(data["total_late"])],
                ["Overall Attendance Rate", f"{data['overall_attendance_rate']}%"],
            ]

            summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
            summary_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 11),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f3f4f6")),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ]
                )
            )
            elements.append(summary_table)
            elements.append(Spacer(1, 20))

        # Sessions list section
        if "sessions" in sections and data["sessions"]:
            elements.append(Paragraph("Sessions Overview", styles["Heading3"]))
            elements.append(Spacer(1, 10))

            session_table_data = [
                ["Date", "Session", "Type", "Time", "Present", "Absent", "Rate"]
            ]

            for session in data["sessions"]:
                session_table_data.append(
                    [
                        session["date"].strftime("%m/%d/%Y"),
                        session["title"][:25]
                        + ("..." if len(session["title"]) > 25 else ""),
                        session["session_type"],
                        session["start_time"].strftime("%H:%M"),
                        str(session["present_count"]),
                        str(session["absent_count"]),
                        f"{session['attendance_rate']}%",
                    ]
                )

            session_table = Table(
                session_table_data,
                colWidths=[
                    0.9 * inch,
                    1.5 * inch,
                    1.1 * inch,
                    0.7 * inch,
                    0.7 * inch,
                    0.7 * inch,
                    0.6 * inch,
                ],
            )
            session_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("ALIGN", (1, 0), (1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 9),
                        ("FONTSIZE", (0, 1), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor("#f9fafb")],
                        ),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]
                )
            )
            elements.append(session_table)
            elements.append(Spacer(1, 20))

        # Detailed attendance section
        if "details" in sections:
            for session in data["sessions"]:
                if session["attendance_records"]:
                    elements.append(
                        Paragraph(
                            f"{session['title']} - {session['date'].strftime('%B %d, %Y')}",
                            styles["Heading4"],
                        )
                    )
                    elements.append(
                        Paragraph(
                            f"Time: {session['start_time'].strftime('%H:%M')} - {session['end_time'].strftime('%H:%M')} | "
                            f"Location: {session['location']} | "
                            f"Attendance: {session['attendance_rate']}%",
                            styles["Normal"],
                        )
                    )
                    elements.append(Spacer(1, 8))

                    detail_data = [["Trainee", "Belt", "Status", "Check-in", "Notes"]]

                    for record in session["attendance_records"]:
                        check_in = (
                            record["check_in_time"].strftime("%H:%M")
                            if record["check_in_time"]
                            else "-"
                        )
                        detail_data.append(
                            [
                                record["trainee_name"],
                                record["belt_rank"],
                                record["status"],
                                check_in,
                                record["notes"][:20]
                                + ("..." if len(record["notes"]) > 20 else "")
                                if record["notes"]
                                else "-",
                            ]
                        )

                    detail_table = Table(
                        detail_data,
                        colWidths=[
                            1.5 * inch,
                            0.9 * inch,
                            0.8 * inch,
                            0.7 * inch,
                            1.8 * inch,
                        ],
                    )
                    detail_table.setStyle(
                        TableStyle(
                            [
                                (
                                    "BACKGROUND",
                                    (0, 0),
                                    (-1, 0),
                                    colors.HexColor("#4b5563"),
                                ),
                                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                                ("ALIGN", (4, 0), (4, -1), "LEFT"),
                                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                                ("FONTSIZE", (0, 0), (-1, 0), 8),
                                ("FONTSIZE", (0, 1), (-1, -1), 7),
                                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                                (
                                    "ROWBACKGROUNDS",
                                    (0, 1),
                                    (-1, -1),
                                    [colors.white, colors.HexColor("#f9fafb")],
                                ),
                            ]
                        )
                    )
                    elements.append(detail_table)
                    elements.append(Spacer(1, 15))

        # Signature section
        if "signature" in sections:
            elements.append(Spacer(1, 30))
            elements.append(Paragraph("_" * 80, styles["Normal"]))
            elements.append(Paragraph("Authorized By:", styles["Normal"]))
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("_" * 40, styles["Normal"]))
            elements.append(Paragraph("Admin Signature", styles["Normal"]))

        return elements

    def _build_session_attendance_csv(self, output: io.StringIO, data: dict) -> None:
        """Build CSV content for session attendance report."""
        writer = csv.writer(output)

    def _build_belt_promotion_pdf(self, data: dict, styles, title_style) -> list:
        """Build PDF elements for belt promotion history report."""
        elements = []

        elements.append(Paragraph("BlackCobra Karate Club", title_style))
        elements.append(Paragraph("Belt Promotion History Report", styles["Heading2"]))

        date_range = ""
        if data.get("start_date") and data.get("end_date"):
            date_range = f" | Period: {data['start_date'].strftime('%B %d, %Y')} to {data['end_date'].strftime('%B %d, %Y')}"
        elif data.get("start_date"):
            date_range = f" | From: {data['start_date'].strftime('%B %d, %Y')}"
        elif data.get("end_date"):
            date_range = f" | To: {data['end_date'].strftime('%B %d, %Y')}"

        elements.append(
            Paragraph(
                f"Generated: {data['generated_date'].strftime('%B %d, %Y')}{date_range}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 20))

        summary = data["summary"]
        summary_data = [
            ["Metric", "Value"],
            ["Total Promotions", str(summary["total_promotions"])],
            ["Automatic Promotions", str(summary["automatic_promotions"])],
            ["Manual Promotions", str(summary["manual_promotions"])],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dc2626")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f3f4f6")),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                ]
            )
        )
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        if data["promotions"]:
            elements.append(Paragraph("Promotion Details", styles["Heading3"]))
            elements.append(Spacer(1, 10))

            promo_data = [
                ["Date", "Trainee", "Old Belt", "New Belt", "Points", "Type", "Promoted By"]
            ]

            for promo in data["promotions"]:
                promo_data.append(
                    [
                        promo["promoted_at"].strftime("%Y-%m-%d"),
                        promo["trainee_name"][:20] + ("..." if len(promo["trainee_name"]) > 20 else ""),
                        promo["old_belt_rank"],
                        promo["new_belt_rank"],
                        str(promo["points_earned"]),
                        promo["promotion_type"],
                        promo["promoted_by"][:20] + ("..." if len(promo["promoted_by"]) > 20 else ""),
                    ]
                )

            promo_table = Table(
                promo_data,
                colWidths=[0.9 * inch, 1.5 * inch, 1 * inch, 1 * inch, 0.6 * inch, 0.8 * inch, 1.2 * inch],
            )
            promo_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("ALIGN", (1, 0), (1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 9),
                        ("FONTSIZE", (0, 1), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor("#f9fafb")],
                        ),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 4),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            elements.append(promo_table)

        elements.append(Spacer(1, 30))
        elements.append(Paragraph("_" * 80, styles["Normal"]))
        elements.append(Paragraph("Authorized By:", styles["Normal"]))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("_" * 40, styles["Normal"]))
        elements.append(Paragraph("Admin Signature", styles["Normal"]))

        return elements

    def _build_skill_progression_pdf(self, data: dict, styles, title_style) -> list:
        """Build PDF elements for trainee skill progression report."""
        elements = []

        elements.append(Paragraph("BlackCobra Karate Club", title_style))
        elements.append(Paragraph("Trainee Skill Progression Report", styles["Heading2"]))

        date_range = ""
        if data.get("start_date") and data.get("end_date"):
            date_range = f" | Period: {data['start_date'].strftime('%B %d, %Y')} to {data['end_date'].strftime('%B %d, %Y')}"

        elements.append(
            Paragraph(
                f"Generated: {data['generated_date'].strftime('%B %d, %Y')}{date_range}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 20))

        summary = data["summary"]
        summary_data = [
            ["Metric", "Value"],
            ["Total Trainees", str(summary["total_trainees"])],
            ["Total Evaluations", str(summary["total_evaluations"])],
            ["Total Achievements", str(summary["total_achievements"])],
            ["Total Belt Promotions", str(summary["total_belt_promotions"])],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dc2626")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f3f4f6")),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                ]
            )
        )
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        for trainee in data["trainees"]:
            elements.append(
                Paragraph(
                    f"{trainee['name']} - {trainee['current_belt_rank']}",
                    styles["Heading3"],
                )
            )
            elements.append(
                Paragraph(
                    f"Current Points: {trainee['current_points']} | Wins: {trainee['wins']} | "
                    f"Losses: {trainee['losses']} | Events: {trainee['events_participated']}",
                    styles["Normal"],
                )
            )
            elements.append(Spacer(1, 10))

            if trainee["evaluations"]:
                elements.append(Paragraph("Recent Evaluations", styles["Heading4"]))
                eval_data = [["Date", "Overall", "Technique", "Speed", "Strength", "Discipline"]]

                for eval_obj in trainee["evaluations"][:5]:
                    eval_data.append(
                        [
                            eval_obj["date"].strftime("%Y-%m-%d"),
                            str(eval_obj["overall_rating"]),
                            str(eval_obj["technique"]),
                            str(eval_obj["speed"]),
                            str(eval_obj["strength"]),
                            str(eval_obj["discipline"]),
                        ]
                    )

                eval_table = Table(
                    eval_data,
                    colWidths=[1 * inch, 0.7 * inch, 0.9 * inch, 0.7 * inch, 0.9 * inch, 0.9 * inch],
                )
                eval_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4b5563")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 8),
                            ("FONTSIZE", (0, 1), (-1, -1), 7),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 3),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                        ]
                    )
                )
                elements.append(eval_table)
                elements.append(Spacer(1, 10))

            if trainee["achievements"]:
                elements.append(Paragraph("Recent Achievements", styles["Heading4"]))
                ach_data = [["Date", "Title", "Type", "Points"]]

                for ach_obj in trainee["achievements"][:5]:
                    ach_data.append(
                        [
                            ach_obj["date_earned"].strftime("%Y-%m-%d"),
                            ach_obj["title"][:25] + ("..." if len(ach_obj["title"]) > 25 else ""),
                            ach_obj["achievement_type"],
                            str(ach_obj["points_awarded"]),
                        ]
                    )

                ach_table = Table(
                    ach_data, colWidths=[1 * inch, 2.5 * inch, 1.2 * inch, 0.7 * inch]
                )
                ach_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4b5563")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("ALIGN", (1, 0), (1, -1), "LEFT"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 8),
                            ("FONTSIZE", (0, 1), (-1, -1), 7),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 3),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                        ]
                    )
                )
                elements.append(ach_table)
                elements.append(Spacer(1, 10))

            if trainee["belt_progressions"]:
                elements.append(Paragraph("Belt Progressions", styles["Heading4"]))
                bp_data = [["Date", "Old Belt", "New Belt", "Points", "Type"]]

                for bp_obj in trainee["belt_progressions"]:
                    bp_data.append(
                        [
                            bp_obj["promoted_at"].strftime("%Y-%m-%d"),
                            bp_obj["old_belt_rank"],
                            bp_obj["new_belt_rank"],
                            str(bp_obj["points_earned"]),
                            bp_obj["promotion_type"],
                        ]
                    )

                bp_table = Table(
                    bp_data, colWidths=[1 * inch, 1.2 * inch, 1.2 * inch, 0.7 * inch, 1.2 * inch]
                )
                bp_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4b5563")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 8),
                            ("FONTSIZE", (0, 1), (-1, -1), 7),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 3),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                        ]
                    )
                )
                elements.append(bp_table)
                elements.append(Spacer(1, 15))

        elements.append(Spacer(1, 20))
        elements.append(Paragraph("_" * 80, styles["Normal"]))
        elements.append(Paragraph("Authorized By:", styles["Normal"]))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("_" * 40, styles["Normal"]))
        elements.append(Paragraph("Admin Signature", styles["Normal"]))

        return elements

    def _build_tournament_participation_pdf(self, data: dict, styles, title_style) -> list:
        """Build PDF elements for tournament participation report."""
        elements = []

        elements.append(Paragraph("BlackCobra Karate Club", title_style))
        elements.append(Paragraph("Tournament Participation Report", styles["Heading2"]))

        date_range = ""
        if data.get("start_date") and data.get("end_date"):
            date_range = f" | Period: {data['start_date'].strftime('%B %d, %Y')} to {data['end_date'].strftime('%B %d, %Y')}"

        elements.append(
            Paragraph(
                f"Generated: {data['generated_date'].strftime('%B %d, %Y')}{date_range}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 20))

        summary = data["summary"]
        summary_data = [
            ["Metric", "Value"],
            ["Total Events", str(summary["total_events"])],
            ["Total Participants", str(summary["total_participants"])],
            ["Total Matches", str(summary["total_matches"])],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dc2626")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f3f4f6")),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                ]
            )
        )
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        for event in data["events"]:
            elements.append(
                Paragraph(
                    f"{event['name']} - {event['event_date'].strftime('%B %d, %Y')}",
                    styles["Heading3"],
                )
            )
            elements.append(
                Paragraph(
                    f"Location: {event['location']} | Status: {event['status']} | "
                    f"Participants: {event['total_registrations']}/{event['max_participants']}",
                    styles["Normal"],
                )
            )
            elements.append(Spacer(1, 10))

            if event["participants"]:
                participant_data = [["Name", "Belt", "Weight Class", "Matches"]]

                for participant in event["participants"]:
                    participant_data.append(
                        [
                            participant["name"][:20] + ("..." if len(participant["name"]) > 20 else ""),
                            participant["belt_rank"],
                            participant["weight_class"],
                            str(participant["matches_count"]),
                        ]
                    )

                participant_table = Table(
                    participant_data,
                    colWidths=[2 * inch, 1 * inch, 1.2 * inch, 0.9 * inch],
                )
                participant_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("ALIGN", (0, 0), (0, -1), "LEFT"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 9),
                            ("FONTSIZE", (0, 1), (-1, -1), 8),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            (
                                "ROWBACKGROUNDS",
                                (0, 1),
                                (-1, -1),
                                [colors.white, colors.HexColor("#f9fafb")],
                            ),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 4),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                        ]
                    )
                )
                elements.append(participant_table)

            elements.append(Spacer(1, 15))

        elements.append(Spacer(1, 20))
        elements.append(Paragraph("_" * 80, styles["Normal"]))
        elements.append(Paragraph("Authorized By:", styles["Normal"]))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("_" * 40, styles["Normal"]))
        elements.append(Paragraph("Admin Signature", styles["Normal"]))

        return elements

    def _build_performance_evaluation_pdf(self, data: dict, styles, title_style) -> list:
        """Build PDF elements for performance evaluation report."""
        elements = []

        elements.append(Paragraph("BlackCobra Karate Club", title_style))
        elements.append(Paragraph("Performance Evaluation Report", styles["Heading2"]))

        date_range = ""
        if data.get("start_date") and data.get("end_date"):
            date_range = f" | Period: {data['start_date'].strftime('%B %d, %Y')} to {data['end_date'].strftime('%B %d, %Y')}"

        elements.append(
            Paragraph(
                f"Generated: {data['generated_date'].strftime('%B %d, %Y')}{date_range}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 20))

        summary = data["summary"]
        summary_data = [
            ["Metric", "Value"],
            ["Total Evaluations", str(summary["total_evaluations"])],
            ["Completed", str(summary["completed_evaluations"])],
            ["Pending", str(summary["pending_evaluations"])],
            ["Avg Overall Rating", f"{summary['average_overall_rating']:.2f}"],
            ["Avg Technique", f"{summary['average_technique']:.2f}"],
            ["Avg Speed", f"{summary['average_speed']:.2f}"],
            ["Avg Strength", f"{summary['average_strength']:.2f}"],
            ["Avg Discipline", f"{summary['average_discipline']:.2f}"],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dc2626")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f3f4f6")),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                ]
            )
        )
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        if data["evaluations"]:
            elements.append(Paragraph("Evaluation Details", styles["Heading3"]))
            elements.append(Spacer(1, 10))

            eval_data = [
                ["Date", "Trainee", "Belt", "Overall", "Technique", "Speed", "Strength", "Discipline", "Evaluator"]
            ]

            for eval_obj in data["evaluations"]:
                eval_data.append(
                    [
                        eval_obj["evaluated_at"].strftime("%Y-%m-%d"),
                        eval_obj["trainee_name"][:15] + ("..." if len(eval_obj["trainee_name"]) > 15 else ""),
                        eval_obj["current_belt_rank"],
                        str(eval_obj["overall_rating"]),
                        str(eval_obj["technique"]),
                        str(eval_obj["speed"]),
                        str(eval_obj["strength"]),
                        str(eval_obj["discipline"]),
                        eval_obj["evaluator"][:15] + ("..." if len(eval_obj["evaluator"]) > 15 else ""),
                    ]
                )

            eval_table = Table(
                eval_data,
                colWidths=[0.9 * inch, 1.2 * inch, 0.9 * inch, 0.6 * inch, 0.7 * inch, 0.6 * inch, 0.7 * inch, 0.8 * inch, 1.1 * inch],
            )
            eval_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("ALIGN", (1, 0), (1, -1), "LEFT"),
                        ("ALIGN", (8, 0), (8, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 8),
                        ("FONTSIZE", (0, 1), (-1, -1), 7),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor("#f9fafb")],
                        ),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 3),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ]
                )
            )
            elements.append(eval_table)

        elements.append(Spacer(1, 20))
        elements.append(Paragraph("_" * 80, styles["Normal"]))
        elements.append(Paragraph("Authorized By:", styles["Normal"]))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("_" * 40, styles["Normal"]))
        elements.append(Paragraph("Admin Signature", styles["Normal"]))

        return elements

    def _build_competition_results_pdf(self, data: dict, styles, title_style) -> list:
        """Build PDF elements for competition results report."""
        elements = []

        elements.append(Paragraph("BlackCobra Karate Club", title_style))
        elements.append(Paragraph("Competition Results Report", styles["Heading2"]))

        date_range = ""
        if data.get("start_date") and data.get("end_date"):
            date_range = f" | Period: {data['start_date'].strftime('%B %d, %Y')} to {data['end_date'].strftime('%B %d, %Y')}"

        elements.append(
            Paragraph(
                f"Generated: {data['generated_date'].strftime('%B %d, %Y')}{date_range}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 20))

        summary = data["summary"]
        summary_data = [
            ["Metric", "Value"],
            ["Total Matches", str(summary["total_matches"])],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dc2626")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f3f4f6")),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                ]
            )
        )
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        if data["matches"]:
            elements.append(Paragraph("Match Results", styles["Heading3"]))
            elements.append(Spacer(1, 10))

            match_data = [
                ["Date", "Event", "Type", "Competitor 1", "Competitor 2", "Winner"]
            ]

            for match in data["matches"]:
                match_data.append(
                    [
                        match["scheduled_time"].strftime("%Y-%m-%d"),
                        match["event_name"][:20] + ("..." if len(match["event_name"]) > 20 else ""),
                        match["match_type"],
                        match["competitor1"][:20] + ("..." if len(match["competitor1"]) > 20 else ""),
                        match["competitor2"][:20] + ("..." if len(match["competitor2"]) > 20 else ""),
                        match["winner"][:20] + ("..." if len(match["winner"]) > 20 else ""),
                    ]
                )

            match_table = Table(
                match_data,
                colWidths=[0.9 * inch, 1.5 * inch, 1 * inch, 1.8 * inch, 1.8 * inch, 1.8 * inch],
            )
            match_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 8),
                        ("FONTSIZE", (0, 1), (-1, -1), 7),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor("#f9fafb")],
                        ),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 3),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ]
                )
            )
            elements.append(match_table)

        elements.append(Spacer(1, 20))
        elements.append(Paragraph("_" * 80, styles["Normal"]))
        elements.append(Paragraph("Authorized By:", styles["Normal"]))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("_" * 40, styles["Normal"]))
        elements.append(Paragraph("Admin Signature", styles["Normal"]))

        return elements

    def _build_trainee_milestones_pdf(self, data: dict, styles, title_style) -> list:
        """Build PDF elements for trainee milestones report."""
        elements = []

        elements.append(Paragraph("BlackCobra Karate Club", title_style))
        elements.append(Paragraph("Trainee Milestones Report", styles["Heading2"]))

        date_range = ""
        if data.get("start_date") and data.get("end_date"):
            date_range = f" | Period: {data['start_date'].strftime('%B %d, %Y')} to {data['end_date'].strftime('%B %d, %Y')}"

        elements.append(
            Paragraph(
                f"Generated: {data['generated_date'].strftime('%B %d, %Y')}{date_range}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 20))

        summary = data["summary"]
        summary_data = [
            ["Metric", "Value"],
            ["Total Trainees", str(summary["total_trainees"])],
            ["Total Milestones", str(summary["total_milestones"])],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dc2626")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f3f4f6")),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                ]
            )
        )
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        for trainee in data["trainees"]:
            elements.append(
                Paragraph(
                    f"{trainee['name']} - {trainee['current_belt_rank']}",
                    styles["Heading3"],
                )
            )
            elements.append(
                Paragraph(
                    f"Status: {trainee['status']} | Joined: {trainee['joined_date'].strftime('%Y-%m-%d')} | "
                    f"Milestones: {trainee['total_milestones']}",
                    styles["Normal"],
                )
            )
            elements.append(Spacer(1, 10))

            if trainee["milestones"]:
                milestone_data = [["Date", "Type", "Title", "Description"]]

                for milestone in trainee["milestones"][:10]:
                    milestone_data.append(
                        [
                            milestone["date"].strftime("%Y-%m-%d"),
                            milestone["type"],
                            milestone["title"][:25] + ("..." if len(milestone["title"]) > 25 else ""),
                            milestone["description"][:30] + ("..." if len(milestone["description"]) > 30 else ""),
                        ]
                    )

                milestone_table = Table(
                    milestone_data,
                    colWidths=[1 * inch, 1.2 * inch, 2.2 * inch, 1.8 * inch],
                )
                milestone_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4b5563")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("ALIGN", (2, 0), (2, -1), "LEFT"),
                            ("ALIGN", (3, 0), (3, -1), "LEFT"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 8),
                            ("FONTSIZE", (0, 1), (-1, -1), 7),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            (
                                "ROWBACKGROUNDS",
                                (0, 1),
                                (-1, -1),
                                [colors.white, colors.HexColor("#f9fafb")],
                            ),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 3),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                        ]
                    )
                )
                elements.append(milestone_table)
                elements.append(Spacer(1, 15))

        elements.append(Spacer(1, 20))
        elements.append(Paragraph("_" * 80, styles["Normal"]))
        elements.append(Paragraph("Authorized By:", styles["Normal"]))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("_" * 40, styles["Normal"]))
        elements.append(Paragraph("Admin Signature", styles["Normal"]))

        return elements

        # Header
        writer.writerow(["BlackCobra Karate Club - Session Attendance Report"])
        writer.writerow([f"Generated: {data['generated_date'].strftime('%B %d, %Y')}"])
        writer.writerow([])

        # Summary
        writer.writerow(["Summary Statistics"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Sessions", data["total_sessions"]])
        writer.writerow(["Total Present", data["total_present"]])
        writer.writerow(["Total Absent", data["total_absent"]])
        writer.writerow(["Total Excused", data["total_excused"]])
        writer.writerow(["Total Late", data["total_late"]])
        writer.writerow(
            ["Overall Attendance Rate", f"{data['overall_attendance_rate']}%"]
        )
        writer.writerow([])

        # Sessions overview
        writer.writerow(["Sessions Overview"])
        writer.writerow(
            [
                "Date",
                "Session",
                "Type",
                "Start Time",
                "End Time",
                "Location",
                "Present",
                "Absent",
                "Excused",
                "Late",
                "Rate",
            ]
        )

        for session in data["sessions"]:
            writer.writerow(
                [
                    session["date"].strftime("%Y-%m-%d"),
                    session["title"],
                    session["session_type"],
                    session["start_time"].strftime("%H:%M"),
                    session["end_time"].strftime("%H:%M"),
                    session["location"],
                    session["present_count"],
                    session["absent_count"],
                    session["excused_count"],
                    session["late_count"],
                    f"{session['attendance_rate']}%",
                ]
            )

        writer.writerow([])

        # Detailed attendance
        writer.writerow(["Detailed Attendance Records"])
        writer.writerow(
            ["Session", "Date", "Trainee", "Belt", "Status", "Check-in Time", "Notes"]
        )

        for session in data["sessions"]:
            for record in session["attendance_records"]:
                check_in = (
                    record["check_in_time"].strftime("%H:%M")
                    if record["check_in_time"]
                    else ""
                )
                writer.writerow(
                    [
                        session["title"],
                        session["date"].strftime("%Y-%m-%d"),
                        record["trainee_name"],
                        record["belt_rank"],
                        record["status"],
                        check_in,
                        record["notes"],
                    ]
                )

    def _build_belt_promotion_csv(self, output: io.StringIO, data: dict) -> None:
        """Build CSV content for belt promotion history report."""
        writer = csv.writer(output)

        writer.writerow(["BlackCobra Karate Club - Belt Promotion History Report"])
        writer.writerow([f"Generated: {data['generated_date'].strftime('%B %d, %Y')}"])
        writer.writerow([])

        summary = data["summary"]
        writer.writerow(["Summary"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Promotions", summary["total_promotions"]])
        writer.writerow(["Automatic Promotions", summary["automatic_promotions"]])
        writer.writerow(["Manual Promotions", summary["manual_promotions"]])
        writer.writerow([])

        writer.writerow(["Promotion Details"])
        writer.writerow(
            [
                "Date",
                "Trainee Name",
                "Email",
                "Old Belt Rank",
                "New Belt Rank",
                "Points Earned",
                "Promotion Type",
                "Promoted By",
                "Admin Notes",
            ]
        )

        for promo in data["promotions"]:
            writer.writerow(
                [
                    promo["promoted_at"].strftime("%Y-%m-%d %H:%M"),
                    promo["trainee_name"],
                    promo["trainee_email"],
                    promo["old_belt_rank"],
                    promo["new_belt_rank"],
                    promo["points_earned"],
                    promo["promotion_type"],
                    promo["promoted_by"],
                    promo["admin_notes"],
                ]
            )

    def _build_skill_progression_csv(self, output: io.StringIO, data: dict) -> None:
        """Build CSV content for trainee skill progression report."""
        writer = csv.writer(output)

        writer.writerow(
            ["BlackCobra Karate Club - Trainee Skill Progression Report"]
        )
        writer.writerow([f"Generated: {data['generated_date'].strftime('%B %d, %Y')}"])
        writer.writerow([])

        summary = data["summary"]
        writer.writerow(["Summary"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Trainees", summary["total_trainees"]])
        writer.writerow(["Total Evaluations", summary["total_evaluations"]])
        writer.writerow(["Total Achievements", summary["total_achievements"]])
        writer.writerow(["Total Belt Promotions", summary["total_belt_promotions"]])
        writer.writerow([])

        for trainee in data["trainees"]:
            writer.writerow([f"Trainee: {trainee['name']}"])
            writer.writerow(
                [
                    "Current Belt Rank",
                    "Weight Class",
                    "Status",
                    "Current Points",
                    "Wins",
                    "Losses",
                    "Events Participated",
                ]
            )
            writer.writerow(
                [
                    trainee["current_belt_rank"],
                    trainee["weight_class"],
                    trainee["status"],
                    trainee["current_points"],
                    trainee["wins"],
                    trainee["losses"],
                    trainee["events_participated"],
                ]
            )
            writer.writerow([])

            if trainee["evaluations"]:
                writer.writerow(["Evaluations"])
                writer.writerow(
                    [
                        "Date",
                        "Overall Rating",
                        "Average Rating",
                        "Technique",
                        "Speed",
                        "Strength",
                        "Flexibility",
                        "Discipline",
                        "Spirit",
                        "Attendance Score",
                        "Sparring Score",
                        "Achievement Score",
                        "Performance Score",
                        "Total Belt Points",
                        "Comments",
                        "Strengths",
                        "Areas for Improvement",
                    ]
                )
                for eval_obj in trainee["evaluations"]:
                    writer.writerow(
                        [
                            eval_obj["date"].strftime("%Y-%m-%d %H:%M"),
                            eval_obj["overall_rating"],
                            f"{eval_obj['average_rating']:.2f}",
                            eval_obj["technique"],
                            eval_obj["speed"],
                            eval_obj["strength"],
                            eval_obj["flexibility"],
                            eval_obj["discipline"],
                            eval_obj["spirit"],
                            eval_obj["attendance_score"],
                            eval_obj["sparring_score"],
                            eval_obj["achievement_score"],
                            eval_obj["performance_score"],
                            eval_obj["total_belt_points"],
                            eval_obj["comments"],
                            eval_obj["strengths"],
                            eval_obj["areas_for_improvement"],
                        ]
                    )
                writer.writerow([])

            if trainee["achievements"]:
                writer.writerow(["Achievements"])
                writer.writerow(
                    [
                        "Title",
                        "Description",
                        "Achievement Type",
                        "Date Earned",
                        "Points Awarded",
                    ]
                )
                for ach_obj in trainee["achievements"]:
                    writer.writerow(
                        [
                            ach_obj["title"],
                            ach_obj["description"],
                            ach_obj["achievement_type"],
                            ach_obj["date_earned"].strftime("%Y-%m-%d"),
                            ach_obj["points_awarded"],
                        ]
                    )
                writer.writerow([])

            if trainee["belt_progressions"]:
                writer.writerow(["Belt Progressions"])
                writer.writerow(
                    [
                        "Old Belt Rank",
                        "New Belt Rank",
                        "Points Earned",
                        "Promotion Type",
                        "Promoted At",
                    ]
                )
                for bp_obj in trainee["belt_progressions"]:
                    writer.writerow(
                        [
                            bp_obj["old_belt_rank"],
                            bp_obj["new_belt_rank"],
                            bp_obj["points_earned"],
                            bp_obj["promotion_type"],
                            bp_obj["promoted_at"].strftime("%Y-%m-%d %H:%M"),
                        ]
                    )
                writer.writerow([])
            writer.writerow([])

    def _build_tournament_participation_csv(self, output: io.StringIO, data: dict) -> None:
        """Build CSV content for tournament participation report."""
        writer = csv.writer(output)

        writer.writerow(
            ["BlackCobra Karate Club - Tournament Participation Report"]
        )
        writer.writerow([f"Generated: {data['generated_date'].strftime('%B %d, %Y')}"])
        writer.writerow([])

        summary = data["summary"]
        writer.writerow(["Summary"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Events", summary["total_events"]])
        writer.writerow(["Total Participants", summary["total_participants"]])
        writer.writerow(["Total Matches", summary["total_matches"]])
        writer.writerow([])

        for event in data["events"]:
            writer.writerow([f"Event: {event['name']}"])
            writer.writerow(
                ["Event Date", "Location", "Status", "Max Participants"]
            )
            writer.writerow(
                [
                    event["event_date"].strftime("%Y-%m-%d"),
                    event["location"],
                    event["status"],
                    event["max_participants"],
                ]
            )
            writer.writerow([])

            writer.writerow(["Participants"])
            writer.writerow(
                [
                    "Trainee Name",
                    "Email",
                    "Belt Rank",
                    "Weight Class",
                    "Registered At",
                    "Matches Count",
                ]
            )

            for participant in event["participants"]:
                writer.writerow(
                    [
                        participant["name"],
                        participant["email"],
                        participant["belt_rank"],
                        participant["weight_class"],
                        participant["registered_at"].strftime("%Y-%m-%d %H:%M"),
                        participant["matches_count"],
                    ]
                )

                if participant["matches"]:
                    writer.writerow([])
                    writer.writerow(["  Matches for " + participant["name"]])
                    writer.writerow(
                        [
                            "  Match ID",
                            "  Match Type",
                            "  Is Promotion Match",
                            "  Scheduled Time",
                            "  Status",
                            "  Is Winner",
                            "  Opponent",
                        ]
                    )

                    for match in participant["matches"]:
                        writer.writerow(
                            [
                                match["match_id"],
                                match["match_type"],
                                match["is_promotion_match"],
                                match["scheduled_time"].strftime("%Y-%m-%d %H:%M"),
                                match["status"],
                                match["is_winner"],
                                match["opponent"],
                            ]
                        )

            writer.writerow([])

    def _build_performance_evaluation_csv(self, output: io.StringIO, data: dict) -> None:
        """Build CSV content for performance evaluation report."""
        writer = csv.writer(output)

        writer.writerow(
            ["BlackCobra Karate Club - Performance Evaluation Report"]
        )
        writer.writerow([f"Generated: {data['generated_date'].strftime('%B %d, %Y')}"])
        writer.writerow([])

        summary = data["summary"]
        writer.writerow(["Summary"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Evaluations", summary["total_evaluations"]])
        writer.writerow(["Completed Evaluations", summary["completed_evaluations"]])
        writer.writerow(["Pending Evaluations", summary["pending_evaluations"]])
        writer.writerow(
            ["Average Overall Rating", f"{summary['average_overall_rating']:.2f}"]
        )
        writer.writerow(["Average Technique", f"{summary['average_technique']:.2f}"])
        writer.writerow(["Average Speed", f"{summary['average_speed']:.2f}"])
        writer.writerow(["Average Strength", f"{summary['average_strength']:.2f}"])
        writer.writerow(["Average Discipline", f"{summary['average_discipline']:.2f}"])
        writer.writerow([])

        writer.writerow(["Evaluation Details"])
        writer.writerow(
            [
                "Trainee Name",
                "Email",
                "Current Belt Rank",
                "Evaluator",
                "Technique",
                "Speed",
                "Strength",
                "Flexibility",
                "Discipline",
                "Spirit",
                "Overall Rating",
                "Average Rating",
                "Attendance Score",
                "Sparring Score",
                "Achievement Score",
                "Performance Score",
                "Total Belt Points",
                "Comments",
                "Strengths",
                "Areas for Improvement",
                "Recommendations",
                "Status",
                "Evaluated At",
                "Next Evaluation Date",
            ]
        )

        for eval_obj in data["evaluations"]:
            next_eval_date = (
                eval_obj["next_evaluation_date"].strftime("%Y-%m-%d")
                if eval_obj["next_evaluation_date"]
                else "N/A"
            )
            writer.writerow(
                [
                    eval_obj["trainee_name"],
                    eval_obj["trainee_email"],
                    eval_obj["current_belt_rank"],
                    eval_obj["evaluator"],
                    eval_obj["technique"],
                    eval_obj["speed"],
                    eval_obj["strength"],
                    eval_obj["flexibility"],
                    eval_obj["discipline"],
                    eval_obj["spirit"],
                    eval_obj["overall_rating"],
                    f"{eval_obj['average_rating']:.2f}",
                    eval_obj["attendance_score"],
                    eval_obj["sparring_score"],
                    eval_obj["achievement_score"],
                    eval_obj["performance_score"],
                    eval_obj["total_belt_points"],
                    eval_obj["comments"],
                    eval_obj["strengths"],
                    eval_obj["areas_for_improvement"],
                    eval_obj["recommendations"],
                    eval_obj["status"],
                    eval_obj["evaluated_at"].strftime("%Y-%m-%d %H:%M"),
                    next_eval_date,
                ]
            )

    def _build_competition_results_csv(self, output: io.StringIO, data: dict) -> None:
        """Build CSV content for competition results report."""
        writer = csv.writer(output)

        writer.writerow(
            ["BlackCobra Karate Club - Competition Results Report"]
        )
        writer.writerow([f"Generated: {data['generated_date'].strftime('%B %d, %Y')}"])
        writer.writerow([])

        summary = data["summary"]
        writer.writerow(["Summary"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Matches", summary["total_matches"]])
        writer.writerow([])

        writer.writerow(["Match Results"])
        writer.writerow(
            [
                "Match ID",
                "Event Name",
                "Event Date",
                "Match Type",
                "Is Promotion Match",
                "Scheduled Time",
                "Competitor 1",
                "Competitor 2",
                "Winner",
            ]
        )

        for match in data["matches"]:
            writer.writerow(
                [
                    match["match_id"],
                    match["event_name"],
                    match["event_date"].strftime("%Y-%m-%d"),
                    match["match_type"],
                    match["is_promotion_match"],
                    match["scheduled_time"].strftime("%Y-%m-%d %H:%M"),
                    match["competitor1"],
                    match["competitor2"],
                    match["winner"],
                ]
            )

        writer.writerow([])
        writer.writerow(["Detailed Judge Results"])

        for match in data["matches"]:
            if match["results"]:
                writer.writerow(
                    [f"Match {match['match_id']} - {match['event_name']}"]
                )
                writer.writerow(
                    [
                        "Judge",
                        "Winner",
                        "Competitor 1 Score",
                        "Competitor 2 Score",
                        "C1 Sparring Score",
                        "C1 Penan Score",
                        "C1 Judo Score",
                        "C1 Breaking Score",
                        "C2 Sparring Score",
                        "C2 Penan Score",
                        "C2 Judo Score",
                        "C2 Breaking Score",
                        "Notes",
                        "Submitted At",
                    ]
                )

                for result in match["results"]:
                    writer.writerow(
                        [
                            result["judge_name"],
                            result["winner"],
                            result["competitor1_score"],
                            result["competitor2_score"],
                            result["c1_sparring_score"],
                            result["c1_penan_score"],
                            result["c1_judo_score"],
                            result["c1_breaking_score"],
                            result["c2_sparring_score"],
                            result["c2_penan_score"],
                            result["c2_judo_score"],
                            result["c2_breaking_score"],
                            result["notes"],
                            result["submitted_at"].strftime("%Y-%m-%d %H:%M"),
                        ]
                    )

    def _build_trainee_milestones_csv(self, output: io.StringIO, data: dict) -> None:
        """Build CSV content for trainee milestones report."""
        writer = csv.writer(output)

        writer.writerow(
            ["BlackCobra Karate Club - Trainee Milestones Report"]
        )
        writer.writerow([f"Generated: {data['generated_date'].strftime('%B %d, %Y')}"])
        writer.writerow([])

        summary = data["summary"]
        writer.writerow(["Summary"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Trainees", summary["total_trainees"]])
        writer.writerow(["Total Milestones", summary["total_milestones"]])
        writer.writerow([])

        for trainee in data["trainees"]:
            writer.writerow([f"Trainee: {trainee['name']}"])
            writer.writerow(
                [
                    "Current Belt Rank",
                    "Weight Class",
                    "Status",
                    "Joined Date",
                    "Total Milestones",
                ]
            )
            writer.writerow(
                [
                    trainee["current_belt_rank"],
                    trainee["weight_class"],
                    trainee["status"],
                    trainee["joined_date"].strftime("%Y-%m-%d"),
                    trainee["total_milestones"],
                ]
            )
            writer.writerow([])

            if trainee["milestones"]:
                writer.writerow(["Milestones"])
                writer.writerow(
                    [
                        "Date",
                        "Type",
                        "Title",
                        "Description",
                        "Achievement Type",
                        "Points Awarded",
                    ]
                )

                for milestone in trainee["milestones"]:
                    points_awarded = milestone.get("points_awarded", "N/A")
                    if milestone["type"] == "belt_promotion":
                        points_awarded = milestone.get("points_earned", "N/A")

                    writer.writerow(
                        [
                            milestone["date"].strftime("%Y-%m-%d"),
                            milestone["type"],
                            milestone["title"],
                            milestone["description"],
                            milestone["achievement_type"],
                            points_awarded,
                        ]
                    )
            writer.writerow([])

    def belt_promotion_history_report(
        self,
        trainee_id: int = None,
        start_date: date = None,
        end_date: date = None,
        belt_rank: str = None,
    ) -> Dict[str, Any]:
        """
        Generate belt promotion history report.
        Includes detailed progression tracking for trainees.

        Args:
            trainee_id: Filter by specific trainee ID
            start_date: Filter promotions from this date
            end_date: Filter promotions until this date
            belt_rank: Filter by specific belt rank

        Returns:
            dict containing belt promotion history data
        """
        from core.models import BeltRankProgress, Trainee

        promotions = BeltRankProgress.objects.select_related(
            "trainee__profile__user", "promoted_by"
        ).all()

        if trainee_id:
            promotions = promotions.filter(trainee_id=trainee_id)
        if start_date:
            promotions = promotions.filter(promoted_at__date__gte=start_date)
        if end_date:
            promotions = promotions.filter(promoted_at__date__lte=end_date)
        if belt_rank:
            promotions = promotions.filter(new_belt_rank=belt_rank)

        promotions = promotions.order_by("-promoted_at")

        promotions_data = []
        for promotion in promotions:
            user = promotion.trainee.profile.user
            promotions_data.append(
                {
                    "trainee_id": promotion.trainee_id,
                    "trainee_name": f"{user.first_name} {user.last_name}".strip()
                    or user.username,
                    "trainee_email": user.email,
                    "old_belt_rank": promotion.get_old_belt_rank_display(),
                    "new_belt_rank": promotion.get_new_belt_rank_display(),
                    "points_earned": promotion.points_earned,
                    "promotion_type": promotion.get_promotion_type_display(),
                    "admin_notes": promotion.admin_notes,
                    "promoted_by": f"{promotion.promoted_by.first_name} {promotion.promoted_by.last_name}"
                    if promotion.promoted_by
                    else "System",
                    "promoted_at": promotion.promoted_at,
                }
            )

        summary_stats = {
            "total_promotions": len(promotions_data),
            "automatic_promotions": sum(
                1 for p in promotions_data if p["promotion_type"] == "Automatic"
            ),
            "manual_promotions": sum(
                1 for p in promotions_data if p["promotion_type"] == "Admin Override"
            ),
            "by_belt": {},
        }

        for promotion in promotions_data:
            belt = promotion["new_belt_rank"]
            summary_stats["by_belt"][belt] = summary_stats["by_belt"].get(belt, 0) + 1

        return {
            "report_type": "belt_promotion_history",
            "generated_date": date.today(),
            "trainee_id": trainee_id,
            "start_date": start_date,
            "end_date": end_date,
            "belt_rank": belt_rank,
            "promotions": promotions_data,
            "summary": summary_stats,
        }

    def trainee_skill_progression_report(
        self,
        trainee_id: int = None,
        start_date: date = None,
        end_date: date = None,
        include_evaluations: bool = True,
        include_achievements: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate individual member skill progression report.
        Includes evaluations, achievements, and belt progress.

        Args:
            trainee_id: Filter by specific trainee ID
            start_date: Filter from this date
            end_date: Filter until this date
            include_evaluations: Include evaluation data
            include_achievements: Include achievement data

        Returns:
            dict containing skill progression data
        """
        from core.models import (
            Trainee,
            TraineeEvaluation,
            TraineeAchievement,
            BeltRankProgress,
            TraineePoints,
        )

        trainees = Trainee.objects.select_related("profile__user").filter(
            archived=False
        )

        if trainee_id:
            trainees = trainees.filter(id=trainee_id)

        trainees_data = []

        for trainee in trainees:
            user = trainee.profile.user

            evaluations = []
            achievements = []
            belt_progressions = []

            if include_evaluations:
                eval_query = trainee.evaluations.filter(status="completed")
                if start_date:
                    eval_query = eval_query.filter(evaluated_at__date__gte=start_date)
                if end_date:
                    eval_query = eval_query.filter(evaluated_at__date__lte=end_date)

                for eval_obj in eval_query.order_by("-evaluated_at"):
                    evaluations.append(
                        {
                            "id": eval_obj.id,
                            "date": eval_obj.evaluated_at,
                            "technique": eval_obj.technique,
                            "speed": eval_obj.speed,
                            "strength": eval_obj.strength,
                            "flexibility": eval_obj.flexibility,
                            "discipline": eval_obj.discipline,
                            "spirit": eval_obj.spirit,
                            "overall_rating": eval_obj.overall_rating,
                            "average_rating": eval_obj.average_rating,
                            "attendance_score": eval_obj.attendance_score,
                            "sparring_score": eval_obj.sparring_score,
                            "achievement_score": eval_obj.achievement_score,
                            "performance_score": eval_obj.performance_score,
                            "total_belt_points": eval_obj.total_belt_points,
                            "comments": eval_obj.comments,
                            "strengths": eval_obj.strengths,
                            "areas_for_improvement": eval_obj.areas_for_improvement,
                        }
                    )

            if include_achievements:
                ach_query = trainee.achievements.all()
                if start_date:
                    ach_query = ach_query.filter(date_earned__gte=start_date)
                if end_date:
                    ach_query = ach_query.filter(date_earned__lte=end_date)

                for ach_obj in ach_query.order_by("-date_earned"):
                    achievements.append(
                        {
                            "id": ach_obj.id,
                            "title": ach_obj.title,
                            "description": ach_obj.description,
                            "achievement_type": ach_obj.get_achievement_type_display(),
                            "date_earned": ach_obj.date_earned,
                            "points_awarded": ach_obj.points_awarded,
                        }
                    )

            belt_prog_query = trainee.belt_rank_progress.all()
            if start_date:
                belt_prog_query = belt_prog_query.filter(promoted_at__date__gte=start_date)
            if end_date:
                belt_prog_query = belt_prog_query.filter(promoted_at__date__lte=end_date)

            for bp_obj in belt_prog_query.order_by("-promoted_at"):
                belt_progressions.append(
                    {
                        "id": bp_obj.id,
                        "old_belt_rank": bp_obj.get_old_belt_rank_display(),
                        "new_belt_rank": bp_obj.get_new_belt_rank_display(),
                        "points_earned": bp_obj.points_earned,
                        "promotion_type": bp_obj.get_promotion_type_display(),
                        "promoted_at": bp_obj.promoted_at,
                    }
                )

            try:
                points_obj = trainee.points
                current_points = points_obj.total_points
                wins = points_obj.wins
                losses = points_obj.losses
                events_participated = points_obj.events_participated
            except TraineePoints.DoesNotExist:
                current_points = 0
                wins = 0
                losses = 0
                events_participated = 0

            trainees_data.append(
                {
                    "trainee_id": trainee.id,
                    "name": f"{user.first_name} {user.last_name}".strip() or user.username,
                    "email": user.email,
                    "current_belt_rank": trainee.get_belt_rank_display(),
                    "weight_class": trainee.weight_class,
                    "status": trainee.get_status_display(),
                    "joined_date": trainee.joined_date,
                    "current_points": current_points,
                    "wins": wins,
                    "losses": losses,
                    "events_participated": events_participated,
                    "evaluations": evaluations,
                    "achievements": achievements,
                    "belt_progressions": belt_progressions,
                }
            )

        summary = {
            "total_trainees": len(trainees_data),
            "total_evaluations": sum(len(t["evaluations"]) for t in trainees_data),
            "total_achievements": sum(len(t["achievements"]) for t in trainees_data),
            "total_belt_promotions": sum(
                len(t["belt_progressions"]) for t in trainees_data
            ),
        }

        return {
            "report_type": "trainee_skill_progression",
            "generated_date": date.today(),
            "trainee_id": trainee_id,
            "start_date": start_date,
            "end_date": end_date,
            "include_evaluations": include_evaluations,
            "include_achievements": include_achievements,
            "trainees": trainees_data,
            "summary": summary,
        }

    def tournament_participation_report(
        self,
        trainee_id: int = None,
        event_id: int = None,
        start_date: date = None,
        end_date: date = None,
        status_filter: str = None,
    ) -> Dict[str, Any]:
        """
        Generate tournament and competition participation report.
        Includes event registrations, matches, and participation history.

        Args:
            trainee_id: Filter by specific trainee ID
            event_id: Filter by specific event ID
            start_date: Filter from this date
            end_date: Filter until this date
            status_filter: Filter by event status

        Returns:
            dict containing tournament participation data
        """
        from core.models import (
            Event,
            EventRegistration,
            Match,
            Trainee,
            MatchResult,
        )

        events = Event.objects.select_related().order_by("-event_date")

        if event_id:
            events = events.filter(id=event_id)
        if start_date:
            events = events.filter(event_date__gte=start_date)
        if end_date:
            events = events.filter(event_date__lte=end_date)
        if status_filter:
            events = events.filter(status=status_filter)

        events_data = []

        for event in events:
            registrations = event.registrations.filter(status="registered").select_related(
                "trainee__profile__user"
            )

            if trainee_id:
                registrations = registrations.filter(trainee_id=trainee_id)

            participants_data = []
            for reg in registrations:
                trainee = reg.trainee
                user = trainee.profile.user

                matches = []
                matches_as_c1 = trainee.matches_as_competitor1.filter(event=event)
                matches_as_c2 = trainee.matches_as_competitor2.filter(event=event)
                all_matches = matches_as_c1.union(matches_as_c2).order_by("scheduled_time")

                for match in all_matches:
                    is_winner = match.winner_id == trainee.id

                    matches.append(
                        {
                            "match_id": match.id,
                            "match_type": match.get_match_type_display(),
                            "is_promotion_match": match.is_promotion_match,
                            "scheduled_time": match.scheduled_time,
                            "status": match.get_status_display(),
                            "is_winner": is_winner,
                            "opponent": (
                                match.competitor2.profile.user.get_full_name()
                                if match.competitor1_id == trainee.id
                                else match.competitor1.profile.user.get_full_name()
                            ),
                        }
                    )

                participants_data.append(
                    {
                        "trainee_id": trainee.id,
                        "name": f"{user.first_name} {user.last_name}".strip()
                        or user.username,
                        "email": user.email,
                        "belt_rank": trainee.get_belt_rank_display(),
                        "weight_class": trainee.weight_class,
                        "registered_at": reg.registered_at,
                        "matches_count": len(matches),
                        "matches": matches,
                    }
                )

            events_data.append(
                {
                    "event_id": event.id,
                    "name": event.name,
                    "event_date": event.event_date,
                    "location": event.location,
                    "status": event.get_status_display(),
                    "max_participants": event.max_participants,
                    "total_registrations": len(participants_data),
                    "participants": participants_data,
                }
            )

        summary = {
            "total_events": len(events_data),
            "total_participants": sum(e["total_registrations"] for e in events_data),
            "total_matches": sum(
                sum(p["matches_count"] for p in e["participants"]) for e in events_data
            ),
            "events_by_status": {},
        }

        for event in events_data:
            status = event["status"]
            summary["events_by_status"][status] = (
                summary["events_by_status"].get(status, 0) + 1
            )

        return {
            "report_type": "tournament_participation",
            "generated_date": date.today(),
            "trainee_id": trainee_id,
            "event_id": event_id,
            "start_date": start_date,
            "end_date": end_date,
            "status_filter": status_filter,
            "events": events_data,
            "summary": summary,
        }

    def performance_evaluation_report(
        self,
        trainee_id: int = None,
        start_date: date = None,
        end_date: date = None,
        evaluation_status: str = None,
        min_rating: int = None,
    ) -> Dict[str, Any]:
        """
        Generate detailed performance evaluation summary report.
        Includes all evaluation criteria and analysis.

        Args:
            trainee_id: Filter by specific trainee ID
            start_date: Filter from this date
            end_date: Filter until this date
            evaluation_status: Filter by status (pending, completed, archived)
            min_rating: Filter by minimum overall rating

        Returns:
            dict containing performance evaluation data
        """
        from core.models import TraineeEvaluation, Trainee

        evaluations = TraineeEvaluation.objects.select_related(
            "trainee__profile__user", "evaluator"
        )

        if trainee_id:
            evaluations = evaluations.filter(trainee_id=trainee_id)
        if start_date:
            evaluations = evaluations.filter(evaluated_at__date__gte=start_date)
        if end_date:
            evaluations = evaluations.filter(evaluated_at__date__lte=end_date)
        if evaluation_status:
            evaluations = evaluations.filter(status=evaluation_status)
        if min_rating:
            evaluations = evaluations.filter(overall_rating__gte=min_rating)

        evaluations = evaluations.order_by("-evaluated_at")

        evaluations_data = []
        for eval_obj in evaluations:
            user = eval_obj.trainee.profile.user
            evaluations_data.append(
                {
                    "id": eval_obj.id,
                    "trainee_id": eval_obj.trainee_id,
                    "trainee_name": f"{user.first_name} {user.last_name}".strip()
                    or user.username,
                    "trainee_email": user.email,
                    "current_belt_rank": eval_obj.trainee.get_belt_rank_display(),
                    "evaluator": (
                        f"{eval_obj.evaluator.first_name} {eval_obj.evaluator.last_name}"
                        if eval_obj.evaluator
                        else "N/A"
                    ),
                    "technique": eval_obj.technique,
                    "speed": eval_obj.speed,
                    "strength": eval_obj.strength,
                    "flexibility": eval_obj.flexibility,
                    "discipline": eval_obj.discipline,
                    "spirit": eval_obj.spirit,
                    "overall_rating": eval_obj.overall_rating,
                    "average_rating": eval_obj.average_rating,
                    "attendance_score": eval_obj.attendance_score,
                    "sparring_score": eval_obj.sparring_score,
                    "achievement_score": eval_obj.achievement_score,
                    "performance_score": eval_obj.performance_score,
                    "total_belt_points": eval_obj.total_belt_points,
                    "comments": eval_obj.comments,
                    "strengths": eval_obj.strengths,
                    "areas_for_improvement": eval_obj.areas_for_improvement,
                    "recommendations": eval_obj.recommendations,
                    "status": eval_obj.get_status_display(),
                    "evaluated_at": eval_obj.evaluated_at,
                    "next_evaluation_date": eval_obj.next_evaluation_date,
                }
            )

        summary = {
            "total_evaluations": len(evaluations_data),
            "completed_evaluations": sum(
                1 for e in evaluations_data if e["status"] == "Completed"
            ),
            "pending_evaluations": sum(
                1 for e in evaluations_data if e["status"] == "Pending"
            ),
            "average_overall_rating": (
                sum(e["overall_rating"] for e in evaluations_data) / len(evaluations_data)
                if evaluations_data
                else 0
            ),
            "average_technique": (
                sum(e["technique"] for e in evaluations_data) / len(evaluations_data)
                if evaluations_data
                else 0
            ),
            "average_speed": (
                sum(e["speed"] for e in evaluations_data) / len(evaluations_data)
                if evaluations_data
                else 0
            ),
            "average_strength": (
                sum(e["strength"] for e in evaluations_data) / len(evaluations_data)
                if evaluations_data
                else 0
            ),
            "average_discipline": (
                sum(e["discipline"] for e in evaluations_data) / len(evaluations_data)
                if evaluations_data
                else 0
            ),
            "by_belt": {},
            "rating_distribution": {},
        }

        for eval_obj in evaluations_data:
            belt = eval_obj["current_belt_rank"]
            summary["by_belt"][belt] = summary["by_belt"].get(belt, 0) + 1

            rating = eval_obj["overall_rating"]
            summary["rating_distribution"][rating] = (
                summary["rating_distribution"].get(rating, 0) + 1
            )

        return {
            "report_type": "performance_evaluation",
            "generated_date": date.today(),
            "trainee_id": trainee_id,
            "start_date": start_date,
            "end_date": end_date,
            "evaluation_status": evaluation_status,
            "min_rating": min_rating,
            "evaluations": evaluations_data,
            "summary": summary,
        }

    def competition_results_report(
        self,
        event_id: int = None,
        trainee_id: int = None,
        start_date: date = None,
        end_date: date = None,
        match_type: str = None,
    ) -> Dict[str, Any]:
        """
        Generate official competition results report.
        Includes match results, winners, scores, and detailed outcomes.

        Args:
            event_id: Filter by specific event ID
            trainee_id: Filter by specific trainee ID
            start_date: Filter from this date
            end_date: Filter until this date
            match_type: Filter by match type

        Returns:
            dict containing competition results data
        """
        from core.models import (
            Match,
            MatchResult,
            Event,
            Trainee,
        )

        matches = Match.objects.select_related(
            "event", "winner", "competitor1__profile__user", "competitor2__profile__user"
        ).filter(status="completed")

        if event_id:
            matches = matches.filter(event_id=event_id)
        if trainee_id:
            matches = matches.filter(
                Q(competitor1_id=trainee_id) | Q(competitor2_id=trainee_id)
            )
        if start_date:
            matches = matches.filter(scheduled_time__date__gte=start_date)
        if end_date:
            matches = matches.filter(scheduled_time__date__lte=end_date)
        if match_type:
            matches = matches.filter(match_type=match_type)

        matches = matches.order_by("-scheduled_time")

        matches_data = []
        for match in matches:
            results = match.results.select_related("judge")

            judge_results = []
            for result in results:
                judge_results.append(
                    {
                        "judge_name": result.judge.profile.user.get_full_name(),
                        "winner": result.winner.profile.user.get_full_name()
                        if result.winner
                        else "N/A",
                        "competitor1_score": result.competitor1_score,
                        "competitor2_score": result.competitor2_score,
                        "c1_sparring_score": result.c1_sparring_score,
                        "c1_penan_score": result.c1_penan_score,
                        "c1_judo_score": result.c1_judo_score,
                        "c1_breaking_score": result.c1_breaking_score,
                        "c2_sparring_score": result.c2_sparring_score,
                        "c2_penan_score": result.c2_penan_score,
                        "c2_judo_score": result.c2_judo_score,
                        "c2_breaking_score": result.c2_breaking_score,
                        "notes": result.notes,
                        "submitted_at": result.submitted_at,
                    }
                )

            matches_data.append(
                {
                    "match_id": match.id,
                    "event_id": match.event_id,
                    "event_name": match.event.name,
                    "event_date": match.event.event_date,
                    "match_type": match.get_match_type_display(),
                    "is_promotion_match": match.is_promotion_match,
                    "scheduled_time": match.scheduled_time,
                    "competitor1": f"{match.competitor1.profile.user.get_full_name()} ({match.competitor1.get_belt_rank_display()})",
                    "competitor2": f"{match.competitor2.profile.user.get_full_name()} ({match.competitor2.get_belt_rank_display()})",
                    "winner": (
                        f"{match.winner.profile.user.get_full_name()} ({match.winner.get_belt_rank_display()})"
                        if match.winner
                        else "No Winner"
                    ),
                    "results": judge_results,
                }
            )

        summary = {
            "total_matches": len(matches_data),
            "by_match_type": {},
            "by_event": {},
        }

        for match in matches_data:
            match_type = match["match_type"]
            summary["by_match_type"][match_type] = (
                summary["by_match_type"].get(match_type, 0) + 1
            )

            event = match["event_name"]
            summary["by_event"][event] = summary["by_event"].get(event, 0) + 1

        return {
            "report_type": "competition_results",
            "generated_date": date.today(),
            "event_id": event_id,
            "trainee_id": trainee_id,
            "start_date": start_date,
            "end_date": end_date,
            "match_type": match_type,
            "matches": matches_data,
            "summary": summary,
        }

    def trainee_milestones_report(
        self,
        trainee_id: int = None,
        start_date: date = None,
        end_date: date = None,
        achievement_type: str = None,
    ) -> Dict[str, Any]:
        """
        Generate key trainee milestones report.
        Includes achievements, belt promotions, and significant events.

        Args:
            trainee_id: Filter by specific trainee ID
            start_date: Filter from this date
            end_date: Filter until this date
            achievement_type: Filter by achievement type

        Returns:
            dict containing trainee milestones data
        """
        from core.models import (
            Trainee,
            TraineeAchievement,
            BeltRankProgress,
            EventRegistration,
            Match,
        )

        trainees = Trainee.objects.select_related("profile__user").filter(
            archived=False
        )

        if trainee_id:
            trainees = trainees.filter(id=trainee_id)

        trainees_data = []

        for trainee in trainees:
            user = trainee.profile.user

            milestones = []

            achievements = trainee.achievements.all()
            if start_date:
                achievements = achievements.filter(date_earned__gte=start_date)
            if end_date:
                achievements = achievements.filter(date_earned__lte=end_date)
            if achievement_type:
                achievements = achievements.filter(achievement_type=achievement_type)

            for ach_obj in achievements.order_by("-date_earned"):
                milestones.append(
                    {
                        "type": "achievement",
                        "title": ach_obj.title,
                        "description": ach_obj.description,
                        "achievement_type": ach_obj.get_achievement_type_display(),
                        "date": ach_obj.date_earned,
                        "points_awarded": ach_obj.points_awarded,
                    }
                )

            belt_promotions = trainee.belt_rank_progress.all()
            if start_date:
                belt_promotions = belt_promotions.filter(promoted_at__date__gte=start_date)
            if end_date:
                belt_promotions = belt_promotions.filter(promoted_at__date__lte=end_date)

            for bp_obj in belt_promotions.order_by("-promoted_at"):
                milestones.append(
                    {
                        "type": "belt_promotion",
                        "title": f"Belt Promotion: {bp_obj.get_old_belt_rank_display()} to {bp_obj.get_new_belt_rank_display()}",
                        "description": bp_obj.admin_notes
                        or "Belt rank promotion achieved",
                        "achievement_type": "belt_promotion",
                        "date": bp_obj.promoted_at.date(),
                        "points_earned": bp_obj.points_earned,
                    }
                )

            event_regs = trainee.event_registrations.filter(status="registered").select_related(
                "event"
            )
            if start_date:
                event_regs = event_regs.filter(event__event_date__gte=start_date)
            if end_date:
                event_regs = event_regs.filter(event__event_date__lte=end_date)

            for reg in event_regs.order_by("-registered_at"):
                milestones.append(
                    {
                        "type": "event_participation",
                        "title": f"Participated in {reg.event.name}",
                        "description": f"{reg.event.name} - {reg.event.location}",
                        "achievement_type": "event",
                        "date": reg.event.event_date,
                    }
                )

            won_matches = trainee.won_matches.filter(status="completed").select_related(
                "event"
            )
            if start_date:
                won_matches = won_matches.filter(scheduled_time__date__gte=start_date)
            if end_date:
                won_matches = won_matches.filter(scheduled_time__date__lte=end_date)

            for match in won_matches.order_by("-scheduled_time"):
                milestones.append(
                    {
                        "type": "match_win",
                        "title": f"Match Victory in {match.event.name}",
                        "description": f"{match.get_match_type_display()} - {match.get_status_display()}",
                        "achievement_type": "competition",
                        "date": match.scheduled_time.date(),
                    }
                )

            milestones.sort(key=lambda x: x["date"], reverse=True)

            trainees_data.append(
                {
                    "trainee_id": trainee.id,
                    "name": f"{user.first_name} {user.last_name}".strip() or user.username,
                    "email": user.email,
                    "current_belt_rank": trainee.get_belt_rank_display(),
                    "weight_class": trainee.weight_class,
                    "joined_date": trainee.joined_date,
                    "status": trainee.get_status_display(),
                    "milestones": milestones,
                    "total_milestones": len(milestones),
                }
            )

        summary = {
            "total_trainees": len(trainees_data),
            "total_milestones": sum(t["total_milestones"] for t in trainees_data),
            "milestone_types": {},
        }

        for trainee_data in trainees_data:
            for milestone in trainee_data["milestones"]:
                milestone_type = milestone["type"]
                summary["milestone_types"][milestone_type] = (
                    summary["milestone_types"].get(milestone_type, 0) + 1
                )

        return {
            "report_type": "trainee_milestones",
            "generated_date": date.today(),
            "trainee_id": trainee_id,
            "start_date": start_date,
            "end_date": end_date,
            "achievement_type": achievement_type,
            "trainees": trainees_data,
            "summary": summary,
        }
