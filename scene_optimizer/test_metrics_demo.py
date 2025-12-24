#!/usr/bin/env python3
"""
Standalone demo of Before/After Metrics functionality
This simulates how the metrics work without requiring Omniverse
"""

import json
from datetime import datetime
from typing import Dict, Any


class MockSceneAnalyzer:
    """Mock analyzer that simulates scene analysis without Omniverse."""
    
    def __init__(self):
        self.high_poly_threshold = 10000
    
    def get_performance_metrics(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate getting performance metrics from a scene."""
        return {
            "total_prims": scene_data.get("total_prims", 0),
            "mesh_prims": scene_data.get("mesh_prims", 0),
            "unique_meshes": scene_data.get("unique_meshes", 0),
            "instances": scene_data.get("instances", 0),
            "total_polygons": scene_data.get("total_polygons", 0),
            "total_vertices": scene_data.get("total_vertices", 0),
            "total_materials": scene_data.get("total_materials", 0),
            "unused_materials": scene_data.get("unused_materials", 0),
            "duplicate_groups": scene_data.get("duplicate_groups", 0),
            "estimated_draw_calls": scene_data.get("estimated_draw_calls", 0),
            "estimated_memory_mb": scene_data.get("estimated_memory_mb", 0.0),
            "hidden_prims": scene_data.get("hidden_prims", 0)
        }


class MetricsDemo:
    """Demo class to show before/after metrics comparison."""
    
    def __init__(self):
        self.analyzer = MockSceneAnalyzer()
        self.before_metrics = None
        self.after_metrics = None
    
    def simulate_scene_before(self) -> Dict[str, Any]:
        """Simulate a scene before optimization."""
        return {
            "total_prims": 5000,
            "mesh_prims": 3200,
            "unique_meshes": 2500,
            "instances": 0,
            "total_polygons": 2500000,
            "total_vertices": 1250000,
            "total_materials": 150,
            "unused_materials": 45,
            "duplicate_groups": 12,
            "estimated_draw_calls": 2500,
            "estimated_memory_mb": 125.5,
            "hidden_prims": 23
        }
    
    def simulate_scene_after(self) -> Dict[str, Any]:
        """Simulate a scene after optimization."""
        return {
            "total_prims": 3200,  # Reduced by merging duplicates
            "mesh_prims": 2488,   # Reduced
            "unique_meshes": 2488, # Same (duplicates converted to instances)
            "instances": 12,      # Created from duplicates
            "total_polygons": 2100000,  # Reduced by removing hidden geometry
            "total_vertices": 1050000,  # Reduced
            "total_materials": 105,     # Removed unused materials
            "unused_materials": 0,      # All removed
            "duplicate_groups": 0,      # All merged
            "estimated_draw_calls": 2500,  # Same (instances don't reduce draw calls in this sim)
            "estimated_memory_mb": 78.3,   # Reduced significantly
            "hidden_prims": 0              # All removed
        }
    
    def calculate_improvement(self, before: float, after: float) -> float:
        """Calculate percentage improvement."""
        if before == 0:
            return 0.0
        change = before - after
        percent = (change / before) * 100
        return percent
    
    def format_metric(self, value: float, is_percentage: bool = False) -> str:
        """Format metric value for display."""
        if isinstance(value, float):
            if is_percentage:
                return f"{value:+.1f}%"
            if value >= 1000:
                return f"{value:,.2f}"
            return f"{value:.2f}"
        return f"{value:,}"
    
    def show_comparison(self):
        """Display before/after comparison."""
        if not self.before_metrics or not self.after_metrics:
            print("Error: Need both before and after metrics")
            return
        
        print("\n" + "=" * 70)
        print("📊 BEFORE / AFTER METRICS COMPARISON")
        print("=" * 70 + "\n")
        
        # Key metrics to compare
        metrics_to_compare = [
            ("Total Prims", "total_prims", False),
            ("Mesh Prims", "mesh_prims", False),
            ("Unique Meshes", "unique_meshes", False),
            ("Instances", "instances", False),
            ("Total Polygons", "total_polygons", False),
            ("Total Vertices", "total_vertices", False),
            ("Total Materials", "total_materials", False),
            ("Unused Materials", "unused_materials", False),
            ("Duplicate Groups", "duplicate_groups", False),
            ("Estimated Draw Calls", "estimated_draw_calls", False),
            ("Estimated Memory (MB)", "estimated_memory_mb", False),
            ("Hidden Prims", "hidden_prims", False),
        ]
        
        for label, key, is_percentage in metrics_to_compare:
            before_val = self.before_metrics.get(key, 0)
            after_val = self.after_metrics.get(key, 0)
            
            # Determine if lower is better
            if key in ["total_prims", "mesh_prims", "total_polygons", "total_vertices",
                      "total_materials", "unused_materials", "duplicate_groups",
                      "estimated_draw_calls", "estimated_memory_mb", "hidden_prims"]:
                improvement = self.calculate_improvement(before_val, after_val)
                arrow = "↓" if improvement > 0 else "↑" if improvement < 0 else "→"
                color_indicator = "🟢" if improvement > 0 else "🔴" if improvement < 0 else "⚪"
            else:
                # For instances, more might be better (shows optimization worked)
                improvement = self.calculate_improvement(before_val, after_val)
                arrow = "↑" if after_val > before_val else "↓" if after_val < before_val else "→"
                color_indicator = "🟢" if after_val > before_val else "⚪"
            
            print(f"{color_indicator} {label}:")
            print(f"   Before: {self.format_metric(before_val)}")
            print(f"   After:  {self.format_metric(after_val)}")
            print(f"   Change: {self.format_metric(improvement, True)} {arrow}")
            print()
        
        # Summary
        print("=" * 70)
        print("📈 SUMMARY:")
        print("=" * 70 + "\n")
        
        memory_improvement = self.calculate_improvement(
            self.before_metrics.get("estimated_memory_mb", 0),
            self.after_metrics.get("estimated_memory_mb", 0)
        )
        draw_call_improvement = self.calculate_improvement(
            self.before_metrics.get("estimated_draw_calls", 0),
            self.after_metrics.get("estimated_draw_calls", 0)
        )
        polygon_reduction = self.calculate_improvement(
            self.before_metrics.get("total_polygons", 0),
            self.after_metrics.get("total_polygons", 0)
        )
        prim_reduction = self.calculate_improvement(
            self.before_metrics.get("total_prims", 0),
            self.after_metrics.get("total_prims", 0)
        )
        
        print(f"💾 Memory: {self.format_metric(memory_improvement, True)} reduction")
        print(f"🎨 Draw Calls: {self.format_metric(draw_call_improvement, True)} reduction")
        print(f"🔺 Polygons: {self.format_metric(polygon_reduction, True)} reduction")
        print(f"📦 Prims: {self.format_metric(prim_reduction, True)} reduction")
        
        if memory_improvement > 0 or draw_call_improvement > 0 or polygon_reduction > 0:
            print("\n✅ Optimization successful! Performance improved significantly.")
        else:
            print("\n⚠️ No significant improvements detected.")
        
        print("\n" + "=" * 70)
    
    def export_report(self, filename: str = "metrics_demo_report.json"):
        """Export metrics report to JSON file."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "before_metrics": self.before_metrics,
            "after_metrics": self.after_metrics
        }
        
        # Calculate improvements
        if self.before_metrics and self.after_metrics:
            improvements = {}
            for key in self.before_metrics.keys():
                before_val = self.before_metrics.get(key, 0)
                after_val = self.after_metrics.get(key, 0)
                if before_val != 0:
                    improvement_pct = ((before_val - after_val) / before_val) * 100
                    improvements[key] = {
                        "before": before_val,
                        "after": after_val,
                        "change": after_val - before_val,
                        "improvement_percent": improvement_pct
                    }
            report["improvements"] = improvements
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Report exported to: {filename}")


def main():
    """Run the demo."""
    print("=" * 70)
    print("Scene Optimizer - Before/After Metrics Demo")
    print("=" * 70)
    print("\nThis demo simulates how the before/after metrics feature works")
    print("in the Scene Optimizer extension.\n")
    
    demo = MetricsDemo()
    
    # Simulate capturing before metrics
    print("📊 Capturing BEFORE metrics...")
    before_scene = demo.simulate_scene_before()
    demo.before_metrics = demo.analyzer.get_performance_metrics(before_scene)
    print("✅ Before metrics captured!\n")
    
    # Simulate applying optimizations
    print("⚙️  Applying optimizations...")
    print("   - Merging duplicate meshes...")
    print("   - Removing unused materials...")
    print("   - Removing hidden geometry...")
    print("   - Optimizing material assignments...")
    print("✅ Optimizations applied!\n")
    
    # Simulate capturing after metrics
    print("📊 Capturing AFTER metrics...")
    after_scene = demo.simulate_scene_after()
    demo.after_metrics = demo.analyzer.get_performance_metrics(after_scene)
    print("✅ After metrics captured!\n")
    
    # Show comparison
    demo.show_comparison()
    
    # Export report
    demo.export_report()
    
    print("\n" + "=" * 70)
    print("Demo completed! This shows how the metrics work in the extension.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

