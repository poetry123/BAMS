from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
import logging
log = logging.getLogger(__name__)

@view_config(route_name='home', renderer='templates/index.pt')
def my_view(request):
    # get all quotations from database
    quotations = []
    for i in range(5):
      quotation = {'quotation_no': (i+1)*1000}
      quotations.append(quotation)
    return {'quotations': quotations}

@view_config(route_name='quotation_new', renderer='templates/new_quotation.pt')
def quotation_new(request):
  quotation_validity = 30
  delivery = 30
  payment = 30
  return {'quotation_validity':quotation_validity, 'delivery':delivery, 'payment':payment}

@view_config(route_name='summary', renderer='templates/summary.pt')
def quotation_summary(request):
  quotation_collection = request.db['quotations']
  quotations = quotation_collection.find()
  print (quotations)
  return {'quotations': quotations}

@view_config(route_name='settings', renderer='templates/settings.pt')
def settings(request):
  return {}

@view_config(route_name='quotation_edit', renderer='templates/edit_form.pt')
def quotation_edit(request):
  quotation_no = request.matchdict['quotation_no']
  # get entry from mongodb based on quotation number
  return {'qt_number': quotation_no}

@view_config(route_name='quotation_create')
def create_quotation(request):
  if request.method == 'POST':
    quotation_raw = request.POST
    log.debug('Raw Quotation Data entered:' + str(quotation_raw))
    quotation = dict()
    quotation['company_name'] = quotation_raw['company_name']
    quotation['department'] = quotation_raw['department']
    quotation['order_address'] = quotation_raw['order_address']
    quotation['tel'] = quotation_raw['tel']
    quotation['email'] = quotation_raw['email']
    quotation['addressee'] = quotation_raw['order_people']

    items = []
    item_nos = quotation_raw.getall('item_no[]')
    item_descriptions = quotation_raw.getall('item_description[]')
    item_quantities = quotation_raw.getall('item_quantity[]')
    item_unit_prices = quotation_raw.getall('item_unit_price[]')
    items_l = zip(item_nos, item_descriptions, item_quantities, item_unit_prices)
    for i in items_l:
        items.append({'number':i[0], 'description': i[1], 'quantity':i[2], 'unit_price':i[3]})

    quotation['items'] = items

    log.debug('Quotation Created:' + str(quotation))

    quotation_collection = request.db['quotations']
    quotation_collection.insert_one(quotation)
    # Save to mongodb
    return HTTPFound(location='/')
