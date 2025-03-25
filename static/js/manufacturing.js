const manufacturingButton =  document.getElementById("manufacturing-button");
const dataInputSection = document.getElementById("data-input-section");
const resultsContainer = document.getElementById("results-container");
let manufacturingData = null;
manufacturingButton.addEventListener('click', async function () {
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
        processManufacturingSheet(workbook.Sheets[firstSheet]);
    };
    reader.readAsBinaryString(file);
})

async function processManufacturingSheet(sheetData) {
    const jsonData = XLSX.utils.sheet_to_json(sheetData);

    try {
      const response = await fetch("/manufacturingChat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: jsonData }),
      });

      const result = await response.json();
      console.log(result.message);
      if (result && result.message) {
        manufacturingData = result.message;
        resultsContainer.classList.remove("hidden");
        updateManufacturingDashboard(manufacturingData);
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

  // // Navigation functionality
  // const navLinks = document.querySelectorAll('.nav-link');
  // const sections = document.querySelectorAll('.section');

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

function updateManufacturingDashboard(data) {
    plantOverview(data);
    productionMonitoring(data);
    qualityControl(data);
    equipmentPerformance(data);
    inventoryManagement(data);
    maintenanceManagement(data);
    financialPerformance(data);
    supplyChain(data);
    sustainability(data);
}

// plantOverview
const productionOutput = document.getElementById("production-output");
const productQualityIndex = document.getElementById("product-quality-index"); 
const workInProgresss = document.getElementById("work-in-progress");
const productSkeleton = document.getElementById("product-sku");
const productDescription = document.getElementById("product-description");
const productLine = document.getElementById("product-line");
const productionStartDate = document.getElementById("production-start-date");
const intendedMarket = document.getElementById("intended-market");
const productMaturity = document.getElementById("product-maturity");
const totalRevenue = document.getElementById("total-revenue");
const salesMarketingSpend = document.getElementById("sales-marketing-spend");
const swotAnalysis = document.getElementById("swot-analysis-div");
// productionMonitoring
const overallEquipmentEffectivness = document.getElementById('overall-equipment-effectiveness')
const productYield = document.getElementById('product-yield')
const throughput = document.getElementById('throughput')
const manufacturingDowntime = document.getElementById('manufacturing-downtime')
const workInProgressProductionMonitoring = document.getElementById('manufacturing-work-in-progress')
const scheduleAdherence = document.getElementById('schedule-adherence')
// qualityControl
const defectRate = document.getElementById('defect-rate')
const firstPassYield = document.getElementById('first-pass-yield')
const scrapRate = document.getElementById('scrap-rate')
const reworkRate = document.getElementById('rework-rate')
const customerReturns = document.getElementById('customer-returns')
const costOfQuality = document.getElementById('cost-of-quality')
// equipmentPerformanceSection
const machineUtilization =  document.getElementById('machine-utilization')
const MTBF = document.getElementById('mean-time-between-failures')
const MTTR = document.getElementById('mean-time-to-repair')
const preventiveMaintenance = document.getElementById('preventive-maintenance-compliance')
const energyConsumption = document.getElementById('energy-consumption')
// inventoryManagement
const rawMaterialInventory = document.getElementById('raw-material-inventory')
const workInProgressInventory = document.getElementById('work-in-progress-inventory')
const finishedGoodsInventory = document.getElementById('finished-goods-inventory')
const inventoryTurnover = document.getElementById('inventory-turnover')
const carryingCosts = document.getElementById('carrying-costs')
const stockoutRate = document.getElementById('stockout-rate')
// maintenanceManagement
const preventitiveMaintenanceCompliance = document.getElementById('preventive-maintenance')
const maintenanceCosts = document.getElementById('maintenance-costs')
const downtimeDueToMaintenance = document.getElementById('downtime-due-to-maintenance')
const partsInventory = document.getElementById('parts-inventory')
// financialPerformance
const COGS = document.getElementById('cost-of-goods-sold')
const grossProfit = document.getElementById('gross-profit')
const operatingExpenses = document.getElementById('operating-expenses')
const netProfit = document.getElementById('net-profit')
const returnOnAssets = document.getElementById('return-on-assets')
const cashFLow = document.getElementById('cash-flow')
// supplyChain
const supplierLeadTime = document.getElementById('supplier-lead-time')
const onTimeDelivery = document.getElementById('on-time-delivery')
const supplierQuality = document.getElementById('supplier-quality')
const materialCosts = document.getElementById('material-costs')
const inventoryLevels = document.getElementById('inventory-levels')
// const supplierRelationship = document.getElementById('supplier-relationships')
// sustainability
const energyConsumptionManufacturing =  document.getElementById('energy-consumption-manufacturing')
const waterUsageManufacturing = document.getElementById('water-usage-manufacturing')
const wasteGenerationManufacturing =  document.getElementById('waste-generation-manufacturing')
const recyclingRate = document.getElementById('recycling-rate')
const emissions = document.getElementById('emissions')

function plantOverview(data){
    productionOutput.innerHTML = data.manufacturing_analysis.product_information.production_output
    productQualityIndex.innerHTML = data.manufacturing_analysis.product_information.product_quality_index
    workInProgresss.innerHTML = data.manufacturing_analysis.production_planning.inventory_levels.work_in_progress
    productSkeleton.innerHTML = data.manufacturing_analysis.product_information.product_sku
    productDescription.innerHTML = data.manufacturing_analysis.product_information.product_type
    productLine.innerHTML = data.manufacturing_analysis.product_information.factory_description
    productionStartDate.innerHTML = data.manufacturing_analysis.product_information.manufacturing_start_date
    intendedMarket.innerHTML = data.manufacturing_analysis.product_information.target_market
    productMaturity.innerHTML = data.manufacturing_analysis.product_information.manufacturing_cycle_stage
    totalRevenue.innerHTML = data.manufacturing_analysis.financial_performance.revenue.total_revenue
    salesMarketingSpend.innerHTML = data.manufacturing_analysis.financial_performance.marketing_spend
    swotAnalysis.innerHTML = data.manufacturing_analysis.swot_analysis
}

function productionMonitoring(data){
    overallEquipmentEffectivness.innerHTML = `${data.manufacturing_analysis.resource_management.equipment_maintenance.equipment_failure_rate}% || ${data.manufacturing_analysis.product_information.product_quality_index}%`
    // productYield.innerHTML = data.manufacturing_analysis.
    throughput.innerHTML = `${data.manufacturing_analysis.production_planning.throughput}units/hour`
    manufacturingDowntime.innerHTML = `${data.manufacturing_analysis.production_planning.total_downtime}hours`
    workInProgressProductionMonitoring.innerHTML = `${data.manufacturing_analysis.production_planning.inventory_levels.work_in_progress}units`
    scheduleAdherence.innerHTML = `${data.manufacturing_analysis.resource_management.equipment_maintenance.schedule_adherence}%`

}

function qualityControl(data){
    defectRate.innerHTML = `${data.manufacturing_analysis.quality_control.defect_rate}units/hour`
    firstPassYield.innerHTML = `${data.manufacturing_analysis.quality_control.first_pass_yield}`
    scrapRate.innerHTML = `${data.manufacturing_analysis.quality_control.scrap_rate}`
    reworkRate.innerHTML = `${data.manufacturing_analysis.quality_control.rework_rate}`
    customerReturns.innerHTML = `${data.manufacturing_analysis.quality_control.customer_returns}`
    costOfQuality.innerHTML = `${data.manufacturing_analysis.quality_control.cost_of_quality}`
}  

function equipmentPerformance(data){
    machineUtilization.innerHTML = `${data.manufacturing_analysis.production_planning.machine_utilization_rate}%`
    MTBF.innerHTML = `${data.manufacturing_analysis.resource_management.equipment_maintenance.equipment_failure_rate}%`
    MTTR.innerHTML = `${data.manufacturing_analysis.resource_management.equipment_maintenance.mean_time_to_repair}hours`
    preventiveMaintenance.innerHTML = `${data.manufacturing_analysis.resource_management.equipment_maintenance.maintenance_schedule}`
    energyConsumption.innerHTML = `${data.manufacturing_analysis.sustainability.sustainable_practices.energy_consmption}`
}

function inventoryManagement(data){
    rawMaterialInventory.innerHTML = `${data.manufacturing_analysis.production_planning.inventory_levels.raw_materials}units`
    workInProgressInventory.innerHTML = `${data.manufacturing_analysis.production_planning.inventory_levels.work_in_progress}units`
    finishedGoodsInventory.innerHTML = `${data.manufacturing_analysis.production_planning.inventory_levels.finished_goods}units`
    inventoryTurnover.innerHTML = `${data.manufacturing_analysis.production_planning.inventory_levels.turnover_rate}%`
    carryingCosts.innerHTML = `${data.manufacturing_analysis.supply_chain_management.logistics_and_transportation.carrying_costs}`
    stockoutRate.innerHTML = `${data.manufacturing_analysis.production_planning.inventory_levels.stockout_rate}%`
}

function maintenanceManagement(data){
    preventitiveMaintenanceCompliance.innerHTML = `${data.manufacturing_analysis.automation_and_technology.predictive_maintenance}`
    maintenanceCosts.innerHTML = `${data.manufacturing_analysis.resource_management.equipment_maintenance.maintenance_costs}`
    downtimeDueToMaintenance.innerHTML = `${data.manufacturing_analysis.resource_management.equipment_maintenance.downtime_due_to_maintenance}hours`
    partsInventory.innerHTML = `${data.manufacturing_analysis.production_planning.inventory_levels.parts_inventory}units`
}   

function financialPerformance(data){
    COGS.innerHTML = `${data.manufacturing_analysis.financial_performance.cost_of_goods_sold}`
    grossProfit.innerHTML = `${data.manufacturing_analysis.financial_performance.gross_profit}`
    operatingExpenses.innerHTML = `${data.manufacturing_analysis.financial_performance.operating_expenses.total_operating_expenses}`
    netProfit.innerHTML = `${data.manufacturing_analysis.financial_performance.net_profit}`
    returnOnAssets.innerHTML = `${data.manufacturing_analysis.financial_performance.return_on_assets}`
    cashFLow.innerHTML = `${data.manufacturing_analysis.financial_performance.cash_flow_analysis.cash_flow_statement}`
}

function supplyChain(data){
    supplierLeadTime.innerHTML = `${data.manufacturing_analysis.supply_chain_management.logistics_and_transportation.delivery_time}days`
    onTimeDelivery.innerHTML = `${data.manufacturing_analysis.supply_chain_management.supplier_performance.on_time_delivery_rate}%`
    supplierQuality.innerHTML = `${data.manufacturing_analysis.supply_chain_management.supplier_performance.quality_rating}/10`
    materialCosts.innerHTML = `${data.manufacturing_analysis.resource_management.raw_material_usage.material_costs}`
    inventoryLevels.innerHTML = `${data.manufacturing_analysis.production_planning.inventory_levels.raw_materials}units || ${data.manufacturing_analysis.production_planning.inventory_levels.work_in_progress}units || ${data.manufacturing_analysis.production_planning.inventory_levels.finished_goods}units || ${data.manufacturing_analysis.production_planning.inventory_levels.parts_inventory}units` 
}

function sustainability(data){
    energyConsumptionManufacturing.innerHTML = `${data.manufacturing_analysis.resource_management.energy_consumption.total_energy_consumption}kWh/year`
    waterUsageManufacturing.innerHTML = `${data.manufacturing_analysis.resource_management.total_water_consumption}cubic meters/year`
    wasteGenerationManufacturing.innerHTML = `${data.manufacturing_analysis.resource_management.waste_management.waste_generation}cubic tons/year`
    // recyclingRate.innerHTML = `${data.manufacturing_analysis.resource_management.waste_management.recycling_rate}%`
    // emissions.innerHTML = `${data.manufacturing_analysis.sustainability.carbon_footprint.scope_1_emissions} || ${data.manufacturing_analysis.sustainability.carbon_footprint.scope_2_emissions} || ${data.manufacturing_analysis.sustainability.carbon_footprint.scope_3_emissions}`
}

