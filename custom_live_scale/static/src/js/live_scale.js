odoo.define('custom_live_scale.live_scale', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    
    // Function to get live scale data
    function getScaleData() {
        ajax.jsonRpc('/get_scale_data', 'call', {})
            .then(function (data) {
                console.log('Scale data:', data);
                alert('Weight: ' + data.weight + ' ' + data.unit);
            })
            .catch(function (error) {
                console.error('Error fetching scale data:', error);
            });
    }

    // Call the function
    getScaleData();
});
