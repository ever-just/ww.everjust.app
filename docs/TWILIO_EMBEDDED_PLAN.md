# Twilio Embedded Telephony — Implementation Plan

## Goal

Replace the Ringover Chrome extension with a fully embedded phone system inside
EVERJUST.APP. Users make/receive calls and send/receive SMS directly in the
browser — no extensions, no external apps, fully white-labeled.

## Reference Implementation

**Oduist Connect** (`github.com/oduist/connect_addons`) — 22,912 lines, uses
Twilio Voice JS SDK, has the exact architecture we need. Source is public.
License is proprietary (Oduist Proprietary License v1.1) so we cannot
redistribute it directly — we use it as a reference to build our own LGPL-3
module.

---

## Architecture

```
Browser (EVERJUST.APP)
├── OWL Softphone Widget
│   ├── Keypad / Dialer
│   ├── Call Controls (mute, hold, transfer, hangup)
│   ├── Call History tab
│   ├── Contacts tab
│   └── SMS Conversation view
│
│   Uses: @twilio/voice-sdk (WebRTC → Twilio)
│
└── Odoo Backend
    ├── TwiML App controllers (/twilio/webhook/*)
    │   ├── Inbound call routing
    │   ├── Call status callbacks
    │   ├── Voicemail handling
    │   └── IVR/auto-attendant
    │
    ├── Models
    │   ├── everjust.phone.call — call records, recordings, transcriptions
    │   ├── everjust.phone.number — provisioned numbers per tenant
    │   ├── everjust.phone.settings — Twilio credentials, config
    │   └── everjust.phone.sms — SMS conversations
    │
    └── Provisioning (control-plane)
        ├── Create Twilio subaccount per tenant
        ├── Purchase local number by area code
        └── Configure TwiML app + webhooks

Twilio Cloud
├── Voice (WebRTC ↔ PSTN bridge)
├── SMS/MMS
├── Subaccounts (per tenant)
├── Number provisioning
├── Call recording + transcription
└── Webhooks → Odoo
```

## Module Structure

```
addons/everjust_phone/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── phone_call.py         — Call records, status, recording links
│   ├── phone_number.py       — Provisioned numbers per tenant
│   ├── phone_sms.py          — SMS message model + conversation threading
│   ├── phone_settings.py     — Twilio SID, auth token, TwiML app SID
│   ├── res_partner.py        — Click-to-call button on contacts
│   ├── crm_lead.py           — Click-to-call on CRM leads
│   └── res_users.py          — Per-user phone preferences
├── controllers/
│   ├── twilio_webhooks.py    — TwiML endpoints for call routing
│   ├── token.py              — Generate Twilio access tokens for browser SDK
│   └── sms_webhook.py        — Inbound SMS webhook
├── static/
│   ├── lib/
│   │   └── twilio.min.js     — Twilio Voice JS SDK
│   └── src/
│       ├── components/
│       │   ├── phone/         — Main softphone widget (OWL)
│       │   │   ├── phone.js
│       │   │   ├── phone.xml
│       │   │   └── phone.scss
│       │   ├── dialer/        — Numpad + call initiation
│       │   ├── call_controls/ — Mute, hold, transfer, hangup
│       │   ├── call_history/  — Recent calls list
│       │   ├── contacts/      — Contact search + click-to-call
│       │   └── sms/           — SMS conversation view
│       ├── widgets/
│       │   └── phone_field.js — Click-to-call on phone fields
│       └── services/
│           └── phone_service.js — Twilio Device management
├── views/
│   ├── phone_call_views.xml
│   ├── phone_number_views.xml
│   ├── phone_sms_views.xml
│   ├── res_config_settings.xml
│   ├── res_partner_views.xml
│   └── menus.xml
├── security/
│   ├── groups.xml
│   └── ir.model.access.csv
└── data/
    └── config.xml
```

## Implementation Phases

### Phase 1 — Core Softphone (Week 1-2)

**Backend:**
- `phone_settings.py` — Store Twilio Account SID, Auth Token, TwiML App SID
- `phone_call.py` — Call model (direction, status, duration, recording_url, partner_id, lead_id)
- Token controller — Generate Twilio access tokens for the Voice JS SDK
  ```python
  @route('/phone/token', type='json', auth='user')
  def get_token(self):
      # Generate AccessToken with VoiceGrant
      token = AccessToken(account_sid, api_key, api_secret, identity=user.login)
      token.add_grant(VoiceGrant(outgoing_application_sid=twiml_app_sid))
      return {'token': token.to_jwt()}
  ```
- TwiML webhook controllers:
  - `/twilio/voice` — Route inbound calls (ring browser, voicemail fallback)
  - `/twilio/voice/status` — Call status updates (answered, completed, etc.)

**Frontend (OWL):**
- Phone service (`phone_service.js`):
  ```javascript
  // Initialize Twilio Device with token from backend
  const { token } = await this.orm.call('phone.token', 'get_token');
  this.device = new Twilio.Device(token);
  this.device.on('incoming', this.handleIncoming);
  ```
- Softphone widget in systray — dialer, call controls, call history
- Phone field widget — click any phone number to initiate call

**Result:** Make and receive calls from the browser. No extension needed.

### Phase 2 — SMS (Week 2-3)

**Backend:**
- `phone_sms.py` — SMS model threaded to partners
- SMS webhook controller — Receive inbound SMS from Twilio
- Override `sms.api._send_sms_batch()` to route through Twilio Programmable SMS
  (replaces both TextBee and the core sms_twilio module)

**Frontend:**
- SMS tab in softphone widget — conversation view per contact
- SMS composer from partner/lead forms

**Result:** Send/receive SMS in the app. Messages appear in chatter.

### Phase 3 — Multi-tenant + Provisioning (Week 3-4)

**Backend:**
- Twilio subaccount creation in `provisioning.py`:
  ```python
  sub = client.api.accounts.create(friendly_name=subdomain)
  # Buy a local number
  number = sub.incoming_phone_numbers.create(
      phone_number=available_numbers[0].phone_number
  )
  ```
- Store subaccount SID + auth token per tenant in `ir.config_parameter`
- Configure TwiML app + webhooks per tenant automatically

**Result:** Each tenant gets their own phone number, call history, and billing.

### Phase 4 — Polish (Week 4-5)

- Call recording playback in call history view
- Voicemail (TwiML `<Record>` on no-answer)
- IVR builder (basic — press 1 for X, 2 for Y)
- CRM integration — auto-create lead from unknown caller
- Call activity logging (schedule follow-up calls)
- Number selection UI for tenants (pick area code, buy number)

---

## Key Technical Decisions

| Decision | Choice | Why |
|---|---|---|
| Twilio SDK version | `@twilio/voice-sdk` 2.x | Current, WebRTC, maintained |
| Token generation | Twilio Access Token (API Key + Secret) | Short-lived, per-user, secure |
| Call routing | TwiML App + webhooks | Standard Twilio pattern |
| Multi-tenant | Twilio subaccounts | Isolated billing, numbers, logs |
| SMS | Twilio Programmable SMS | Same account, unified billing |
| Recording storage | Twilio-hosted (S3 optional later) | No infra needed |
| License | LGPL-3 | Distributable to tenants |

## Cost Per Tenant (estimated)

| Item | Cost/month |
|---|---|
| Local number | $1.15 |
| Outbound calls (200 min) | $2.80 |
| Inbound calls (100 min) | $0.85 |
| Browser SDK (300 min) | $1.20 |
| SMS (200 messages) | $1.66 |
| **Total** | **~$7.66** |

## What This Replaces

| Current | Replaced by |
|---|---|
| Ringover Chrome Extension ($44/user/mo) | Embedded softphone (Twilio ~$8/tenant/mo) |
| voip_oca (SIP softphone, can't connect to Twilio) | `everjust_phone` (Twilio Voice SDK) |
| everjust_sms_gateway (TextBee) | Twilio Programmable SMS |
| everjust_ringover (API sync module) | Native — calls/SMS happen inside Odoo |

## Dependencies

- Python: `twilio` (PyPI)
- JS: `@twilio/voice-sdk` (bundled in static/lib/)
- Twilio account with: Account SID, Auth Token, API Key + Secret, TwiML App

## Reference Code (Oduist Connect)

Key files to study as reference (NOT to copy — proprietary license):

| File | Lines | What to learn |
|---|---|---|
| `connect/static/src/components/phone/phone/phone.js` | 999 | Softphone UI architecture, Twilio Device init, call state machine |
| `connect/controllers/twilio_webhooks.py` | 157 | TwiML webhook patterns, signature verification |
| `connect/controllers/main.py` | 377 | Token generation, call initiation, settings API |
| `connect/models/call.py` | 1587 | Call model design, status tracking, recording handling |
| `connect/models/settings.py` | 976 | Twilio config management, subaccount handling |
| `connect/static/src/components/phone/tray/tray.js` | 109 | Systray integration pattern |

## Open Questions

- [ ] Use Twilio API Key + Secret (recommended) or Account SID + Auth Token for token generation?
- [ ] Recording storage: keep on Twilio or sync to Odoo attachments?
- [ ] Number porting: support transferring existing numbers to Twilio?
- [ ] WhatsApp: Twilio supports it — include in Phase 2 or defer?
- [ ] AI transcription: Twilio has built-in — enable by default or as add-on?
