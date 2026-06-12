# -*- coding: utf-8 -*-
"""Bridge between hr.attendance and OCA payroll.

Overrides the payslip's ``_compute_worked_days`` to use actual attendance
check-in/out records instead of the theoretical resource calendar.  This
means payslips reflect real hours worked, not just the contract schedule.

The ``worked_hours`` on each attendance record drives the calculation.
Employees who clock in/out via the Attendance app will automatically have
their payslip "Worked Days" line computed from those records.

If an employee has no attendance records for the period the method falls
back to the original calendar-based computation so salaried employees
without attendance tracking are unaffected.
"""

from datetime import datetime, time

from odoo import api, models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def _compute_worked_days(self, contract, day_from, day_to):
        """Compute worked days from actual attendance records.

        Falls back to the parent (calendar-based) computation when no
        attendance records exist for the period — so salaried employees
        on a fixed schedule are not affected.
        """
        employee = self.employee_id
        date_from = day_from.date() if isinstance(day_from, datetime) else day_from
        date_to = day_to.date() if isinstance(day_to, datetime) else day_to

        attendances = self.env["hr.attendance"].search([
            ("employee_id", "=", employee.id),
            ("check_in", ">=", datetime.combine(date_from, time.min)),
            ("check_in", "<=", datetime.combine(date_to, time.max)),
            ("check_out", "!=", False),
        ])

        if not attendances:
            # No attendance records — use the calendar-based default
            return super()._compute_worked_days(contract, day_from, day_to)

        # Sum actual hours and count distinct days
        total_hours = sum(attendances.mapped("worked_hours"))
        worked_days = len(set(a.check_in.date() for a in attendances))
        hours_per_day = total_hours / worked_days if worked_days else 0.0

        return {
            "name": "Attendance",
            "sequence": 1,
            "code": "ATTN",
            "number_of_days": worked_days,
            "number_of_hours": total_hours,
            "contract_id": contract.id,
        }
