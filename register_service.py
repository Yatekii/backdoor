from models import Service
from models import Field, Type
from models import FieldChoice
import helpers


import re


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
def register_service(sqlsession, name, desc, fields):
    # fields = (key, description, type, condition, choices = (c_value, c_description)
    m_string = ''
    f = []
    s = sqlsession.query(Service).filter_by(name=name).first()
    if s:
        print('Service %s exists yet. Aborting.' % name)
        return False
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
    print('Successfully registered new service %s: %s' % (name, desc))
    print('%s the following fields:' % name)
    print(m_string)
    return True


if __name__ == "__main__":
    register_service('basics', 'Basic services and commands', (
        ('text', 'txt', Type.text, '.', (('2345', 'adsd'), ('2345', 'adsd'), ('2345', 'adsd'))),
        ('int', 'd', Type.int, '', ()),
        ('bool', 'truefalse', Type.bool, '', ())
    ))