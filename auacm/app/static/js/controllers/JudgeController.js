app.controller('JudgeController', ['$scope', '$rootScope', '$http',
        '$routeParams', '$window',
        function($scope, $rootScope, $http, $routeParams, $window) {
    var i;
    $scope.problem = '';
    $scope.submitted = [];
    $scope.python = {version: 'py'};
    $scope.problemSelected = false;
    $scope.fileSelected = false;

    if ($routeParams.problem) {
        for (i = 0; i < $scope.problems.length; i++) {
            var problem = $scope.problems[i];
            if (problem.pid === parseInt($routeParams.problem)) {
                $scope.problem = problem;
                $scope.problemSelected = true;
                break;
            }
        }
    }

    var STATUS_NAMES = {
        compile: 'Compilation Error',
        runtime: 'Runtime Error',
        running: 'Running',
        timeout: 'Time Limit Exceeded',
        incorrect: 'Incorrect',
        correct: 'Correct'
    };

    // Watch the problem variable in case the user does not press enter or click
    // the problem name from the dropdown
    $scope.$watch('problem', function(newValue, oldValue) {
        if (typeof newValue === 'string') {
            for (var i = 0; i < $scope.problems.length; i++) {
                var problem = $scope.problems[i];
                if (problem.name.toLowerCase().trim() ===
                        newValue.toLowerCase().trim()) {
                    $scope.problem = problem;
                    $scope.problemSelected = true;
                    return;
                }
            }
            $scope.problemSelected = false;
        } else {
            $scope.problemSelected = true;
        }
    });

    // Map problem ID's to the name for easy retrieval
    var pidToName = new Map();
    for (i = 0; i < $scope.problems.length; i++) {
        pidToName[$scope.problems[i].pid] = $scope.problems[i].name;
    }

    $scope.submit = function() {
        if ($scope.file.name.toLowerCase().includes('bern')) {
            $rootScope.bernitize = 'bernitdown';
        }
        var fd = new FormData();
        fd.append('pid', $scope.problem.pid);
        fd.append('file', $scope.file);
        if ($scope.file.name.endsWith('.py')) {
            fd.append('python', $scope.python.version);
        }
        var submission = {};
        var name;
        for (var i = 0; i < $scope.problems.length; i++) {
            if ($scope.problems[i].pid === $scope.problem.pid) {
                name = $scope.problems[i].name;
                break;
            }
        }
        submission.problem = name;
        submission.fileName = $scope.file.name;
        submission.status = 'uploading';
        submission.statusDescription = 'Uploading';
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
            submission.statusDescription = 'Compiling';
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
                submitted.statusDescription = STATUS_NAMES[submitted.status];
                $scope.$apply();
                break;
            }
        }
    });

    // Get the recent submission for this user
    var getSubmits = function() {
        // FIXME: Sometimes current user is undefined. Happens if this is
        // executed before the call to `/api/me` completes.
        if ($scope.username !== undefined) {
            $http.get('/api/submit?user=' + $scope.username + '&limit=10')
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
                        current.statusDescription = STATUS_NAMES[current.status];
                    }
                }, function (error) {
                    console.error(error);
                });
        } else {
            console.error('Username is not defined');
        }
    };
    getSubmits();

    // Reset recent submits upon logging in or out
    $scope.$watch('loggedIn', function(newValue, oldValue) {
        if (newValue) {
            getSubmits();
        } else {
            $scope.submitted = [];
        }
    });

    if ($scope.problems) {
        $scope.problems.sort(function(a, b) {
            return a.name > b.name ? 1 : (a.name < b.name ? -1 : 0);
        });
    }

}]);
