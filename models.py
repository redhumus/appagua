"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later

db.commit()



# Crear la tabla calendario
db.define_table('calendario',
                Field('mes', 'string', length=128, required=True),
                Field('tiempo', 'string', length=256, required=True),
                Field('actividades', 'string', length=256, required=True),
                Field('fiestas', 'string', length=256, required=True)
                )


db.commit()