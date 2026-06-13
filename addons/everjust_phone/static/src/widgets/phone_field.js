/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PhoneField } from "@web/views/fields/phone/phone_field";

/**
 * Patch the core PhoneField to add a "call" button that triggers
 * the embedded Twilio softphone instead of opening tel: links.
 */
patch(PhoneField.prototype, {
    onClickCall(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        const phone = this.env.services.everjust_phone;
        if (phone && this.props.record.data[this.props.name]) {
            phone.makeCall(this.props.record.data[this.props.name]);
        }
    },
});
