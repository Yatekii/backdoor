import argparse
from models import Service
from models import Field, Type
from models import FieldChoice
import helpers


import re
import os
import importlib
import shutil
import services


def check_condition(value, condition, type):
    if type == Type.bool:
        return True
    elif type == Type.int:
        try:
            float(value)
            return True
        except ValueError:
            return False
    elif type == Type.text:
        a = re.compile(condition)
        return a.match(value)


@helpers.handle_dbsession()
def prepare_service_db(sqlsession, name, desc, fields, uses_blueprint):
    # fields = (key, description, type, condition, choices = (c_value, c_description)
    m_string = ''
    f = []
    s = sqlsession.query(Service).filter_by(name=name).first()
    if s:
        print('Service %s exists yet. Aborting.' % name)
        return False
    if fields:
        for field in fields:
            key, description, type, condition, choices = field
            c = []
            c_string = ''
            for choice in choices:
                c_value, c_description = choice
                if not check_condition(c_value, condition, type):
                    print('Choice for field %s doesn\'t match it\'s rule. Aborting.')
                    return False
                cm = FieldChoice(value=c_value, description=c_description)
                c.append(cm)
                c_string += '\t\t %s: %s\n' % (c_value, c_description)
            fm = Field(key=key, description=description, type=type, condition=condition, choices=c)
            f.append(fm)
            m_string += '\t %s(type=%s, condition=%s): %s\n' % (key, type, condition, description)
    s = Service(name=name, fields=f, uses_blueprint=uses_blueprint)
    sqlsession.add(s)
    sqlsession.commit()
    print('Successfully prepared DB new service %s: %s' % (name, desc))
    if fields:
        print('%s contains the following fields:' % name)
        print(m_string)
    else:
        print('%s contains no fields.' % name)
    return True


def validate_service(path):
    if os.path.isdir(path):
        servicename = os.path.basename(path)
        if not os.path.isfile(os.path.join(path, '__init__.py')):
            print('Service contains no __init__.py.')
            return False
        m = importlib.import_module('%s' % servicename, '')
        if m.__uses_blueprint__:
            blueprint = os.path.join(path, 'blueprint')
            if not os.path.isdir(blueprint):
                print('Service contains no blueprint. Please place it in the blueprint dir.')
                return False
            if not os.path.isfile(os.path.join(blueprint, '__init__.py')):
                print('Service blueprint contains no __init__.py.')
                return False
            templates = os.path.join(blueprint, 'templates')
            if not os.path.isdir(templates):
                print('Warning: Service blueprint contains no template dir.')
            elif not os.listdir(templates):
                print('Warning: Service blueprint template dir is empty.')
        return True
    else:
        print('%s is not a directory. Please check your input' % path)
        return False


def register_service(path):
    print('Importing service from %s.' % path)
    if validate_service(path):
        servicename = os.path.basename(path)
        if os.path.isdir(os.path.join('services/', servicename)):
            print('Service could not be imported due to a service using the same name existing yet.')
            return False
        else:
            destination = os.path.join('services/', servicename)
            try:
                shutil.copytree(path, destination)
                m = importlib.import_module('.%s' % servicename, 'services')
                if m.__uses_blueprint__:
                    os.symlink('../../../../webui/templates/layout.html', os.path.join(destination, 'blueprint/templates/layout.html'))
                    os.symlink('../../../../webui/templates/layout_admin.html', os.path.join(destination, 'blueprint/templates/layout_admin.html'))
                    os.symlink('../../../../webui/templates/service.html', os.path.join(destination, 'blueprint/templates/service.html'))
                    os.symlink('../../../../webui/templates/list_services.html', os.path.join(destination, 'blueprint/templates/list_services.html'))
            except Exception as e:
                print(e)
                shutil.rmtree(destination)
                return False
    else:
        print('Service is faulty, please consult the errors.')
        return False

    print('Preparing the DB for service %s' % servicename)
    try:
        m = importlib.import_module('.%s' % servicename, 'services')
        if prepare_service_db(m.__service_name__, m.__description__, m.__fields__, m.__uses_blueprint__):
            print('Successfully prepared DB for service %s' % servicename)
        else:
            print('Failed to prepare the DB fro service %s', servicename)
            return False
    except Exception as e:
        print(e)
        print('Failed to load service %s due to a faulty module' % servicename)
        return False

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Service importer')
    parser.add_argument('--path',
                        metavar='url',
                        type=str,
                        nargs='+',
                        help='Path to the service to import')
    args = parser.parse_args()
    if not args.path or len(args.path) < 1:
        print('Please specify at least one service to import')
    else:
        for p in args.path:
            if register_service(p):
                print('Successfully registered new service %s' % p)
            else:
                print('Failed to register service %s' % p)
            # prepare_service_db('basics', 'Basic services and commands', (
            #     ('text', 'txt', Type.text, '.', (('2345', 'adsd'), ('2345', 'adsd'), ('2345', 'adsd'))),
            #     ('int', 'd', Type.int, '', ()),
            #     ('bool', 'truefalse', Type.bool, '', ())
            # ))