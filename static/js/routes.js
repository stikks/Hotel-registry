/**
 * Created by stikks-workstation on 3/16/17.
 */

var app = angular.module('hotels.routes', ['ui.router']);

app.config(function ($stateProvider, $urlRouterProvider) {
    $stateProvider
        .state('home', {
            url: '/',
            templateUrl: '/static/partials/home.html',
            controller: 'HomeController'
        })
        .state('customers', {
            url: '/customers',
            templateUrl: '/static/partials/customers.html',
            controller: 'CustomerController'
        })
        .state('create_customer', {
            url: '/create',
            parent: 'customers',
            templateUrl: '/static/partials/forms/customer.html'
        })
        .state('update_customer', {
            url: '/customers/:id/update',
            templateUrl: '/static/partials/forms/customer.html',
            controller: 'CustomerController'
        })
        .state('rooms', {
            url: '/rooms',
            templateUrl: '/static/partials/rooms.html',
            controller: 'RoomController'
        })
        .state('create_room', {
            url: '/create',
            parent: 'rooms',
            templateUrl: '/static/partials/forms/room.html'
        })
        .state('update_room', {
            url: '/rooms/:id/update',
            templateUrl: '/static/partials/forms/room.html',
            controller: 'RoomController'
        })
        .state('bookings', {
            url: '/bookings',
            templateUrl: '/static/partials/bookings.html',
            controller: 'BookingController'
        })
        .state('create_booking', {
            url: '/create',
            parent: 'bookings',
            templateUrl: '/static/partials/forms/booking.html'
        })
        .state('update_booking', {
            url: '/bookings/:id/update',
            templateUrl: '/static/partials/forms/booking.html',
            controller: 'BookingController'
        });
    $urlRouterProvider.otherwise('/');
});