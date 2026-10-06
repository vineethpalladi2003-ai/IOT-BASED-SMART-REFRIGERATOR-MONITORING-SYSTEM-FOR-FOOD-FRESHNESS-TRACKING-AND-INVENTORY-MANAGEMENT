"""
Smart Refrigerator Monitoring System - IoT-Based Food Freshness Tracking and Inventory Management
Comprehensive simulation engine for monitoring refrigerator conditions and food items.
"""

import json
import csv
import random
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple


class FreshnessLevel(Enum):
    """Enumeration for food freshness levels."""
    FRESH = "Fresh"
    GOOD = "Good"
    EXPIRING_SOON = "Expiring Soon"
    EXPIRED = "Expired"


class InventoryLevel(Enum):
    """Enumeration for inventory stock levels."""
    ADEQUATE = "Adequate"
    LOW = "Low"
    CRITICAL = "Critical"
    OVERSTOCKED = "Overstocked"


class AlertType(Enum):
    """Enumeration for alert types."""
    TEMPERATURE_HIGH = "Temperature High"
    TEMPERATURE_LOW = "Temperature Low"
    HUMIDITY_HIGH = "Humidity High"
    HUMIDITY_LOW = "Humidity Low"
    EXPIRY_WARNING = "Expiry Warning"
    EXPIRED_ITEM = "Expired Item"
    LOW_STOCK = "Low Stock"
    DOOR_OPEN = "Door Open"
    POWER_ISSUE = "Power Issue"


@dataclass
class FoodItem:
    """Represents a food item in the refrigerator."""
    item_id: str
    item_name: str
    category: str
    quantity: int
    unit: str
    expiry_date: str
    storage_location: str
    barcode: str
    entry_date: str


@dataclass
class RefrigeratorReading:
    """Represents a refrigerator monitoring reading."""
    timestamp: str
    temperature: float
    humidity: float
    door_open: bool
    power_status: str
    light_status: str
    compressor_status: str
    internal_pressure: float
    air_circulation: float


@dataclass
class FoodFreshnessReading:
    """Represents a food freshness assessment."""
    timestamp: str
    item_id: str
    item_name: str
    freshness_level: str
    days_until_expiry: int
    quality_score: float
    storage_condition_score: float
    recommendation: str


@dataclass
class InventoryReading:
    """Represents an inventory status reading."""
    timestamp: str
    item_id: str
    item_name: str
    quantity: int
    inventory_level: str
    consumption_rate: float
    reorder_point: int
    reorder_quantity: int


@dataclass
class Alert:
    """Represents a system alert."""
    timestamp: str
    alert_type: str
    severity: str
    item_id: str
    message: str
    recommended_action: str


class RefrigeratorMonitor:
    """Monitors refrigerator environmental conditions."""
    
    def __init__(self, fridge_id: str):
        self.fridge_id = fridge_id
        self.temperature = 4.0  # Optimal temperature in Celsius
        self.humidity = 65.0  # Optimal humidity percentage
        self.door_open_count = 0
        self.power_status = "Normal"
        self.light_status = "Off"
        self.compressor_status = "Running"
        self.internal_pressure = 101.3  # kPa
        self.air_circulation = 85.0  # Percentage
        
    def simulate_reading(self) -> RefrigeratorReading:
        """Generate a simulated refrigerator reading."""
        # Simulate temperature fluctuations
        temp_variation = random.gauss(0, 0.5)
        self.temperature = max(-5, min(10, self.temperature + temp_variation))
        
        # Simulate humidity fluctuations
        humidity_variation = random.gauss(0, 2)
        self.humidity = max(30, min(95, self.humidity + humidity_variation))
        
        # Simulate door opening (5% chance)
        self.door_open = random.random() < 0.05
        if self.door_open:
            self.door_open_count += 1
        
        # Simulate power status (99% normal)
        if random.random() < 0.01:
            self.power_status = "Abnormal"
        else:
            self.power_status = "Normal"
        
        # Simulate light status based on door
        self.light_status = "On" if self.door_open else "Off"
        
        # Simulate compressor status
        if self.power_status == "Normal":
            self.compressor_status = "Running"
        else:
            self.compressor_status = "Stopped"
        
        # Simulate internal pressure
        pressure_variation = random.gauss(0, 0.2)
        self.internal_pressure = max(95, min(110, self.internal_pressure + pressure_variation))
        
        # Simulate air circulation
        circulation_variation = random.gauss(0, 2)
        self.air_circulation = max(60, min(100, self.air_circulation + circulation_variation))
        
        return RefrigeratorReading(
            timestamp=datetime.now().isoformat(),
            temperature=round(self.temperature, 2),
            humidity=round(self.humidity, 2),
            door_open=self.door_open,
            power_status=self.power_status,
            light_status=self.light_status,
            compressor_status=self.compressor_status,
            internal_pressure=round(self.internal_pressure, 2),
            air_circulation=round(self.air_circulation, 2)
        )


class FoodFreshnessAnalyzer:
    """Analyzes food freshness based on storage conditions and time."""
    
    @staticmethod
    def calculate_freshness(item: FoodItem, fridge_reading: RefrigeratorReading) -> Tuple[str, int, float]:
        """Calculate freshness level and quality score."""
        expiry_date = datetime.fromisoformat(item.expiry_date)
        current_date = datetime.fromisoformat(fridge_reading.timestamp)
        days_until_expiry = (expiry_date - current_date).days
        
        # Determine freshness level
        if days_until_expiry < 0:
            freshness_level = FreshnessLevel.EXPIRED.value
        elif days_until_expiry <= 1:
            freshness_level = FreshnessLevel.EXPIRING_SOON.value
        elif days_until_expiry <= 3:
            freshness_level = FreshnessLevel.GOOD.value
        else:
            freshness_level = FreshnessLevel.FRESH.value
        
        # Calculate quality score based on storage conditions
        quality_score = 100.0
        
        # Temperature impact (optimal: 2-4°C)
        if fridge_reading.temperature < 0 or fridge_reading.temperature > 8:
            quality_score -= 15
        elif fridge_reading.temperature < 2 or fridge_reading.temperature > 5:
            quality_score -= 5
        
        # Humidity impact (optimal: 60-70%)
        if fridge_reading.humidity < 40 or fridge_reading.humidity > 90:
            quality_score -= 10
        elif fridge_reading.humidity < 50 or fridge_reading.humidity > 80:
            quality_score -= 5
        
        # Door opening impact
        if fridge_reading.door_open:
            quality_score -= 2
        
        # Power status impact
        if fridge_reading.power_status != "Normal":
            quality_score -= 20
        
        quality_score = max(0, min(100, quality_score))
        
        return freshness_level, days_until_expiry, quality_score
    
    @staticmethod
    def get_recommendation(freshness_level: str, days_until_expiry: int, quality_score: float) -> str:
        """Get recommendation based on freshness analysis."""
        if freshness_level == FreshnessLevel.EXPIRED.value:
            return "Item has expired. Remove immediately."
        elif freshness_level == FreshnessLevel.EXPIRING_SOON.value:
            return f"Item expires in {days_until_expiry} day(s). Use soon."
        elif quality_score < 70:
            return "Storage conditions may affect quality. Check item condition."
        else:
            return "Item is in good condition. Safe to consume."


class InventoryManager:
    """Manages food inventory and stock levels."""
    
    def __init__(self):
        self.reorder_points = {}
        self.consumption_history = {}
    
    def calculate_inventory_level(self, quantity: int, reorder_point: int) -> str:
        """Calculate inventory level classification."""
        if quantity <= 0:
            return InventoryLevel.CRITICAL.value
        elif quantity <= reorder_point:
            return InventoryLevel.LOW.value
        elif quantity >= reorder_point * 3:
            return InventoryLevel.OVERSTOCKED.value
        else:
            return InventoryLevel.ADEQUATE.value
    
    def calculate_consumption_rate(self, item_id: str, current_quantity: int) -> float:
        """Calculate consumption rate based on history."""
        if item_id not in self.consumption_history:
            self.consumption_history[item_id] = []
        
        self.consumption_history[item_id].append(current_quantity)
        
        if len(self.consumption_history[item_id]) < 2:
            return 0.0
        
        # Calculate average consumption per cycle
        history = self.consumption_history[item_id][-10:]  # Last 10 readings
        if len(history) > 1:
            consumption = sum(history[i] - history[i+1] for i in range(len(history)-1)) / (len(history) - 1)
            return max(0, consumption)
        
        return 0.0


class AlertGenerator:
    """Generates alerts based on system conditions."""
    
    @staticmethod
    def generate_alerts(fridge_reading: RefrigeratorReading, food_readings: List[FoodFreshnessReading], 
                       inventory_readings: List[InventoryReading]) -> List[Alert]:
        """Generate alerts based on current conditions."""
        alerts = []
        
        # Temperature alerts
        if fridge_reading.temperature < 0:
            alerts.append(Alert(
                timestamp=fridge_reading.timestamp,
                alert_type=AlertType.TEMPERATURE_LOW.value,
                severity="CRITICAL",
                item_id="FRIDGE",
                message=f"Temperature too low: {fridge_reading.temperature}°C. Risk of freezing food.",
                recommended_action="Adjust thermostat to increase temperature."
            ))
        elif fridge_reading.temperature > 8:
            alerts.append(Alert(
                timestamp=fridge_reading.timestamp,
                alert_type=AlertType.TEMPERATURE_HIGH.value,
                severity="CRITICAL",
                item_id="FRIDGE",
                message=f"Temperature too high: {fridge_reading.temperature}°C. Risk of spoilage.",
                recommended_action="Check refrigerator seal and adjust thermostat."
            ))
        elif fridge_reading.temperature < 2 or fridge_reading.temperature > 5:
            alerts.append(Alert(
                timestamp=fridge_reading.timestamp,
                alert_type=AlertType.TEMPERATURE_HIGH.value if fridge_reading.temperature > 5 else AlertType.TEMPERATURE_LOW.value,
                severity="WARNING",
                item_id="FRIDGE",
                message=f"Temperature suboptimal: {fridge_reading.temperature}°C. Ideal range: 2-4°C.",
                recommended_action="Fine-tune thermostat for optimal preservation."
            ))
        
        # Humidity alerts
        if fridge_reading.humidity < 40:
            alerts.append(Alert(
                timestamp=fridge_reading.timestamp,
                alert_type=AlertType.HUMIDITY_LOW.value,
                severity="WARNING",
                item_id="FRIDGE",
                message=f"Humidity too low: {fridge_reading.humidity}%. Food may dry out.",
                recommended_action="Check humidity control and add water if available."
            ))
        elif fridge_reading.humidity > 90:
            alerts.append(Alert(
                timestamp=fridge_reading.timestamp,
                alert_type=AlertType.HUMIDITY_HIGH.value,
                severity="WARNING",
                item_id="FRIDGE",
                message=f"Humidity too high: {fridge_reading.humidity}%. Risk of mold growth.",
                recommended_action="Improve air circulation and check for leaks."
            ))
        
        # Power status alerts
        if fridge_reading.power_status != "Normal":
            alerts.append(Alert(
                timestamp=fridge_reading.timestamp,
                alert_type=AlertType.POWER_ISSUE.value,
                severity="CRITICAL",
                item_id="FRIDGE",
                message="Power issue detected. Refrigerator may not be cooling properly.",
                recommended_action="Check power supply and contact technician if issue persists."
            ))
        
        # Door open alerts
        if fridge_reading.door_open:
            alerts.append(Alert(
                timestamp=fridge_reading.timestamp,
                alert_type=AlertType.DOOR_OPEN.value,
                severity="INFO",
                item_id="FRIDGE",
                message="Refrigerator door is open.",
                recommended_action="Close the door to maintain temperature."
            ))
        
        # Food expiry alerts
        for food_reading in food_readings:
            if food_reading.freshness_level == FreshnessLevel.EXPIRED.value:
                alerts.append(Alert(
                    timestamp=food_reading.timestamp,
                    alert_type=AlertType.EXPIRED_ITEM.value,
                    severity="CRITICAL",
                    item_id=food_reading.item_id,
                    message=f"{food_reading.item_name} has expired.",
                    recommended_action="Remove expired item immediately."
                ))
            elif food_reading.freshness_level == FreshnessLevel.EXPIRING_SOON.value:
                alerts.append(Alert(
                    timestamp=food_reading.timestamp,
                    alert_type=AlertType.EXPIRY_WARNING.value,
                    severity="WARNING",
                    item_id=food_reading.item_id,
                    message=f"{food_reading.item_name} expires in {food_reading.days_until_expiry} day(s).",
                    recommended_action="Use this item soon or consider alternative storage."
                ))
        
        # Low stock alerts
        for inventory_reading in inventory_readings:
            if inventory_reading.inventory_level == InventoryLevel.LOW.value:
                alerts.append(Alert(
                    timestamp=inventory_reading.timestamp,
                    alert_type=AlertType.LOW_STOCK.value,
                    severity="WARNING",
                    item_id=inventory_reading.item_id,
                    message=f"{inventory_reading.item_name} stock is low: {inventory_reading.quantity} units.",
                    recommended_action=f"Reorder {inventory_reading.reorder_quantity} units."
                ))
            elif inventory_reading.inventory_level == InventoryLevel.CRITICAL.value:
                alerts.append(Alert(
                    timestamp=inventory_reading.timestamp,
                    alert_type=AlertType.LOW_STOCK.value,
                    severity="CRITICAL",
                    item_id=inventory_reading.item_id,
                    message=f"{inventory_reading.item_name} stock is critical: {inventory_reading.quantity} units.",
                    recommended_action=f"Urgently reorder {inventory_reading.reorder_quantity} units."
                ))
        
        return alerts


class SmartRefrigeratorSystem:
    """Main system controller for smart refrigerator monitoring."""
    
    def __init__(self, fridge_id: str):
        self.fridge_id = fridge_id
        self.monitor = RefrigeratorMonitor(fridge_id)
        self.analyzer = FoodFreshnessAnalyzer()
        self.inventory_manager = InventoryManager()
        self.alert_generator = AlertGenerator()
        self.food_items = []
        self.fridge_readings = []
        self.food_readings = []
        self.inventory_readings = []
        self.alerts = []
        
    def initialize_food_items(self, num_items: int = 15):
        """Initialize food items in the refrigerator."""
        categories = ["Vegetables", "Fruits", "Dairy", "Meat", "Prepared Meals", "Beverages"]
        units = ["kg", "L", "pieces", "boxes", "containers"]
        
        for i in range(num_items):
            item_id = f"FOOD_{i+1:03d}"
            category = random.choice(categories)
            quantity = random.randint(1, 20)
            unit = random.choice(units)
            
            # Random expiry date (1-30 days from now)
            expiry_date = datetime.now() + timedelta(days=random.randint(1, 30))
            entry_date = datetime.now() - timedelta(days=random.randint(0, 7))
            
            item = FoodItem(
                item_id=item_id,
                item_name=f"{category} Item {i+1}",
                category=category,
                quantity=quantity,
                unit=unit,
                expiry_date=expiry_date.isoformat(),
                storage_location=f"Shelf {(i % 4) + 1}",
                barcode=f"123456789{i:03d}",
                entry_date=entry_date.isoformat()
            )
            self.food_items.append(item)
            self.inventory_manager.reorder_points[item_id] = max(1, quantity // 3)
    
    def run_simulation(self, num_cycles: int = 1000):
        """Run the simulation for specified number of cycles."""
        print(f"\n{'='*80}")
        print(f"RUNNING SMART REFRIGERATOR MONITORING SIMULATION")
        print(f"Refrigerator ID: {self.fridge_id}")
        print(f"Food Items: {len(self.food_items)}")
        print(f"Simulation Cycles: {num_cycles}")
        print(f"{'='*80}\n")
        
        for cycle in range(num_cycles):
            if (cycle + 1) % 100 == 0:
                print(f"✓ Completed cycle {cycle + 1}/{num_cycles}")
            
            # Generate refrigerator reading
            fridge_reading = self.monitor.simulate_reading()
            self.fridge_readings.append(fridge_reading)
            
            # Generate food freshness readings
            food_readings_cycle = []
            for item in self.food_items:
                freshness_level, days_until_expiry, quality_score = self.analyzer.calculate_freshness(item, fridge_reading)
                recommendation = self.analyzer.get_recommendation(freshness_level, days_until_expiry, quality_score)
                storage_condition_score = 100 - abs(fridge_reading.temperature - 3) * 5 - abs(fridge_reading.humidity - 65) * 0.5
                storage_condition_score = max(0, min(100, storage_condition_score))
                
                food_reading = FoodFreshnessReading(
                    timestamp=fridge_reading.timestamp,
                    item_id=item.item_id,
                    item_name=item.item_name,
                    freshness_level=freshness_level,
                    days_until_expiry=days_until_expiry,
                    quality_score=round(quality_score, 2),
                    storage_condition_score=round(storage_condition_score, 2),
                    recommendation=recommendation
                )
                food_readings_cycle.append(food_reading)
                self.food_readings.append(food_reading)
            
            # Generate inventory readings
            inventory_readings_cycle = []
            for item in self.food_items:
                # Simulate consumption
                consumption = random.randint(0, 2)
                item.quantity = max(0, item.quantity - consumption)
                
                reorder_point = self.inventory_manager.reorder_points[item.item_id]
                inventory_level = self.inventory_manager.calculate_inventory_level(item.quantity, reorder_point)
                consumption_rate = self.inventory_manager.calculate_consumption_rate(item.item_id, item.quantity)
                
                inventory_reading = InventoryReading(
                    timestamp=fridge_reading.timestamp,
                    item_id=item.item_id,
                    item_name=item.item_name,
                    quantity=item.quantity,
                    inventory_level=inventory_level,
                    consumption_rate=round(consumption_rate, 2),
                    reorder_point=reorder_point,
                    reorder_quantity=max(5, reorder_point * 2)
                )
                inventory_readings_cycle.append(inventory_reading)
                self.inventory_readings.append(inventory_reading)
            
            # Generate alerts
            cycle_alerts = self.alert_generator.generate_alerts(fridge_reading, food_readings_cycle, inventory_readings_cycle)
            self.alerts.extend(cycle_alerts)
        
        print(f"\n{'='*80}")
        print(f"✓ SIMULATION COMPLETED SUCCESSFULLY")
        print(f"{'='*80}\n")
    
    def export_data(self):
        """Export all data to CSV and JSON files."""
        # Export refrigerator readings
        with open("refrigerator_readings.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=RefrigeratorReading.__dataclass_fields__.keys())
            writer.writeheader()
            writer.writerows([asdict(r) for r in self.fridge_readings])
        
        # Export food freshness readings
        with open("food_freshness_readings.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FoodFreshnessReading.__dataclass_fields__.keys())
            writer.writeheader()
            writer.writerows([asdict(r) for r in self.food_readings])
        
        # Export inventory readings
        with open("inventory_readings.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=InventoryReading.__dataclass_fields__.keys())
            writer.writeheader()
            writer.writerows([asdict(r) for r in self.inventory_readings])
        
        # Export alerts
        with open("system_alerts.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=Alert.__dataclass_fields__.keys())
            writer.writeheader()
            writer.writerows([asdict(a) for a in self.alerts])
        
        # Export analytics to JSON
        analytics = {
            "fridge_id": self.fridge_id,
            "simulation_timestamp": datetime.now().isoformat(),
            "total_cycles": len(self.fridge_readings),
            "refrigerator_statistics": self._calculate_refrigerator_stats(),
            "food_freshness_statistics": self._calculate_freshness_stats(),
            "inventory_statistics": self._calculate_inventory_stats(),
            "alert_statistics": self._calculate_alert_stats(),
            "food_items": [asdict(item) for item in self.food_items]
        }
        
        with open("refrigerator_analytics.json", "w") as f:
            json.dump(analytics, f, indent=2)
        
        print("✓ Data exported to CSV and JSON files")
    
    def _calculate_refrigerator_stats(self) -> Dict:
        """Calculate refrigerator statistics."""
        if not self.fridge_readings:
            return {}
        
        temps = [r.temperature for r in self.fridge_readings]
        humidities = [r.humidity for r in self.fridge_readings]
        pressures = [r.internal_pressure for r in self.fridge_readings]
        circulations = [r.air_circulation for r in self.fridge_readings]
        door_opens = sum(1 for r in self.fridge_readings if r.door_open)
        power_issues = sum(1 for r in self.fridge_readings if r.power_status != "Normal")
        
        return {
            "avg_temperature": round(sum(temps) / len(temps), 2),
            "min_temperature": round(min(temps), 2),
            "max_temperature": round(max(temps), 2),
            "avg_humidity": round(sum(humidities) / len(humidities), 2),
            "min_humidity": round(min(humidities), 2),
            "max_humidity": round(max(humidities), 2),
            "avg_pressure": round(sum(pressures) / len(pressures), 2),
            "avg_air_circulation": round(sum(circulations) / len(circulations), 2),
            "total_door_opens": door_opens,
            "power_issues": power_issues
        }
    
    def _calculate_freshness_stats(self) -> Dict:
        """Calculate food freshness statistics."""
        if not self.food_readings:
            return {}
        
        freshness_counts = {}
        quality_scores = [r.quality_score for r in self.food_readings]
        
        for reading in self.food_readings:
            freshness_counts[reading.freshness_level] = freshness_counts.get(reading.freshness_level, 0) + 1
        
        return {
            "freshness_distribution": freshness_counts,
            "avg_quality_score": round(sum(quality_scores) / len(quality_scores), 2),
            "min_quality_score": round(min(quality_scores), 2),
            "max_quality_score": round(max(quality_scores), 2)
        }
    
    def _calculate_inventory_stats(self) -> Dict:
        """Calculate inventory statistics."""
        if not self.inventory_readings:
            return {}
        
        inventory_counts = {}
        quantities = [r.quantity for r in self.inventory_readings]
        
        for reading in self.inventory_readings:
            inventory_counts[reading.inventory_level] = inventory_counts.get(reading.inventory_level, 0) + 1
        
        return {
            "inventory_level_distribution": inventory_counts,
            "avg_quantity": round(sum(quantities) / len(quantities), 2) if quantities else 0,
            "min_quantity": min(quantities) if quantities else 0,
            "max_quantity": max(quantities) if quantities else 0,
            "total_items_tracked": len(self.food_items)
        }
    
    def _calculate_alert_stats(self) -> Dict:
        """Calculate alert statistics."""
        if not self.alerts:
            return {}
        
        alert_types = {}
        severity_counts = {}
        
        for alert in self.alerts:
            alert_types[alert.alert_type] = alert_types.get(alert.alert_type, 0) + 1
            severity_counts[alert.severity] = severity_counts.get(alert.severity, 0) + 1
        
        return {
            "total_alerts": len(self.alerts),
            "alert_types": alert_types,
            "severity_distribution": severity_counts
        }
    
    def print_statistics(self):
        """Print simulation statistics."""
        print(f"\n{'='*80}")
        print(f"REFRIGERATOR MONITORING STATISTICS")
        print(f"{'='*80}\n")
        
        stats = self._calculate_refrigerator_stats()
        print("REFRIGERATOR CONDITIONS")
        print(f"  Average Temperature: {stats.get('avg_temperature', 'N/A')}°C")
        print(f"  Temperature Range: {stats.get('min_temperature', 'N/A')}°C to {stats.get('max_temperature', 'N/A')}°C")
        print(f"  Average Humidity: {stats.get('avg_humidity', 'N/A')}%")
        print(f"  Door Opens: {stats.get('total_door_opens', 'N/A')}")
        print(f"  Power Issues: {stats.get('power_issues', 'N/A')}\n")
        
        freshness_stats = self._calculate_freshness_stats()
        print("FOOD FRESHNESS ANALYSIS")
        print(f"  Average Quality Score: {freshness_stats.get('avg_quality_score', 'N/A')}/100")
        print(f"  Freshness Distribution: {freshness_stats.get('freshness_distribution', {})}\n")
        
        inventory_stats = self._calculate_inventory_stats()
        print("INVENTORY STATUS")
        print(f"  Total Items Tracked: {inventory_stats.get('total_items_tracked', 'N/A')}")
        print(f"  Average Quantity: {inventory_stats.get('avg_quantity', 'N/A')} units")
        print(f"  Inventory Level Distribution: {inventory_stats.get('inventory_level_distribution', {})}\n")
        
        alert_stats = self._calculate_alert_stats()
        print("ALERT SUMMARY")
        print(f"  Total Alerts: {alert_stats.get('total_alerts', 'N/A')}")
        print(f"  Severity Distribution: {alert_stats.get('severity_distribution', {})}\n")
        print(f"{'='*80}\n")


def main():
    """Main entry point."""
    system = SmartRefrigeratorSystem("FRIDGE_001")
    system.initialize_food_items(15)
    system.run_simulation(num_cycles=1000)
    system.print_statistics()
    system.export_data()


if __name__ == "__main__":
    main()
