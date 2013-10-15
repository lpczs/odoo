# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (c) 2013-TODAY OpenERP S.A. <http://www.openerp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.addons.mail.tests.common import TestMail
from openerp.osv.orm import except_orm

class TestSaleCrm(TestMail):

    def setUp(self):
        super(TestSaleCrm, self).setUp()
        cr, uid = self.cr, self.uid

class TestSaleCrmCase(TestSaleCrm):

    def test_sale_crm_case(self):
        """ Testing Sale Crm  """

        cr, uid, = self.cr, self.uid

        # Usefull models
        ir_model_obj = self.registry('ir.model.data')
        res_company_obj = self.registry('res.company')
        res_users_obj = self.registry('res.users')
        crm_case_section_obj = self.registry('crm.case.section')
        crm_lead_obj = self.registry('crm.lead')

        # Find Direct Sales
        direct_sales_ref = ir_model_obj.get_object_reference(cr, uid, 'crm' , 'section_sales_department')

        # for Opportunities
        usd_ref = ir_model_obj.get_object_reference(cr, uid, 'base' , 'USD')
        your_company_ref = ir_model_obj.get_object_reference(cr, uid, 'base', 'main_company')

        # Before opportunities
        opportunities_before = crm_case_section_obj._get_opportunities_data(cr, uid, [direct_sales_ref[1]], field_name=False, arg=False, context=False)

        #I Create company with USD currency.
        res_company_id = res_company_obj.create(cr, uid,{
            'name': 'New Company',
            'currency_id': usd_ref and  usd_ref[1] or False,
            'parent_id': your_company_ref and your_company_ref[1] or False
          })

        # Find Sale Manager group
        group_sale_manager_id = ir_model_obj.get_object_reference(cr, uid, 'base', 'group_sale_manager')[1]

        #I Create User of new company.
        res_users_id = res_users_obj.create(cr, uid,{
            'name': 'User',
            'login': 'admin@example.com',
            'company_id': res_company_id,
            'company_ids': [(6, 0, [res_company_id])],
            'email': 'admin@gmail.com',
            'groups_id': [(6, 0, [group_sale_manager_id])]
          })

        #I create Opportunitie for new created user
        opportunities_id = crm_lead_obj.create(cr, res_users_id,{
            'name': 'Opportunities',
            'type': 'opportunity',
            'planned_revenue': 10000,
            'user_id' : res_users_id,
            'section_id': direct_sales_ref and  direct_sales_ref[1] or False
          })

        user_rate = res_company_obj.browse(cr, uid ,[res_company_id])[0].currency_id.rate_silent

        # After opportunities
        opportunities_after = crm_case_section_obj._get_opportunities_data(cr, uid, [direct_sales_ref[1]], field_name=False, arg=False, context=False)

        #Assertion Error
        self.assertTrue(int(opportunities_after[1]['monthly_planned_revenue'][4]['value']) == int(opportunities_before[1]['monthly_planned_revenue'][4]['value'] + (10000 / user_rate)), "Not Proper Currency Conversion for Opportunities")

        # Before Sale or Quotations
        sale_order_before = crm_case_section_obj._get_sale_orders_data(cr, uid, [direct_sales_ref[1]], field_name=False, arg=False, context=False)

        # Before Invoice
        invoice_before = crm_case_section_obj._get_invoices_data(cr, uid, [direct_sales_ref[1]], field_name=False, arg=False, context=False)

        #I Write company .
        company_id = res_users_obj._get_company(cr, uid, context=False, uid2=False)
        in_ref = ir_model_obj.get_object_reference(cr, uid, 'base' , 'INR')
        res_company_obj.write(cr, uid,[company_id], {
            'currency_id': in_ref and  in_ref[1] or False
          })

        # After Sale or Quotations
        sale_order_after = crm_case_section_obj._get_sale_orders_data(cr, uid, [direct_sales_ref[1]], field_name=False, arg=False, context=False)

        # After Invoice
        invoice_after = crm_case_section_obj._get_invoices_data(cr, uid, [direct_sales_ref[1]], field_name=False, arg=False, context=False)

        new_rate = res_company_obj.browse(cr, uid , [company_id])[0].currency_id.rate_silent

        #Assertion Error
        for i in range(0,5):
            # for Quotations
            self.assertTrue(sale_order_before[1]['monthly_quoted'][i]['value'] * new_rate == sale_order_after[1]['monthly_quoted'][i]['value'], "Not Proper Currency Conversion for Quotations ")
            # for sale odrer
            self.assertTrue(sale_order_before[1]['monthly_confirmed'][i]['value'] * new_rate == sale_order_after[1]['monthly_confirmed'][i]['value'], "Not Proper Currency Conversion for Sale Order")
            # for Invoice
            self.assertTrue(invoice_before[1][i]['value'] * new_rate == invoice_after[1][i]['value'], "Not Proper Currency Conversion for Invoice")
