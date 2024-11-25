# Carbon Footprint Calculator Documentation

## Overview

The Carbon Footprint Calculator is a comprehensive Python application designed to calculate and analyze carbon emissions for both individuals and businesses. It provides detailed breakdowns of emissions by category, comparative analysis, and generates visual representations of the results.

## Core Features

- Dual calculation modes: individual and business
- Detailed emissions analysis by category
- Comparative analysis with city/country averages
- Visual data representation (pie charts and bar graphs)
- Report generation functionality
- Data persistence through CSV files

## Class Structure

### CarbonCalculator

The main class handling all calculator functionality.

#### Key Constants

```python
ELECTRICITY_CO2_FACTOR = 0.309  # kg CO2 per kWh
GREEN_ELECTRICITY_REDUCTION = 0.25  # 25% reduction for green tariffs
GAS_CO2_FACTOR = 0.203  # kg CO2 per kWh
CAR_CO2_FACTOR = 14.3  # kg CO2 per gallon
OFFICE_SPACE_CO2_FACTOR = 0.05  # tonnes CO2 per sq ft per year
EMPLOYEE_CO2_FACTOR = 2.5  # tonnes CO2 per employee per year
DATA_CENTER_CO2_FACTOR = 0.000475  # tonnes CO2 per kWh
```

#### Data Classes

1. `Household`
   - Stores residential energy usage and transportation data
   - Fields: members, electricity_kwh, electricity_green, gas_kwh, other_heating, num_cars, car_mileages

2. `Personal`
   - Stores individual lifestyle and consumption choices
   - Fields: organic_food, meat_dairy, local_food, processed_food, composting, food_waste, bus_miles, train_miles, flight_hours, spending, recycles_basic, recycles_plastic

3. `Business`
   - Stores business-related emissions data
   - Fields: name, sector, num_employees, office_space_sqft, electricity_kwh, electricity_green, gas_kwh, company_vehicles, air_travel_hours, waste_recycling_rate, data_center_usage, supply_chain_assessment, renewable_energy_percent

## Key Methods

### Data Collection

- `collect_household_data()`: Gathers residential energy and transport information
- `collect_personal_data()`: Gathers lifestyle and consumption choices
- `collect_business_data()`: Gathers business operations and resource usage data

### Calculations

- `calculate_household_emissions()`: Computes emissions from household energy and vehicle use
- `calculate_personal_emissions()`: Computes emissions from individual choices and activities
- `calculate_business_emissions()`: Computes business-related emissions by category

### Analysis and Display

- `analyze_individual_emissions()`: Provides detailed breakdown of personal emissions
- `compare_emissions()`: Compares results with city/country averages
- `display_results()`: Shows comprehensive analysis with visualizations
- `display_business_results()`: Shows business-specific analysis

### Reporting

- `generate_report()`: Creates detailed PDF report of calculations and analysis

## Usage Examples

### Individual Calculator

```python
calculator = CarbonCalculator()
calculator.calculator_type = 'individual'
calculator.collect_household_data()
calculator.collect_personal_data()
calculator.display_results()
```

### Business Calculator

```python
calculator = CarbonCalculator()
calculator.calculator_type = 'business'
calculator.collect_business_data()
emissions = calculator.calculate_business_emissions()
calculator.display_business_results(emissions)
```

## Data Requirements

### CSV Files
The calculator requires two CSV files:
- `Cities.csv`: Contains city-level emissions data
- `Countries.csv`: Contains country-level emissions data

Format:
```
Location,CO2
CityName,EmissionValue
CountryName,EmissionValue
```

## Calculation Methodology

### Individual Emissions

1. **Household Energy**
   - Electricity: Usage × CO2 factor (adjusted for green tariffs)
   - Gas: Usage × CO2 factor
   - Vehicle emissions based on mileage and vehicle type

2. **Personal Activities**
   - Food choices (organic, meat consumption, local sourcing)
   - Transportation (public transport, flights)
   - Consumer spending
   - Public services (constant factor)

### Business Emissions

1. **Direct Operations**
   - Building operations
   - Energy consumption
   - Company vehicles
   - Business travel

2. **Indirect Impact**
   - Employee-related emissions
   - Data center usage
   - Supply chain considerations
   - Sector-specific multipliers

## Output Formats

### Visual Representations
- Pie charts showing emission distribution
- Bar graphs comparing with regional averages

### Reports
Generated reports include:
- Timestamp
- Total emissions
- Category breakdown
- Comparative analysis
- Recommendations for reduction

## Error Handling

The calculator includes comprehensive error handling for:
- Invalid input validation
- File loading errors
- Data format inconsistencies
- Calculation edge cases

## Dependencies

- pandas: Data manipulation and analysis
- matplotlib: Visualization
- dataclasses: Data structure organization
- datetime: Timestamp handling

## Future Enhancements

Potential areas for improvement:
1. Additional emission factors for different regions
2. More detailed transportation calculations
3. Integration with external carbon databases
4. Enhanced reporting formats (PDF, HTML)
5. Real-time data updates
6. Mobile device support
7. Cloud data storage integration

## License

This project is licensed under MIT License. See LICENSE file for details.
