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
def prepare_service_db(sqlsession, name, desc, fields):
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
    s = Service(name=name, fields=f)
    sqlsession.add(s)
    sqlsession.commit()
    print('Successfully prepared DB new service %s: %s' % (name, desc))
    if fields:
        print('%s contains the following fields:' % name)
        print(m_string)
    else:
        print('%s contains no fields.' % name)
    return True


def register_service(path):
    print('Importing service from %s.' % path)

    filename = os.path.basename(path)
    servicename = filename[:-3]
    if os.path.isfile(os.path.join('service/', servicename)):
        print('Service could not be imported due to a service using the same name existing yet.')
        return False
    else:
        dstdir = os.path.join('services/', os.path.dirname(path))
        try:
            shutil.copy(path, dstdir)
        except Exception as e:
            print(e)
            return False

    print('Preparing the DB for service %s' % servicename)
    try:
        m = importlib.import_module('.%s' % servicename, 'services')
        if prepare_service_db(m.__service_name__, m.__description__, m.__fields__):
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
    print(args)
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