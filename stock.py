
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby

from osv import fields, osv
from tools.translate import _
import netsvc
import tools
import decimal_precision as dp
import logging


class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'
    
    def _get_stock(self, cr, uid, ids, field_name, arg, context=None):
        res = super(stock_production_lot, self)._get_stock(cr, uid, ids, field_name, arg, context=None)
        import pdb;pdb.set_trace() 
        return res
    
    def _stock_search(self, cr, uid, obj, name, args, context=None):
        ids = super(stock_production_lot, self)._stock_search(cr, uid, obj, name, args, context=None)
        import pdb;pdb.set_trace()
        return ids
    
    def _product_price_lot(self, cr, uid, ids, name, arg, context=None):
        # import pdb;pdb.set_trace()
        res = {}
        if context is None:
            context = {}
        pricelist = context.get('listino', False)
        if not pricelist:
            pricelist = context.get('pricelist', False)
        if not pricelist:
             for id_lot in ids:
                try:
                    price_id = self.pool.get('listini.lotti').search(cr, uid, [('lotto_id', '=', id_lot), ('default_price', '=', True)], context=context)[0]
                    if price_id:
                        price = self.pool.get('listini.lotti').browse(cr, uid, [price_id])[0].prezzo_netto
                    else:
                        price = 0.0
                except:
                    price = 0.0
                res[id_lot] = price           
        else:
            # cerco e prendo il prezzo del listino selezionato se non trovo nulla 
            for id_lot in ids:
                try:
                    price_id = self.pool.get('listini.lotti').search(cr, uid, [('lotto_id', '=', id_lot), ('listino_id', '=', pricelist)], context=context)[0]
                    if price_id:
                        price = self.pool.get('listini.lotti').browse(cr, uid, [price_id])[0].prezzo_netto
                    else:
                        price = 0.0
                except:
                    price = 0.0
                res[id_lot] = price
                
        for id in ids:
            res.setdefault(id, 0.0)
        return res


    def get_price_lot(self, cr, uid, ids, pricelist, context):
        #import pdb;pdb.set_trace()
        res = {}
        if ids and pricelist:
            for lotto in ids:
              price_id = self.pool.get('listini.lotti').search(cr, uid, [('lotto_id', '=', lotto), ('listino_id', '=', pricelist)], context=context)[0]
              if price_id:
                        price_rec = self.pool.get('listini.lotti').browse(cr, uid, [price_id])[0]
                        res.update({'prezzo_netto':price_rec.prezzo_netto})
                        res.update({'sconti':price_rec.sconti})
                        res.update({'discount_riga':price_rec.discount_riga})
                        res.update({'prezzo':price_rec.prezzo})                        
        return res
    
    _columns = {
                'listini_ids': fields.one2many('listini.lotti', 'lotto_id', 'Listini Particolari del lotto', readonly=False),
                'ucaprod':fields.float('Ultimo Costo Acquisto/Produzione', digits=(12, 5)),
                'price_default': fields.function(_product_price_lot, method=True, type='float', string='Pricelist', digits_compute=dp.get_precision('Sale Price')),
                }
    
stock_production_lot()    

class listini_lotti(osv.osv):
    
   _name = "listini.lotti"
   _description = "Listini prezzi Lotti"
   
   _columns = {
               
               'lotto_id': fields.many2one('stock.production.lot', 'Lotto di Produzione', required=True, ondelete='cascade', select=True),
               'listino_id': fields.many2one('product.pricelist', 'Pricelist', required=True, help="Listino "),
               'prezzo':fields.float('Prezzo di Vendita', digits=(12, 5)),
               'sconti':fields.char("Sconti", size=20),
               'discount_riga':fields.float('Sconto Totale di Riga', digits=(12, 3)),
               'prezzo_netto':fields.float('Prezzo Netto di Riga', digits=(12, 5)),
               'default_price': fields.boolean('Default', help="Prezzo da visualizzare in automatico nelle ricerche"),

               } 

   def on_change_prezzo(self, cr, uid, ids, sconto, prezzo): 
       v = {}
       
       if sconto:
           v['prezzo_netto'] = self.calcola_netto(prezzo, sconto) 
       else:
            v['prezzo_netto'] = prezzo
       return  {'value': v}    
   
   def calcola_netto(self, prezzo, sconto):
       return prezzo - (prezzo * sconto / 100)
   
   def on_change_sconti(self, cr, uid, ids, value, prezzo):
       #import pdb;pdb.set_trace()
        v = {}
        if value :
            lista_sconti = value.split("+")
            sconto = float(100)
            for scontoStr in lista_sconti:
                if '-' in scontoStr :
                    First = True
                    for ScoMeno in scontoStr.split('-'):
                        if First:
                            First = False
                            sconto = sconto - (sconto * float(ScoMeno) / 100)
                        else:
                            sconto = sconto + (sconto * float(ScoMeno) / 100)                        
                else:
                    sconto = sconto - (sconto * float(scontoStr) / 100)
                    
            sconto = (100 - sconto)
            v['discount_riga'] = sconto
            v['prezzo_netto'] = self.calcola_netto(prezzo, sconto)          
        else:
            sconto = 0
            v['discount_riga'] = sconto
            v['prezzo_netto'] = prezzo          
            

        return  {'value': v}    
    
   def on_change_listino(self, cr, uid, ids, value):
       #import pdb;pdb.set_trace()
        v = {}
        if value:
            PriceDefault = self.pool.get("product.pricelist").browse(cr, uid, [value])[0].default_price
            v['default_price'] = PriceDefault          
        return  {'value': v}        

listini_lotti()



class product_product(osv.osv):
    _inherit = 'product.product'
    
    _columns = {
                'elenco_lotti': fields.one2many('stock.production.lot', 'product_id', 'Elenco Lotti', required=False, readonly=True),

                }

product_product()

   
