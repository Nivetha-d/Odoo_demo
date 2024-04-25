/** @odoo-module */

//import { registry } from '@web/core/registry';
//import { listView } from '@web/views/list/list_view';
//import { ListController } from '@web/views/list/list_controller';
//import { actionService } from '@web/core/action_service';
//
//export class SaleListController extends ListController {
//    setup() {
//        super.setup();
//    }
//
//    OnTestClick() {
//        this.actionService.do_action({
//            type: 'ir.actions.act_window',
//            res_model: 'product.template',
//            views: [[false, 'form']],
//            target: 'new',
//        });
//    }
//}
//
//registry.add("button_in_tree", {
//    listView,
//    Controller: SaleListController,
//    buttonTemplate: "sale_button.ListView.buttons"
//});

//console.log("HEELLO");
//
//
//odoo.define('sale_button.SaleViewButton',[], function (require) {
//    "use strict";
//
//
//    var ListController = require('web.ListController');
//    var ListView = require('web.ListView');
//    var viewRegistry = require('web.view_registry');
//    var core = require('web.core');
//
//    console.log("OOOOOO99");
//
//    if (!ListController || !ListController.extend) {
//        console.error('ListController is not defined or does not have the extend method.');
//        return;
//    }
//
//
//    var TreeButton = sale_list_button.extend({
//        buttons_template: 'sale_button.buttons',
//        events: _.extend({}, ListController.prototype.events, {
//            'click .open_wizard_action': '_OpenWizard',
//        }),
//
//        _OpenWizard: function () {
//            var self = this;
//            this.do_action({
//                type: 'ir.actions.act_window',
//                res_model: 'product.template',
//                views: [[false, 'form']],
//                target: 'new',
//            });
//            console.log("OOOOOOO");
//        }
//    });
//
//    console.log("OOOOOO11");
//
//    var SaleOrderListView = ListView.extend({
//        config: _.extend({}, ListView.prototype.config, {
//            Controller: TreeButton,
//        }),
//    });
//
//    viewRegistry.add('button_in_tree', SaleOrderListView);
//});
