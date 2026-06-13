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


# ── App catalog taxonomy ────────────────────────────────────────────────
# Ordered categories for the /apps catalog and the home app grid.

CATEGORIES = {
    "sales":         {"name": "Sales",           "icon": "chart-column", "blurb": "Win deals and sell, online and in person."},
    "finance":       {"name": "Finance",         "icon": "banknote",     "blurb": "Invoice, get paid, and track every cost."},
    "operations":    {"name": "Operations",      "icon": "kanban",       "blurb": "Run projects, stock, purchasing, and production."},
    "hr":            {"name": "Human Resources", "icon": "users",        "blurb": "Hire, manage, and pay your team."},
    "marketing":     {"name": "Marketing",       "icon": "sparkles",     "blurb": "Reach your audience and measure what works."},
    "website":       {"name": "Website",         "icon": "globe",        "blurb": "Build a site, sell online, and publish content."},
    "productivity":  {"name": "Productivity",    "icon": "layout-grid",  "blurb": "Documents, signatures, knowledge, and chat."},
    "communication": {"name": "Communication",   "icon": "phone",        "blurb": "Calls, SMS, and a shared address book."},
}

# Category + "what it replaces" for the 8 detailed apps (kept out of their
# entries above to keep those readable). 'replaces' powers the pricing
# savings calculator.
_APP_META = {
    "crm-sales":   {"category": "sales",         "replaces": ["Salesforce", "HubSpot CRM", "Pipedrive"]},
    "projects":    {"category": "operations",    "replaces": ["Asana", "Monday.com", "Trello", "Jira"]},
    "documents":   {"category": "productivity",  "replaces": ["Dropbox", "Google Drive", "SharePoint"]},
    "esign":       {"category": "productivity",  "replaces": ["DocuSign", "Dropbox Sign", "Adobe Acrobat Sign"]},
    "knowledge":   {"category": "productivity",  "replaces": ["Notion", "Confluence"]},
    "hr-time-off": {"category": "hr",            "replaces": ["BambooHR", "Rippling"]},
    "payroll":     {"category": "hr",            "replaces": ["Gusto", "ADP"]},
    "calls-sms":   {"category": "communication", "replaces": ["RingCentral", "Aircall", "Twilio"]},
}
for _slug, _meta in _APP_META.items():
    APPS[_slug].update(_meta)

# Lighter catalog entries for the rest of the suite. Each tenant's workspace
# includes these out of the box; detailed pages can be deepened over time.
_MORE_APPS = {
    "sales": {
        "name": "Sales", "icon": "hand-coins", "category": "sales",
        "tagline": "Quotes to orders, without the back-and-forth.",
        "summary": "Build quotations, send them for online acceptance, and turn them into confirmed orders and invoices — pricelists, discounts, and upsells included.",
        "replaces": ["PandaDoc", "Qwilr"],
    },
    "pos": {
        "name": "Point of Sale", "icon": "credit-card", "category": "sales",
        "tagline": "Ring up sales in-store and online — one catalog.",
        "summary": "A touch-friendly point of sale for shops and counters that shares products, customers, and stock with the rest of your workspace, online or off.",
        "replaces": ["Square", "Shopify POS", "Lightspeed"],
    },
    "invoicing": {
        "name": "Invoicing", "icon": "receipt", "category": "finance",
        "tagline": "Send invoices, get paid, see the cash.",
        "summary": "Create and send branded invoices, track payments, automate reminders, and watch what's owed — wired to your sales and contacts.",
        "replaces": ["QuickBooks", "FreshBooks", "Wave"],
    },
    "expenses": {
        "name": "Expenses", "icon": "wallet", "category": "finance",
        "tagline": "Snap a receipt, get reimbursed.",
        "summary": "Employees submit expenses with a photo; managers approve from their inbox; approved expenses flow to accounting and payroll.",
        "replaces": ["Expensify", "SAP Concur"],
    },
    "inventory": {
        "name": "Inventory", "icon": "package", "category": "operations",
        "tagline": "Know what you have, everywhere.",
        "summary": "Real-time stock across locations with barcode receiving, deliveries, and replenishment — updated by every sale, purchase, and transfer.",
        "replaces": ["Fishbowl", "Cin7"],
    },
    "purchase": {
        "name": "Purchase", "icon": "shopping-cart", "category": "operations",
        "tagline": "Turn needs into purchase orders.",
        "summary": "Request quotes from vendors, compare them, and issue purchase orders that update inventory and vendor bills automatically.",
        "replaces": ["Coupa", "Procurify"],
    },
    "manufacturing": {
        "name": "Manufacturing", "icon": "factory", "category": "operations",
        "tagline": "From bill of materials to finished goods.",
        "summary": "Plan and track production orders, manage bills of materials and work centers, and keep stock accurate as you build.",
        "replaces": ["Katana", "MRPeasy"],
    },
    "maintenance": {
        "name": "Maintenance", "icon": "wrench", "category": "operations",
        "tagline": "Keep equipment running, not broken.",
        "summary": "Schedule preventive maintenance, log breakdowns, and track requests against every machine and asset.",
        "replaces": ["UpKeep", "Fiix"],
    },
    "recruitment": {
        "name": "Recruitment", "icon": "user-plus", "category": "hr",
        "tagline": "From job post to hire, organized.",
        "summary": "Publish openings, collect applications into a hiring pipeline, schedule interviews, and move candidates to onboarding.",
        "replaces": ["Greenhouse", "Lever", "Workable"],
    },
    "fleet": {
        "name": "Fleet", "icon": "truck", "category": "hr",
        "tagline": "Every vehicle, cost, and contract tracked.",
        "summary": "Manage company vehicles, drivers, leases, services, and fuel costs in one register.",
        "replaces": ["Fleetio"],
    },
    "email-marketing": {
        "name": "Email Marketing", "icon": "mail", "category": "marketing",
        "tagline": "Design, send, and measure campaigns.",
        "summary": "Build emails with a drag-and-drop editor, segment from your real contacts, and track opens, clicks, and conversions.",
        "replaces": ["Mailchimp", "Campaign Monitor"],
    },
    "events": {
        "name": "Events", "icon": "calendar-days", "category": "marketing",
        "tagline": "Run events people actually attend.",
        "summary": "Create event pages, register or sell tickets, send reminders, and check attendees in — all tied to your CRM.",
        "replaces": ["Eventbrite", "Cvent"],
    },
    "surveys": {
        "name": "Surveys", "icon": "clipboard-list", "category": "marketing",
        "tagline": "Ask, measure, improve.",
        "summary": "Build surveys and quizzes, share them anywhere, and analyze responses — for feedback, NPS, or assessments.",
        "replaces": ["SurveyMonkey", "Typeform"],
    },
    "website": {
        "name": "Website Builder", "icon": "globe", "category": "website",
        "tagline": "A real website, no developer required.",
        "summary": "Drag-and-drop pages with built-in SEO, forms, and blocks — connected to the same data as the rest of your apps.",
        "replaces": ["Wix", "Squarespace", "WordPress"],
    },
    "ecommerce": {
        "name": "eCommerce", "icon": "shopping-bag", "category": "website",
        "tagline": "An online store wired to your stock.",
        "summary": "Sell online with a storefront that shares products, pricing, and inventory with your workspace — orders flow straight in.",
        "replaces": ["Shopify", "BigCommerce"],
    },
    "blog": {
        "name": "Blog", "icon": "file-text", "category": "website",
        "tagline": "Publish content that ranks.",
        "summary": "Write and publish posts with SEO controls and your brand's look, right alongside your website.",
        "replaces": ["Medium", "Ghost"],
    },
    "elearning": {
        "name": "eLearning", "icon": "graduation-cap", "category": "website",
        "tagline": "Courses for customers or staff.",
        "summary": "Build courses with videos, quizzes, and certificates — for customer education or internal training.",
        "replaces": ["Teachable", "Thinkific"],
    },
    "livechat": {
        "name": "Live Chat", "icon": "message-circle", "category": "website",
        "tagline": "Talk to visitors while they're interested.",
        "summary": "A live-chat widget for your site that routes conversations to your team and logs them against the contact.",
        "replaces": ["Intercom", "Drift", "Tidio"],
    },
    "calendar": {
        "name": "Calendar", "icon": "calendar-days", "category": "productivity",
        "tagline": "Everyone's schedule, shared.",
        "summary": "Shared calendars, meeting scheduling, and reminders that connect to CRM activities, projects, and time off.",
        "replaces": ["Google Calendar", "Calendly"],
    },
    "discuss": {
        "name": "Discuss", "icon": "message-square", "category": "productivity",
        "tagline": "Team chat where the work is.",
        "summary": "Channels and direct messages built into the workspace, so conversations sit next to the records they're about.",
        "replaces": ["Slack", "Microsoft Teams"],
    },
    "contacts": {
        "name": "Contacts", "icon": "contact", "category": "communication",
        "tagline": "One address book for everything.",
        "summary": "The shared directory of customers, vendors, and people that every app draws from — no more duplicate lists.",
        "replaces": ["Google Contacts"],
    },
}
APPS.update(_MORE_APPS)


def apps_by_category():
    """Return an ordered {category_slug: [(app_slug, app), ...]} mapping."""
    grouped = {cat: [] for cat in CATEGORIES}
    for slug, app in APPS.items():
        grouped.setdefault(app.get("category", "productivity"), []).append((slug, app))
    return grouped


# ── "Cut your software bill" calculator ─────────────────────────────────
# Typical list prices for the point tools EVERJUST replaces, so visitors can
# estimate what their current stack costs vs one flat plan. Figures are
# rounded public ballparks labelled as estimates in the UI. type: "user"
# (per user / month) or "flat" (per month regardless of seats).
CALCULATOR_TOOLS = [
    {"id": "crm",      "label": "CRM (Salesforce, HubSpot)",        "price": 25, "type": "user"},
    {"id": "account",  "label": "Accounting (QuickBooks)",          "price": 30, "type": "flat"},
    {"id": "projects", "label": "Projects (Asana, Monday)",         "price": 12, "type": "user"},
    {"id": "chat",     "label": "Team chat (Slack)",                "price": 8,  "type": "user"},
    {"id": "files",    "label": "File storage (Dropbox)",           "price": 15, "type": "user"},
    {"id": "esign",    "label": "eSignatures (DocuSign)",           "price": 25, "type": "user"},
    {"id": "email",    "label": "Email marketing (Mailchimp)",      "price": 20, "type": "flat"},
    {"id": "store",    "label": "Online store (Shopify)",           "price": 39, "type": "flat"},
    {"id": "hr",       "label": "HR (BambooHR)",                    "price": 8,  "type": "user"},
    {"id": "payroll",  "label": "Payroll (Gusto)",                  "price": 40, "type": "flat"},
]


# ── Depth for the catalog apps (features + day-to-day flow) ─────────────
# Merged into APPS so every app page has the same substance as the eight
# original guides. Icons are all already in the sprite.
APP_DEPTH = {
    "sales": {
        "features": [
            ("file-text", "Quotes that close themselves", "Build a quote, send a link, and let the customer review, accept, and pay online — no PDF ping-pong."),
            ("layers", "Pricelists and bundles", "Set prices per customer, region, or quantity, and add optional products and upsells to any quote."),
            ("refresh-cw", "Quote to order to invoice", "An accepted quote becomes a confirmed order and a draft invoice automatically — nothing retyped."),
        ],
        "workflow": [
            "Build a quotation from your catalog, with discounts and optional extras.",
            "Send it; the customer reviews, accepts, and pays online.",
            "It rolls into a sales order and invoice without re-entry.",
        ],
    },
    "pos": {
        "features": [
            ("credit-card", "Built for speed", "A touch screen that scans, takes payment, and prints or emails the receipt in seconds."),
            ("package", "Stock stays accurate", "Every sale updates inventory in real time, from the same catalog as the rest of your workspace."),
            ("wifi-off", "Works offline", "Keep selling if the connection drops; orders sync the moment you're back online."),
        ],
        "workflow": [
            "Open a register session and ring up products by scan, search, or favorites.",
            "Take cash or card and hand over a printed or emailed receipt.",
            "Close the session — sales, stock, and cash reconcile automatically.",
        ],
    },
    "invoicing": {
        "features": [
            ("receipt", "Send and get paid", "Email branded invoices with an online pay button; customers settle by card or bank transfer."),
            ("clock", "Reminders that chase for you", "Overdue invoices follow up automatically on a schedule you set."),
            ("chart-column", "Know what you're owed", "Outstanding balances, aging, and cash position at a glance."),
        ],
        "workflow": [
            "Create an invoice from an order or from scratch.",
            "Send it with an online payment link; reminders go out on their own.",
            "Match payments and watch what's owed update live.",
        ],
    },
    "expenses": {
        "features": [
            ("smartphone", "Snap and submit", "Employees photograph a receipt and submit an expense in seconds, from their phone."),
            ("check", "Approve from your inbox", "Managers approve or reject with one tap; approved expenses flow to accounting."),
            ("banknote", "Reimburse and reconcile", "Approved expenses become bills to pay and reconcile against company cards."),
        ],
        "workflow": [
            "An employee photographs a receipt and submits the expense.",
            "Their manager approves it from the activity inbox.",
            "It posts to accounting and is queued for reimbursement.",
        ],
    },
    "inventory": {
        "features": [
            ("package", "Real-time stock", "Quantities update on every sale, purchase, and transfer, across all your locations."),
            ("search", "Barcodes everywhere", "Receive, pick, pack, and count with a scanner or your phone camera."),
            ("refresh-cw", "Replenish automatically", "Set reordering rules and let the system raise purchase or production orders when stock runs low."),
        ],
        "workflow": [
            "Set up your warehouses, locations, and products.",
            "Receive deliveries and fulfill orders with barcode scanning.",
            "Let reordering rules keep stock topped up automatically.",
        ],
    },
    "purchase": {
        "features": [
            ("shopping-cart", "Requests to orders", "Turn needs into requests for quotation, compare vendor prices, and issue purchase orders."),
            ("package", "Wired to stock and bills", "Confirmed orders update incoming inventory and create draft vendor bills to check."),
            ("badge-check", "Vendor terms remembered", "Per-vendor pricing, lead times, and minimum quantities apply automatically."),
        ],
        "workflow": [
            "Raise a request for quotation, or let low stock raise it for you.",
            "Compare vendor responses and confirm a purchase order.",
            "Receive the goods; the vendor bill is ready to reconcile.",
        ],
    },
    "manufacturing": {
        "features": [
            ("factory", "Production orders", "Plan and track manufacturing from bill of materials to finished goods."),
            ("layers", "Bills of materials", "Define what goes into each product, including sub-assemblies and by-products."),
            ("package", "Stock stays in sync", "Components are consumed and finished goods added as you build, so inventory is always right."),
        ],
        "workflow": [
            "Define the bill of materials and work centers for a product.",
            "Launch a manufacturing order and track each work step.",
            "Mark it done; components and finished stock update automatically.",
        ],
    },
    "maintenance": {
        "features": [
            ("wrench", "Preventive schedules", "Plan recurring maintenance so equipment gets serviced before it breaks."),
            ("clipboard-list", "Breakdown requests", "Anyone can log a fault against a machine; the team triages from one board."),
            ("chart-column", "Equipment history", "Every request and service stays on the asset's record, so patterns are obvious."),
        ],
        "workflow": [
            "Register your equipment and set preventive schedules.",
            "Staff log breakdowns; the team triages and assigns them.",
            "Close requests and build a service history per machine.",
        ],
    },
    "recruitment": {
        "features": [
            ("user-plus", "One hiring pipeline", "Publish openings and move every applicant through the stages you define."),
            ("calendar-days", "Interviews, organized", "Book interviews, share feedback, and keep the team aligned on each candidate."),
            ("folder-open", "Resumes in one place", "Applications, CVs, and notes live on the candidate record, not in someone's inbox."),
        ],
        "workflow": [
            "Post a job and collect applications into your pipeline.",
            "Screen, interview, and score candidates as a team.",
            "Hire, and move the new starter into onboarding.",
        ],
    },
    "fleet": {
        "features": [
            ("truck", "Every vehicle tracked", "Drivers, models, plates, and assignments in one register."),
            ("receipt", "Costs and contracts", "Track leases, insurance, services, and fuel against each vehicle."),
            ("clock", "Renewals on time", "Get ahead of contract and service due dates instead of chasing them."),
        ],
        "workflow": [
            "Add your vehicles and assign drivers.",
            "Log services, fuel, and contracts as they happen.",
            "Watch upcoming renewals and costs per vehicle.",
        ],
    },
    "email-marketing": {
        "features": [
            ("mail", "Drag-and-drop emails", "Design campaigns with blocks and your branding — no HTML required."),
            ("users", "Segment from real data", "Target lists built from your actual contacts, customers, and activity."),
            ("chart-column", "See what worked", "Opens, clicks, and conversions tracked back to revenue."),
        ],
        "workflow": [
            "Build an email with the drag-and-drop editor.",
            "Pick a segment of your contacts and send or schedule it.",
            "Track opens and clicks, then refine the next one.",
        ],
    },
    "events": {
        "features": [
            ("calendar-days", "Pages and tickets", "Publish an event page and sell or register attendees online."),
            ("mail", "Reminders that show up", "Automated confirmations and reminders cut no-shows."),
            ("clipboard-list", "Easy check-in", "Scan tickets at the door; attendance flows back to your CRM."),
        ],
        "workflow": [
            "Create the event, set tickets, and publish the page.",
            "Attendees register or buy; reminders go out automatically.",
            "Check them in at the door and follow up afterward.",
        ],
    },
    "surveys": {
        "features": [
            ("clipboard-list", "Build any survey", "Questionnaires, quizzes, and feedback forms with logic and scoring."),
            ("globe", "Share anywhere", "Send by email or drop a link; collect responses from anyone."),
            ("chart-column", "Read the results", "Live charts and per-question breakdowns, exportable for deeper analysis."),
        ],
        "workflow": [
            "Build your survey with the question types you need.",
            "Share it by email or public link.",
            "Watch responses come in and analyze the results.",
        ],
    },
    "website": {
        "features": [
            ("globe", "Drag-and-drop pages", "Build pages from blocks with your fonts and colors — no developer."),
            ("search", "SEO built in", "Titles, metadata, sitemaps, and clean URLs handled for you."),
            ("layers", "Connected to your data", "Forms, products, and content share the same database as the rest of your apps."),
        ],
        "workflow": [
            "Pick a starting layout and edit blocks in place.",
            "Add pages, forms, and your branding.",
            "Publish — mobile and SEO are handled.",
        ],
    },
    "ecommerce": {
        "features": [
            ("shopping-bag", "A real storefront", "Sell online with product pages, variants, and a checkout that converts."),
            ("package", "Stock-aware", "The store shares inventory and pricing with your workspace; orders flow straight in."),
            ("credit-card", "Pay your way", "Connect the payment providers you already use."),
        ],
        "workflow": [
            "Add products — they share your catalog and stock.",
            "Design the store and set shipping and payment.",
            "Orders arrive in your workspace, ready to fulfill.",
        ],
    },
    "blog": {
        "features": [
            ("file-text", "Write and publish", "A clean editor with your brand's look, right beside your website."),
            ("search", "Built to rank", "SEO controls, tags, and clean URLs on every post."),
            ("users", "Grow an audience", "Comments, subscriptions, and social sharing built in."),
        ],
        "workflow": [
            "Write a post with images and formatting.",
            "Set its SEO and publish or schedule it.",
            "Readers subscribe, comment, and share.",
        ],
    },
    "elearning": {
        "features": [
            ("graduation-cap", "Courses that teach", "Build courses from videos, documents, and quizzes."),
            ("badge-check", "Certificates and progress", "Track who completed what and issue certificates automatically."),
            ("users", "For customers or staff", "Use it for customer education or internal training, public or private."),
        ],
        "workflow": [
            "Create a course and add lessons and quizzes.",
            "Invite learners — customers or your team.",
            "Track completion and award certificates.",
        ],
    },
    "livechat": {
        "features": [
            ("message-circle", "Chat on your site", "A widget that lets visitors talk to your team in real time."),
            ("users", "Routed to the right person", "Conversations go to the right team, with canned responses to move fast."),
            ("contact", "Logged on the contact", "Every chat is saved against the visitor's record for context next time."),
        ],
        "workflow": [
            "Add the chat widget to your site pages.",
            "Your team answers visitor questions live.",
            "Each conversation is saved against the contact.",
        ],
    },
    "calendar": {
        "features": [
            ("calendar-days", "One shared calendar", "See your team's schedule, meetings, and time off in one view."),
            ("users", "Book without the back-and-forth", "Share availability and let people pick a slot."),
            ("refresh-cw", "Tied to your work", "Meetings link to CRM activities, projects, and contacts."),
        ],
        "workflow": [
            "Connect calendars and set your availability.",
            "Book meetings or share a link for others to book.",
            "Everything links back to the related record.",
        ],
    },
    "discuss": {
        "features": [
            ("message-square", "Channels and DMs", "Team chat built into the workspace, organized by channel."),
            ("layers", "Next to the work", "Conversations sit beside the records they're about, not in a separate app."),
            ("mail", "Notifications that matter", "Follow what you care about and mute the rest."),
        ],
        "workflow": [
            "Create channels for teams and topics.",
            "Chat, share files, and mention teammates.",
            "Discussions stay linked to the records they touch.",
        ],
    },
    "contacts": {
        "features": [
            ("contact", "One address book", "Customers, vendors, and people every app draws from."),
            ("search", "Find anyone fast", "Search and filter by company, tag, or activity."),
            ("layers", "Shared everywhere", "The same contact powers CRM, invoicing, projects, and more — no duplicates."),
        ],
        "workflow": [
            "Add companies and the people inside them.",
            "Tag and organize them for easy filtering.",
            "Every app uses the same records automatically.",
        ],
    },
}
for _slug, _depth in APP_DEPTH.items():
    if _slug in APPS:
        APPS[_slug].update(_depth)
