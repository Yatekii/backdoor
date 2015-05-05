# Service File Structure

- service name
    - __init__.py -- contains all the major functions
    - more files included by __init__.py
    - blueprint -- blueprint for the service
        - __init__.py -- all the blueprint methods. MUST specify a variable __blueprint__ with the blueprint!
        - additional files concerning the blueprint
        - templates -- html files for the webui part

# Blueprints

Every blueprint must look like this:


__blueprint__ = Blueprint('service_lock', __name__, template_folder='templates')


@__blueprint__.route('/view')
@__blueprint__.route('/view', methods=['POST', 'GET'])
@check_session()
@check_rights(0)
@helpers.handle_dbsession()
def view(sqlsession, id):
    active = 'service'
    id = int(id)

    services = sqlsession.query(models.Service).filter_by(uses_blueprint=True).order_by(models.Service.name.asc()).all()
    service = sqlsession.query(models.Service).filter_by(id=id).first()
    return render_template(
        'main.html',
        active=active,
        id=id,
        service=service,
        services=services
    )

You can extend that to your wishes, but it ALWAYS has to contain a view route which wants an id and hands the id in INTEGER FORM,
as well as a list of all services with a blueprint and a service corresponding to the id given to the renderer!

# Templates

Templates must look like this:

{% extends service.html %}

{% block service %}<!-- YOUR CODE HERE -->{% endblock %}