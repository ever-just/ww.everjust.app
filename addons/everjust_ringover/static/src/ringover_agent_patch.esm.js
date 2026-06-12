/** @odoo-module **/

import { VoipAgent } from "@voip_oca/services/voip_agent_service.esm";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

/**
 * Patch the VoIP agent to use Ringover's callback API instead of SIP.
 * When a user clicks "call" from the softphone, this triggers a server-side
 * RPC to /ringover/initiate_call, which calls Ringover's /callback endpoint.
 * Ringover then rings the agent's phone first, and auto-dials the recipient.
 */
patch(VoipAgent.prototype, {
    async connectAgent() {
        // Skip SIP connection entirely — we use Ringover's API instead.
        // Just mark as connected so the UI is usable.
        if (this.voip.mode === "prod") {
            this.voip.status = "connected";
            console.info("Ringover mode: using callback API instead of SIP");
        } else {
            console.info("Voip agent is not available in non-production mode");
        }
    },

    async call({ number, partner }) {
        this.voip.isOpened = true;
        this.voip.isFolded = false;
        var phone_number = number;
        if (!number && partner) {
            phone_number = partner.phone;
        }
        if (!phone_number) {
            this.notification.add(_t("No phone number to call."), { type: "warning" });
            return;
        }

        // Create call record in Odoo
        await this.createCall({
            partner_id: partner && partner.id,
            phone_number: phone_number,
            type_call: "outgoing",
            state: "calling",
        });
        this.voip.inCall = true;

        if (this.voip.mode === "prod") {
            // Use Ringover callback API via server RPC
            try {
                const result = await this.orm.call(
                    "ringover.call",
                    "initiate_call",
                    [phone_number, phone_number],
                );
                if (result && result.error) {
                    this.notification.add(
                        _t("Ringover call failed: %(error)s", { error: result.error }),
                        { type: "danger" }
                    );
                    this.voip.inCall = false;
                    this.stopTone();
                } else {
                    this.notification.add(
                        _t("Ringover is connecting your call to %(number)s...", {
                            number: phone_number,
                        }),
                        { type: "info" }
                    );
                    // Auto-end the UI call state after 5 seconds
                    // (Ringover handles the actual call on the phone)
                    setTimeout(() => {
                        this.voip.inCall = false;
                        this.stopTone();
                    }, 5000);
                }
            } catch (error) {
                this.notification.add(
                    _t("Failed to initiate call: %(error)s", {
                        error: error.message || String(error),
                    }),
                    { type: "danger" }
                );
                this.voip.inCall = false;
            }
        }
    },
});
