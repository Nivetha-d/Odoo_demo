/** @odoo-module */

import {registry} from "@web/core/registry"

import {listView} from "@web/views/list/list_view"

import {ListController} from "@web/views/list/list_controller"

import {useService} from "@web/core/utils/hooks"

class OwlTodoController extends ListController {

      setup(){
         super.setup()

         this.action = useService("action")
      }

   OpenSalesView() {
     this.action.doAction({
     type:"ir.actions.act_window",
     name:"payment upload",
     res_model:"upload.payments",
      view_mode: 'form',

      views: [[false,'form']],
      target:'new'


     })
   }


}

export const owlTodoListView = {
   ...listView,
   Controller : OwlTodoController,
    buttonTemplate: "accounting_payments.owlTodoListView.Buttons",
}


registry.category("views").add("owl_todo_list_view",owlTodoListView)