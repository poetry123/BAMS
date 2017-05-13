from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

# @view_config(route_name='home', renderer='templates/status_tables.pt')
# @view_config(route_name='home', renderer='templates/new_quotation.pt')
@view_config(route_name='home', renderer='templates/index.pt')
def my_view(request):
    # get all quotations from database
    quotations = []
    for i in range(5):
      quotation = {'quotation_no': (i+1)*1000}
      quotations.append(quotation)
    return {'quotations': quotations}

# @view_config(route_name='quotation_new', renderer='templates/new_form.pt')
@view_config(route_name='quotation_new', renderer='templates/new_quotation.pt')
def quotation_new(request):
  quotation_validity = 30
  delivery = 30
  payment = 30
  return {'quotation_validity':quotation_validity, 'delivery':delivery, 'payment':payment}

@view_config(route_name='quotation_summary', renderer='templates/quotation_summary.pt')
def quotation_summary(request):
  quotation_collection = request.db['quotations']
  quotations = quotation_collection.find()
  print (quotations)
  return {'quotations': quotations}

@view_config(route_name='DO_summary', renderer='templates/DO_summary.pt')
def DO_summary(request):
  return {}

@view_config(route_name='invoice_summary', renderer='templates/invoice_summary.pt')
def invoice_summary(request):
  return {}

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
    quotation = request.POST
    quotation_collection = request.db['quotations']
    quotation_collection.insert_one(quotation)
    # Save to mongodb
    return HTTPFound(location='/')
