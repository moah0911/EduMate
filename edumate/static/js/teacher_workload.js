// Teacher Workload Dashboard Charts
document.addEventListener('DOMContentLoaded', function() {
    // Time Savings Chart
    const timeSavingsCtx = document.getElementById('timeSavingsChart').getContext('2d');
    const timeSavingsChart = new Chart(timeSavingsCtx, {
        type: 'line',
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            datasets: [
                {
                    label: 'Time with AI (hours)',
                    data: [5, 4.5, 4, 3.5],
                    borderColor: '#4e73df',
                    backgroundColor: 'rgba(78, 115, 223, 0.05)',
                    borderWidth: 2,
                    pointBackgroundColor: '#4e73df',
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'Estimated Time without AI (hours)',
                    data: [15, 16, 17, 18],
                    borderColor: '#e74a3b',
                    backgroundColor: 'rgba(231, 74, 59, 0.05)',
                    borderWidth: 2,
                    pointBackgroundColor: '#e74a3b',
                    tension: 0.3,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Hours'
                    }
                }
            }
        }
    });

    // Assignment Types Chart
    const assignmentTypesCtx = document.getElementById('assignmentTypesChart').getContext('2d');
    const assignmentTypesChart = new Chart(assignmentTypesCtx, {
        type: 'doughnut',
        data: {
            labels: ['Essays', 'Code Assignments', 'Quizzes', 'File Uploads'],
            datasets: [{
                data: [35, 25, 30, 10],
                backgroundColor: [
                    '#4e73df',
                    '#1cc88a',
                    '#36b9cc',
                    '#f6c23e'
                ],
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                }
            }
        }
    });

    // AI Grading Accuracy Chart
    const accuracyCtx = document.getElementById('accuracyChart').getContext('2d');
    const accuracyChart = new Chart(accuracyCtx, {
        type: 'bar',
        data: {
            labels: ['Essays', 'Code Assignments', 'Quizzes', 'Overall'],
            datasets: [{
                label: 'AI Grading Accuracy (%)',
                data: [92, 95, 98, 94],
                backgroundColor: [
                    'rgba(78, 115, 223, 0.7)',
                    'rgba(28, 200, 138, 0.7)',
                    'rgba(54, 185, 204, 0.7)',
                    'rgba(246, 194, 62, 0.7)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Accuracy (%)'
                    }
                }
            }
        }
    });
});