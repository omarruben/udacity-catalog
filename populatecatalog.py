from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base,Category, Item, User
import datetime

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# database.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# database.rollback()
database = DBSession()


# Create dummy user
User1 = User(name="Rufus the Great", username="rufus", password="xxx", email="rufino@udacity.com",
             picture='http://www.wearepetnation.com/wp-content/uploads/2011/12/Rufus-18.jpg')
database.add(User1)
database.commit()

# add a Category
category1 = Category(user_id=1, name="Desktop PC")
database.add(category1)
database.commit()

# add new item
item1 = Item(user_id=1, name="Powerspec 2000", description="The great performance and the best price",
                     category=category1,date=datetime.datetime.now())
database.add(item1)
database.commit()

# add new item
item2 = Item(user_id=1, name="Star All in One 3000", description="All in one is the best solution for your dorm",
                     category=category1,date=datetime.datetime.now())
database.add(item2)
database.commit()


# add a Category ****************************************
category2 = Category(user_id=1, name="Laptops")
database.add(category2)
database.commit()

# add new item
item3 = Item(user_id=1, name="HP Gaming Laptop pro", description="Play awesome games on the go",
                     category=category2,date=datetime.datetime.now())
database.add(item3)
database.commit()

# add new item
item4 = Item(user_id=1, name="Lenovo Entertainment GO", description="Best solution for your entertainment for the park",
                     category=category2,date=datetime.datetime.now())
database.add(item4)
database.commit()
