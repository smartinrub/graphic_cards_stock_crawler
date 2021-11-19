import os
from typing import List

import sqlalchemy as db
from sqlalchemy import String, Column, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func, desc

Base = declarative_base()


class GraphicCard(Base):
    __tablename__ = 'graphic_card'
    model = Column(String, primary_key=True)
    max_price = Column(DateTime)


class Stock(Base):
    __tablename__ = 'stock'
    id = Column(String, primary_key=True)
    name = Column(String)
    model = Column(String)
    price = Column(Float)
    in_stock_date = Column(DateTime, server_default=func.now())


class DB:
    session = None

    def __get_sql_session(self):
        if not self.session:
            engine = db.create_engine(
                f'mysql+pymysql://{os.getenv("MARIADB_USER")}:{os.getenv("MARIADB_PASSWORD")}@{os.getenv("MARIADB_HOST")}:{os.getenv("MARIADB_PORT")}/{os.getenv("MARIADB_SCHEMA")}')
            engine.connect()
            Session = db.orm.sessionmaker()
            Session.configure(bind=engine)
            self.session = Session()
        return self.session

    def get_all_graphic_cards(self) -> List[GraphicCard]:
        return self.__get_sql_session().query(GraphicCard).all()

    def get_all_stock_by_name(self, name: str) -> List[Stock]:
        return self.__get_sql_session().query(Stock).filter_by(name=name).order_by(desc(Stock.in_stock_date)).all()

    def add_stock(self, stock: Stock):
        self.__get_sql_session().add(stock)
        self.__get_sql_session().commit()
