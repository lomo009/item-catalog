from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, CategoryItem

engine = create_engine('sqlite:///itemCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

category1 = Category(name="Clothing")

session.add(category1)
session.commit()

category2 = Category(name="Computers")

session.add(category2)
session.commit()

category3 = Category(name="Movies")

session.add(category3)
session.commit()

category4 = Category(name="Music")

session.add(category4)
session.commit()

category5 = Category(name="Sports")

session.add(category5)
session.commit()

categoryItem1 = CategoryItem(
  name="Air Jordan I - Notorious",
  subcategory="Shoes",
  description="NEW, never used, First pair of Air Jordan's ever made in 1984",
  price="$399.99",
  category=category1)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(
  name="Custom Tee-Shirts",
  subcategory="Tee-Shirts",
  description="Create your own custom tee-shirt with your design!",
  price="$14.99",
  category=category1)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(
  name="Good Conditioned MacBook Pro 2012",
  subcategory="Laptops",
  description="Used, good conditioned MacBook Pro late 2012 model; 16GB",
  price="$400.00",
  category=category2)

session.add(categoryItem3)
session.commit()

categoryItem4 = CategoryItem(
  name="The Incredibles",
  subcategory="Animation",
  description=(
    "Undercover superheroes living a normal life, are called to save the world"
    ),
  price="$4.99",
  category=category3)

session.add(categoryItem4)
session.commit()

categoryItem5 = CategoryItem(
  name="For the Love of the Game",
  subcategory="Drama",
  description="A pitcher reflects of his career in his last game",
  price="$4.99",
  category=category3)

session.add(categoryItem5)
session.commit()

categoryItem6 = CategoryItem(
  name="Scarface",
  subcategory="Action",
  description=(
    "In Miami 1980, a determined Cuban immigrant takes over a drug carel"
    ),
  price="$7.99",
  category=category3)

session.add(categoryItem6)
session.commit()

categoryItem7 = CategoryItem(
  name="Lil Wayne: Tha Carter 3",
  subcategory="Hip-Hop",
  description="The sixth studio album by American rapper Lil Wayne.",
  price="$9.99",
  category=category4)

session.add(categoryItem7)
session.commit()

categoryItem8 = CategoryItem(
  name="OAR: 34th and 8th",
  subcategory="Rock",
  description="34th & 8th is a live album by O.A.R. in NYC",
  price="$7.99",
  category=category4)

session.add(categoryItem8)
session.commit()

categoryItem9 = CategoryItem(
  name="Rawlings Heart of the Hide Dual Core 11.5",
  subcategory="Baseball",
  description=(
    "Rawlings has always been a fielder's top choice, this is no different."
    ),
  price="$249.99",
  category=category5)

session.add(categoryItem9)
session.commit()

categoryItem10 = CategoryItem(
  name="Cleveland Browns 16x16 Tavern Sign",
  subcategory="Collectibles",
  description=(
    "Display Cleveland Browns pride with this 16 x 16 tavern sign!"
    ),
  price="$49.99",
  category=category5)

session.add(categoryItem10)
session.commit()

print("Completed adding items to Catalog")
