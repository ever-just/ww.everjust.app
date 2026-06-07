/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { browser } from "@web/core/browser/browser";
import { UserMenu } from "@web/webclient/user_menu/user_menu";

// Force the browser tab title to EVERJUST.APP regardless of upstream defaults.
const _setTitle = browser.document
    ? Object.getOwnPropertyDescriptor(Document.prototype, "title")
    : null;

function enforceTitle() {
    try {
        if (document.title && !document.title.startsWith("EVERJUST.APP")) {
            const parts = document.title.split(" - ");
            const suffix = parts.length > 1 ? parts.slice(1).join(" - ") : "";
            document.title = suffix ? `EVERJUST.APP - ${suffix}` : "EVERJUST.APP";
        }
    } catch (e) {
        // no-op
    }
}
setInterval(enforceTitle, 1000);
enforceTitle();

// Strip external upstream links (documentation, support, account) from the
// user menu so no upstream product references remain.
patch(UserMenu.prototype, {
    getElements() {
        const items = super.getElements(...arguments);
        const blocked = ["documentation", "support", "odoo_account", "shortcuts"];
        return items.filter((item) => !blocked.includes(item.id));
    },
});
