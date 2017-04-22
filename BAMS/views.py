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
    print(quotation)
    # Save to mongodb
    return HTTPFound(location='/')
