#!/usr/bin/python3

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, func, desc
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Define your models here
class Restaurant(Base):
    __tablename__ = 'restaurants'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    reviews = relationship('Review', back_populates='restaurant')
    customers = relationship('Customer', secondary='reviews', back_populates='restaurants')

    @property
    def all_reviews(self):
        # Get all reviews for this restaurant in the requested format
        return [f"Review for {self.name} by {review.customer.full_name()}: {review.rating} stars." for review in self.reviews]

    @classmethod
    def fanciest(cls):
        # Find the restaurant with the highest price
        return session.query(cls).order_by(desc(cls.price)).first()

class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    rating = Column(Integer)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    restaurant = relationship('Restaurant', back_populates='reviews')
    customer = relationship('Customer', back_populates='reviews')

    def full_review(self):
        restaurant_name = self.restaurant.name
        customer_name = self.customer.full_name()
        return f"Review for {restaurant_name} by {customer_name}: {self.rating} stars."

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    reviews = relationship('Review', back_populates='customer')
    restaurants = relationship('Restaurant', secondary='reviews', back_populates='customers')

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def favorite_restaurant(self):
        # Use a subquery to find the restaurant with the highest rating for this customer
        subquery = session.query(Review.restaurant_id, func.max(Review.rating).label('max_rating')).filter_by(customer_id=self.id).group_by(Review.restaurant_id).subquery()
        favorite_restaurant_id = session.query(subquery.c.restaurant_id).order_by(desc(subquery.c.max_rating)).limit(1).scalar()
        return session.query(Restaurant).get(favorite_restaurant_id)

    def add_review(self, restaurant, rating):
        # Create a new review
        review = Review(restaurant=restaurant, customer=self, rating=rating)
        session.add(review)
        session.commit()

    def delete_reviews(self, restaurant):
        # Delete all reviews by this customer for the specified restaurant
        session.query(Review).filter_by(customer=self, restaurant=restaurant).delete()
        session.commit()

# Create SQLite database and session
engine = create_engine('sqlite:///database.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Create some sample data

# Create Restaurants
restaurant1 = Restaurant(name="Restaurant A", price=50.0)
restaurant2 = Restaurant(name="Restaurant B", price=60.0)

# Create Customers
customer1 = Customer(first_name="Humphrey", last_name="Njuguna")
customer2 = Customer(first_name="Juliet", last_name="Nyongesa")

# Add Reviews
customer1.add_review(restaurant1, 4)
customer1.add_review(restaurant2, 5)
customer2.add_review(restaurant1, 3)

# Commit the data to the database
session.commit()

# Demonstrate the methods

# Customer full_name() method
print(customer1.full_name())  # Output: Humphrey Njuguna

# Customer favorite_restaurant() method
favorite_restaurant = customer1.favorite_restaurant()
print(f"{customer1.full_name()}'s favorite restaurant is {favorite_restaurant.name}.")

# Customer reviews() method
customer_reviews = customer1.reviews
for review in customer_reviews:
    print(review.full_review())

# Restaurant fanciest() method
fanciest_restaurant = Restaurant.fanciest()
print(f"The fanciest restaurant is {fanciest_restaurant.name} with a price of ${fanciest_restaurant.price}.")

# Restaurant all_reviews() method
restaurant1_reviews = restaurant1.all_reviews
for review in restaurant1_reviews:
    print(review)

# ... Your code continues ...
