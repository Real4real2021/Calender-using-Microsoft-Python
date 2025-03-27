const agricultreCalculate = document.getElementById(
    "calculate-agriculture-button"
  );

const resultsContainer = document.getElementById("results-container");
const dataInputSection = document.getElementById("data-input-section");
let currentAgriData = null;


async function processAgriSheet(sheetData) {
    const jsonData = XLSX.utils.sheet_to_json(sheetData);
    const csvData = XLSX.utils.sheet_to_csv(sheetData);
    try {
      const response = await fetch("/agricultureChat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: csvData }),
      });

      const result = await response.json();
      console.log(result.message);
      if (result && result.message) {
        currentAgriData = result.message;
        resultsContainer.classList.remove("hidden");
        updateAgriDashboard(currentAgriData);
      } else {
        alert("Failed to retrieve data or invalid data format.");
      }

      spinner.classList.add("hidden");
      calculateButton.disabled = false;
      calculateButton.classList.remove("opacity-75");
    } catch (error) {
      console.error("Error:", error);
      //   alert('An error occurred while processing the data');
    }
  }


  const totalRevenueGenerated = document.getElementById(
    "total-revenue-generated"
  );
  const productionEfficiency = document.getElementById(
    "production-efficiency"
  );
  const resourceAvailability = document.getElementById(
    "resource-availability"
  );
  const farmID = document.getElementById("farm-id");
  const farmName = document.getElementById("farm-name");
  const farmType = document.getElementById("farm-type");
  const estabDate = document.getElementById("establishment-date");
  const targetMarket = document.getElementById("target-market");
  const farmSize = document.getElementById("farm-size");
  const totalRevenue = document.getElementById("total-sales-revenue");
  const marketInvestment = document.getElementById("market-investment");
  const swotAnalysis = document.getElementById("swot-analysis");
  const swotAnlysisList = document.getElementById("swot-analysis-list");

  const cropYield = document.getElementById("crop-yield");
  const cropHealthIndex = document.getElementById("crop-health-index");
  const irrigationEfficiency = document.getElementById("irrigation-efficiency");
  const fertilizerUsage = document.getElementById("fertilizer-usage");
  const pestDiseaseIncidence = document.getElementById("pest-disease-incidence");
  const soilMoistureLevels = document.getElementById("soil-moisture-levels");

  const animalHealthStatus = document.getElementById("animal-health-status");
  const weightGain = document.getElementById("weight-gain");
  const feedConversionRatio = document.getElementById("feed-conversion-ratio");
  const mortalityRate = document.getElementById("mortality-rate");
  const reproductionRate = document.getElementById("reproduction-rate");
  const milkProduction = document.getElementById("milk-production");
  const eggProduction = document.getElementById("egg-production");
  const grazingLandUtilization = document.getElementById("grazing-land-utilization");
  const feedCosts = document.getElementById("feed-costs");
  const waterConsumption = document.getElementById("water-consumption");

  const waterUsage = document.getElementById("water-usage");
  const waterCost = document.getElementById("water-cost");
  const energyConsumption = document.getElementById("energy-consumption");
  const fuelConsumption = document.getElementById("fuel-consumption");
  const fertilizerInventory = document.getElementById("fertilizer-inventory");
  const feedInventory = document.getElementById("feed-inventory");
  const wasteManagement = document.getElementById("waste-management");
  const wasteDisposalCost = document.getElementById("waste-disposal-cost");
  const renewableEnergyUsage = document.getElementById("renewable-energy-generation");

  const grossRevenue = document.getElementById("gross-revenue");
  const operatingExpenses = document.getElementById("operating-expenses");
  const netProfit = document.getElementById("net-profit");
  const returnOnInvestment = document.getElementById("return-on-investment");
  const cashFlow = document.getElementById("cash-flow");
  const debtToEquityRatio = document.getElementById("debt-to-equity-ratio");
  const breakEvenPointUnits = document.getElementById("break-even-point");

  const weatherRIskindex = document.getElementById("weather-risk-index");
  const pestDiseaseRiskindex = document.getElementById("pest-disease-risk");
  const marketVolatilityRiskindex = document.getElementById("market-volatility-risk");
  const regulatoryRiskindex = document.getElementById("regulatory-risk");
  const supplyChainRiskindex = document.getElementById("supply-chain-risk");
  const biosecurityRiskindex = document.getElementById("biosecurity-risk");
  const riskTableBody = document.getElementById("risk-table-body");

  function farmOverview(data){
    totalRevenueGenerated.innerHTML = data.agricultural_analysis.financial_performance.revenue.total_revenue
    productionEfficiency.innerHTML = data.agricultural_analysis.resource_management.resource_efficiency_metrics.overall_rating
    resourceAvailability.innerHTML = data.agricultural_analysis.resource_management.total_resource_availability
    farmID.innerHTML= data.agricultural_analysis.product_information.farm_id;
    farmName.innerHTML= data.agricultural_analysis.product_information.farm_name
    farmType.innerHTML= data.agricultural_analysis.product_information.farm_category
    estabDate.innerHTML= data.agricultural_analysis.product_information.farm_establishment_date
    targetMarket.innerHTML= data.agricultural_analysis.product_information.target_market
    farmSize.innerHTML= data.agricultural_analysis.product_information.farm_size
    totalRevenue.innerHTML= data.agricultural_analysis.financial_performance.revenue.total_revenue
    // marketInvestment.innerHTML= data.product_information.
    // swotAnalysis.innerHTML= data.product_information.
    const swotData = data.agricultural_analysis.swot_analysis
  }

  function cropManagement(data){
    cropYield.innerHTML = data.agricultural_analysis.crop_management.yield_per_acre
    cropHealthIndex.innerHTML = data.agricultural_analysis.crop_management.crop_health_index
    irrigationEfficiency.innerHTML = data.agricultural_analysis.resource_management.water_usage.total_water_consumption
    fertilizerUsage.innerHTML = data.agricultural_analysis.resource_management.fertilizer_usage.total_fertilizer_consumption
    pestDiseaseIncidence.innerHTML = data.agricultural_analysis.crop_management.pest_incidence
    soilMoistureLevels.innerHTML = data.agricultural_analysis.crop_management.soil_health_assessment.moisture_level
  }

  function liveStockManagement(data){
    animalHealthStatus.innerHTML =  data.agricultural_analysis.livestock_management.animal_health_management.health_status
    weightGain.innerHTML =  data.agricultural_analysis.livestock_management.animal_health_management.weight_gain
    feedConversionRatio.innerHTML =  data.agricultural_analysis.livestock_management.production_metrics.feed_conversion_ration
    mortalityRate.innerHTML =  data.agricultural_analysis.livestock_management.production_metrics.mortality_rate
    reproductionRate.innerHTML =  data.agricultural_analysis.livestock_management.production_metrics.reproduction_rate
    milkProduction.innerHTML =  data.agricultural_analysis.livestock_management.production_metrics.mild_yield_per_cow
    // eggProduction.innerHTML =  data.agricultural_analysis.
    // grazingLandUtilization.innerHTML =  data.agricultural_analysis.
    // feedCosts.innerHTML =  data.agricultural_analysis.
    // waterConsumption.innerHTML =  data.agricultural_analysis.
  }

  function resourceManagement(data){
    waterUsage.innerHTML = data.agricultural_analysis.resource_management.water_usage.total_water_consumption
    // waterCost.innerHTML = data.agricultural_analysis
    energyConsumption.innerHTML = data.agricultural_analysis.resource_management.energy_consumption.electricity_consumption 
    fuelConsumption.innerHTML = data.agricultural_analysis.resource_management.energy_consumption.fuel_consumption
    fertilizerInventory.innerHTML = data.agricultural_analysis.resource_management.fertilizer_usage.fertilizer_inventory
    feedInventory.innerHTML = data.agricultural_analysis.resource_management.feed.fee_inventory
    wasteManagement.innerHTML = data.agricultural_analysis.resource_management.waste_management.crop_residue_management
    wasteDisposalCost.innerHTML = data.agricultural_analysis.resource_management.waste_management.disposal_costs
    renewableEnergyUsage.innerHTML = data.agricultural_analysis.resource_management.energy_consumption.renewable_energy_usage
  }

  function financialPerformance(data){
    grossRevenue.innerHTML = data.agricultural_analysis.financial_performance.revenue.total_revenue
    operatingExpenses.innerHTML = data.agricultural_analysis.financial_performance.operating_expenses.total_operating_expenses
    netProfit.innerHTML = data.agricultural_analysis.financial_performance.profit_margin
    returnOnInvestment.innerHTML = data.agricultural_analysis.financial_performance.return_on_investment
    cashFlow.innerHTML = data.agricultural_analysis.financial_performance.cash_flow_analysis.cash_flow_statement
    debtToEquityRatio.innerHTML = data.agricultural_analysis.financial_performance.cash_flow_analysis.debt_to_equity_ratio
    breakEvenPointUnits.innerHTML = data.agricultural_analysis.financial_performance.break_even_point_units
  }

  function riskManagement(data){
    weatherRIskindex.innerHTML = data.agricultural_analysis.risk_management.weather_risks
    pestDiseaseRiskindex.innerHTML = data.agricultural_analysis.risk_management.disease_risks.crop_disease_risk
    marketVolatilityRiskindex.innerHTML = data.agricultural_analysis.risk_management.market_risks.input_cost_fluctuations
    regulatoryRiskindex.innerHTML = data.agricultural_analysis.risk_management.regulatory_risks
    supplyChainRiskindex.innerHTML = data.agricultural_analysis.risk_management.supply_chain_risks
    // biosecurityRiskindex.innerHTML = data.agricultural_analysis
    // riskTableBody.innerHTML = data.agricultural_analysis
  }

 function updateAgriDashboard(data) {
      farmOverview(data);  
      cropManagement(data);
      liveStockManagement(data);
      resourceManagement(data);
      financialPerformance(data);
      riskManagement(data);

  }

  // NAVIGATION CODE
  const navLinks = document.querySelectorAll(".nav-link");
  const sections = document.querySelectorAll(".section");

  navLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault();

      // Deactivate all links and hide all sections
      navLinks.forEach((l) => l.classList.remove("active"));
      sections.forEach((s) => s.classList.add("hidden"));

      // Activate the clicked link and show the corresponding section
      this.classList.add("active");
      const targetId = this.getAttribute("href").substring(1); // Remove the '#'
      document.getElementById(targetId).classList.remove("hidden");
    });
  });

  navLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault();

      // Remove active class from all links
      navLinks.forEach((l) => l.classList.remove("active"));

      // Add active class to clicked link
      this.classList.add("active");

      // Hide all sections
      sections.forEach((section) => {
        section.classList.add("hidden");
      });

      // Show the target section
      const targetId = this.getAttribute("href");
      const targetSection = document.querySelector(targetId);
      if (targetSection) {
        targetSection.classList.remove("hidden");
      }
    });
})

    agricultreCalculate.addEventListener('click', async function () {
        const file = document.getElementById('spreadsheet-upload').files[0];
        const spinner = document.getElementById('loading-spinner');
        if (!file) {
            alert('Please select a file');
            return;
        }

        spinner.classList.remove('hidden');
        dataInputSection.classList.add('hidden');
        // fetchData();

        const reader = new FileReader();
        reader.onload = async function (e) {
            const data = e.target.result;
            const workbook = XLSX.read(data, { type: 'binary' });

            const firstSheet = workbook.SheetNames[0];
            processAgriSheet(workbook.Sheets[firstSheet]);
        };
        reader.readAsBinaryString(file);
    })
