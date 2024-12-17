odoo.define('custom_live_scale.live_scale', function (require) {
    "use strict";

    var rpc = require('web.rpc');
    var core = require('web.core');
    var Widget = require('web.Widget');

    var LiveScaleWidget = Widget.extend({
        template: 'LiveScaleWidget',
        start: function () {
            this._updateScaleData();
        },
        _updateScaleData: function () {
            var self = this;
            setInterval(function () {
                rpc.query({
                    route: '/get_weight',
                }).then(function (data) {
                    if (data.error) {
                        console.error("Error fetching scale data:", data.error);
                    } else {
                        self.$('.weight').text(data.weight + " " + data.unit);
                    }
                }).catch(function (err) {
                    console.error("RPC Error:", err);
                });
            }, 3000);  // Fetch every 3 seconds
        },
    });

    core.action_registry.add('live_scale_widget', LiveScaleWidget);
    return LiveScaleWidget;
});
