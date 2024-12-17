odoo.define('stock_picking.live_weight', function (require) {
    "use strict";

    const bus = require('bus.bus').bus;
    const core = require('web.core');
    const fieldRegistry = require('web.field_registry');

    bus.on('notification', this, function (notifications) {
        _.each(notifications, function (notif) {
            if (notif.channel === 'stock.move.external_weight') {
                const weight = notif.message.external_weight;
                const unit = notif.message.external_unit;
                console.log("External Weight Update:", weight, unit);

                // Dynamically update UI fields
                $('input[name="external_weight"]').val(weight);
                $('input[name="external_unit"]').val(unit);
            }
        });
    });

    bus.startPolling();
});
