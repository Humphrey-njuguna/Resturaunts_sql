#!/usr/bin/python3
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

#all classes comes here
class Restaurant(Base):
    __tablename__ = 'restaurants'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    reviews = relationship('Review', back_populates='restaurant')
    customers = relationship('Customer', secondary='reviews', back_populates='restaurants')

class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    rating = Column(Integer)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    restaurant = relationship('Restaurant', back_populates='reviews')
    customer = relationship('Customer', back_populates='reviews')

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    reviews = relationship('Review', back_populates='customer')
    restaurants = relationship('Restaurant', secondary='reviews', back_populates='customers')



engine = create_engine('sqlite:///database.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Review class methods
class Review(Base):
    # ...

    def customer(self):
        return self.customer

    def restaurant(self):
        return self.restaurant

    def full_review(self):
        return f'Review for {self.restaurant.name} by {self.customer.full_name()}: {self.rating} stars.'

# Restaurant class methods
class Restaurant(Base):
    # ...

    def reviews(self):
        return self.reviews

    def customers(self):
        return self.customers

    @classmethod
    def fanciest(cls):
        return session.query(cls).order_by(cls.price.desc()).first()

    def all_reviews(self):
        reviews = []
        for review in self.reviews:
            reviews.append(review.full_review())
        return reviews

# Customer class methods
class Customer(Base):
    # ...

    def reviews(self):
        return self.reviews

    def restaurants(self):
        return self.restaurants

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def favorite_restaurant(self):
        max_rating = 0
        favorite_restaurant = None
        for review in self.reviews:
            if review.rating > max_rating:
                max_rating = review.rating
                favorite_restaurant = review.restaurant
        return favorite_restaurant

    def add_review(self, restaurant, rating):
        new_review = Review(restaurant=restaurant, customer=self, rating=rating)
        session.add(new_review)
        session.commit()

    def delete_reviews(self, restaurant):
        reviews_to_delete = [review for review in self.reviews if review.restaurant == restaurant]
        for review in reviews_to_delete:
            session.delete(review)
        session.commit()





