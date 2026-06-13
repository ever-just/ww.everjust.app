/** @odoo-module **/

import { reactive } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { loadBundle } from "@web/core/assets";

/**
 * Phone service — manages the Twilio Device, call state, and provides
 * methods for the softphone widget to make/receive/control calls.
 */
export const phoneService = {
    dependencies: ["orm", "notification"],
    start(env, { orm, notification }) {
        const state = reactive({
            // UI state
            isOpen: false,
            activeTab: "dialer", // dialer | history | contacts
            // Connection
            status: "disconnected", // disconnected | connecting | ready | on-call
            identity: "",
            // Active call
            callDirection: "",
            callNumber: "",
            callPartner: "",
            callDuration: 0,
            isMuted: false,
            // Data
            recentCalls: [],
        });

        let device = null;
        let activeConnection = null;
        let durationTimer = null;

        async function connect() {
            if (state.status !== "disconnected") return;
            state.status = "connecting";
            try {
                await loadBundle("everjust_phone.twilio_assets");
            } catch (e) {
                console.error("Failed to load Twilio SDK:", e);
                state.status = "disconnected";
                return;
            }
            try {
                const result = await orm.call("everjust.phone.call", "get_twilio_token", []);
                if (result.error) {
                    console.warn("Phone:", result.error);
                    state.status = "disconnected";
                    return;
                }
                state.identity = result.identity;

                device = new Twilio.Device(result.token, {
                    edge: "ashburn",
                    logLevel: "warn",
                });

                device.on("registered", () => {
                    state.status = "ready";
                    console.info("Phone: registered as", state.identity);
                });
                device.on("error", (err) => {
                    console.error("Phone error:", err);
                    notification.add("Phone error: " + err.message, { type: "danger" });
                });
                device.on("incoming", handleIncoming);
                device.on("tokenWillExpire", refreshToken);

                await device.register();
            } catch (e) {
                console.error("Phone connect failed:", e);
                state.status = "disconnected";
            }
        }

        async function refreshToken() {
            try {
                const result = await orm.call("everjust.phone.call", "get_twilio_token", []);
                if (result.token && device) {
                    device.updateToken(result.token);
                }
            } catch (e) {
                console.error("Token refresh failed:", e);
            }
        }

        function handleIncoming(call) {
            state.status = "on-call";
            state.callDirection = "inbound";
            state.callNumber = call.parameters.From || "Unknown";
            state.isOpen = true;
            activeConnection = call;

            notification.add("Incoming call from " + state.callNumber, {
                type: "info",
                sticky: true,
                buttons: [
                    {
                        name: "Answer",
                        primary: true,
                        onClick: () => {
                            call.accept();
                            startDurationTimer();
                        },
                    },
                    {
                        name: "Reject",
                        onClick: () => call.reject(),
                    },
                ],
            });

            call.on("accept", () => startDurationTimer());
            call.on("disconnect", () => endCall());
            call.on("cancel", () => endCall());
        }

        async function makeCall(number, partnerName) {
            if (!device || state.status === "on-call") return;
            state.status = "on-call";
            state.callDirection = "outbound";
            state.callNumber = number;
            state.callPartner = partnerName || "";
            state.isOpen = true;

            try {
                activeConnection = await device.connect({
                    params: { To: number },
                });
                activeConnection.on("accept", () => startDurationTimer());
                activeConnection.on("disconnect", () => endCall());
                activeConnection.on("reject", () => endCall());
                activeConnection.on("cancel", () => endCall());
            } catch (e) {
                notification.add("Call failed: " + e.message, { type: "danger" });
                endCall();
            }
        }

        function hangup() {
            if (activeConnection) {
                activeConnection.disconnect();
            }
            endCall();
        }

        function toggleMute() {
            if (activeConnection) {
                state.isMuted = !state.isMuted;
                activeConnection.mute(state.isMuted);
            }
        }

        function sendDtmf(digit) {
            if (activeConnection) {
                activeConnection.sendDigits(digit);
            }
        }

        function startDurationTimer() {
            state.callDuration = 0;
            durationTimer = setInterval(() => {
                state.callDuration++;
            }, 1000);
        }

        function endCall() {
            if (durationTimer) {
                clearInterval(durationTimer);
                durationTimer = null;
            }
            activeConnection = null;
            state.status = device ? "ready" : "disconnected";
            state.callDirection = "";
            state.callNumber = "";
            state.callPartner = "";
            state.callDuration = 0;
            state.isMuted = false;
            // Refresh call history
            loadHistory();
        }

        async function loadHistory() {
            try {
                state.recentCalls = await orm.searchRead(
                    "everjust.phone.call",
                    [],
                    ["display_name", "direction", "status", "duration", "start_time",
                     "from_number", "to_number", "recording_url", "partner_id"],
                    { limit: 20, order: "start_time desc" }
                );
            } catch (e) {
                console.error("Failed to load call history:", e);
            }
        }

        function toggle() {
            state.isOpen = !state.isOpen;
            if (state.isOpen && state.status === "disconnected") {
                connect();
            }
        }

        // Auto-connect on service start
        connect();

        return {
            state,
            toggle,
            makeCall,
            hangup,
            toggleMute,
            sendDtmf,
            loadHistory,
            connect,
        };
    },
};

registry.category("services").add("everjust_phone", phoneService);
