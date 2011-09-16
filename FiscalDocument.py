# -*- encoding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import decimal_precision as dp
import time
import netsvc
import pooler, tools
import math
from tools.translate import _


from osv import fields, osv

class FiscalDocRighe(osv.osv):
    _inherit = "fiscaldoc.righe"
    _columns = {
                'lotto_id': fields.many2one('stock.production.lot', 'Lotto di Produzione', required=False, ondelete='cascade', select=True),
                }
    
     

    def lotto_id_change(self, cr, uid, ids, lotto_id, product_id, pricelist, partner_id):
        # cerca l'eventuale prezzo particolare del lotto e ne verifica la disponibilità
        #import pdb;pdb.set_trace()
        result = {}
        domain = {}
        warning = '' 
        if lotto_id:       
         riga_listino = self.pool.get('stock.production.lot').get_price_lot(cr, uid, [lotto_id], pricelist, context=False)
         if riga_listino:
            # assegna i campi che ha a disposizione
                     result.update({'product_prezzo_unitario':riga_listino['prezzo']})
                     result.update({'sconti_riga':riga_listino['sconti']})
                     result.update({'discount_riga':riga_listino['discount_riga']})
                     result.update({'prezzo_netto':riga_listino['prezzo_netto']})
         else:
             #import pdb;pdb.set_trace()
             if product_id:
                 #import pdb;pdb.set_trace()
                 qty = 1
                 riga_listino = self.pool.get('product.pricelist').price_get_adhoc(cr, uid, [pricelist], product_id, qty, partner_id, context=False)
                 if riga_listino:
                     # assegna i campi che ha a disposizione
                     result.update({'prezzo':riga_listino['prezzo']})
                     result.update({'StringaSconto':riga_listino['sconti']})
                     result.update({'sconto':riga_listino['discount_riga']})
                     result.update({'prezzo_netto':riga_listino['prezzo_netto']})       
        return {'value': result, 'domain': domain, 'warning': warning}
   
    
    
FiscalDocRighe()


class FiscalDocHeader(osv.osv):
   _inherit = "fiscaldoc.header"
 

   def agg_magazzino(self, cr, uid, ids, context={}):
       var = super(FiscalDocHeader, self).agg_magazzino(cr, uid, ids, context)
       testata = self.browse(cr, uid, ids)[0]  
       if testata.tipo_doc.flag_magazzino:
           # SE FALSE IL DOC NON CREA MOVIMENTI DI MAGAZZINO 
           if ids:   
               righe_ids = self.pool.get('fiscaldoc.righe').search(cr, uid, [('name', "=", ids)]) 
               # import pdb;pdb.set_trace()
               company_id = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id
               first_line = True
               if testata.picking_ids:
                   #import pdb;pdb.set_trace()
                   OK = self.pool.get('stock.picking').write(cr, uid, [testata.picking_ids.id], {'address_id': testata.partner_indcons_id.id, })
               for riga_art in self.pool.get('fiscaldoc.righe').browse(cr, uid, righe_ids, context=context):                 
                   if riga_art.move_ids and riga_art.lotto_id:
                       # c'è il movimento e c'è il lotto e quindi scrive il lotto sui movimenti
                       riga_lot = {'prodlot_id':riga_art.lotto_id.id}
                       OK = self.pool.get('stock.move').write(cr, uid, [riga_art.move_ids.id], riga_lot)
       return True

FiscalDocHeader()


