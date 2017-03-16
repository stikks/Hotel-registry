/**
 * Created by stikks-workstation on 3/16/17.
 */

var app = angular.module('hotels.controllers', []);

app.controller('HomeController', function ($scope, $timeout, $q, Customer, Booking, Room) {

    var load_bookings = function () {
        var deferred = $q.defer();

        $timeout(function () {
            var bookings = Booking.query();

            bookings.$promise.then(function (data) {
                $scope.data.bookings = data.results
                $scope.data.booking_count = data.count
            })
        });

        return deferred.promise;
    };

    var load_rooms = function () {
        var deferred = $q.defer();

        $timeout(function () {
            var rooms = Room.query();
            rooms.$promise.then(function (data) {
                $scope.data.rooms = data.results
                $scope.data.room_count = data.count
            })
        });

        return deferred.promise;
    };

    var load_customers = function () {
        var deferred = $q.defer();

        $timeout(function () {
            var customers = Customer.query();

            customers.$promise.then(function (data) {
                $scope.data.customers = data.results
                $scope.data.customer_count = data.count
            })
        });

        return deferred.promise;
    };

    var startParallel = function () {

        $q.all([load_bookings(), load_rooms(), load_customers()]).then(
            function (successResult) {
            }, function (failureReason) {
                // renew()
            }
        );
    };

    var init = function () {

        $scope.data = {"rooms": [], "room_count": 0, 'bookings': [], "booking_count": 0, "customers": [], "customer_count": 0};
        startParallel();
    }

    init();
});

app.controller('CustomerController', function ($scope, $rootScope, Customer, $timeout, $q, $state, $stateParams) {

    var load_customers = function () {
        var deferred = $q.defer();

        $timeout(function () {
            var customers = Customer.query();

            customers.$promise.then(function (data) {
                $scope.data.customers = data.results
                $scope.data.customer_count = data.count
            })
        });

        return deferred.promise;
    };

    var startParallel = function () {

        $q.all([load_customers()]).then(
            function (successResult) {
            }, function (failureReason) {
                // renew()
            }
        );
    };

    $scope.save = function () {
        var customer = new Customer($scope.form);
        if ($scope.form.id) {
            customer.$update({id: $scope.form.id}, function (data) {
                $state.go('^')
            }, function (err) {
                if (err) {
                    $scope.data.error = err.data
                }
            })
        }
        else {
            customer.$save(function (data) {
                $state.go('^')
            }, function (err) {
                if (err) {
                    $scope.data.error = err.data
                }
            })
        }

    };

    $scope.delete = function (customer_id) {
        var customer = new Customer({id: customer_id});
        customer.$delete({id: customer_id}, function (data, status) {
            location.reload()
        }, function (err) {
            if (err) {
                $scope.data.error = err.data.message
            }
        })
    };

    $scope.data = {"customers": [], "customer_count": 0}
    startParallel();
    $scope.form = {'first_name': null, "last_name": null, "address": null, "phone_number": null};

    if ($stateParams.id) {
        $timeout(function () {
            var cust = Customer.get({id: $stateParams.id})
            cust.$promise.then(function (data) {
                $scope.form = data
                if ($scope.form.phone_number) {
                    $scope.form.phone_number = parseInt($scope.form.phone_number)
                }
            }, function (err) {
                $state.go('^')
            })
        })
    }
    ;
});

app.controller('RoomController', function ($scope, $rootScope, Room, $timeout, $q, $state) {

    var load_rooms = function () {
        var deferred = $q.defer();

        $timeout(function () {
            var rooms = Room.query();
            rooms.$promise.then(function (data) {
                $scope.data.rooms = data.results
                $scope.data.room_count = data.count
            })
        });

        return deferred.promise;
    };

    var startParallel = function () {

        $q.all([load_rooms()]).then(
            function (successResult) {
            }, function (failureReason) {
                // renew()
            }
        );
    };

    var init = function () {
        $scope.data = {"rooms": [], "room_count": 0, 'error': null};
        startParallel();
        $scope.form = {'number': 0};
    }

    init();

    $scope.save = function () {
        var room = new Room({'number': $scope.form.number})
        room.$save(function (data) {
            $state.go('^')
        }, function (err) {
            if (err) {
                $scope.data.error = err.data
            }
        })
    }

    $scope.delete = function (room_id) {
        var room = new Room({id: room_id});
        room.$delete({id: room_id}, function (data, status) {
            location.reload()
        }, function (err) {
            if (err) {
                $scope.data.error = err.data.message
            }
        })
    };

});

app.controller('BookingController', function ($scope, $rootScope, Booking, Room, Customer, $timeout, $q, $state, $stateParams) {

    var load_bookings = function () {
        var deferred = $q.defer();

        $timeout(function () {
            var bookings = Booking.query();

            bookings.$promise.then(function (data) {
                $scope.data.bookings = data.results
                $scope.data.bookings_count = data.count
            })
        });

        return deferred.promise;
    };

    var load_rooms = function () {
        var deferred = $q.defer();

        $timeout(function () {
            var rooms = Room.query();
            rooms.$promise.then(function (data) {
                $scope.data.rooms = data.results
                $scope.data.room_count = data.count
            })
        });

        return deferred.promise;
    };

    var load_customers = function () {
        var deferred = $q.defer();

        $timeout(function () {
            var customers = Customer.query();

            customers.$promise.then(function (data) {
                $scope.data.customers = data.results
                $scope.data.customer_count = data.count
            })
        });

        return deferred.promise;
    };

    var startParallel = function () {

        $q.all([load_bookings(), load_rooms(), load_customers()]).then(
            function (successResult) {
            }, function (failureReason) {
                // renew()
            }
        );
    };

    var init = function () {
        $scope.data = {
            "bookings": [],
            "bookings_count": 0,
            "rooms": [],
            "room_count": 0,
            "customers": [],
            "customer_count": 0,
            "error": null
        }
        startParallel()
        $scope.form = {'room_number': 0, "customerID": null};
        if ($stateParams.id) {
            $timeout(function () {
                var book = Booking.get({id: $stateParams.id})
                book.$promise.then(function (data) {
                    $scope.form = data
                    if ($scope.form.room_number) {
                        $scope.form.room_number = parseInt($scope.form.room_number)
                    }
                }, function (err) {
                    $state.go('^')
                })
            })
        }
    }

    init();

    $scope.delete = function (booking_id) {
        var booking = new Booking({id: booking_id});
        booking.$delete({id: booking_id}, function (data, status) {
            location.reload()
        }, function (err) {
            if (err) {
                $scope.data.error = err.data.message
            }
        })
    };

    $scope.save = function () {
        var booking = new Booking($scope.form);
        if ($scope.form.id) {
            booking.$update({id: $scope.form.id}, function (data) {
                $state.go('^')
            }, function (err) {
                if (err) {
                    $scope.data.error = err.data
                }
            })
        }
        else {
            booking.$save(function (data) {
                $state.go('^')
            }, function (err) {
                if (err) {
                    $scope.data.error = err.data
                }
                console.log($scope.data.error)
            })
        }

    };

    $scope.cancel = function (booking_id) {
        var book = new Booking({'id': booking_id});
        book.$update({'id': booking_id, 'is_active': false}, function (data) {
            location.reload()
        }, function (err) {
            if (err) {
                $scope.data.error = err.data
            }
        })

    };
});