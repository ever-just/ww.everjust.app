/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class PhoneWidget extends Component {
    static template = "everjust_phone.PhoneWidget";
    static props = {};

    setup() {
        this.phone = useState(useService("everjust_phone"));
        this.dialInput = useState({ value: "" });
        onWillStart(() => this.phone.loadHistory());
    }

    get formattedDuration() {
        const s = this.phone.state.callDuration;
        const m = Math.floor(s / 60);
        const sec = s % 60;
        return `${m}:${sec < 10 ? "0" : ""}${sec}`;
    }

    onDialDigit(digit) {
        this.dialInput.value += digit;
        if (this.phone.state.status === "on-call") {
            this.phone.sendDtmf(digit);
        }
    }

    onBackspace() {
        this.dialInput.value = this.dialInput.value.slice(0, -1);
    }

    onCall() {
        const number = this.dialInput.value.trim();
        if (number) {
            this.phone.makeCall(number);
        }
    }

    onHangup() {
        this.phone.hangup();
    }

    onToggleMute() {
        this.phone.toggleMute();
    }

    onCallFromHistory(call) {
        const number = call.direction === "inbound" ? call.from_number : call.to_number;
        if (number) {
            this.dialInput.value = number;
            this.phone.state.activeTab = "dialer";
        }
    }

    onSelectTab(tab) {
        this.phone.state.activeTab = tab;
    }
}

// Systray icon that opens the softphone
export class PhoneSystray extends Component {
    static template = "everjust_phone.PhoneSystray";
    static components = { PhoneWidget };

    setup() {
        this.phone = useState(useService("everjust_phone"));
    }

    onClick() {
        this.phone.toggle();
    }
}

registry.category("systray").add("everjust_phone.PhoneSystray", {
    Component: PhoneSystray,
    isDisplayed: () => true,
}, { sequence: 999 });
