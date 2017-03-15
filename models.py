import hashlib

from google.appengine.ext import ndb


class Address(ndb.Model):
    """An address model."""
    # date stamp
    id = ndb.IntegerProperty()
    userID = ndb.StringProperty()
    date_created = ndb.DateProperty(auto_now_add=True)
    date_modified = ndb.DateProperty(auto_now_add=True)

    # Basic info.
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()

    # Address info.
    address = ndb.TextProperty()

    # Phone info.
    phone_number = ndb.StringProperty()


class User(ndb.Model):
    """
    User model
    """
    userID = ndb.StringProperty()
    username = ndb.StringProperty()
    password = ndb.TextProperty()

    def check_password(self, password):
        """
        compares user object password and password argument
        :param password:
        :return:
        """
        return hashlib.md5(password) == self.password


class Room(ndb.Model):
    """
    room to be booked
    """
    number = ndb.StringProperty()
    is_booked = ndb.BooleanProperty()


class Customer(ndb.Model):
    """
    Hotel customer
    """
    customerID = ndb.StringProperty()
    addressID = ndb.IntegerProperty()


class Booking(ndb.Model):
    """
    Booking model for storing customer booking records
    """
    customerID = ndb.StringProperty()
    room = ndb.StringProperty()
    is_active = ndb.BooleanProperty()
