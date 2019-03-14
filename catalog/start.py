from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from setup import *

engine = create_engine('sqlite:///laptop.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Delete laptop if it exists.
session.query(Laptop).delete()
# Delete laptopdetails if it exists.
session.query(Types).delete()
# Delete User if exists.
session.query(LapyUser).delete()

# Createing sample users data
User1 = LapyUser(name="RagaNavya.Mokkapati",
                 email="navyachowdary225@gmail.com")
session.add(User1)
session.commit()
print (" Added Successfully First User")
User2 = LapyUser(name="navyadolly",
                 email="raganavyamokkapati9999@gmail.com")
session.add(User2)
session.commit()
print("Added Successfully Second User")
# Creating sample laptop companys
laptop1 = Laptop(name="Dell",
                 user_id=1)
session.add(laptop1)
session.commit()

laptop2 = Laptop(name="Hp",
                 user_id=1)
session.add(laptop2)
session.commit

laptop3 = Laptop(name="Acer",
                 user_id=1)
session.add(laptop3)
session.commit()
laptop4 = Laptop(name="Lenovo",
                 user_id=1)
session.add(laptop4)
session.commit()
laptop5 = Laptop(name="Apple",
                 user_id=1)
session.add(laptop5)
session.commit()
laptop6 = Laptop(name="Samsung",
                 user_id=1)
session.add(laptop6)
session.commit()
laptop7 = Laptop(name="Asus",
                 user_id=1)
session.add(laptop7)
session.commit()
laptop8 = Laptop(name="Toshibha",
                 user_id=2)
session.add(laptop8)
session.commit()
laptop9 = Laptop(name="Aspire",
                 user_id=2)
session.add(laptop9)
session.commit()
# Populare a bykes with models for testing
# Using different users for bykes names year also
laptop1 = Types(lapyname="Apple",
                speciality="high speed",
                price="60000",
                ram="8gb",
                storage="1tb",
                warrenty="2yrs",
                rating="excellent",
                date=datetime.datetime.now(),
                laptopid=1,
                lapyuser_id=1)
session.add(laptop1)
session.commit()
laptop2 = Types(lapyname="Hp",
                speciality="fast charging",
                price="50000",
                ram="4gb",
                storage="1tb",
                warrenty="1yr",
                rating="awesome",
                date=datetime.datetime.now(),
                laptopid=2,
                lapyuser_id=1)
session.add(laptop2)
session.commit()
laptop3 = Types(lapyname="Acer",
                speciality="high speed",
                price="55000",
                ram="8gb",
                storage="2tb",
                warrenty="2yrs",
                rating="excellent",
                date=datetime.datetime.now(),
                laptopid=3,
                lapyuser_id=1)
session.add(laptop3)
session.commit()
laptop4 = Types(lapyname="Lenovo",
                speciality="fast charging",
                price="60000",
                ram="8gb",
                storage="1tb",
                warrenty="2yrs",
                rating="super",
                date=datetime.datetime.now(),
                laptopid=4,
                lapyuser_id=1)
session.add(laptop4)
session.commit()
laptop5 = Types(lapyname="Dell",
                speciality="high speed and fast charging",
                price="80000",
                ram="16gb",
                storage="2tb",
                warrenty="2yrs",
                rating="excellent",
                date=datetime.datetime.now(),
                laptopid=5,
                lapyuser_id=1)
session.add(laptop5)
session.commit()
laptop6 = Types(lapyname="Samsung",
                speciality="large storage",
                price="60000",
                ram="8gb",
                storage="4tb",
                warrenty="2yrs",
                rating="awesome",
                date=datetime.datetime.now(),
                laptopid=6,
                lapyuser_id=1)
session.add(laptop6)
session.commit()
laptop7 = Types(lapyname="Asus",
                speciality="high speed and reasonable cost",
                price="45000",
                ram="4gb",
                storage="1tb",
                warrenty="2yrs",
                rating="excellent",
                date=datetime.datetime.now(),
                laptopid=7,
                lapyuser_id=1)
session.add(laptop7)
session.commit()
laptop8 = Types(lapyname="Toshibha",
                speciality="high speed and reasonable cost",
                price="45000",
                ram="4gb",
                storage="1tb",
                warrenty="2yrs",
                rating="nice",
                date=datetime.datetime.now(),
                laptopid=8,
                lapyuser_id=2)
session.add(laptop8)
session.commit()
laptop9 = Types(lapyname="Aspire",
                speciality="high speed and reasonable cost",
                price="50000",
                ram="4gb/8gb",
                storage="1tb",
                warrenty="2yrs",
                rating="excellent",
                date=datetime.datetime.now(),
                laptopid=9,
                lapyuser_id=2)
session.add(laptop9)
session.commit()

print("Sample User,Restaurent and menuItems has been insert!")
