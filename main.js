let priceChart = null;

document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const query = document.getElementById('searchInput').value.trim();
    if (!query) return;
    
    // UI Elements
    const searchBtn = document.getElementById('searchBtn');
    const btnText = searchBtn.querySelector('.btn-text');
    const spinner = document.getElementById('searchSpinner');
    const loadingState = document.getElementById('loadingState');
    const resultsContainer = document.getElementById('resultsContainer');
    const errorState = document.getElementById('errorState');
    const errorMessage = document.getElementById('errorMessage');
    
    // Set loading state
    btnText.style.display = 'none';
    spinner.style.display = 'block';
    searchBtn.disabled = true;
    
    resultsContainer.style.display = 'none';
    errorState.style.display = 'none';
    loadingState.style.display = 'block';
    
    try {
        // Fetch current search results
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch data');
        }
        
        // Update Dashboard UI
        updateDashboard(data.results, data.best_deal);
        
        // Fetch historical data for chart
        await updateChart(query);
        
        // Show results
        loadingState.style.display = 'none';
        resultsContainer.style.display = 'block';
        
    } catch (error) {
        loadingState.style.display = 'none';
        errorState.style.display = 'block';
        errorMessage.textContent = `Error: ${error.message}`;
    } finally {
        // Reset button state
        btnText.style.display = 'block';
        spinner.style.display = 'none';
        searchBtn.disabled = false;
    }
});

function updateDashboard(results, bestDeal) {
    // Update Best Deal Card
    if (bestDeal) {
        document.getElementById('bestDealName').textContent = bestDeal.product_name;
        document.getElementById('bestDealPrice').textContent = bestDeal.price.toLocaleString('en-IN');
        document.getElementById('bestDealStore').textContent = bestDeal.website;
    }
    
    // Update Table
    const tbody = document.getElementById('resultsBody');
    tbody.innerHTML = '';
    
    // Sort results by price
    const sortedResults = [...results].sort((a, b) => a.price - b.price);
    
    sortedResults.forEach(item => {
        const tr = document.createElement('tr');
        
        let storeClass = 'store-other';
        if (item.website.toLowerCase().includes('amazon')) storeClass = 'store-amazon';
        if (item.website.toLowerCase().includes('flipkart')) storeClass = 'store-flipkart';
        if (item.website.toLowerCase().includes('snapdeal')) storeClass = 'store-snapdeal';
        
        // Simple search link (since we don't have direct product URLs in mock data)
        const searchUrl = item.website.toLowerCase().includes('amazon') 
            ? `https://www.amazon.in/s?k=${encodeURIComponent(item.product_name)}`
            : item.website.toLowerCase().includes('flipkart') 
                ? `https://www.flipkart.com/search?q=${encodeURIComponent(item.product_name)}`
                : `https://www.snapdeal.com/search?keyword=${encodeURIComponent(item.product_name)}`;
            
        tr.innerHTML = `
            <td><span class="store-badge ${storeClass}">${item.website}</span></td>
            <td>${item.product_name}</td>
            <td class="price-cell">₹${item.price.toLocaleString('en-IN')}</td>
            <td>
                <div style="font-size: 0.85em; color: var(--text-muted);">
                    <span style="color: #fbbf24;">★</span> ${item.rating || 'N/A'} 
                    (${item.reviews || '0'})
                </div>
            </td>
            <td><a href="${searchUrl}" target="_blank" class="btn-visit">View Deal</a></td>
        `;
        
        tbody.appendChild(tr);
    });
}

async function updateChart(query) {
    try {
        const response = await fetch(`/data?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (!response.ok) throw new Error(data.error);
        
        const ctx = document.getElementById('priceChart').getContext('2d');
        
        if (priceChart) {
            priceChart.destroy();
        }
        
        // Ensure text is visible in light mode
        Chart.defaults.color = '#64748b';
        Chart.defaults.borderColor = 'rgba(0,0,0,0.1)';
        
        priceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: data.datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#0f172a',
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        titleColor: '#0f172a',
                        bodyColor: '#0f172a',
                        borderColor: 'rgba(0,0,0,0.1)',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        ticks: {
                            callback: function(value) {
                                return '₹' + value;
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
        
    } catch (error) {
        console.error("Error updating chart:", error);
    }
}
