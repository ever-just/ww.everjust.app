# -*- coding: utf-8 -*-
"""Twilio webhook endpoints for call routing and status updates.

These are called by Twilio's servers, NOT by the browser. They return
TwiML (XML) that tells Twilio what to do with the call.
"""
import logging

from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

TWIML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'


def twiml_response(body):
    return Response(
        TWIML_HEADER + body,
        content_type="text/xml",
        status=200,
    )


class TwilioWebhookController(http.Controller):

    # ── Outbound call (from browser via TwiML App) ──────────────────────

    @http.route("/phone/twiml/outbound", type="http", auth="none", csrf=False, methods=["POST"])
    def outbound_call(self, **kw):
        """TwiML App voice URL — called when browser initiates an outbound call.

        The browser sends the 'To' number via the Voice SDK connection params.
        We return TwiML that dials out to that number from our Twilio number.
        """
        to_number = kw.get("To", "")
        ICP = request.env["ir.config_parameter"].sudo()
        from_number = ICP.get_param("everjust_phone.phone_number") or ""

        if not to_number:
            return twiml_response("<Response><Say>No number specified.</Say></Response>")

        _logger.info("Outbound call to %s from %s", to_number, from_number)

        # Log the call
        request.env["everjust.phone.call"].sudo().log_call_from_webhook(kw)

        return twiml_response(
            '<Response>'
            '<Dial callerId="%s" record="record-from-answer-dual" '
            'recordingStatusCallback="/phone/webhook/recording">'
            '<Number>%s</Number>'
            '</Dial>'
            '</Response>' % (from_number, to_number)
        )

    # ── Inbound call ────────────────────────────────────────────────────

    @http.route("/phone/twiml/inbound", type="http", auth="none", csrf=False, methods=["POST"])
    def inbound_call(self, **kw):
        """Webhook for inbound calls to our Twilio number.

        Rings the browser client (Voice SDK). If no answer after 25 seconds,
        falls back to voicemail.
        """
        from_number = kw.get("From", "")
        _logger.info("Inbound call from %s", from_number)

        # Log the call
        request.env["everjust.phone.call"].sudo().log_call_from_webhook(kw)

        # Get all connected browser identities (ring all logged-in users)
        # For now, ring a default identity — multi-user routing comes in Phase 4
        return twiml_response(
            '<Response>'
            '<Dial timeout="25" record="record-from-answer-dual" '
            'recordingStatusCallback="/phone/webhook/recording" '
            'action="/phone/twiml/voicemail">'
            '<Client>default_user</Client>'
            '</Dial>'
            '</Response>'
        )

    # ── Voicemail (no answer fallback) ──────────────────────────────────

    @http.route("/phone/twiml/voicemail", type="http", auth="none", csrf=False, methods=["POST"])
    def voicemail(self, **kw):
        """Called when the <Dial> in inbound_call times out or is rejected."""
        dial_status = kw.get("DialCallStatus", "")
        if dial_status == "completed":
            return twiml_response("<Response></Response>")

        return twiml_response(
            '<Response>'
            '<Say voice="Polly.Joanna">Sorry, no one is available right now. '
            'Please leave a message after the beep.</Say>'
            '<Record maxLength="120" action="/phone/twiml/voicemail/done" '
            'transcribe="true" transcribeCallback="/phone/webhook/transcription" />'
            '<Say voice="Polly.Joanna">We did not receive a recording. Goodbye.</Say>'
            '</Response>'
        )

    @http.route("/phone/twiml/voicemail/done", type="http", auth="none", csrf=False, methods=["POST"])
    def voicemail_done(self, **kw):
        """Called after voicemail recording completes."""
        return twiml_response(
            '<Response>'
            '<Say voice="Polly.Joanna">Thank you. Your message has been recorded. Goodbye.</Say>'
            '<Hangup/>'
            '</Response>'
        )

    # ── Status callbacks ────────────────────────────────────────────────

    @http.route("/phone/webhook/status", type="http", auth="none", csrf=False, methods=["POST"])
    def call_status(self, **kw):
        """Twilio calls this when call status changes (ringing, answered, completed, etc.)."""
        try:
            request.env["everjust.phone.call"].sudo().log_call_from_webhook(kw)
        except Exception as exc:
            _logger.error("Call status webhook error: %s", exc)
        return Response("OK", status=200)

    @http.route("/phone/webhook/recording", type="http", auth="none", csrf=False, methods=["POST"])
    def recording_status(self, **kw):
        """Called when a call recording is ready."""
        call_sid = kw.get("CallSid", "")
        recording_url = kw.get("RecordingUrl", "")
        recording_sid = kw.get("RecordingSid", "")
        if call_sid and recording_url:
            call = request.env["everjust.phone.call"].sudo().search(
                [("call_sid", "=", call_sid)], limit=1
            )
            if call:
                call.write({
                    "recording_url": recording_url,
                    "recording_sid": recording_sid,
                })
        return Response("OK", status=200)

    @http.route("/phone/webhook/transcription", type="http", auth="none", csrf=False, methods=["POST"])
    def transcription_status(self, **kw):
        """Called when voicemail transcription is ready."""
        recording_sid = kw.get("RecordingSid", "")
        transcription = kw.get("TranscriptionText", "")
        if recording_sid and transcription:
            call = request.env["everjust.phone.call"].sudo().search(
                [("recording_sid", "=", recording_sid)], limit=1
            )
            if call:
                call.write({"transcription": transcription})
                if call.partner_id:
                    call.partner_id.message_post(
                        body="<b>Voicemail transcription:</b> %s" % transcription,
                        message_type="notification",
                        subtype_xmlid="mail.mt_note",
                    )
        return Response("OK", status=200)

    # ── Inbound SMS ─────────────────────────────────────────────────────

    @http.route("/phone/webhook/sms", type="http", auth="none", csrf=False, methods=["POST"])
    def inbound_sms(self, **kw):
        """Twilio sends inbound SMS here."""
        try:
            request.env["everjust.phone.sms"].sudo().log_sms_from_webhook(kw)
        except Exception as exc:
            _logger.error("SMS webhook error: %s", exc)
        return twiml_response("<Response></Response>")
