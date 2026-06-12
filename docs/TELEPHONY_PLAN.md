# Telephony Plan — Phone Calls + SMS for EVERJUST.APP

## Goal

Replicate the Odoo 19 Enterprise "Phone" app experience on Community Edition
at near-zero recurring cost. Every feature a tenant would get from upgrading to
Enterprise should either work identically or have a clear equivalent.

## Constraint

No Twilio/Plivo production accounts. Self-hosted where possible.

---

## Enterprise Feature → Community Replacement Map

### VOICE — Softphone & Calling

| Enterprise feature | How we deliver it | Source |
|---|---|---|
| Softphone widget (systray, top-right) | `voip_oca` — identical placement + layout | OCA 19.0 (exists) |
| 4 tabs: Keypad, Recent, Contacts, Activities | `voip_oca` has 3 tabs: Recent, Activities, Contacts + numpad | OCA 19.0 |
| Click-to-dial (hover phone field → call icon) | `voip_oca` — green phone numbers, click to call | OCA 19.0 |
| Click-to-dial from chatter phone numbers | `voip_oca` — patches phone fields globally | OCA 19.0 |
| Incoming call popup + caller ID lookup | `voip_oca` — `voip.call` model + partner reverse lookup | OCA 19.0 |
| In-call controls: mute, hold, transfer, hang up | `voip_oca` — all implemented | OCA 19.0 |
| Call logging in chatter (auto on hang-up) | `voip_oca` — `voip.call` model, states: calling/ongoing/terminated/missed | OCA 19.0 |
| Call activity scheduling (Activities tab) | `voip_oca` — fetches due/overdue `mail.activity` of type "Call" | OCA 19.0 |
| Contact search from widget | `voip_oca` — search by name/phone/mobile/email | OCA 19.0 |
| Create contact from unknown caller | `voip_oca` — from Recent Calls tab | OCA 19.0 |
| Per-user SIP credentials | `voip_oca` — `voip_username`, `voip_password` on `res.users` | OCA 19.0 |
| PBX configuration screen | `voip_oca` — `voip.pbx` model (domain, WSS URL, mode) | OCA 19.0 |
| Navigate Odoo freely during active call | `voip_oca` — widget is overlay, persists across pages | OCA 19.0 |
| Call queues (strategy: ring-all, least-calls, etc.) | FusionPBX — native queue management with all strategies | FusionPBX |
| IVR / dial plans (visual editor) | FusionPBX — GUI-based dial plan editor | FusionPBX |
| Voicemail + voicemail-to-email | FusionPBX — per-extension voicemail, email notification | FusionPBX |
| Conference calling | FusionPBX — conference rooms with access codes | FusionPBX |
| Call recording | FusionPBX — per-extension or per-route recording | FusionPBX |
| Dynamic caller ID (company + per-user) | FusionPBX — outbound caller ID rules | FusionPBX |
| Music on hold | FusionPBX — upload MP3/WAV | FusionPBX |
| Agent login/logout for queues | FusionPBX — dynamic agents via dial codes | FusionPBX |

### SMS — Sending & Receiving

| Enterprise feature | How we deliver it | Source |
|---|---|---|
| SMS button on every phone field | Already in Community `sms` module — `phone_field.js` patches all PhoneField widgets | Odoo core |
| SMS Composer wizard (modal) | Already in Community — `sms.composer` with template selection, recipient validation | Odoo core |
| SMS templates (`sms.template`) | Already in Community — create templates linked to models | Odoo core |
| SMS logged in chatter (`message_type='sms'`) | Already in Community — threaded in chatter alongside emails/notes | Odoo core |
| Character counter + segment calculator | Already in Community — `sms_widget.js` | Odoo core |
| Bulk SMS / SMS Marketing | Already in Community — `mass_mailing_sms` module | Odoo core |
| CRM SMS integration (`crm_sms`) | Already in Community — auto-install bridge module | Odoo core |
| Sale SMS (`sale_sms`) | Already in Community — order confirmation SMS | Odoo core |
| Event SMS (`event_sms`) | Already in Community — event reminder SMS | Odoo core |
| Stock SMS (`stock_sms`) | Already in Community — delivery notification SMS | Odoo core |
| SMS sending backend (replaces Odoo IAP) | `everjust_sms_gateway` — override `sms.api._send_sms_batch()` to route through TextBee | Custom module |
| SMS receiving + threading | `everjust_sms_gateway` — webhook from TextBee → Odoo controller → chatter | Custom module |
| Phone number validation + formatting | Already in Community — `phone_validation` module (Google `phonenumbers` lib) | Odoo core |
| Phone blacklist | Already in Community — `phone.blacklist` model | Odoo core |

### What Enterprise has that we skip (not worth replicating)

| Feature | Why skip |
|---|---|
| Axivox management console integration | Axivox is a paid service; FusionPBX has its own GUI |
| Odoo IAP credit purchasing UI | We're not using IAP — TextBee is free |
| A/B testing for SMS campaigns | Nice-to-have; standard `mass_mailing_sms` still works for campaigns |
| Twilio provider module | We're using TextBee instead of Twilio |

---

## Key Insight: Less Custom Code Than Expected

**Voice:** `voip_oca` (OCA, 19.0 branch confirmed) already replicates ~90% of the Enterprise
softphone. It uses SIP.js, has the systray widget, click-to-dial, call logging, activities,
transfer/hold/mute — all of it. We just need a PBX for it to connect to.

**SMS:** Odoo Community already ships the entire SMS UI framework (`sms` module) —
composer wizard, templates, phone field buttons, chatter threading, character counter,
and all the bridge modules (CRM, Sales, Events, etc.). The ONLY thing missing is the
sending backend. Enterprise uses Odoo IAP (pay-per-message). We replace that single
function (`_send_sms_batch`) with a TextBee API call. That's one small module.

---

## Architecture

```
                         PSTN / Carriers
                               |
                      [SIP Trunk: VoIP.ms]
                       ~$0.85/DID + $0.005/min
                               |
                  [FusionPBX / FreeSWITCH]              [TextBee Server]
                  self-hosted, multi-tenant              (Docker, self-hosted)
                  queues, IVR, voicemail,                      |
                  recording, conferencing               [TextBee Android App]
                       |           |                    (old phone + SIM)
                [WSS/SIP]       [CDR API]                      |
                       |           |                    [REST API + Webhooks]
                       |           |                           |
    ┌──────────────────┴───────────┴───────────────────────────┘
    |                                                          |
    |              Odoo 19 Community Edition                    |
    |                                                          |
    |  ┌─────────────┐  ┌──────────────────────┐               |
    |  │ voip_oca    │  │ sms (Odoo core)      │               |
    |  │ (OCA 19.0)  │  │ + crm_sms            │               |
    |  │             │  │ + sale_sms            │               |
    |  │ • Softphone │  │ + event_sms           │               |
    |  │ • Click2dial│  │ + stock_sms           │               |
    |  │ • Call log  │  │ + mass_mailing_sms    │               |
    |  │ • Transfer  │  │                       │               |
    |  │ • Hold/Mute │  │ Composer, templates,  │               |
    |  └─────────────┘  │ phone field buttons   │               |
    |                    └──────────┬────────────┘               |
    |                               |                           |
    |                    ┌──────────┴────────────┐               |
    |                    │ everjust_sms_gateway  │←──────────────┘
    |                    │ (custom, ~200 lines)  │
    |                    │                       │
    |                    │ Overrides:            │
    |                    │ sms.api._send_batch() │
    |                    │ + webhook controller  │
    |                    │ for incoming SMS      │
    |                    └──────────────────────┘
    └──────────────────────────────────────────────
```

### Cost (per tenant, light usage)

| Component | Cost/month |
|---|---|
| FusionPBX + FreeSWITCH | $0 (self-hosted) |
| voip_oca + sms modules | $0 (open source) |
| everjust_sms_gateway | $0 (custom) |
| TextBee + Android phone | $0 (uses phone's plan) |
| SIP trunk — 1 DID | $0.85 |
| SIP trunk — 500 min | ~$2.50 |
| **Total** | **~$3.35** |

Zero-cost for dev/testing: extension-to-extension SIP calls are free,
TextBee SMS is free on any unlimited plan.

---

## Implementation Plan

### Phase 3A — Voice

**Step 1: Deploy FusionPBX** (1 day)

- Spin up on existing EC2 or a $6/mo DigitalOcean droplet
- Docker install: `docker pull fusionpbx/fusionpbx`
- Configure FreeSWITCH for WebSocket (wss://) on port 7443
- Create wildcard SSL cert or use existing `*.everjust.app`
- Accessible at `pbx.everjust.app` (add DNS A record)

**Step 2: Configure multi-tenant domains** (per tenant)

- Create one FusionPBX domain per Odoo tenant (e.g., `headsup`, `tcstartupweek`)
- Create extensions (e.g., 1001, 1002) for each user
- Set up voicemail boxes per extension
- Configure ring groups and basic IVR if needed

**Step 3: SIP trunk** (1 hour)

- Register VoIP.ms account ($15 deposit)
- Purchase 1 DID per tenant (or shared with routing)
- Point trunk at FusionPBX IP
- Test inbound/outbound PSTN calls

**Step 4: Install voip_oca in Odoo** (1 day)

- Clone OCA/connector-telephony 19.0 branch
- Copy `voip_oca/` to `addons/`
- Add to `EVERJUST_MODULES` in `provisioning.py`
- Install on existing tenants
- Configure `voip.pbx` record:
  - Domain: `pbx.everjust.app`
  - WebSocket: `wss://pbx.everjust.app:7443`
  - Mode: Production
- Configure per-user SIP credentials (voip tab on user form)
- Test: click-to-dial, incoming call popup, transfer, hold, mute

**Step 5: Provisioning automation**

- Extend `provisioning.py` to:
  - Create FusionPBX domain via FusionPBX API
  - Create admin extension (1001)
  - Configure voip.pbx record in new tenant DB
  - Set admin user SIP credentials

### Phase 3B — SMS

**Step 1: Deploy TextBee** (2 hours)

- Self-host TextBee server via Docker on existing infra
- Install TextBee Android app on a dedicated phone (old phone + Wi-Fi + SIM)
- Connect app to server, verify REST API (`POST /api/messages`)
- Test send/receive SMS through the API

**Step 2: Build `everjust_sms_gateway` module** (~200 lines, 1 day)

This is the ONLY custom code needed for SMS. Everything else exists in Odoo core.

```python
# What the module does:
#
# 1. Override sms.api._send_sms_batch() to route through TextBee
#    instead of Odoo IAP. This makes ALL existing SMS features work:
#    - SMS button on phone fields (phone_field.js)
#    - SMS Composer wizard
#    - SMS templates
#    - Chatter threading
#    - mass_mailing_sms campaigns
#    - crm_sms, sale_sms, event_sms, stock_sms bridges
#
# 2. Add a webhook controller for incoming SMS from TextBee.
#    Match incoming number → partner → create mail.message in chatter.
#
# 3. Configuration: TextBee server URL + API key in ir.config_parameter.
```

Module structure:
```
addons/everjust_sms_gateway/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── sms_api.py          # Override _send_sms_batch()
├── controllers/
│   ├── __init__.py
│   └── webhook.py           # POST /sms/incoming → chatter message
└── data/
    └── config_params.xml    # Default TextBee URL + key params
```

Key override:
```python
class SmsApi(models.AbstractModel):
    _inherit = "sms.api"

    def _send_sms_batch(self, messages):
        """Route SMS through TextBee instead of Odoo IAP."""
        gateway_url = self.env["ir.config_parameter"].sudo().get_param(
            "everjust.sms_gateway_url"
        )
        api_key = self.env["ir.config_parameter"].sudo().get_param(
            "everjust.sms_gateway_key"
        )
        results = []
        for msg in messages:
            # POST to TextBee API
            resp = requests.post(
                f"{gateway_url}/api/messages",
                json={"phone": msg["number"], "message": msg["content"]},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10,
            )
            if resp.ok:
                results.append({"state": "success", "credit": 0})
            else:
                results.append({"state": "server_error", "credit": 0})
        return results
```

Incoming SMS webhook:
```python
class SmsWebhook(http.Controller):
    @http.route("/sms/incoming", type="json", auth="none", csrf=False)
    def incoming_sms(self, **kwargs):
        """TextBee sends: {from, message, timestamp}"""
        phone = kwargs.get("from")
        body = kwargs.get("message")
        # Reverse lookup: find partner by phone
        partner = request.env["res.partner"].sudo().search(
            ["|", ("phone", "=", phone), ("mobile", "=", phone)], limit=1
        )
        if partner:
            partner.message_post(body=body, message_type="sms")
        return {"status": "ok"}
```

**Step 3: Test the full native experience**

After installing `everjust_sms_gateway`, ALL of these should work with zero
additional configuration because they already exist in Odoo Community:

- [ ] SMS icon next to every phone field → opens Composer
- [ ] SMS Composer with template selection + character counter
- [ ] SMS logged in chatter as `message_type='sms'`
- [ ] CRM: send SMS to leads/opportunities
- [ ] Sales: order confirmation SMS
- [ ] Events: event reminder SMS
- [ ] Stock: delivery notification SMS
- [ ] SMS Marketing: bulk campaigns from `mass_mailing_sms`
- [ ] Phone blacklist respected
- [ ] Incoming SMS → chatter message on matched partner

### Phase 3C — Polish & Parity

**Call history in Odoo** (voip_oca already does this via `voip.call` model)
- Verify call records link to correct partner/opportunity
- Add CDR sync from FusionPBX for calls made outside the browser (e.g., desk phones)

**Per-tenant DID management**
- Store DID assignment in control plane
- Display tenant's phone number in their Odoo settings
- Route inbound calls per-DID → correct FusionPBX domain

**Voicemail-to-email**
- FusionPBX natively supports this
- Configure email notification per extension
- Uses Resend (already configured for each tenant)

**SMS templates for common flows**
- Pre-create templates: appointment reminder, invoice follow-up, delivery notification
- Attach to automated actions where needed

**Provisioning automation**
- `provisioning.py` creates FusionPBX domain + admin extension
- Sets `voip.pbx` + user SIP creds in new tenant DB
- Configures TextBee gateway URL in `ir.config_parameter`

---

## What the User Sees (Native Experience)

### Making a call
1. Open any contact, lead, or invoice
2. Hover over the phone number → green phone icon appears
3. Click → softphone widget opens in top-right, call connects
4. During call: mute, hold, transfer buttons available
5. Navigate Odoo freely while on the call
6. Hang up → call automatically logged in the record's chatter
7. Mark the call activity as done

### Receiving a call
1. Incoming call notification in the softphone widget
2. Caller name displayed (matched from contacts)
3. Accept or reject
4. Call logged after hang-up

### Sending an SMS
1. Open any record with a phone number
2. Click the SMS icon next to the phone field
3. Composer wizard opens — pick a template or write custom message
4. Character counter shows segment count
5. Send → message logged in chatter as SMS
6. Works from CRM, Sales, Contacts, Events, everywhere

### Receiving an SMS
1. Incoming SMS matched to contact by phone number
2. Appears as a chatter message on the contact record
3. Visible alongside emails and internal notes

### SMS Marketing
1. Open SMS Marketing app (already in Community)
2. Create campaign → select recipients → write content
3. Send or schedule

---

## Resolved Questions

| Question | Answer |
|---|---|
| Does voip_oca have a 19.0 branch? | **Yes** — v19.0.1.0.0, actively maintained by Dixmit/etobella |
| Run FusionPBX on same EC2 or separate? | Start on same EC2; move to separate instance if resources constrained |
| One DID per tenant or shared? | One DID per tenant ($0.85/mo each) for proper caller ID |
| Android phone for TextBee? | Old phone on Wi-Fi + cheapest unlimited SIM ($15-25/mo shared across all tenants) |
| How much custom code? | ~200 lines for `everjust_sms_gateway`. Everything else exists. |

---

## Modules to Install (per tenant)

| Module | Source | Purpose |
|---|---|---|
| `voip_oca` | OCA/connector-telephony 19.0 | Softphone widget, click-to-dial, call logging |
| `everjust_sms_gateway` | Custom (build) | Replace Odoo IAP with TextBee for SMS sending/receiving |
| `sms` | Odoo core (already installed) | SMS framework, composer, templates, phone field buttons |
| `crm_sms` | Odoo core (auto-install) | CRM + SMS bridge |
| `sale_sms` | Odoo core (auto-install) | Sales + SMS bridge |
| `event_sms` | Odoo core (auto-install) | Events + SMS bridge |
| `stock_sms` | Odoo core (auto-install) | Delivery notifications |
| `mass_mailing_sms` | Odoo core | SMS Marketing app |
| `phone_validation` | Odoo core (already installed) | Number formatting, validation, blacklist |

---

## Alternatives Considered

| Option | Verdict |
|---|---|
| Twilio/Plivo as primary SMS | $0.007+/msg, adds up fast at scale |
| FreePBX | Not multi-tenant — needs one VM per tenant |
| Asterisk + asterisk_click2dial | OCA module not ported past 17.0; voip_oca is the successor |
| OCA sms_alternative_provider | Stuck on 16.0, not ported; easier to override `_send_sms_batch` directly |
| OCA mail_gateway (for SMS) | Not ported to 19.0; designed for WhatsApp/Telegram, not SMS |
| Jitsi/LiveKit/Matrix | WebRTC only — no PSTN connectivity |
| httpSMS | 200 msg/month hard cap |
| Google Voice API | Doesn't exist |
