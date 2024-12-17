/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart } from "@odoo/owl";

class LiveScaleWidget extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.weight = 0.0;
        this.unit = "kg";

        onWillStart(async () => {
            await this.updateLiveWeight();
            setInterval(this.updateLiveWeight.bind(this), 2000); // Update every 2 seconds
        });
    }

    async updateLiveWeight() {
        try {
            const result = await this.rpc("/scale/get_live_weight", {});
            this.weight = result.weight;
            this.unit = result.unit;
            this.render();  // Rerender the widget
        } catch (error) {
            console.error("Error fetching live scale data:", error);
        }
    }
}

LiveScaleWidget.template = "LiveScaleTemplate";
registry.category("actions").add("live_scale_widget", LiveScaleWidget);
