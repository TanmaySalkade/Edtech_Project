// Charts for the Learning Platform

// Create XP progress chart
function createXPChart(elementId, currentXP, nextLevelXP, previousLevelXP) {
  const ctx = document.getElementById(elementId).getContext('2d');
  
  const xpProgress = currentXP - previousLevelXP;
  const xpNeeded = nextLevelXP - previousLevelXP;
  const percentage = Math.min(100, (xpProgress / xpNeeded) * 100);
  
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [percentage, 100 - percentage],
        backgroundColor: ['#4e73df', '#e3e6f0'],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '75%',
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          enabled: false
        }
      },
      animation: {
        animateRotate: true,
        animateScale: true
      }
    }
  });
  
  // Add text in the center
  const centerText = document.getElementById('xp-chart-text');
  if (centerText) {
    centerText.textContent = `${Math.round(percentage)}%`;
  }
}

// Create streak chart
function createStreakChart(elementId, streakData) {
  const ctx = document.getElementById(elementId).getContext('2d');
  
  // Prepare data - last 30 days
  const labels = [];
  const data = [];
  
  // Generate dates for the past 30 days
  const today = new Date();
  for (let i = 29; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    
    // Check if we have activity for this date
    const dateString = date.toISOString().split('T')[0];
    data.push(streakData[dateString] ? 1 : 0);
  }
  
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Activity',
        data: data,
        backgroundColor: function(context) {
          const index = context.dataIndex;
          const value = context.dataset.data[index];
          return value ? '#4e73df' : '#e3e6f0';
        },
        borderRadius: 4,
        barThickness: 8
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const value = context.raw;
              return value ? 'Active' : 'Inactive';
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            display: false
          },
          ticks: {
            maxRotation: 90,
            minRotation: 45,
            autoSkip: true,
            maxTicksLimit: 10
          }
        },
        y: {
          beginAtZero: true,
          max: 1,
          ticks: {
            stepSize: 1,
            callback: function(value) {
              return value === 1 ? 'Active' : 'Inactive';
            }
          },
          grid: {
            drawBorder: false
          }
        }
      }
    }
  });
}

// Create course progress chart 
function createCourseProgressChart(elementId, courseData) {
  const ctx = document.getElementById(elementId).getContext('2d');
  
  const courseNames = courseData.map(course => course.name);
  const progressValues = courseData.map(course => course.progress);
  
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: courseNames,
      datasets: [{
        label: 'Progress (%)',
        data: progressValues,
        backgroundColor: 'rgba(78, 115, 223, 0.7)',
        borderColor: 'rgba(78, 115, 223, 1)',
        borderWidth: 1,
        borderRadius: 5
      }]
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
          }
        },
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            callback: function(value) {
              return value + '%';
            }
          }
        }
      }
    }
  });
}

// Create admin stats chart
function createAdminStatsChart(elementId, statsData) {
  const ctx = document.getElementById(elementId).getContext('2d');
  
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: statsData.dates,
      datasets: [{
        label: 'New Users',
        data: statsData.users,
        borderColor: 'rgba(78, 115, 223, 1)',
        backgroundColor: 'rgba(78, 115, 223, 0.1)',
        tension: 0.3,
        fill: true
      },
      {
        label: 'Lesson Completions',
        data: statsData.completions,
        borderColor: 'rgba(28, 200, 138, 1)',
        backgroundColor: 'rgba(28, 200, 138, 0.1)',
        tension: 0.3,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top'
        }
      },
      scales: {
        x: {
          grid: {
            display: false
          }
        },
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        }
      }
    }
  });
}
