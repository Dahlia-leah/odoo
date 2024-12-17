odoo.define('custom_live_scale.live_scale', function (require) {
    "use strict";

    var core = require('web.core');
    var ajax = require('web.ajax');
    var Widget = require('web.Widget');

    var _t = core._t;

    // Define a new widget that will interact with the scale API
    var LiveScaleWidget = Widget.extend({
        template: 'custom_live_scale.LiveScaleTemplate',

        // Initialize the widget and bind methods
        init: function (parent, options) {
            this._super(parent, options);
        },

        // Method to fetch live scale data from the Flask API
        fetchLiveScaleData: function () {
            var self = this;
            ajax.jsonRpc('http://localhost:5000/get_weight', 'GET', {}).then(function (data) {
                // Check if the data was successfully retrieved
                if (data) {
                    self.$el.find('.o_live_scale_weight').text(data.weight);
                    self.$el.find('.o_live_scale_unit').text(data.unit);
                }
            }).fail(function (error) {
                console.error('Error fetching scale data:', error);
                self.$el.find('.o_live_scale_weight').text('Error');
                self.$el.find('.o_live_scale_unit').text('');
            });
        },

        // Trigger when the button is clicked to fetch data
        start: function () {
            var self = this;
            this._super.apply(this, arguments);
            // Fetch live scale data on widget start
            this.fetchLiveScaleData();

            // Set up an interval to refresh the data every 5 seconds
            setInterval(function () {
                self.fetchLiveScaleData();
            }, 5000);  // Refresh every 5 seconds
        }
    });

    // Register the widget with Odoo
    core.action_registry.add('custom_live_scale.live_scale_widget', LiveScaleWidget);

});
