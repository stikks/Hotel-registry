import hashlib

from google.appengine.ext import ndb


class Address(ndb.Model):
    """An address model."""
    # date stamp
    id = ndb.TextProperty(indexed=True)
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
    id = ndb.TextProperty(indexed=True)
    username = ndb.StringProperty(indexed=True)
    password = ndb.TextProperty(indexed=True)
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    address = ndb.TextProperty()
    phone_number = ndb.StringProperty()
    is_admin = ndb.BooleanProperty()

    # date stamp
    date_created = ndb.DateProperty(auto_now_add=True)
    date_modified = ndb.DateProperty(auto_now_add=True)

    def check_password(self, password):
        """
        compares user object password and password argument
        :param password:
        :return:
        """
        return hashlib.md5(password).hexdigest() == self.password


class Room(ndb.Model):
    """
    room to be booked
    """
    id = ndb.TextProperty(indexed=True)
    number = ndb.StringProperty()
    is_booked = ndb.BooleanProperty()

    # date stamp
    date_created = ndb.DateProperty(auto_now_add=True)
    date_modified = ndb.DateProperty(auto_now_add=True)


class Customer(ndb.Model):
    """
    Hotel customer
    """
    id = ndb.TextProperty(indexed=True)
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    address = ndb.TextProperty()
    phone_number = ndb.StringProperty()

    # date stamp
    date_created = ndb.DateProperty(auto_now_add=True)
    date_modified = ndb.DateProperty(auto_now_add=True)


class Booking(ndb.Model):
    """
    Booking model for storing customer booking records
    """
    id = ndb.TextProperty(indexed=True)
    customerID = ndb.StringProperty()
    room_number = ndb.StringProperty()
    is_active = ndb.BooleanProperty()

    # date stamp
    date_created = ndb.DateProperty(auto_now_add=True)
    date_modified = ndb.DateProperty(auto_now_add=True)
