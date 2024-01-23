from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

import simplejson as json
def init(db_uri="sqlite+pysqlite:///:memory:", echo=True):
    engine = create_engine(db_uri, echo=echo,
                           json_serializer=lambda obj: json.dumps(obj, ignore_nan=True))
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    return (engine, Session)