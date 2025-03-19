document.addEventListener('DOMContentLoaded', function () {
    const industry = localStorage.getItem('industry');
    // console.log(industry)
    const calculateButton = document.getElementById('calculate-button');
    const resultsContainer = document.getElementById('results-container');
    const sheetTabs = document.getElementById('sheet-tabs');
    const dataInputSection = document.getElementById('data-input-section');

    let currentData = null;
    let charts = {};

    calculateButton.addEventListener('click', async function () {
        const file = document.getElementById('spreadsheet-upload').files[0];
        const spinner = document.getElementById('loading-spinner');
        if (!file) {
            alert('Please select a file');
            return;
        }

        spinner.classList.remove('hidden');
        calculateButton.disabled = true;
        calculateButton.classList.add('opacity-75');
        dataInputSection.classList.add('hidden');
        fetchData();

        const reader = new FileReader();
        reader.onload = async function (e) {
            const data = e.target.result;
            const workbook = XLSX.read(data, { type: 'binary' });

            const firstSheet = workbook.SheetNames[0];
            processSheet(workbook.Sheets[firstSheet]);
        };
        reader.readAsBinaryString(file);
    });

  // NAVIGATION CODE
  const navLinks = document.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('.section');

  navLinks.forEach(link => {
      link.addEventListener('click', function (e) {
          e.preventDefault();

          // Deactivate all links and hide all sections
          navLinks.forEach(l => l.classList.remove('active'));
          sections.forEach(s => s.classList.add('hidden'));

          // Activate the clicked link and show the corresponding section
          this.classList.add('active');
          const targetId = this.getAttribute('href').substring(1); // Remove the '#'
          document.getElementById(targetId).classList.remove('hidden');
      });
  });

function updateMarketAnalysis(data) {
    if (!data || !data.market_analysis) {
        console.warn("No market analysis data available.");
        return;
    }

    const marketData = data.market_analysis;
    document.getElementById('market-size-display').textContent = `Market Size: ${marketData.market_size || 'N/A'}`;
    document.getElementById('market-growth-rate-display').textContent = `Growth Rate: ${marketData.market_growth_rate || 'N/A'}`;

    if (data.external_market_data) {
        const externalData = data.external_market_data;
        document.getElementById('industry-growth-rate').textContent = `Industry Growth: ${externalData.industry_growth_rate || 'N/A'}`;
    }

    updateMarketSizeChart(marketData);
    updateMarketGrowthChart(marketData);

    const trendsList = document.getElementById('market-trends-list');
    trendsList.innerHTML = ''; // Clear existing list
    if (marketData.market_trends && marketData.market_trends.length > 0) {
        for (let i = 0; i < marketData.market_trends.length; i++) {
            const trend = marketData.market_trends[i];
            const listItem = document.createElement('li');
            listItem.textContent = trend.trend,trend.impact_on_product,trend.opportunity_or_threat;
            trendsList.appendChild(listItem); 
        }
    }      
}

function updateMarketSizeChart(marketData) {
    const ctx = document.getElementById('market-size-chart').getContext('2d');
    if (charts.marketSizeChart) charts.marketSizeChart.destroy();

    const labels = marketData.market_segments ? Object.keys(marketData.market_segments) : [];
    const dataPoints = marketData.market_segments ? Object.values(marketData.market_segments) : [];

    charts.marketSizeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Market Size by Segment',
                data: dataPoints,
                backgroundColor: '#2563eb' // Primary color
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function updateMarketGrowthChart(marketData) {
    const ctx = document.getElementById('market-growth-chart').getContext('2d');
    if (charts.marketGrowthChart) charts.marketGrowthChart.destroy();

    const labels = marketData.historical_growth ? Object.keys(marketData.historical_growth) : [];
    const dataPoints = marketData.historical_growth ? Object.values(marketData.historical_growth) : [];

    charts.marketGrowthChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Historical Market Growth',
                data: dataPoints,
                borderColor: '#1e40af', // Secondary color
                fill: false
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function updateCompetitorAnalysis(data) {
    if (!data || !data.market_analysis) {
        console.warn("No market analysis data available.");
        return;
    }

    // console.log(data.market_analysis)
    const competitorData = data.market_analysis.competitor_analysis
    // console.log("Competitor data:",competitorData);
    const tableBody = document.getElementById('competitor-table-body');
    tableBody.innerHTML = ''; // Clear existing table

    if (competitorData && competitorData.customer_segmentation && competitorData.customer_segmentation.length > 0) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">${competitorData.competitor_name || 'N/A'}</td>
            <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">${competitorData.market_share || 'N/A'}</td>
            <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">${competitorData.customer_segmentation[0].segment_name || 'N/A'}</td>
            <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">${competitorData.customer_segmentation[0].segment_needs[0] || 'N/A'}, ${competitorData.customer_segmentation[0].segment_needs[1] || 'N/A'}</td>
            <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">${competitorData.customer_segmentation[0].segment_growth_potential || 'N/A'}</td>
            <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">${competitorData.customer_segmentation[0].segment_profitability || 'N/A'}</td>
            `;
        tableBody.appendChild(row);
    } else {
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="6" class="px-5 py-5 border-b border-gray-200 bg-white text-sm">No competitor data available.</td>`;
        tableBody.appendChild(row);
    }

    if (data.external_competitor_data && Array.isArray(data.external_competitor_data)) {
        data.external_competitor_data.forEach(competitor => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">${competitor.name || 'N/A'}</td>
                <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">${competitor.market_share || 'N/A'}</td>
                <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">-</td>
                <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">-</td>
                <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">-</td>
            `; // Add competitor.pricing, competitor.sentiment_score, etc. as needed
            tableBody.appendChild(row);
        });
    }
}

function updateScenarioPlanningElements(data) {
//   console.log("Scenario planning element data:",data);
  //   document.getElementById('projected-revenue').textContent = data.scenario_planning.projected_revenue;
}
function updateScenarioPlanning(data) {
//   console.log("Update Scenario planning data:", data);
    const marketingSpendInput = document.getElementById('marketing-spend');
    const runScenarioButton = document.getElementById('run-scenario-button');
    const projectedRevenueDisplay = document.getElementById('projected-revenue');
    const scenarioChartCanvas = document.getElementById('scenario-chart').getContext('2d');
    let scenarioChart;

    runScenarioButton.addEventListener('click', () => {
        const marketingSpend = parseFloat(marketingSpendInput.value);
        // Make a request to your backend to get the projected revenue based on the marketing spend
        fetch('/api/scenario', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                marketing_spend: marketingSpend,
            }),
        })
        .then(response => response.json())
        .then(data => {
            projectedRevenueDisplay.textContent = `$${data.projected_revenue}`;
            // Update chart with the new scenario data
            updateChart(data.scenario_data);
            updateScenarioPlanningElements(data);
        })
        .catch(error => {
            console.error('Error:', error);
            projectedRevenueDisplay.textContent = 'Error calculating revenue.';
        });
    });

    function updateChart(scenarioData) {
        if (scenarioChart) {
            scenarioChart.destroy();
        }

        scenarioChart = new Chart(scenarioChartCanvas, {
            type: 'line',
            data: {
                labels: scenarioData.labels,
                datasets: [{
                    label: 'Projected Revenue',
                    data: scenarioData.data,
                    borderColor: '#3b82f6',
                    fill: false
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                    },
                },
            },
        });
    }
}

function updateRecommendations(data) {
  const recommendationsContainer = document.getElementById('recommendations-list');
  recommendationsContainer.innerHTML = '';

  const allRecommendations = [];

  if (data.cost_profit_analysis && data.cost_profit_analysis.recommendations) {
      allRecommendations.push({
          area: "Cost Profit",
          recommendations: [data.cost_profit_analysis.recommendations]
      });
  }

  if (data.revenue_break_even_analysis && data.revenue_break_even_analysis.recommendations) {
       allRecommendations.push({
          area: "Revenue Break Even",
          recommendations: [data.revenue_break_even_analysis.recommendations]
      });
  }

  if (data.external_market_insights && data.external_market_insights.recommendations) {
    allRecommendations.push({
       area: "External Market",
       recommendations: [data.external_market_insights.recommendations]
   });
}

  if (allRecommendations.length === 0) {
      recommendationsContainer.innerHTML = `<div class="p-4 bg-gray-50 rounded-lg">No recommendations available.</div>`;
      return;
  }

  allRecommendations.forEach(areaRecommendation => {
    console.log(areaRecommendation);
    areaRecommendation.recommendations[0].forEach(recommendation => {
        const recDiv = document.createElement('div');
        recDiv.className = 'p-4 bg-blue-50 rounded-lg';
        recDiv.innerHTML = `
            <h4 class="font-semibold text-blue-800">${recommendation.area || 'N/A'}</h4>
            <p class="text-gray-700">${recommendation.advice || 'N/A'}</p>
            <p class="text-sm text-blue-600 mt-2">Impact: ${recommendation.impact || 'N/A'}</p>
            ${recommendation.priority ? `<p class="text-xs text-gray-500">Priority: ${recommendation.priority} | Feasibility: ${recommendation.feasibility || 'N/A'}</p>` : ''}
        `;
        recommendationsContainer.appendChild(recDiv);
      });
  });
}

function updateKeyFindings(findings) {
    const keyFindingsList = document.getElementById('key-findings-list');
    keyFindingsList.innerHTML = ''; // Clear existing list

    if (findings && findings.length > 0) {
        findings.forEach(finding => {
            const listItem = document.createElement('li');
            listItem.textContent = finding.finding;
            keyFindingsList.appendChild(listItem);
        });
    } else {
        const listItem = document.createElement('li');
        listItem.textContent = "No key findings available.";
        keyFindingsList.appendChild(listItem);
    }
}

function updateCostChart(data) {
    const ctx = document.getElementById('costChart').getContext('2d');
    if (charts.costChart) charts.costChart.destroy();

    let fixedCosts = 0;
    let variableCosts = 0;

    if (data.cost_profit_analysis && data.cost_profit_analysis.costs) {
        if (data.cost_profit_analysis.costs.fixed_costs) {
            fixedCosts = data.cost_profit_analysis.costs.fixed_costs.total_fixed_costs || 0;
        }
        if (data.cost_profit_analysis.costs.variable_costs) {
            variableCosts = data.cost_profit_analysis.costs.variable_costs.total_variable_costs || 0;
        }
    }

    charts.costChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Fixed Costs', 'Variable Costs'],
            datasets: [{
                data: [fixedCosts, variableCosts],
                backgroundColor: ['#3b82f6', '#60a5fa']
            }]
        }
    });
}

function updateRevenueChart(data) {
    const ctx = document.getElementById('revenueChart').getContext('2d');
    if (charts.revenueChart) charts.revenueChart.destroy();

    let totalRevenue = 0;
    let totalCosts = 0;
    let totalProfit = 0;

    if (data.revenue_break_even_analysis) {
        totalRevenue = data.revenue_break_even_analysis.total_revenue || 0;
        totalProfit = data.revenue_break_even_analysis.total_profit || 0;
    }
    if (data.cost_profit_analysis) {
        totalCosts = (data.cost_profit_analysis.total_cost_per_unit || 0) * (data.revenue_break_even_analysis.total_units_sold || 0);
    }
    charts.revenueChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Revenue', 'Costs', 'Profit'],
            datasets: [{
                data: [totalRevenue, totalCosts, totalProfit],
                backgroundColor: ['#3b82f6', '#ef4444', '#10b981']
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

  async function processSheet(sheetData) {
      const jsonData = XLSX.utils.sheet_to_json(sheetData);

      try {
          const response = await fetch('/chat', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({ message: jsonData })
          });

          const result = await response.json();
          if (result && result.message) {
              currentData = result.message;
              resultsContainer.classList.remove('hidden');
              updateDashboard(result.message);
          } else {
              alert('Failed to retrieve data or invalid data format.');
          }

          spinner.classList.add('hidden');
          calculateButton.disabled = false;
          calculateButton.classList.remove('opacity-75');
      } catch (error) {
          console.error('Error:', error);
          // alert('An error occurred while processing the data');
      }
  }

    function updateDashboard(data) {
        // Ensure data exists before proceeding
        if (!data) {
            console.error('No data received in updateDashboard');
            return;
        }

        // console.log("Data received for updateDashboard:", data);

        // Update each section of the dashboard
        updateProductInformation(data.product_information);
        updateMarketAnalysis(data); // Ensure this handles undefined gracefully
        updateCompetitorAnalysis(data);
        updateScenarioPlanning(data); // Ensure this handles undefined gracefully
        updateRecommendations(data);
        updateRiskAssessment(data.risk_assessment);
        updateOperationalEfficiency(data.operational_efficiency);
        updateProductDevelopment(data.product_development);
        updateSalesPerformance(data.sales_performance);
        updateCostProfitAnalysis(data.cost_profit_analysis);
        

        function updateProductInformation(productInfo) {
            const info = data.product_information

            document.getElementById('product-id').textContent = info.product_id || '-';
            document.getElementById('product-name').textContent = info.product_name || '-';
            document.getElementById('product-category').textContent = info.product_category || '-';
            document.getElementById('launch-date').textContent = info.launch_date || '-';
            document.getElementById('target-market').textContent = info.target_market || '-';
            document.getElementById('lifecycle-stage').textContent = info.product_lifecycle_stage || '-';

            const swotDiv = document.getElementById('swot-analysis-div');


           const ulElement = document.createElement('ul')
           ulElement.classList.add('list-disc', 'pl-5', 'text-gray-600');
           ulElement.innerHTML = `
           <li><strong>Strengths:</strong>${info.swot_analysis.strengths}</li>
           <li><strong>Weaknesses:</strong>${info.swot_analysis.weaknesses}</li>
           <li><strong>Opportunities:</strong>${info.swot_analysis.opportunities}</li>
           <li><strong>Threats:</strong>${info.swot_analysis.threats}</li>
           `;

           swotDiv.appendChild(ulElement)
            
        }
        function updateRevenueBreakEvenAnalysis(revenueBreakEvenAnalysis) {
            if (!revenueBreakEvenAnalysis) return;

            document.getElementById('break-even-point-revenue').textContent = revenueBreakEvenAnalysis.break_even_point_revenue || '-';
            document.getElementById('break-even-point-units').textContent = revenueBreakEvenAnalysis.break_even_point_units || '-';
            document.getElementById('profit-margin').textContent = revenueBreakEvenAnalysis.profit_margin || '-';
            document.getElementById('total-profit').textContent = revenueBreakEvenAnalysis.total_profit || '-';
            document.getElementById('total-revenue').textContent = revenueBreakEvenAnalysis.total_revenue || '-';
            document.getElementById('total-units-sold').textContent = revenueBreakEvenAnalysis.total_units_sold || '-';
        }
        function updateMarketingPerformance(marketingPerformance) {
            if (!marketingPerformance) return;

            document.getElementById('marketing-roi').textContent = marketingPerformance.marketing_roi || '-';
        }

        function updateInterconnectedness(interconnectedness) {
            if (!interconnectedness) return;

            document.getElementById('notes').textContent = interconnectedness.notes || '-';
            // Handle dependency mapping and scenario planning divs similarly
        }

        function updateCustomerAnalysis(customerAnalysis) {
            if (!customerAnalysis) return;

            document.getElementById('churn-rate').textContent = customerAnalysis.churn_rate || '-';
            document.getElementById('customer-acquisition-cost').textContent = customerAnalysis.customer_acquisition_cost || '-';
            document.getElementById('customer-lifetime-value').textContent = customerAnalysis.customer_lifetime_value || '-';
            document.getElementById('customer-retention-rate').textContent = customerAnalysis.customer_retention_rate || '-';
        }
        function updateCostProfitAnalysis(costProfitAnalysis) {
            if (!costProfitAnalysis) return;

            document.getElementById('contribution-margin').textContent = costProfitAnalysis.contribution_margin || '-';
            document.getElementById('contribution-margin-ratio').textContent = costProfitAnalysis.contributino_margin_ratio || '-';
            document.getElementById('profit-per-unit').textContent = costProfitAnalysis.profit_per_unit || '-';
            document.getElementById('total-cost-per-unit').textContent = costProfitAnalysis.total_cost_per_unit || '-';
            document.getElementById('varibale-cost-per-unit').textContent = costProfitAnalysis.varibale_cost_per_unit || '-';
        }
        function updateSalesPerformance(salesPerformance) {
            if (!salesPerformance) return;

            document.getElementById('average-order-value').textContent = salesPerformance.average_order_value || '-';
            document.getElementById('sales-conversion-rate').textContent = salesPerformance.sales_conversion_rate || '-';
            document.getElementById('sales-cycle-length').textContent = salesPerformance.sales_cycle_length || '-';
            document.getElementById('sales-growth-rate').textContent = salesPerformance.sales_growth_rate || '-';
            document.getElementById('total-sales-revenue').textContent = salesPerformance.total_sales_revenue || '-';
        }

        function updateProductDevelopment(productDevelopment) {
            if (!productDevelopment) return;

            document.getElementById('development-cost').textContent = productDevelopment.development_cost || '-';
            document.getElementById('innovation-rate').textContent = productDevelopment.innovation_rate || '-';
            document.getElementById('new-feature-released').textContent = productDevelopment.new_feature_released || '-';
            document.getElementById('time-to-market').textContent = productDevelopment.time_to_market || '-';
        }

        function updateOperationalEfficiency(operationalEfficiency) {

            document.getElementById('defect-rate').textContent = data.operational_efficiency.defect_rate || '-';
            document.getElementById('inventory-turnover-rate').textContent = data.operational_efficiency.inventory_turnover_rate || '-';
            document.getElementById('order-fulfillment-rate').textContent = data.operational_efficiency.order_fulfillment_time || '-';
            document.getElementById('product-capacity-utilization').textContent = data.operational_efficiency.production_capacity_utilization || '-';
            document.getElementById('return-rate').textContent = data.operational_efficiency.return_rate || '-';
            document.getElementById('supply-chain-costs').textContent = data.operational_efficiency.supply_chain_costs || '-';
        }

        function updateRiskAssessment(riskAssessment) {
            // if (!riskAssessment) return;
            const riskAssesment = data.risk_assessment;
            // console.log(riskAssesment)
            for(let i = 0; i<riskAssesment.identified_risks.length;i++){
                // console.log(riskAssesment.identified_risks[i].risk_name);
                let risk = riskAssesment.identified_risks[i];
                let tableHTML = `
                <tr>
                    <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">${risk.risk_name || 'N/A'}</td>
                    <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">${risk.impact || 'N/A'}</td>
                    <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">${risk.probability || 'N/A'}</td>
                    <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">${risk.severity || 'N/A'}</td>
                    <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">${risk.mitigation_strategy || 'N/A'}</td>
                </tr>
                 `
                // console.log(tableHTML);
                document.getElementById('risk-table-body').innerHTML += tableHTML;    
            }

            // Ensure identified_risks is an array before iterating
            // if (Array.isArray(riskAssessment.identified_risks)) {
            //     const identifiedRisksDiv = document.getElementById('identified-risks');
            //     identifiedRisksDiv.innerHTML = ''; // Clear existing content

            //     riskAssessment.identified_risks.forEach(risk => {
            //         const riskDiv = document.createElement('div');
            //         riskDiv.innerHTML = `
            //             <p><strong>Risk Name:</strong> ${risk.risk_name || 'N/A'}</p>
            //             <p><strong>Description:</strong> ${risk.description || 'N/A'}</p>
            //             <p><strong>Mitigation Strategy:</strong> ${risk.mitigation_strategy || 'N/A'}</p>
            //         `;
            //         identifiedRisksDiv.appendChild(riskDiv);
            //     });
            // } else {
            //     document.getElementById('identified-risks').innerHTML = '<p>No identified risks available.</p>';
            // }

            // document.getElementById('overall-effectiveness').textContent = riskAssessment.overall_effectiveness || '-';
            // if(data.external_risk_data && Array.isArray(data.external_risk_data)){
            //     data.external_risk_data.forEach(risk=>{
            //         const riskDiv = document.createElement('div');
            //         riskDiv.innerHTML = `
            //             <p><strong>External Risk:</strong> ${risk.risk_name || 'N/A'}</p>
            //             <p><strong>Source:</strong> ${risk.source || 'N/A'}</p>
            //             <p><strong>Severity:</strong> ${risk.severity || 'N/A'}</p>
            //             <p><strong>Impact:</strong> ${risk.potential_impact || 'N/A'}</p>
            //         `;
            //         identifiedRisksDiv.appendChild(riskDiv);
            //     })
            // }
            console.log(data)
            document.getElementById('average-order-value').textContent = data.sales_performance.average_order_value || '-';
            document.getElementById('sales-conversion-rate').textContent = data.sales_performance.sales_conversion_rate || '-';
            document.getElementById('sales-cycle-length').textContent = data.sales_performance.sales_cycle_length || '-';
            document.getElementById('sales-growth-rate').textContent = data.sales_performance.sales_growth_rate || '-';
            document.getElementById('churn-rate').textContent = data.customer_analysis.churn_rate || '-';  
            document.getElementById('customer-acquisition-cost').textContent = data.customer_analysis.customer_acquisition_cost || '-';
            document.getElementById('overall-effectiveness').textContent = data.risk_assessment.risk_mitigation_effectiveness.overall_effectiveness || '-';
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
            // Navigation functionality
            const navLinks = document.querySelectorAll('.nav-link');
            const sections = document.querySelectorAll('.section');
            
            navLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    // Remove active class from all links
                    navLinks.forEach(l => l.classList.remove('active'));
                    
                    // Add active class to clicked link
                    this.classList.add('active');
                    
                    // Hide all sections
                    sections.forEach(section => {
                        section.classList.add('hidden');
                    });
                    
                    // Show the target section
                    const targetId = this.getAttribute('href');
                    const targetSection = document.querySelector(targetId);
                    if (targetSection) {
                        targetSection.classList.remove('hidden');
                    }
                });
            });
            
            // File upload visual feedback
            const fileUpload = document.querySelector('.file-upload');
            const fileInput = document.getElementById('spreadsheet-upload');
            
            fileInput.addEventListener('change', function() {
                if (this.files.length > 0) {
                    fileUpload.style.borderColor = 'var(--success-color)';
                    const fileName = document.createElement('p');
                    fileName.textContent = `Selected: ${this.files[0].name}`;
                    fileName.style.marginTop = '0.5rem';
                    fileName.style.color = 'var(--success-color)';
                    
                    // Remove any previous file name
                    const prevFileName = fileUpload.querySelector('p:last-child');
                    if (prevFileName && prevFileName !== fileUpload.querySelector('p:first-of-type')) {
                        prevFileName.remove();
                    }
                    
                    fileUpload.appendChild(fileName);
                }
            });
            
            // Generate insights button
            const loadingSpinner = document.getElementById('loading-spinner');
            
            calculateButton.addEventListener('click', function() {
                // Show loading spinner
                loadingSpinner.classList.remove('hidden');
                
                // Simulate loading (replace with actual data processing)
                setTimeout(() => {
                    loadingSpinner.classList.add('hidden');
                    
                    // Show all sections (in a real app, you'd populate with actual data)
                    document.querySelectorAll('.section').forEach(section => {
                        section.classList.remove('hidden');
                    });
                    
                    
                    // Initialize charts (if Chart.js is loaded)
                    if (typeof Chart !== 'undefined') {
                        // Example chart initialization
                        const costCtx = document.getElementById('costChart');
                        if (costCtx) {
                            new Chart(costCtx, {
                                type: 'pie',
                                data: {
                                    labels: ['Materials', 'Labor', 'Overhead', 'Marketing'],
                                    datasets: [{
                                        data: [30, 25, 20, 25],
                                        backgroundColor: [
                                            '#3a86ff',
                                            '#ff006e',
                                            '#fb5607',
                                            '#8338ec'
                                        ]
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    plugins: {
                                        legend: {
                                            position: 'bottom',
                                            labels: {
                                                color: 'white'
                                            }
                                        }
                                    }
                                }
                            });
                        }
                        
                        const revenueCtx = document.getElementById('revenueChart');
                        if (revenueCtx) {
                            new Chart(revenueCtx, {
                                type: 'line',
                                data: {
                                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                                    datasets: [
                                        {
                                            label: 'Revenue',
                                            data: [50000, 55000, 60000, 58000, 65000, 70000],
                                            borderColor: '#3a86ff',
                                            backgroundColor: 'rgba(58, 134, 255, 0.1)',
                                            tension: 0.3
                                        },
                                        {
                                            label: 'Costs',
                                            data: [40000, 42000, 45000, 44000, 48000, 50000],
                                            borderColor: '#ff006e',
                                            backgroundColor: 'rgba(255, 0, 110, 0.1)',
                                            tension: 0.3
                                        },
                                        {
                                            label: 'Profit',
                                            data: [10000, 13000, 15000, 14000, 17000, 20000],
                                            borderColor: '#4caf50',
                                            backgroundColor: 'rgba(76, 175, 80, 0.1)',
                                            tension: 0.3
                                        }
                                    ]
                                },
                                options: {
                                    responsive: true,
                                    plugins: {
                                        legend: {
                                            position: 'bottom',
                                            labels: {
                                                color: 'white'
                                            }
                                        }
                                    },
                                    scales: {
                                        x: {
                                            grid: {
                                                color: 'rgba(255, 255, 255, 0.1)'
                                            },
                                            ticks: {
                                                color: 'white'
                                            }
                                        },
                                        y: {
                                            grid: {
                                                color: 'rgba(255, 255, 255, 0.1)'
                                            },
                                            ticks: {
                                                color: 'white'
                                            }
                                        }
                                    }
                                }
                            });
                        }
                    }
                    
                }, 2000);
            });
            
            // Scenario planning
            const runScenarioButton = document.getElementById('run-scenario-button');
            if (runScenarioButton) {
                runScenarioButton.addEventListener('click', function() {
                    const marketingSpend = document.getElementById('marketing-spend').value;
                    document.getElementById('projected-revenue').textContent = `$${(marketingSpend * 2.5).toLocaleString()}`;
                    
                    // Update scenario chart if Chart.js is loaded
                    if (typeof Chart !== 'undefined') {
                        const scenarioCtx = document.getElementById('scenario-chart');
                        if (scenarioCtx) {
                            new Chart(scenarioCtx, {
                                type: 'bar',
                                data: {
                                    labels: ['Current', 'Projected'],
                                    datasets: [{
                                        label: 'Revenue',
                                        data: [100000, 100000 + (marketingSpend * 2.5)],
                                        backgroundColor: [
                                            'rgba(58, 134, 255, 0.7)',
                                            'rgba(76, 175, 80, 0.7)'
                                        ],
                                        borderColor: [
                                            '#3a86ff',
                                            '#4caf50'
                                        ],
                                        borderWidth: 1
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    plugins: {
                                        legend: {
                                            display: false
                                        }
                                    },
                                    scales: {
                                        x: {
                                            grid: {
                                                color: 'rgba(255, 255, 255, 0.1)'
                                            },
                                            ticks: {
                                                color: 'white'
                                            }
                                        },
                                        y: {
                                            grid: {
                                                color: 'rgba(255, 255, 255, 0.1)'
                                            },
                                            ticks: {
                                                color: 'white',
                                                callback: function(value) {
                                                    return '$' + value.toLocaleString();
                                                }
                                            }
                                        }
                                    }
                                }
                            });
                        }
                    }
                });
            }
        });

        document.addEventListener('DOMContentLoaded', function() {
            // Make results container visible initially for development
            document.getElementById('results-container').classList.remove('hidden');
            
            // Navigation functionality
            const navLinks = document.querySelectorAll('.nav-link');
            const sections = document.querySelectorAll('.section');
            
            navLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    // Remove active class from all links
                    navLinks.forEach(l => l.classList.remove('active'));
                    
                    // Add active class to clicked link
                    this.classList.add('active');
                    
                    // Hide all sections
                    sections.forEach(section => {
                        section.classList.add('hidden');
                    });
                    
                    // Show the target section
                    const targetId = this.getAttribute('href');
                    const targetSection = document.querySelector(targetId);
                    if (targetSection) {
                        targetSection.classList.remove('hidden');
                    }
                });
            });
            
            // Generate insights button
            const loadingSpinner = document.getElementById('loading-spinner');
            const resultsContainer = document.getElementById('results-container');
            
            calculateButton.addEventListener('click', function() {
                // Show loading spinner
                loadingSpinner.classList.remove('hidden');
                
                // Simulate loading (this would be replaced by your actual data processing)
                setTimeout(() => {
                    loadingSpinner.classList.add('hidden');
                    
                    // Show results container
                    document.getElementById('results-container').classList.remove('hidden');

                    
                    // Initialize charts if Chart.js is loaded
                    if (typeof Chart !== 'undefined') {
                        // Example chart initialization for cost structure
                        const costCtx = document.getElementById('costChart');
                        if (costCtx) {
                            new Chart(costCtx, {
                                type: 'pie',
                                data: {
                                    labels: ['Materials', 'Labor', 'Overhead', 'Marketing'],
                                    datasets: [{
                                        data: [30, 25, 20, 25],
                                        backgroundColor: [
                                            '#3a86ff',
                                            '#ff006e',
                                            '#fb5607',
                                            '#8338ec'
                                        ]
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    plugins: {
                                        legend: {
                                            position: 'bottom',
                                            labels: {
                                                color: 'white'
                                            }
                                        }
                                    }
                                }
                            });
                        }
                        
                        // Example chart initialization for revenue
                        const revenueCtx = document.getElementById('revenueChart');
                        if (revenueCtx) {
                            new Chart(revenueCtx, {
                                type: 'line',
                                data: {
                                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                                    datasets: [
                                        {
                                            label: 'Revenue',
                                            data: [50000, 55000, 60000, 58000, 65000, 70000],
                                            borderColor: '#3a86ff',
                                            backgroundColor: 'rgba(58, 134, 255, 0.1)',
                                            tension: 0.3
                                        },
                                        {
                                            label: 'Costs',
                                            data: [40000, 42000, 45000, 44000, 48000, 50000],
                                            borderColor: '#ff006e',
                                            backgroundColor: 'rgba(255, 0, 110, 0.1)',
                                            tension: 0.3
                                        },
                                        {
                                            label: 'Profit',
                                            data: [10000, 13000, 15000, 14000, 17000, 20000],
                                            borderColor: '#4caf50',
                                            backgroundColor: 'rgba(76, 175, 80, 0.1)',
                                            tension: 0.3
                                        }
                                    ]
                                },
                                options: {
                                    responsive: true,
                                    plugins: {
                                        legend: {
                                            position: 'bottom',
                                            labels: {
                                                color: 'white'
                                            }
                                        }
                                    },
                                    scales: {
                                        x: {
                                            grid: {
                                                color: 'rgba(255, 255, 255, 0.1)'
                                            },
                                            ticks: {
                                                color: 'white'
                                            }
                                        },
                                        y: {
                                            grid: {
                                                color: 'rgba(255, 255, 255, 0.1)'
                                            },
                                            ticks: {
                                                color: 'white',
                                                callback: function(value) {
                                                    return '$' + value.toLocaleString();
                                                }
                                            }
                                        }
                                    }
                                }
                            });
                        }
                    }
                }, 2000);
            });
            
            // Scenario planning
            const runScenarioButton = document.getElementById('run-scenario-button');
            if (runScenarioButton) {
                runScenarioButton.addEventListener('click', function() {
                    const marketingSpend = document.getElementById('marketing-spend').value;
                    document.getElementById('projected-revenue').textContent = `$${(marketingSpend * 2.5).toLocaleString()}`;
                    
                    // Update scenario chart if Chart.js is loaded
                    if (typeof Chart !== 'undefined') {
                        const scenarioCtx = document.getElementById('scenario-chart');
                        if (scenarioCtx) {
                            new Chart(scenarioCtx, {
                                type: 'bar',
                                data: {
                                    labels: ['Current', 'Projected'],
                                    datasets: [{
                                        label: 'Revenue',
                                        data: [100000, 100000 + (marketingSpend * 2.5)],
                                        backgroundColor: [
                                            'rgba(58, 134, 255, 0.7)',
                                            'rgba(76, 175, 80, 0.7)'
                                        ],
                                        borderColor: [
                                            '#3a86ff',
                                            '#4caf50'
                                        ],
                                        borderWidth: 1
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    plugins: {
                                        legend: {
                                            display: false
                                        }
                                    },
                                    scales: {
                                        x: {
                                            grid: {
                                                color: 'rgba(255, 255, 255, 0.1)'
                                            },
                                            ticks: {
                                                color: 'white'
                                            }
                                        },
                                        y: {
                                            grid: {
                                                color: 'rgba(255, 255, 255, 0.1)'
                                            },
                                            ticks: {
                                                color: 'white',
                                                callback: function(value) {
                                                    return '$' + value.toLocaleString();
                                                }
                                            }
                                        }
                                    }
                                }
                            });
                        }
                    }
                });
            }
        });

        // Example JavaScript (assuming you have these values)
    // document.addEventListener('DOMContentLoaded', function() {
    //     //Product Development
    //     document.getElementById('development-cost').textContent = '$120,000';
    //     document.getElementById('innovation-rate').textContent = '85%';
    //     document.getElementById('new-feature-released').textContent = '3';
    //     document.getElementById('time-to-market').textContent = '6 months';
    //     document.getElementById('current-stage').textContent = 'Development';
    //     document.getElementById('development-completion').textContent = '60';
    //     document.getElementById('team-size').textContent = '8';
    //     document.getElementById('sprint-velocity').textContent = '30 story points/sprint';

    //     // Set the width of the progress bar dynamically
    //     const completionPercentage = 60; // Example value
    //     document.getElementById('development-progress-fill').style.width = completionPercentage + '%';
    // });
    async function fetchData() {
        const industry = localStorage.getItem('industry');
        // console.log(industry)
        try {
          const message = industry
          const response = await fetch('/data', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
          });
      
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
      
          const data = await response.json();
      
          if (data.error) {
            console.error('Error from server:', data.error);
          } else if (data.message) {
            // console.log('Data from server:', data.message);
          } else {
            console.warn('Unexpected response structure:', data);
          }
      
        } catch (error) {
          console.error('Fetch error:', error);
        }
      }
      
    //   document.getElementById('run-button').addEventListener('click', fetchData); 
      
      document.getElementById('industry-button').addEventListener('click', function(event) {
        event.preventDefault(); 
        alert('industry selected')
        const selectedIndustry = document.getElementById('industry').value;
        // console.log(selectedIndustry)

        localStorage.setItem('industry', selectedIndustry);

        if (selectedIndustry === "") {
            alert("Please select an industry.");
            return;
        }
    });    
})
