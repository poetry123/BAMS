from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from forex_python.converter import CurrencyRates
from bson.objectid import ObjectId
import json
import arrow

import logging

log = logging.getLogger(__name__)

c = CurrencyRates()

currency_codes = ['EUR','IDR','BGN','ILS','GBP','DKK','CAD','JPY','HUF',\
                  'RON','MYR','SEK','SGD','HKD','AUD','CHF','KRW','CNY',\
                  'TRY','HRK','NZD','THB','USD','NOK','RUB','INR','MXN',\
                  'CZK','BRL','PLN','PHP','ZAR']

def getNextSequence(collection, name):
  ret = collection.find_and_modify(query={"_id": name}, update={"$inc": {"seq": 1}}, new=True)
  return ret['seq'];

@view_config(route_name='home', renderer='templates/index.pt')
def my_view(request):
  quotation_collection = request.db['quotations']
  cursor = quotation_collection.find()
  quotations = []
  for q in cursor:
    time_created = arrow.get(q['time_created'])
    year = time_created.year % 2000
    q['quotation_number_c'] = 'QTN-%d%s' % (year, format(int(q['quotation_number']), '04d'))
    q['time_created_c'] = time_created.humanize()
    q['time_modified_c'] = arrow.get(q['time_modified']).humanize()
    quotations.append(q)
  # get all quotations from database
  for qq in quotations:
    print(qq)
  return {'project': 'BAMS', 'quotation_list': quotations}

@view_config(route_name='quotation_new', renderer='templates/new_quotation.pt')
def quotation_new(request):
  setting_doc = request.db['others'].find_one({'_id':'settings'})
  if setting_doc == None:
    quotation_validity = 30
    delivery = 30
    payment = 30
  else:
    quotation_validity = setting_doc['quotation_validity']
    delivery = setting_doc['delivery_days_allowed']
    payment = setting_doc['payment_days_allowed']

  currency_rate = dict()
  for code in currency_codes:
    rate = 1 if code == 'SGD' else c.get_rate(code, 'SGD')
    currency_rate[code] = rate
  return {'quotation_validity':quotation_validity, 'delivery':delivery, 'payment':payment, 'currency_rate':currency_rate}

@view_config(route_name='summary', renderer='templates/summary.pt')
def quotation_summary(request):
  quotation_collection = request.db['quotations']
  quotations = quotation_collection.find()
  return {'quotations': quotations}

@view_config(route_name='settings', renderer='templates/settings.pt')
def settings(request):
  others_collection = request.db['others']
  if request.method=='POST':
    setting_raw = request.POST
    print(setting_raw)
    setting_data = {'owner': setting_raw['owner'],
                'owner_phone': setting_raw['owner_phone'],
                'quotation_validity': setting_raw['quotation_validity'],
                'delivery_days_allowed': setting_raw['delivery_days_allowed'],
                'payment_days_allowed': setting_raw['payment_days_allowed'],
                '_id': 'settings'
                }
    existing_setting = others_collection.find_and_modify(query={'_id': 'settings'},
                          update=setting_data, new=True, upsert=True)
    print(existing_setting)
    return {'settings': existing_setting}
  else:
    existing_setting = others_collection.find_one({'_id': 'settings'})
    if(existing_setting == None):
      return {'settings': {'delivery_days_allowed':30, 'quotation_validity':30, 'payment_days_allowed':30,'owner':'', 'owner_phone':''}}

    return {'settings':existing_setting}

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
    quotation['quotation_validity'] = quotation_raw['quotation_validity']
    quotation['delivery_days_allowed'] = quotation_raw['delivery_days_allowed']
    quotation['payment_days_allowed'] = quotation_raw['payment_days_allowed']

    current_time = arrow.now().timestamp
    quotation['time_created'] = current_time
    quotation['time_modified'] = current_time
    quotation['status'] = 'quotation created'
    quotation['quotation_number'] = getNextSequence(request.db['counters'], 'quotation_id')

    items = []

    items_l = zip(quotation_raw.getall('item_number'), quotation_raw.getall('item_description'), \
                  quotation_raw.getall('item_quantity'), quotation_raw.getall('item_unit_price'), \
                  quotation_raw.getall('item_currency'), quotation_raw.getall('item_rate'), \
                  quotation_raw.getall('item_offset'))

    for i in items_l:
      items.append({'number':i[0],      'description': i[1], 'quantity':i[2], \
                    'unit_price':i[3], 'currency':i[4],     'convert_rate':i[5], \
                    'offset':i[6]})

    quotation['items'] = items

    log.debug('Quotation Created:' + str(quotation))

    quotation_collection = request.db['quotations']
    quotation_collection.insert_one(quotation)
    # Save to mongodb
    return HTTPFound(location='/')

@view_config(route_name='quotation_json', renderer='json')
def get_quotation(request):
  if 'quotation_id' not in request.GET:
    return {}
  quotation_id = request.GET['quotation_id']
  print(quotation_id)

  quotation = request.db['quotations'].find_one({'_id': ObjectId(quotation_id)})
  if quotation is None:
    return {}
  quotation['_id'] = str(quotation['_id'])

  return quotation





