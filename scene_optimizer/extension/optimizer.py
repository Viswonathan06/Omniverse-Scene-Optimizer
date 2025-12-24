"""
Scene Optimizer - Applies optimizations to USD scenes
"""

from pxr import Usd, UsdGeom, UsdShade, Sdf
from omni.usd import get_context


class SceneOptimizer:
    """Applies optimizations to USD scenes."""
    
    def merge_duplicate_meshes(self, stage: Usd.Stage, analysis_results: dict) -> int:
        """Merge duplicate meshes by converting them to instances."""
        duplicates = analysis_results.get("duplicate_meshes", [])
        merged_count = 0
        
        for duplicate_group in duplicates:
            if len(duplicate_group) < 2:
                continue
            
            # Keep the first mesh as the master
            master_mesh = duplicate_group[0]
            master_path = master_mesh.GetPath()
            
            # Convert others to instances
            for duplicate_mesh in duplicate_group[1:]:
                duplicate_path = duplicate_mesh.GetPath()
                
                # Create instance reference
                try:
                    # Remove the duplicate and create an instance
                    stage.RemovePrim(duplicate_path)
                    
                    # Create instance at parent path
                    parent_path = duplicate_path.GetParentPath()
                    instance_name = duplicate_path.name
                    
                    instance_prim = stage.DefinePrim(
                        parent_path.AppendChild(instance_name),
                        "Xform"
                    )
                    instance_prim.GetReferences().AddReference(
                        master_path,
                        master_path
                    )
                    
                    merged_count += 1
                except Exception as e:
                    print(f"Error merging {duplicate_path}: {e}")
        
        return merged_count
    
    def remove_unused_materials(self, stage: Usd.Stage, analysis_results: dict) -> int:
        """Remove materials that are not used in the scene."""
        unused_materials = analysis_results.get("unused_materials", [])
        removed_count = 0
        
        for material_prim in unused_materials:
            try:
                stage.RemovePrim(material_prim.GetPath())
                removed_count += 1
            except Exception as e:
                print(f"Error removing material {material_prim.GetPath()}: {e}")
        
        return removed_count
    
    def optimize_material_assignments(self, stage: Usd.Stage) -> int:
        """Optimize material assignments (consolidate duplicate bindings)."""
        optimized_count = 0
        
        # Group meshes by material
        material_groups = {}
        
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Mesh):
                mesh = UsdGeom.Mesh(prim)
                binding_api = UsdShade.MaterialBindingAPI(mesh)
                material = binding_api.GetDirectBinding().GetMaterial()
                
                if material:
                    material_path = material.GetPrim().GetPath()
                    if material_path not in material_groups:
                        material_groups[material_path] = []
                    material_groups[material_path].append(prim)
        
        # For now, just count potential optimizations
        # (In a full implementation, you'd consolidate bindings)
        optimized_count = len(material_groups)
        
        return optimized_count
    
    def remove_hidden_geometry(self, stage: Usd.Stage, analysis_results: dict) -> int:
        """Remove geometry that is marked as hidden."""
        hidden_geometry = analysis_results.get("hidden_geometry", [])
        removed_count = 0
        
        for hidden_prim in hidden_geometry:
            # Only remove if it's not referenced or instanced
            if not hidden_prim.HasAuthoredReferences() and not hidden_prim.IsInstance():
                try:
                    stage.RemovePrim(hidden_prim.GetPath())
                    removed_count += 1
                except Exception as e:
                    print(f"Error removing hidden prim {hidden_prim.GetPath()}: {e}")
        
        return removed_count
    
    def simplify_high_poly_meshes(self, stage: Usd.Stage, analysis_results: dict) -> int:
        """Simplify high-polygon meshes (placeholder - would need decimation library)."""
        high_poly_meshes = analysis_results.get("high_poly_meshes", [])
        simplified_count = 0
        
        # Note: Actual mesh decimation would require additional libraries
        # This is a placeholder that marks meshes for simplification
        for mesh_info in high_poly_meshes:
            mesh_prim = mesh_info["prim"]
            # In a full implementation, you would:
            # 1. Use a decimation library (like Open3D or similar)
            # 2. Reduce polygon count while preserving shape
            # 3. Update the mesh data
            
            # For now, we'll just add a custom attribute to mark it
            mesh_prim.SetCustomDataByKey("needs_simplification", True)
            simplified_count += 1
        
        return simplified_count

