/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { computeAppsAndMenuItems } from "@web/webclient/menus/menu_helpers";

export class HomeMenu extends Component {
    static template = "everjust_home.HomeMenu";
    static props = { ...Component.props };

    setup() {
        this.menuService = useService("menu");
        this.actionService = useService("action");
        this.state = useState({ apps: [], query: "" });

        onWillStart(() => {
            const menuTree = this.menuService.getMenuAsTree("root");
            const { apps } = computeAppsAndMenuItems(menuTree);
            this.state.apps = apps;
        });
    }

    get displayedApps() {
        const q = this.state.query.toLowerCase().trim();
        if (!q) return this.state.apps;
        return this.state.apps.filter(
            (app) => app.label.toLowerCase().includes(q)
        );
    }

    onAppClick(app) {
        this.menuService.selectMenu(app);
    }

    onSearchInput(ev) {
        this.state.query = ev.target.value;
    }

    onSearchKeydown(ev) {
        if (ev.key === "Enter") {
            const apps = this.displayedApps;
            if (apps.length === 1) {
                this.onAppClick(apps[0]);
            }
        }
        if (ev.key === "Escape") {
            this.state.query = "";
            ev.target.value = "";
        }
    }
}

// Register as a client action so doAction("everjust_home") works.
registry.category("actions").add("everjust_home", HomeMenu);

// Patch WebClient so the home menu shows instead of loading the first app.
patch(WebClient.prototype, {
    _loadDefaultApp() {
        return this.actionService.doAction("everjust_home", {
            clearBreadcrumbs: true,
        });
    },
});
