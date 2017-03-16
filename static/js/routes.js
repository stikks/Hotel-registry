/**
 * Created by stikks-workstation on 3/16/17.
 */

var app = angular.module('hotels.routes', ['ui.router']);

app.config(function($stateProvider, $urlRouterProvider){
    $stateProvider
    .state('home', {
        url: '/',
        templateUrl: 'partials/home',
        controller: 'BaseController'
    })
    .state('customers', {
        url: '/customers',
        templateUrl: 'customers',
        controller: 'CustomerController'
    })
    .state('rooms', {
        url: '/rooms',
        templateUrl: 'rooms',
        controller: 'RoomController'
    })
    .state('bookings', {
        url: '/bookings',
        templateUrl: 'bookings',
        controller: 'BookingController'
    });
    $urlRouterProvider.otherwise('/');
});

console.log(app.config);