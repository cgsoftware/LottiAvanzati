# -*- encoding: utf-8 -*-

import netsvc
import pooler, tools
import math
from tools.translate import _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import decimal_precision as dp
import time


from osv import fields, osv


class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    _columns = {
                'lotto_id': fields.many2one('stock.production.lot', 'Lotto di Produzione', required=False, ondelete='cascade', select=True),
                
                }
    
    def lotto_id_change(self, cr, uid, ids, lotto_id, product_id, pricelist, partner_id):
        # cerca l'eventuale prezzo particolare del lotto e ne verifica la disponibilità
        result = {}
        domain = {}
        warning = '' 
        if lotto_id:       
         riga_listino = self.pool.get('stock.production.lot').get_price_lot(cr, uid, [lotto_id], pricelist, context=False)
         if riga_listino:
            # assegna i campi che ha a disposizione
              result.update({'price_unit':riga_listino['prezzo']})
              result.update({'string_discount':riga_listino['sconti']})
              result.update({'discount':riga_listino['discount_riga']})
              result.update({'prezzo_netto':riga_listino['prezzo_netto']})          
         else:
             import pdb;pdb.set_trace()
             if product_id:
                 import pdb;pdb.set_trace()
                 qty = 1
                 riga_listino = self.pool.get('product.pricelist').price_get_adhoc(cr, uid, [pricelist], product_id, qty, partner_id, context=False)
                 if riga_listino:
                     # assegna i campi che ha a disposizione
                     result.update({'price_unit':riga_listino['prezzo']})
                     result.update({'string_discount':riga_listino['sconti']})
                     result.update({'discount':riga_listino['discount_riga']})
                     result.update({'prezzo_netto':riga_listino['prezzo_netto']})       
        return {'value': result, 'domain': domain, 'warning': warning}


    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False, name='', partner_id=False, lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False):

        reso = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging, fiscal_position, flag)
        # segue prima la strada normale poi si cerca il listino secondo le vecchie regole ad-Hoc
        result = reso['value']
        domain = reso['domain']
        warning = ''
        # assegna i campi che ha a disposizione
        result.update({'lotto_id':0})
        
        return {'value': result, 'domain': domain, 'warning': warning}
    
sale_order_line()
