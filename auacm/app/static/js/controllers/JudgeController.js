app.controller('JudgeController', ['$scope', '$rootScope', '$http',
        '$routeParams', '$window',
        function($scope, $rootScope, $http, $routeParams, $window) {
    $scope.pid = parseInt($routeParams.problem);
    $scope.submitted = [];
    $scope.python = {version: 'py'};

    // Map problem ID's to the name for easy retrieval
    var pidToName = new Map();
    for (var i = 0; i < $scope.problems.length; i++) {
        pidToName[$scope.problems[i].pid] = $scope.problems[i].name;
    }

    $scope.submit = function() {
        if ($scope.file.name.toLowerCase().includes('bern')) {
            $rootScope.bernitize = 'bernitdown';
        }
        var fd = new FormData();
        fd.append('pid', $scope.pid);
        fd.append('file', $scope.file);
        if ($scope.file.name.endsWith('.py')) {
            fd.append('python', $scope.python.version);
        }
        var submission = {};
        var name;
        for (var i = 0; i < $scope.problems.length; i++) {
            if ($scope.problems[i].pid === $scope.pid) {
                name = $scope.problems[i].name;
                break;
            }
        }
        submission.problem = name;
        submission.fileName = $scope.file.name;
        submission.status = 'uploading';
        $http({
            method: 'POST',
            url: '/api/submit',
            headers: {'Content-Type': undefined},
            transformRequest: angular.identity,
            data: fd
        }).then(function(response) {
            submission.submissionId = response.data.data.submissionId;
            submission.status = 'compiling';
            submission.testNum = 0;
            $scope.submitted.unshift(submission);
            if ($scope.submitted.length > 10) {
                $scope.submitted.pop();
            }
        }, function(response) {
            console.error(response);
        });
    };

    $scope.socket.on('status', function(event) {
        for (var i = 0; i < $scope.submitted.length; i++) {
            if (event.submissionId === $scope.submitted[i].submissionId) {
                var submitted = $scope.submitted[i];
                submitted.status = event.status;
                submitted.testNum = event.testNum;
                $scope.$apply();
                break;
            }
        }
    });

    // Get the recent submission for this user
    var getSubmits = function() {
        // FIXME: Sometimes current user is undefined
        if ($scope.username !== undefined) {
            $http.get('/api/submit/user/' + $scope.username + '/10')
                .then(function (response) {
                    $scope.submitted = response.data.data;

                    // Do a smidge of parsing
                    for (var i = 0; i < $scope.submitted.length; i++) {
                        var current = $scope.submitted[i];

                        current.problem = pidToName[current.pid];
                        current.submissionId = current.job_id;
                        if (current.status == 'good') {
                            current.status = 'correct';
                        } else if (current.status == 'wrong') {
                            current.status = 'incorrect';
                        }
                    }
                }, function (error) {
                    console.error(error);
                });
        }
    };
    getSubmits();

    if ($scope.problems) {
        $scope.problems.sort(function(a, b) {
            return a.name > b.name ? 1 : (a.name < b.name ? -1 : 0);
        });
    }

}]);
