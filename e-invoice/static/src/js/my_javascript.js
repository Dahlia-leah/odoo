z.;odoo.define('e-invoice.view', function (require) {
"use strict";
     var core = require('web.core');
     var FormController = require('web.FormController');
     var FormView = require('web.FormView');
     var viewRegistry = require('web.view_registry');
     var EsignFormViewController = FormController.extend( {
        events: _.extend({}, FormController.prototype.events, {
            'click .e-sign-get': '_onClickE',
        }),

        _onClickE: function (event) {

             var self =this;
             var host = "localhost"
             let pin = prompt("Please enter your pin", "");
             if (pin){
             self._rpc({
             model: 'stock.move.line',
             method :'get_document_cana',
             args:[[self.renderer.state.res_id]],
             }).then(function (result) {
                var xmlHttp = new XMLHttpRequest();
                const params = {
                    data:result,
                    user_pin: pin
                     }
                try {

                xmlHttp.open( "POST", "http://localhost:5000/sign", false ); // false for synchronous request
                xmlHttp.setRequestHeader('Content-type', 'application/json')
                xmlHttp.send(JSON.stringify(params));
                console.log(xmlHttp.responseText);
                var sign = xmlHttp.responseText;
                 if (sign=="Token is not connected" || sign=="Token pin is not available now" || sign=="Unexpected Error")
                {
                 alert(sign);
                }
                else{
                 self._rpc({
                           model: 'account.move',
                           method :'send_e_invoice_sign',
                           args:[[self.renderer.state.res_id],sign]}).then(function (res) {
                                            self.trigger_up('reload');
                                        });
                    }
                }catch(err) {
                console.log(err);
                alert("Token Connection Failed");
                         }

                    });
                    }

        }

    });

    var EsignFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: EsignFormViewController,
        }),
    });

    viewRegistry.add('e-sign', EsignFormView);
});




