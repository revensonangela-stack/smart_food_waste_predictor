// -----------------------------
// KPI DATA
// -----------------------------
fetch('/dashboard-data')
    .then(res => res.json())
    .then(data => {
        document.getElementById('totalUsed').innerText =
            data.total_used.toFixed(2);

        document.getElementById('totalWasted').innerText =
            data.total_wasted.toFixed(2);

        const avgWaste =
            data.total_used > 0
                ? (data.total_wasted / data.total_used) * 100
                : 0;

        document.getElementById('avgWaste').innerText =
            avgWaste.toFixed(1) + '%';
    });


// -----------------------------
// DAILY USAGE VS WASTE CHART
// -----------------------------
fetch('/daily-summary')
    .then(res => res.json())
    .then(data => {

        const labels = Object.keys(data);
        const used = labels.map(d => data[d].total_used);
        const wasted = labels.map(d => data[d].total_wasted);

        new Chart(document.getElementById('dailyWasteChart'), {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Used (kg)',
                        data: used,
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Wasted (kg)',
                        data: wasted,
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    });


// -----------------------------
// INGREDIENT WASTE % CHART
// -----------------------------
fetch('/ingredient-waste-report')
    .then(res => res.json())
    .then(data => {

        const ingredients = data.map(i => i.ingredient);
        const wastePercents = data.map(i => i.waste_percentage);

        new Chart(document.getElementById('ingredientWasteChart'), {
            type: 'bar',
            data: {
                labels: ingredients,
                datasets: [
                    {
                        label: 'Waste % per Ingredient',
                        data: wastePercents,
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Waste Percentage (%)'
                        }
                    }
                }
            }
        });
    });


// -----------------------------
// WEEKLY SMART RECOMMENDATIONS
// -----------------------------
fetch('/weekly-recommendations')
    .then(res => res.json())
    .then(data => {
        const container =
            document.getElementById('recommendationsContainer');

        container.innerHTML = '';

        data.recommendations.forEach(rec => {
            const div = document.createElement('div');
            div.className = 'recommendation-item';
            div.innerText = rec.message;
            container.appendChild(div);
        });
    });
