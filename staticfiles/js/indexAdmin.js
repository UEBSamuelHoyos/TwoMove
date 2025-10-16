// Toggle Sidebar
const menuToggle = document.getElementById('menuToggle');
const sidebar = document.getElementById('sidebar');

menuToggle.addEventListener('click', () => {
    sidebar.classList.toggle('active');
});

// Close sidebar when clicking outside on mobile
document.addEventListener('click', (e) => {
    if (window.innerWidth <= 1024) {
        if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    }
});

// Recovered Chart
const recoveredCtx = document.getElementById('recoveredChart').getContext('2d');
new Chart(recoveredCtx, {
    type: 'bar',
    data: {
        labels: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        datasets: [
            {
                label: 'New',
                data: [120, 150, 180, 200, 140, 160, 190],
                backgroundColor: '#f43f5e',
                borderRadius: 8,
                barThickness: 20
            },
            {
                label: 'Recovered',
                data: [80, 130, 210, 240, 110, 140, 210],
                backgroundColor: '#10b981',
                borderRadius: 8,
                barThickness: 20
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                },
                border: {
                    display: false
                }
            },
            y: {
                display: false
            }
        }
    }
});

// Visitors Chart
const visitorsCtx = document.getElementById('visitorsChart').getContext('2d');
new Chart(visitorsCtx, {
    type: 'line',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [
            {
                label: 'Visitors',
                data: [30, 45, 35, 50, 65, 75, 70, 85, 80, 90, 75, 60],
                borderColor: '#7c3aed',
                backgroundColor: 'rgba(124, 58, 237, 0.1)',
                fill: true,
                tension: 0.4,
                borderWidth: 3,
                pointRadius: 0,
                pointHoverRadius: 6
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                },
                border: {
                    display: false
                }
            },
            y: {
                display: false
            }
        }
    }
});

// Nav Item Click Handler
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function(e) {
        // Remove active class from all items
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        // Add active class to clicked item
        this.classList.add('active');
    });
});