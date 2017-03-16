/**
 * Created by stikks-workstation on 3/16/17.
 */

var app = angular.module('hotels.controllers', []);

app.controller('BaseController', function ($scope, $timeout, $q, $rootScope) {

    console.log('here');

    $scope.init = function () {

    };
});

app.controller('CustomerController', function ($scope, $rootScope, Customer, $timeout) {

    var load_customers = function () {
        var deferred = $q.defer();

        $timeout(function () {
            var customers = Customer.query();
            customers.$promise.then(function (result) {
                $scope.data.customers = result
            })
        });

        return deferred.promise;
    };

    $scope.init = function () {
      $scope.data = {"customers": []}
    };

    var startParallel = function () {

        $q.all([load_customers()]).then(
            function (successResult) {
            }, function (failureReason) {
                // renew()
            }
        );
    };
});

app.controller('RoomController', function ($scope, $rootScope, Room, $timeout) {

    var load_rooms = function () {
        var deferred = $q.defer();

        $timeout(function () {
            var rooms = Room.query();
            rooms.$promise.then(function (result) {
                $scope.data.rooms = result
            })
        });

        return deferred.promise;
    };

    $scope.init = function () {
      $scope.data = {"rooms": []}
    };

    var startParallel = function () {

        $q.all([load_rooms()]).then(
            function (successResult) {
            }, function (failureReason) {
                // renew()
            }
        );
    };
});

app.controller('BookingController', function ($scope, $rootScope, Booking, $timeout) {

    var load_bookings = function () {
        var deferred = $q.defer();

        $timeout(function () {
            var bookings = Booking.query();
            bookings.$promise.then(function (result) {
                $scope.data.bookings = result
            })
        });

        return deferred.promise;
    };

    $scope.init = function () {
      $scope.data = {"bookings": []}
    };

    var startParallel = function () {

        $q.all([load_bookings()]).then(
            function (successResult) {
            }, function (failureReason) {
                // renew()
            }
        );
    };
});