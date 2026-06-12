# Telephony Plan — Phone Calls + SMS for EVERJUST.APP

## Constraint

Zero or near-zero recurring cost. No Twilio/Plivo production accounts. Self-hosted where possible.

## Problem

Odoo 19 Community Edition has **no VoIP or SMS capability**. The "Phone" app is Enterprise-only. We need to add voice calling and texting to the multi-tenant platform without paying per-minute or per-message.

---

## Recommended Architecture

```
                      PSTN / Carriers
                            |
                   [SIP Trunk: VoIP.ms]
                    ~$0.85/DID + $0.005/min
                            |
               [FusionPBX / FreeSWITCH]         [TextBee]
               (self-hosted, multi-tenant)       (Android phone → SMS API)
               (one install, all tenants)        ($0 — uses phone's plan)
                    |            |                     |
             [WebSocket/SIP]  [REST API]          [REST API + Webhooks]
                    |            |                     |
            [OCA voip_oca]   [everjust_sms]       [everjust_sms]
            (click-to-dial)  (custom Odoo module)  (send/receive SMS)
            (browser VoIP)
                    |                 |
              [Odoo 19 CE — Multi-Tenant]
```

### Cost breakdown (per tenant, light usage)

| Component | Monthly cost |
|---|---|
| FusionPBX + FreeSWITCH (self-hosted) | $0 |
| OCA voip_oca module | $0 |
| TextBee SMS gateway (Android phone) | $0 |
| SIP trunk — 1 DID (VoIP.ms) | $0.85 |
| SIP trunk — 500 minutes | ~$2.50 |
| **Total** | **~$3.35/tenant** |

For zero-cost dev/testing: SIP-to-SIP calling between extensions is free. TextBee SMS is free on any unlimited phone plan.

---

## Components

### 1. FusionPBX (Voice — PBX)

**Why FusionPBX over FreePBX:** FusionPBX is natively multi-tenant. One install serves all tenants with isolated domains, extensions, and routing. FreePBX needs one VM per tenant.

- **License:** MPL 1.1 (free, open source)
- **Engine:** FreeSWITCH
- **Features:** IVR, voicemail, call recording, ring groups, conferencing, WebSocket for browser calling
- **Install:** Docker or bare metal on the existing EC2 or a separate small instance
- **Multi-tenant:** Each Odoo tenant maps to a FusionPBX domain

### 2. OCA voip_oca (Voice — Odoo integration)

- **Source:** [OCA/connector-telephony](https://github.com/OCA/connector-telephony)
- **How it works:** SIP.js in the browser connects via WebSocket to FusionPBX. Click-to-dial from any partner/contact form. Incoming call popup with caller ID lookup.
- **No server-side PBX connection needed** — it's all browser-based
- **Check:** Verify 19.0 branch exists; if not, port from 18.0

### 3. TextBee (SMS — Gateway)

- **Source:** [github.com/vernu/textbee](https://github.com/vernu/textbee)
- **How it works:** Android app + self-hosted server. REST API to send SMS; webhooks for incoming SMS. Uses the phone's SIM/carrier — no per-message cost.
- **Requirements:** One Android phone with an active SIM (any unlimited plan)
- **Capacity:** Limited by carrier throughput (~1 msg/sec). Fine for business SMS, not bulk marketing.

### 4. everjust_sms (SMS — Custom Odoo module)

New module to build. Connects Odoo's messaging system to the TextBee API:

- Send SMS from partner forms (phone number field)
- Receive SMS via webhook → create chatter messages
- Log all SMS in mail.message for audit trail
- Multi-tenant: route messages per-tenant if needed, or share a single gateway

### 5. SIP Trunk Provider (PSTN connectivity)

For calling real phone numbers (not just extension-to-extension):

| Provider | DID/month | Outbound/min | Inbound | Why |
|---|---|---|---|---|
| **VoIP.ms** (recommended) | $0.85 | $0.005 | $0.009/min | Cheapest, no contract, $15 min deposit |
| **Telnyx** | $1.00 | $0.008 | Included | Carrier-owned network, great quality |
| **SignalWire** | Varies | ~50% less than Twilio | ~50% less | Built by FreeSWITCH team |

---

## Implementation Phases

### Phase 3A — Voice (FusionPBX + voip_oca)

1. **Deploy FusionPBX** on the existing EC2 (or a $6/mo DigitalOcean droplet)
   - Install via Docker
   - Configure WebSocket (wss://) for browser SIP
   - Create one domain per tenant
   - Set up extensions for admin users

2. **Configure SIP trunk** (VoIP.ms or Telnyx)
   - Register account, get a DID
   - Point trunk at FusionPBX

3. **Install OCA voip_oca** in Odoo
   - Add to `addons/` or install from OCA repo
   - Configure SIP server URL (wss://pbx.everjust.app)
   - Test click-to-dial, incoming call popup

4. **Per-tenant provisioning**
   - Add FusionPBX domain creation to `provisioning.py`
   - Auto-create admin extension when tenant is provisioned

### Phase 3B — SMS (TextBee + custom module)

1. **Deploy TextBee server** (Docker on existing infra)
   - Install Android app on a dedicated phone
   - Connect to self-hosted server
   - Verify REST API works (send test SMS)

2. **Build `everjust_sms` module**
   - Model: `sms.message` (phone, body, direction, status, tenant)
   - Controller: webhook endpoint for incoming SMS
   - Views: send SMS button on partner form, SMS log in chatter
   - Config: TextBee API URL + auth token in `ir.config_parameter`

3. **Test end-to-end**
   - Send SMS from Odoo partner form → TextBee → phone
   - Receive SMS → webhook → Odoo chatter message

### Phase 3C — Polish

- Call history logging in Odoo (via FreeSWITCH CDR → Odoo)
- Voicemail-to-email
- SMS templates for common messages
- Per-tenant DID assignment in the control plane

---

## Alternatives considered

| Option | Verdict |
|---|---|
| Twilio/Plivo/Telnyx as primary | Too expensive at scale ($0.008/min + $0.007/msg adds up) |
| FreePBX | Not multi-tenant — needs one VM per tenant |
| Asterisk directly | Lower-level than FusionPBX, more ops work for same result |
| Jitsi/LiveKit/Matrix | WebRTC only — no PSTN, can't call real phone numbers |
| Kannel/Jasmin | SMS only, needs SMPP carrier account ($$), overkill |
| httpSMS | 200 msg/month hard cap — useless for production |
| Google Voice API | Doesn't exist — no programmatic API |

---

## Open questions

- [ ] Does OCA voip_oca have a 19.0 branch, or do we port from 18.0?
- [ ] Run FusionPBX on same EC2 or separate instance? (RAM/CPU check needed)
- [ ] One DID per tenant or shared DID with routing rules?
- [ ] Android phone for TextBee: use an old phone on Wi-Fi or buy a $30 prepaid?
