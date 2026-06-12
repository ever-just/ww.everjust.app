/** @odoo-module **/

import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class HomeButton extends Component {
    static template = "everjust_home.HomeButton";

    setup() {
        this.actionService = useService("action");
    }

    goHome() {
        this.actionService.doAction("everjust_home", {
            clearBreadcrumbs: true,
        });
    }
}

// Systray items with higher sequence appear further LEFT in the navbar.
// Use 1000 so it's the leftmost systray item (close to the app menu).
registry.category("systray").add("everjust_home.HomeButton", {
    Component: HomeButton,
    isDisplayed: () => true,
}, { sequence: 1000 });
