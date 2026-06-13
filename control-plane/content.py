# -*- coding: utf-8 -*-
"""Structured content for app feature pages (/apps/*) and per-app docs
guides (/docs/guide-*). Keeping copy as data keeps templates generic and
pages consistent. All copy is original EVERJUST.APP content.
"""

# ── App feature pages (marketing depth behind the landing cards) ────────

APPS = {
    "crm-sales": {
        "name": "CRM & Sales",
        "icon": "chart-column",
        "tagline": "Every lead, followed up. Every deal, visible.",
        "summary": (
            "A pipeline your team will actually keep updated: leads come in, "
            "activities tell everyone what's next, and won deals flow straight "
            "into quotes and orders — with the full conversation history attached."
        ),
        "features": [
            ("kanban", "Pipeline you can see",
             "Drag deals across stages you define. Expected revenue, close dates, and "
             "probabilities roll up automatically, so the forecast is always live."),
            ("clock", "Next steps, never forgotten",
             "Every lead carries a scheduled next activity — call, email, meeting. "
             "Overdue items chase their owner, not the other way around."),
            ("mail", "The whole thread in one place",
             "Emails, calls, SMS, and notes log onto the customer record automatically. "
             "Anyone can pick up an account cold and sound informed."),
            ("file-text", "From won deal to quote",
             "Convert opportunities into quotations and orders without retyping — "
             "products, prices, and the customer come along."),
        ],
        "workflow": [
            "Capture leads by email, form, or manual entry — duplicates are flagged.",
            "Qualify and drag through your pipeline; schedule the next activity as you go.",
            "Win the deal and convert it to a quote; the record keeps the whole story.",
        ],
        "guide": "guide-crm-sales",
        "related": ["calls-sms", "documents", "projects"],
    },
    "projects": {
        "name": "Projects & Timesheets",
        "icon": "kanban",
        "tagline": "Plan the work. See the work. Bill the work.",
        "summary": (
            "Kanban boards for planning, tasks that hold their own discussion, and "
            "timesheets logged where the work happens — so status meetings get shorter "
            "and invoicing gets accurate."
        ),
        "features": [
            ("kanban", "Boards that match how you work",
             "Stages, tags, and milestones are yours to define per project. Switch to "
             "list, calendar, or Gantt-style views when planning ahead."),
            ("users", "Discussion lives on the task",
             "Comments, files, and decisions stay attached to the task — not lost in a "
             "chat scroll. Followers get notified on what they watch."),
            ("timer", "Hours logged in context",
             "Log time on the task as you finish it. Timesheets roll up by project, "
             "person, and week for review or billing."),
            ("chart-column", "Honest progress",
             "Burned hours vs. planned, overdue tasks, and workload per person — "
             "visible before they become surprises."),
        ],
        "workflow": [
            "Create a project, set its stages, and load the backlog.",
            "Assign tasks with deadlines; teammates discuss and attach files on the task.",
            "Log hours as work completes; review timesheets weekly per project or person.",
        ],
        "guide": "guide-projects",
        "related": ["documents", "hr-time-off", "crm-sales"],
    },
    "documents": {
        "name": "Documents",
        "icon": "folder-open",
        "tagline": "One organized home for every file.",
        "summary": (
            "A real document management system — not a dumping ground. Folders with "
            "permissions, tags and categories for findability, and every attachment "
            "from across your workspace searchable in one place."
        ),
        "features": [
            ("folder-open", "Folders with real permissions",
             "Access groups control who can read, edit, or delete per directory — "
             "HR files stay with HR, contracts with the people who need them."),
            ("search", "Find it in seconds",
             "Tags, categories, and full filtering mean the file you need is a search "
             "away, not a folder spelunking trip."),
            ("file-text", "Attachments, centralized",
             "Files attached to deals, tasks, and employees surface here too — one "
             "library, not ten silos."),
            ("database", "Bulk in, bulk out",
             "Drag-and-drop uploads, and any selection downloads as a single ZIP. "
             "Your data is never locked in."),
        ],
        "workflow": [
            "Create directories for how your company thinks — clients, legal, HR, finance.",
            "Set access groups per directory; sensitive folders stay restricted.",
            "Upload, tag, and let search do the remembering.",
        ],
        "guide": "guide-documents",
        "related": ["esign", "knowledge", "projects"],
    },
    "esign": {
        "name": "eSign",
        "icon": "signature",
        "tagline": "Signatures in minutes, not mail rooms.",
        "summary": (
            "Send any PDF for legally-binding electronic signature. Place fields, "
            "assign roles, and track every envelope — signed copies file themselves "
            "back into Documents."
        ),
        "features": [
            ("signature", "Drag fields onto the page",
             "Signature, initials, date, and text fields go exactly where you want "
             "them, assigned per signer role."),
            ("users", "Multiple signers, right order",
             "Route to several people at once or in sequence. Everyone signs from a "
             "simple link — no account required."),
            ("clock", "Know where it stands",
             "See who has viewed, who has signed, and who needs a nudge. Reminders "
             "are one click."),
            ("shield-check", "Audit trail included",
             "Completed documents carry a full signing log, and the signed PDF is "
             "stored with the record it belongs to."),
        ],
        "workflow": [
            "Upload the PDF and place fields for each signer role.",
            "Send — each signer gets a secure link and signs from any device.",
            "Track progress and find the completed, audit-trailed PDF in Documents.",
        ],
        "guide": "guide-esign",
        "related": ["documents", "crm-sales", "hr-time-off"],
    },
    "knowledge": {
        "name": "Knowledge",
        "icon": "book-open",
        "tagline": "Write it once. Stop re-explaining it.",
        "summary": (
            "Wiki-style pages for the things your team keeps asking: processes, "
            "policies, how-tos. Versioned, organized by category, and linkable from "
            "anywhere — including straight onto a contact."
        ),
        "features": [
            ("book-open", "Pages with structure",
             "Categories group related pages; templates give new pages a consistent "
             "skeleton so docs don't rot into chaos."),
            ("refresh-cw", "Every change, versioned",
             "Full history on every page — compare versions, see who changed what, "
             "and roll back when needed."),
            ("badge-check", "Approval when it matters",
             "Policy pages can require a reviewer's approval before changes publish."),
            ("users", "Knowledge where work happens",
             "Link pages to contacts and records so account context lives with the "
             "account."),
        ],
        "workflow": [
            "Create categories that mirror how your team thinks — onboarding, ops, policies.",
            "Write pages from templates; link related pages instead of repeating.",
            "Let version history and approvals keep the truth trustworthy.",
        ],
        "guide": "guide-knowledge",
        "related": ["documents", "projects", "hr-time-off"],
    },
    "hr-time-off": {
        "name": "HR & Time Off",
        "icon": "users",
        "tagline": "People ops without the spreadsheet sprawl.",
        "summary": (
            "Employee records, contracts, leave policies, and attendance in one "
            "place. Requests flow to managers, balances compute themselves, and the "
            "team calendar shows who's out before you schedule that meeting."
        ),
        "features": [
            ("users", "One record per person",
             "Role, manager, contract, documents, and history — the employee file "
             "that's actually complete."),
            ("calendar-days", "Time off that runs itself",
             "Define leave types and allocation rules. Employees request in two "
             "clicks; managers approve from their inbox; balances update live."),
            ("clock", "Attendance, captured",
             "Clock in and out from the workspace. Worked time feeds payroll without "
             "re-entry."),
            ("shield-check", "Private by default",
             "HR data is permission-fenced — visible to HR and the right managers, "
             "invisible to everyone else."),
        ],
        "workflow": [
            "Add employees with their contracts and managers.",
            "Set leave types and yearly allocations once.",
            "Approvals, balances, and the out-of-office calendar take care of themselves.",
        ],
        "guide": "guide-hr-time-off",
        "related": ["payroll", "projects", "documents"],
    },
    "payroll": {
        "name": "Payroll",
        "icon": "banknote",
        "tagline": "Payslips computed from reality.",
        "summary": (
            "Salary structures and rules turn contracts into payslips — and worked "
            "days come from actual clock-in/out attendance, not optimistic averages. "
            "Run the whole company in one batch."
        ),
        "features": [
            ("settings", "Rules you control",
             "Build salary structures from rules — base, allowances, deductions, "
             "contributions — and reuse them across contracts."),
            ("clock", "Attendance-driven worked days",
             "Payslip worked days reconcile against real attendance records, so pay "
             "matches presence."),
            ("banknote", "Batch runs",
             "Generate payslips for everyone at once, review exceptions, confirm, "
             "and export for your accountant."),
            ("file-text", "Registers and reports",
             "Contribution registers and payslip detail reports are built in for "
             "filing and audits."),
        ],
        "workflow": [
            "Define salary structures and assign them on contracts.",
            "Each period, generate a payslip batch — worked days pull from attendance.",
            "Review, confirm, and export the results.",
        ],
        "guide": "guide-payroll",
        "related": ["hr-time-off", "documents", "projects"],
    },
    "calls-sms": {
        "name": "Calls & SMS",
        "icon": "phone",
        "tagline": "Your phone system, inside the CRM.",
        "summary": (
            "Click any number to call, take notes while you talk, and let the call "
            "log itself on the contact. Texts work the same way — sent from records, "
            "threaded with the rest of the conversation."
        ),
        "features": [
            ("phone", "Click-to-dial everywhere",
             "Every phone number in the workspace is callable. The softphone overlay "
             "follows you across pages mid-call."),
            ("message-square", "Two-way SMS on the record",
             "Send texts from any phone field — templates included. Replies thread "
             "into the contact's history automatically."),
            ("clock", "Calls that log themselves",
             "Duration, direction, and your notes attach to the contact, so 'did we "
             "call them?' has an answer."),
            ("zap", "Built for follow-up",
             "Pair with CRM activities: call from the pipeline, log the outcome, "
             "schedule the next touch — without leaving the deal."),
        ],
        "workflow": [
            "Click a number anywhere — contact, lead, or task.",
            "Talk with the softphone overlay while you navigate and take notes.",
            "The call and any texts land on the record's timeline automatically.",
        ],
        "guide": "guide-calls-sms",
        "related": ["crm-sales", "projects", "hr-time-off"],
    },
}


# ── Per-app docs guides (task-oriented how-tos) ──────────────────────────
# Each guide: title, icon, blurb (for cards/search), intro, and sections of
# (heading, html). Rendered by templates/docs/_guide.html.

APP_GUIDES = {
    "guide-crm-sales": {
        "title": "CRM & Sales",
        "icon": "chart-column",
        "blurb": "Set up your pipeline, work leads, and convert wins to quotes.",
        "intro": "How to set up a pipeline that matches your sales process and keep every lead moving.",
        "sections": [
            ("Set up your pipeline", """
<p>Open <b>CRM</b> from the app grid. The default stages (New → Qualified → Proposition → Won) are a starting point — rename, add, or remove stages by clicking the gear on each column. Keep it to 4–6 stages your team can answer "what does it mean to be here?" about.</p>"""),
            ("Create and qualify leads", """
<p>Add leads with <b>New</b>, or forward emails to your sales alias to create them automatically. Each card carries the company, contact, expected revenue, and probability.</p>
<ul><li>Set <b>expected revenue</b> and <b>close date</b> early — the forecast uses them.</li>
<li>Use tags for segments you'll want to filter later (industry, source, size).</li></ul>"""),
            ("Always schedule the next activity", """
<p>The discipline that makes CRM work: every open deal should have a scheduled activity. Click the clock icon on a card and pick <i>Call</i>, <i>Email</i>, or <i>Meeting</i> with a due date. Your activity inbox shows today's follow-ups; overdue ones turn red.</p>"""),
            ("Log the conversation", """
<p>Emails to the customer, <a href="/docs/guide-calls-sms">calls and texts</a>, and internal notes all land in the chatter at the bottom of the deal. Use <b>Log note</b> for internal context and <b>Send message</b> for customer-visible email.</p>"""),
            ("Win and convert to a quote", """
<p>Drag the deal to <b>Won</b>, then create a quotation from it — the customer and contact come along. Lost deals get a <b>lost reason</b>, which makes your loss report worth reading at quarter end.</p>"""),
            ("Reports worth checking weekly", """
<ul><li><b>Pipeline by stage</b> — where revenue is sitting.</li>
<li><b>Activities</b> — who's keeping up with follow-ups.</li>
<li><b>Lost reasons</b> — what's actually killing deals.</li></ul>"""),
        ],
    },
    "guide-projects": {
        "title": "Projects & Timesheets",
        "icon": "kanban",
        "blurb": "Boards, tasks, deadlines, and logging hours where work happens.",
        "intro": "Run projects on kanban boards and capture hours without a separate time tracker.",
        "sections": [
            ("Create a project", """
<p>Open <b>Project</b> and create one project per real-world effort (client engagement, product area, internal ops). Set the stages for its board — e.g. <i>Backlog → In progress → Review → Done</i>. Stages are per-project, so client work and internal ops don't have to share a workflow.</p>"""),
            ("Work with tasks", """
<ul><li>Create tasks with an assignee and deadline; drag them across stages as work moves.</li>
<li>Discuss <i>in the task</i> — comments, files, and decisions stay attached and searchable.</li>
<li>Use checklists for subtasks and tags for cross-cutting themes.</li></ul>"""),
            ("Log timesheets", """
<p>On any task, add a timesheet line with the hours spent and a short description. Do it when you finish the work — accuracy drops fast after the fact. Hours roll up on the task and the project.</p>"""),
            ("Review workload and progress", """
<p>The project dashboard shows hours logged vs. planned, open vs. overdue tasks, and load per person. Check it before the status meeting and the status meeting gets shorter.</p>"""),
            ("Weekly timesheet review", """
<p>Open <b>Timesheets</b> for the grid view by person and week — useful for approvals, invoicing inputs, and spotting under-logged days.</p>"""),
        ],
    },
    "guide-documents": {
        "title": "Documents",
        "icon": "folder-open",
        "blurb": "Folders, permissions, tags, and bulk upload/download.",
        "intro": "Set up a document library with real permissions, then let search do the filing.",
        "sections": [
            ("Plan your directory tree", """
<p>Open <b>Documents</b>. Create top-level directories for how your company thinks — <i>Clients</i>, <i>Legal</i>, <i>HR</i>, <i>Finance</i>. Shallow and predictable beats deep and clever.</p>"""),
            ("Set permissions with access groups", """
<p>Each directory can carry <b>access groups</b> that define who can read, create, edit, or delete inside it. Create one group per audience (e.g. <i>HR only</i>, <i>Managers</i>) and attach it to the right directories. Subdirectories inherit unless you override.</p>"""),
            ("Upload and organize", """
<ul><li>Drag and drop files or whole batches into a directory.</li>
<li>Add <b>tags</b> (status: signed, draft) and <b>categories</b> (type: contract, invoice) — they're the difference between storage and findability.</li></ul>"""),
            ("Find anything", """
<p>Use the search bar with tag and category filters. Attachments added elsewhere in the workspace (on deals, tasks, employees) are indexed here too.</p>"""),
            ("Bulk download", """
<p>Select multiple files and download them as one ZIP — handy for audits, handoffs, and your own peace of mind that nothing is locked in.</p>"""),
        ],
    },
    "guide-esign": {
        "title": "eSign",
        "icon": "signature",
        "blurb": "Prepare a PDF, route signers, track to completion.",
        "intro": "From PDF to signed-and-archived in four steps.",
        "sections": [
            ("Prepare the document", """
<p>Open <b>eSign</b> and upload your PDF. Drag fields onto the page — signature, initials, date, free text — and assign each field to a <b>role</b> (Customer, Manager). Save frequently-used documents as templates.</p>"""),
            ("Send for signature", """
<p>Click <b>Send</b>, map each role to a real person (name + email), and choose simultaneous or sequential signing. Signers receive a secure link and sign from any device — they don't need an account.</p>"""),
            ("Track and remind", """
<p>The request shows per-signer status: sent, viewed, signed. Send a reminder with one click instead of a "just checking in" email.</p>"""),
            ("After completion", """
<p>Everyone gets the final PDF; the signed copy carries an audit trail (who, when, from where) and is archived in <a href="/docs/guide-documents">Documents</a> with the record it relates to.</p>"""),
        ],
    },
    "guide-knowledge": {
        "title": "Knowledge",
        "icon": "book-open",
        "blurb": "Pages, categories, templates, history, and approvals.",
        "intro": "Build an internal wiki your team will actually read — and trust.",
        "sections": [
            ("Organize with categories", """
<p>Open <b>Knowledge</b> and create categories that mirror how people search: <i>Onboarding</i>, <i>How we work</i>, <i>Policies</i>, <i>Tools</i>. A page belongs to one category; cross-link related pages rather than duplicating.</p>"""),
            ("Write pages from templates", """
<p>Give each category a <b>template</b> (Summary → Details → Conclusion → Resources) so new pages start consistent. Keep pages short: one question, answered well, beats a novel nobody finishes.</p>"""),
            ("Use history and approvals", """
<p>Every edit creates a version — compare and restore from the page's history. For policy pages, enable <b>approval</b> so changes publish only after a reviewer signs off.</p>"""),
            ("Put knowledge on records", """
<p>Pages can be linked to contacts, so account-specific runbooks live on the account. See it on the contact's <i>Pages</i> tab.</p>"""),
        ],
    },
    "guide-hr-time-off": {
        "title": "HR & Time Off",
        "icon": "users",
        "blurb": "Employee records, leave types, approvals, attendance.",
        "intro": "Set up people ops once; let requests and balances run themselves.",
        "sections": [
            ("Create employee records", """
<p>Open <b>Employees</b> and add each person with their job position, manager, and work information. Attach contracts and HR documents directly to the record — permissions keep them HR-only.</p>"""),
            ("Configure time off", """
<ul><li>Define <b>leave types</b> (vacation, sick, unpaid) and whether they need approval.</li>
<li>Create <b>allocations</b> per year (e.g. 20 days vacation) individually or in bulk.</li></ul>"""),
            ("Requests and approvals", """
<p>Employees request time off in two clicks from their own profile or the Time Off app. Managers approve from their activity inbox; balances update instantly and the team calendar shows who's out.</p>"""),
            ("Attendance", """
<p>With check-in/check-out enabled, worked hours accumulate per employee — visible to managers and consumed by <a href="/docs/guide-payroll">Payroll</a> as real worked days.</p>"""),
            ("Privacy", """
<p>HR data is fenced by access rights: HR officers see everything, managers see their team, employees see themselves. Review who holds HR roles in <a href="/docs/invite-team">user settings</a>.</p>"""),
        ],
    },
    "guide-payroll": {
        "title": "Payroll",
        "icon": "banknote",
        "blurb": "Salary structures, rules, batches, and attendance-driven pay.",
        "intro": "Turn contracts plus attendance into reviewed, exportable payslips.",
        "sections": [
            ("Set up salary structures", """
<p>Open <b>Payroll → Configuration</b>. A <b>structure</b> is a set of <b>rules</b> — basic pay, allowances, deductions, contributions — that compute payslip lines. Start from the provided structure and adjust rules to your policy.</p>"""),
            ("Assign contracts", """
<p>Each employee needs a running <b>contract</b> with their wage and structure. Payslips read everything from the contract, so keep it current when compensation changes.</p>"""),
            ("Run a payslip batch", """
<ol><li>Create a <b>batch</b> for the period and generate payslips for all (or selected) employees.</li>
<li><b>Worked days reconcile against attendance</b> — actual clock-in/out records, not assumptions.</li>
<li>Review computed slips, fix exceptions, then confirm the batch.</li></ol>"""),
            ("Reports and export", """
<p>Use payslip detail reports and contribution registers for filing; export lists to spreadsheet for your accountant.</p>"""),
        ],
    },
    "guide-calls-sms": {
        "title": "Calls & SMS",
        "icon": "phone",
        "blurb": "Click-to-dial, call logging, and two-way texting from records.",
        "intro": "Use the built-in softphone and SMS so every conversation lands on the record.",
        "sections": [
            ("Make calls", """
<p>Click any phone number — on a contact, lead, or task — and the softphone dials. The widget overlays the page and persists while you navigate, so you can open the customer's history mid-call. Use the dialpad for ad-hoc numbers.</p>"""),
            ("Log outcomes", """
<p>When the call ends, duration and direction are saved on the record. Add your notes in the chatter while they're fresh; schedule the next activity right there.</p>"""),
            ("Send SMS", """
<p>Every phone field has an SMS button. Compose directly or pick a <b>template</b>; messages appear in the record's conversation thread alongside emails and calls.</p>"""),
            ("Receive replies", """
<p>Inbound texts thread automatically into the same conversation — no separate inbox to check.</p>"""),
            ("Tips", """
<ul><li>Templates make appointment reminders and follow-ups one click.</li>
<li>Respect the blacklist: numbers that opt out are excluded automatically.</li></ul>"""),
        ],
    },
}
