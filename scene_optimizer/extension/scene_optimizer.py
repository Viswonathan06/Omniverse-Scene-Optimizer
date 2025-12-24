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
        
        self._analysis_results = self._analyzer.analyze(stage)
        self._display_analysis_results()
    
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
            self._refresh_scene_info()
            self._analyze_scene()  # Re-analyze after optimization
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
        if not self._analysis_results:
            print("No analysis results to export")
            return
        
        import json
        from pathlib import Path
        
        report_path = Path.home() / "scene_optimizer_report.json"
        with open(report_path, 'w') as f:
            json.dump(self._analysis_results, f, indent=2, default=str)
        
        print(f"Report exported to: {report_path}")
    
    def _reset_scene(self):
        """Reset scene analysis."""
        self._analysis_results = {}
        self._analysis_results_label.text = ""
        self._stats_label.text = "Run analysis to see statistics"
        print("Scene analysis reset")

