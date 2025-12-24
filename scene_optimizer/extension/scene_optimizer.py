"""
Scene Optimizer Window - Main UI for the extension
"""

import omni.ui as ui
from omni.usd import get_context
from pxr import Usd, UsdGeom, UsdShade
from .analyzer import SceneAnalyzer
from .optimizer import SceneOptimizer


class SceneOptimizerWindow(ui.Window):
    """Main window for Scene Optimizer extension."""
    
    def __init__(self, title="Scene Optimizer", width=600, height=800):
        super().__init__(title, width=width, height=height)
        self._analyzer = SceneAnalyzer()
        self._optimizer = SceneOptimizer()
        self._analysis_results = {}
        self._before_metrics = None  # Store metrics before optimization
        self._after_metrics = None   # Store metrics after optimization
        self._build_ui()
    
    def _build_ui(self):
        """Build the user interface."""
        with self.frame:
            with ui.VStack(spacing=10):
                # Header
                ui.Label("Scene Optimizer", style={"font_size": 24, "color": 0xFF00FF00})
                ui.Spacer(height=10)
                
                # Scene Info Section
                with ui.CollapsableFrame("Scene Information", collapsed=False):
                    with ui.VStack(spacing=5):
                        self._scene_info_label = ui.Label("No scene loaded", word_wrap=True)
                        ui.Button("Refresh Scene Info", clicked_fn=self._refresh_scene_info)
                
                # Analysis Section
                with ui.CollapsableFrame("Scene Analysis", collapsed=False):
                    with ui.VStack(spacing=5):
                        ui.Label("Click 'Analyze Scene' to identify optimization opportunities")
                        ui.Button("Analyze Scene", clicked_fn=self._analyze_scene)
                        self._analysis_results_label = ui.Label("", word_wrap=True)
                
                # Optimization Options
                with ui.CollapsableFrame("Optimization Options", collapsed=False):
                    with ui.VStack(spacing=5):
                        self._merge_duplicates_check = ui.CheckBox(text="Merge Duplicate Meshes")
                        self._remove_unused_materials_check = ui.CheckBox(text="Remove Unused Materials")
                        self._optimize_materials_check = ui.CheckBox(text="Optimize Material Assignments")
                        self._remove_hidden_geometry_check = ui.CheckBox(text="Remove Hidden Geometry")
                        self._simplify_meshes_check = ui.CheckBox(text="Simplify High-Poly Meshes")
                        
                        ui.Spacer(height=5)
                        ui.Button("Apply Optimizations", clicked_fn=self._apply_optimizations)
                
                # Statistics Section
                with ui.CollapsableFrame("Performance Statistics", collapsed=False):
                    with ui.VStack(spacing=5):
                        self._stats_label = ui.Label("Run analysis to see statistics", word_wrap=True)
                        ui.Button("Update Statistics", clicked_fn=self._update_statistics)
                
                # Before/After Metrics Section
                with ui.CollapsableFrame("Before/After Comparison", collapsed=False):
                    with ui.VStack(spacing=5):
                        ui.Label("Compare scene metrics before and after optimization", word_wrap=True)
                        self._metrics_comparison_label = ui.Label("Run analysis and apply optimizations to see comparison", word_wrap=True)
                        ui.Button("Capture Before Metrics", clicked_fn=self._capture_before_metrics)
                        ui.Button("Capture After Metrics", clicked_fn=self._capture_after_metrics)
                        ui.Button("Show Comparison", clicked_fn=self._show_metrics_comparison)
                
                # Actions
                ui.Spacer()
                with ui.HStack():
                    ui.Button("Export Report", clicked_fn=self._export_report)
                    ui.Button("Reset Scene", clicked_fn=self._reset_scene)
    
    def _refresh_scene_info(self):
        """Refresh and display current scene information."""
        stage = get_context().get_stage()
        if not stage:
            self._scene_info_label.text = "No USD stage loaded"
            return
        
        prim_count = len(list(stage.Traverse()))
        default_prim = stage.GetDefaultPrim()
        root_layer = stage.GetRootLayer().identifier
        
        info_text = f"""
Scene Path: {root_layer}
Prim Count: {prim_count}
Default Prim: {default_prim.GetPath() if default_prim else "None"}
"""
        self._scene_info_label.text = info_text
    
    def _analyze_scene(self):
        """Analyze the current scene for optimization opportunities."""
        stage = get_context().get_stage()
        if not stage:
            self._analysis_results_label.text = "Error: No USD stage loaded"
            return
        
        # Capture before metrics automatically when analyzing
        self._before_metrics = self._analyzer.get_performance_metrics(stage)
        
        self._analysis_results = self._analyzer.analyze(stage)
        self._display_analysis_results()
        
        print("[Scene Optimizer] Before metrics captured")
    
    def _display_analysis_results(self):
        """Display analysis results in the UI."""
        if not self._analysis_results:
            self._analysis_results_label.text = "No analysis results available"
            return
        
        results_text = "Analysis Results:\n\n"
        
        # Duplicate meshes
        duplicates = self._analysis_results.get("duplicate_meshes", [])
        results_text += f"Duplicate Meshes: {len(duplicates)}\n"
        if duplicates:
            results_text += f"  - Can merge {len(duplicates)} duplicate instances\n"
        
        # Unused materials
        unused_materials = self._analysis_results.get("unused_materials", [])
        results_text += f"\nUnused Materials: {len(unused_materials)}\n"
        if unused_materials:
            results_text += f"  - Can remove {len(unused_materials)} unused materials\n"
        
        # High-poly meshes
        high_poly = self._analysis_results.get("high_poly_meshes", [])
        results_text += f"\nHigh-Poly Meshes: {len(high_poly)}\n"
        if high_poly:
            results_text += f"  - {len(high_poly)} meshes with >10k polygons\n"
        
        # Hidden geometry
        hidden = self._analysis_results.get("hidden_geometry", [])
        results_text += f"\nHidden Geometry: {len(hidden)}\n"
        if hidden:
            results_text += f"  - {len(hidden)} prims with visibility hidden\n"
        
        # Material optimization
        material_issues = self._analysis_results.get("material_issues", [])
        results_text += f"\nMaterial Issues: {len(material_issues)}\n"
        
        self._analysis_results_label.text = results_text
    
    def _apply_optimizations(self):
        """Apply selected optimizations to the scene."""
        stage = get_context().get_stage()
        if not stage:
            print("Error: No USD stage loaded")
            return
        
        if not self._analysis_results:
            print("Please run analysis first")
            return
        
        optimizations_applied = []
        
        if self._merge_duplicates_check.checked:
            count = self._optimizer.merge_duplicate_meshes(stage, self._analysis_results)
            optimizations_applied.append(f"Merged {count} duplicate meshes")
        
        if self._remove_unused_materials_check.checked:
            count = self._optimizer.remove_unused_materials(stage, self._analysis_results)
            optimizations_applied.append(f"Removed {count} unused materials")
        
        if self._optimize_materials_check.checked:
            count = self._optimizer.optimize_material_assignments(stage)
            optimizations_applied.append(f"Optimized {count} material assignments")
        
        if self._remove_hidden_geometry_check.checked:
            count = self._optimizer.remove_hidden_geometry(stage, self._analysis_results)
            optimizations_applied.append(f"Removed {count} hidden prims")
        
        if self._simplify_meshes_check.checked:
            count = self._optimizer.simplify_high_poly_meshes(stage, self._analysis_results)
            optimizations_applied.append(f"Simplified {count} high-poly meshes")
        
        if optimizations_applied:
            print("Optimizations applied:")
            for opt in optimizations_applied:
                print(f"  - {opt}")
            
            # Capture after metrics
            stage = get_context().get_stage()
            if stage:
                self._after_metrics = self._analyzer.get_performance_metrics(stage)
                print("[Scene Optimizer] After metrics captured")
            
            self._refresh_scene_info()
            self._analyze_scene()  # Re-analyze after optimization
            
            # Auto-show comparison if both metrics exist
            if self._before_metrics and self._after_metrics:
                self._show_metrics_comparison()
        else:
            print("No optimizations selected")
    
    def _update_statistics(self):
        """Update performance statistics."""
        stage = get_context().get_stage()
        if not stage:
            self._stats_label.text = "No scene loaded"
            return
        
        stats = self._analyzer.get_statistics(stage)
        
        stats_text = f"""
Performance Statistics:

Total Prims: {stats['total_prims']}
Mesh Prims: {stats['mesh_prims']}
Material Prims: {stats['material_prims']}
Total Polygons: {stats['total_polygons']:,}
Total Vertices: {stats['total_vertices']:,}
Total Materials: {stats['total_materials']}
Instances: {stats['instances']}
References: {stats['references']}

Estimated Memory: {stats['estimated_memory_mb']:.2f} MB
"""
        self._stats_label.text = stats_text
    
    def _export_report(self):
        """Export analysis report to file."""
        import json
        from pathlib import Path
        from datetime import datetime
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "analysis_results": self._analysis_results if self._analysis_results else {},
            "before_metrics": self._before_metrics if self._before_metrics else None,
            "after_metrics": self._after_metrics if self._after_metrics else None
        }
        
        # Calculate improvements if both metrics exist
        if self._before_metrics and self._after_metrics:
            improvements = {}
            for key in self._before_metrics.keys():
                before_val = self._before_metrics.get(key, 0)
                after_val = self._after_metrics.get(key, 0)
                if before_val != 0:
                    improvement_pct = ((before_val - after_val) / before_val) * 100
                    improvements[key] = {
                        "before": before_val,
                        "after": after_val,
                        "change": after_val - before_val,
                        "improvement_percent": improvement_pct
                    }
            report["improvements"] = improvements
        
        report_path = Path.home() / "scene_optimizer_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Report exported to: {report_path}")
        if self._before_metrics and self._after_metrics:
            print("Report includes before/after metrics comparison")
    
    def _capture_before_metrics(self):
        """Manually capture before metrics."""
        stage = get_context().get_stage()
        if not stage:
            print("Error: No USD stage loaded")
            return
        
        self._before_metrics = self._analyzer.get_performance_metrics(stage)
        print("[Scene Optimizer] Before metrics captured manually")
        self._metrics_comparison_label.text = "Before metrics captured. Apply optimizations and capture after metrics."
    
    def _capture_after_metrics(self):
        """Manually capture after metrics."""
        stage = get_context().get_stage()
        if not stage:
            print("Error: No USD stage loaded")
            return
        
        self._after_metrics = self._analyzer.get_performance_metrics(stage)
        print("[Scene Optimizer] After metrics captured manually")
        if self._before_metrics:
            self._show_metrics_comparison()
        else:
            self._metrics_comparison_label.text = "After metrics captured. Capture before metrics to see comparison."
    
    def _show_metrics_comparison(self):
        """Display before/after metrics comparison."""
        if not self._before_metrics:
            self._metrics_comparison_label.text = "Error: No before metrics captured. Run analysis first."
            return
        
        if not self._after_metrics:
            self._metrics_comparison_label.text = "Error: No after metrics captured. Apply optimizations first."
            return
        
        # Calculate improvements
        def calculate_improvement(before, after):
            """Calculate percentage improvement."""
            if before == 0:
                return 0.0
            change = before - after
            percent = (change / before) * 100
            return percent
        
        def format_metric(value, is_percentage=False):
            """Format metric value for display."""
            if isinstance(value, float):
                if is_percentage:
                    return f"{value:+.1f}%"
                return f"{value:,.2f}"
            return f"{value:,}"
        
        # Build comparison text
        comparison_text = "📊 BEFORE / AFTER COMPARISON\n"
        comparison_text += "=" * 50 + "\n\n"
        
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
            before_val = self._before_metrics.get(key, 0)
            after_val = self._after_metrics.get(key, 0)
            
            if key in ["total_prims", "mesh_prims", "unique_meshes", "instances", 
                      "total_polygons", "total_vertices", "total_materials", 
                      "unused_materials", "duplicate_groups", "estimated_draw_calls", "hidden_prims"]:
                # For these, lower is better
                improvement = calculate_improvement(before_val, after_val)
                arrow = "↓" if improvement > 0 else "↑" if improvement < 0 else "→"
                color_indicator = "🟢" if improvement > 0 else "🔴" if improvement < 0 else "⚪"
            else:
                # For memory, lower is better
                improvement = calculate_improvement(before_val, after_val)
                arrow = "↓" if improvement > 0 else "↑" if improvement < 0 else "→"
                color_indicator = "🟢" if improvement > 0 else "🔴" if improvement < 0 else "⚪"
            
            comparison_text += f"{color_indicator} {label}:\n"
            comparison_text += f"   Before: {format_metric(before_val)}\n"
            comparison_text += f"   After:  {format_metric(after_val)}\n"
            comparison_text += f"   Change: {format_metric(improvement, True)} {arrow}\n\n"
        
        # Summary
        comparison_text += "\n" + "=" * 50 + "\n"
        comparison_text += "📈 SUMMARY:\n\n"
        
        # Calculate key improvements
        memory_improvement = calculate_improvement(
            self._before_metrics.get("estimated_memory_mb", 0),
            self._after_metrics.get("estimated_memory_mb", 0)
        )
        draw_call_improvement = calculate_improvement(
            self._before_metrics.get("estimated_draw_calls", 0),
            self._after_metrics.get("estimated_draw_calls", 0)
        )
        polygon_reduction = calculate_improvement(
            self._before_metrics.get("total_polygons", 0),
            self._after_metrics.get("total_polygons", 0)
        )
        
        comparison_text += f"💾 Memory: {format_metric(memory_improvement, True)} reduction\n"
        comparison_text += f"🎨 Draw Calls: {format_metric(draw_call_improvement, True)} reduction\n"
        comparison_text += f"🔺 Polygons: {format_metric(polygon_reduction, True)} reduction\n"
        
        if memory_improvement > 0 or draw_call_improvement > 0 or polygon_reduction > 0:
            comparison_text += "\n✅ Optimization successful! Performance improved."
        else:
            comparison_text += "\n⚠️ No significant improvements detected."
        
        self._metrics_comparison_label.text = comparison_text
    
    def _reset_scene(self):
        """Reset scene analysis."""
        self._analysis_results = {}
        self._before_metrics = None
        self._after_metrics = None
        self._analysis_results_label.text = ""
        self._stats_label.text = "Run analysis to see statistics"
        self._metrics_comparison_label.text = "Run analysis and apply optimizations to see comparison"
        print("Scene analysis reset")

