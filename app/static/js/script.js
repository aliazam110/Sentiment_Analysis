document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('prediction-form');
    const resultsContainer = document.getElementById('results-container');
    const resultsPlaceholder = document.getElementById('results-placeholder');
    const loadingIndicator = document.getElementById('loading-indicator');
    const predictedSentimentEl = document.getElementById('predicted-sentiment');
    const confidenceList = document.getElementById('confidence-list');
    
    let sentimentChart = null;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const reviewText = document.getElementById('review-text').value.trim();
        if (!reviewText) return;
        
        // Show loading indicator
        resultsPlaceholder.classList.add('d-none');
        resultsContainer.classList.add('d-none');
        loadingIndicator.classList.remove('d-none');
        
        try {
            // Send request to backend
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'text': reviewText
                })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            // Update UI with results
            updateResults(data);
            
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during sentiment analysis. Please try again.');
            
            // Reset UI
            loadingIndicator.classList.add('d-none');
            resultsPlaceholder.classList.remove('d-none');
        }
    });
    
    function updateResults(data) {
        // Update predicted sentiment
        predictedSentimentEl.textContent = data.predicted_sentiment.charAt(0).toUpperCase() + 
                                          data.predicted_sentiment.slice(1);
        
        // Update confidence values
        confidenceList.innerHTML = '';
        
        // Sort sentiments by confidence (highest first)
        const sortedConfidences = Object.entries(data.confidences)
            .sort((a, b) => b[1] - a[1]);
        
        sortedConfidences.forEach(([sentiment, confidence]) => {
            const confidenceItem = document.createElement('div');
            confidenceItem.className = 'col-md-4 fade-in';
            
            const sentimentClass = sentiment.toLowerCase();
            const iconClass = sentiment === 'positive' ? 'fa-smile' : 
                             sentiment === 'neutral' ? 'fa-meh' : 'fa-frown';
            
            confidenceItem.innerHTML = `
                <div class="confidence-item">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="fw-bold">
                            <i class="fas ${iconClass} me-2 text-${sentimentClass}"></i>
                            ${sentiment.charAt(0).toUpperCase() + sentiment.slice(1)}
                        </span>
                        <span class="fw-bold">${confidence.toFixed(1)}%</span>
                    </div>
                    <div class="confidence-bar">
                        <div class="confidence-fill ${sentimentClass}-fill" style="width: 0%"></div>
                    </div>
                </div>
            `;
            
            confidenceList.appendChild(confidenceItem);
            
            // Animate confidence bar after a short delay
            setTimeout(() => {
                const fillElement = confidenceItem.querySelector(`.${sentimentClass}-fill`);
                fillElement.style.width = `${confidence}%`;
            }, 300);
        });
        
        // Create or update chart
        renderChart(data.chart_data);
        
        // Show results
        loadingIndicator.classList.add('d-none');
        resultsContainer.classList.remove('d-none');
    }
    
    function renderChart(chartData) {
        const ctx = document.getElementById('sentiment-chart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (sentimentChart) {
            sentimentChart.destroy();
        }
        
        // Sort data by confidence (highest first)
        const sortedData = [...chartData].sort((a, b) => b.confidence - a.confidence);
        
        // Create new chart
        sentimentChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: sortedData.map(item => 
                    item.sentiment.charAt(0).toUpperCase() + item.sentiment.slice(1)
                ),
                datasets: [{
                    label: 'Confidence %',
                    data: sortedData.map(item => item.confidence),
                    backgroundColor: [
                        'rgba(25, 135, 84, 0.7)',  // Positive
                        'rgba(255, 193, 7, 0.7)',   // Neutral
                        'rgba(220, 53, 69, 0.7)'    // Negative
                    ],
                    borderColor: [
                        'rgba(25, 135, 84, 1)',
                        'rgba(255, 193, 7, 1)',
                        'rgba(220, 53, 69, 1)'
                    ],
                    borderWidth: 2,
                    borderRadius: 8,
                    barThickness: 60
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 2000,
                    easing: 'easeOutQuart'
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.7)',
                        titleFont: {
                            size: 16,
                            weight: 'bold'
                        },
                        bodyFont: {
                            size: 14
                        },
                        padding: 12,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                return `Confidence: ${context.parsed.y.toFixed(1)}%`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            },
                            font: {
                                size: 12
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    }
                }
            }
        });
    }
});