from sqlalchemy import create_engine, text, Table, Column,Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List, Optional

def Core_db():
    #engine facts:
    #1) sqlite: what kind of db are we comunicating with; it liks to an sqlalchemy called dialect
    #2) pysqlite: what DBAPI are we using (third party driver that SQLAlchemy use to interact with a particular db)
    #3) /:memory: indicates to sqlite3 module that we are using an in-memory database

    #Connection Core = Session ORM
    #The purpose of the engine is to connect to a db by providing a connection object

    #create engine = lazy connection (at first task requested)
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

    #when working with the core, all the db operations are made with the Connection
    #since the Connection object creates an opne resource against the db, we want to limit it's use to a specific context (with)
    #text for temporary sql statemant
    with engine.connect() as conn:
        result = conn.execute(text("select 'hello world'"))

        #database metadata = python objects representing db concepts like tables and columns
        #python table = variable to represent tables in python (ORM manages those automatically)
        #metadata = dictioary of tables containing all the pair(table, name)
        #metadata can be accessed by orm with BaseClass

        metadata_obj = MetaData()

        #columns collection can be accessed in terms of the parent table via an associative array located at Table.c
        #Integer/String: classes that represent SQL datatypes; can receive length etc.

        incidents_table = Table(
            "incident_header",
            metadata_obj, #assings itself to the metadata collection
            Column("id", Integer, primary_key=True), #represent a column in a db table, and ssings itself to the table object 
            Column("type", String(30)),# the column contains: a string name and a type object
        )

        incidents_info = Table(
            "incident_info",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("incident_id", Integer, ForeignKey("incident_header.id"), nullable=False),
            Column("icon_category", Integer),
        )

        #invokes the create table statements
        metadata_obj.create_all(engine)


def ORM_db():
    #declarative base is a metadata created automatically
    #this collection retain class -> table
    class Base(DeclarativeBase):
        pass

    #when a new class is created by inheriting the Base, it will be atuomatically associated with a db table (not impl)
    class incident_table_orm(Base):
        #automatically creates the table
        __tablename__="incidents_header"

        id: Mapped[int] = mapped_column(primary_key=True)
        type: Mapped[str] = mapped_column(String(30))

        def __repr__(self) -> str:
            return f"id: {self.id}, type: {self.type}"

    class incidents_info_orm(Base):
        __tablename__ = "incidents_info"

        id: Mapped[int] = mapped_column(primary_key=True)
        incident_id: Mapped[int] = mapped_column(ForeignKey("incidents_table_orm.id"))
        icon_category: Mapped[int] = mapped_column(Integer)

        def __repr__(self) -> str:
            return f"id: {self.id}, icon category: {self.icon_category}"