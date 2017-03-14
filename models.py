from google.appengine.ext import ndb


class Address(ndb.Model):
    """An address model."""
    # date stamp
    date_created = ndb.DateProperty(auto_now_add=True)
    date_modified = ndb.DateProperty(auto_now_add=True)

    # Basic info.
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    birth_day = ndb.DateProperty()

    # Address info.
    address = ndb.TextProperty()

    # Phone info.
    phone_number = ndb.StringProperty()


class Room(ndb.Model):
    """
    room to be booked
    """
    number = ndb.StringProperty()
    floor = ndb.StringProperty()


class Customer(ndb.Model):
    """
    Hotel customer
    """
    address_id = ndb.StringProperty()


class Booking(ndb.Model):
    """
    Booking model for storing customer booking records
    """
    customer_id = ndb.StringProperty()
    room = ndb.StringProperty()