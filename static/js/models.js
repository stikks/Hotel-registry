/**
 * Created by stikks-workstation on 3/16/17.
 */

var app = angular.module('hotels.models', ['ngResource']);

// User Account resources
app.factory('User', function ($resource) {
    return $resource('/v1/users/:id/', { id: '@_id' }, {
        query: {
            method: 'GET', isArray: false
        },
        update: {
          method: 'PUT' // this method issues a PUT request
        }
    });
});

app.factory('Customer', function ($resource) {
    return $resource('/v1/customers/:id', { id: '@_id'}, {
        query: {
            method: 'GET', isArray: false
        },
        update: {
          method: 'PUT' // this method issues a PUT request
        }
    });
});

app.factory('Booking', function ($resource) {
    return $resource('/v1/bookings/:id/', { id: '@_id' }, {
        query: {
            method: 'GET', isArray: false
        },
        update: {
          method: 'PUT' // this method issues a PUT request
        }
    });
});

app.factory('Room', function ($resource) {
    return $resource('/v1/rooms/:id/', { id: '@_id'}, {
        query: {
            method: 'GET', isArray: false
        },
        update: {
          method: 'PUT' // this method issues a PUT request
        }
    });
});