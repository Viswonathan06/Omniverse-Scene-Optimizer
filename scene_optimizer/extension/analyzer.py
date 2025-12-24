"""
Scene Analyzer - Analyzes USD scenes for optimization opportunities
"""

from pxr import Usd, UsdGeom, UsdShade, Gf
from collections import defaultdict
import hashlib


class SceneAnalyzer:
    """Analyzes USD scenes to identify optimization opportunities."""
    
    def __init__(self):
        self.high_poly_threshold = 10000  # Polygons
        self.duplicate_threshold = 0.001  # Distance threshold for duplicates
    
    def analyze(self, stage: Usd.Stage) -> dict:
        """Analyze the stage and return optimization opportunities."""
        results = {
            "duplicate_meshes": [],
            "unused_materials": [],
            "high_poly_meshes": [],
            "hidden_geometry": [],
            "material_issues": []
        }
        
        # Get all meshes and materials
        meshes = self._get_all_meshes(stage)
        materials = self._get_all_materials(stage)
        used_materials = self._get_used_materials(stage)
        
        # Find duplicate meshes
        results["duplicate_meshes"] = self._find_duplicate_meshes(meshes)
        
        # Find unused materials
        results["unused_materials"] = [
            mat for mat in materials if mat not in used_materials
        ]
        
        # Find high-poly meshes
        results["high_poly_meshes"] = self._find_high_poly_meshes(meshes)
        
        # Find hidden geometry
        results["hidden_geometry"] = self._find_hidden_geometry(stage)
        
        # Find material issues
        results["material_issues"] = self._find_material_issues(stage)
        
        return results
    
    def _get_all_meshes(self, stage: Usd.Stage) -> list:
        """Get all mesh prims in the stage."""
        meshes = []
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Mesh):
                meshes.append(prim)
        return meshes
    
    def _get_all_materials(self, stage: Usd.Stage) -> list:
        """Get all material prims in the stage."""
        materials = []
        for prim in stage.Traverse():
            if prim.IsA(UsdShade.Material):
                materials.append(prim)
        return materials
    
    def _get_used_materials(self, stage: Usd.Stage) -> set:
        """Get all materials that are actually used in the scene."""
        used_materials = set()
        
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Mesh):
                mesh = UsdGeom.Mesh(prim)
                material = UsdShade.MaterialBindingAPI(mesh).GetDirectBinding().GetMaterial()
                if material:
                    used_materials.add(material.GetPrim())
        
        return used_materials
    
    def _find_duplicate_meshes(self, meshes: list) -> list:
        """Find meshes that are duplicates (same geometry)."""
        mesh_hashes = defaultdict(list)
        
        for mesh_prim in meshes:
            mesh = UsdGeom.Mesh(mesh_prim)
            
            # Get mesh data
            points = mesh.GetPointsAttr().Get()
            face_vertex_counts = mesh.GetFaceVertexCountsAttr().Get()
            face_vertex_indices = mesh.GetFaceVertexIndicesAttr().Get()
            
            if not points or not face_vertex_counts:
                continue
            
            # Create a hash of the mesh geometry
            mesh_data = (
                tuple(points),
                tuple(face_vertex_counts),
                tuple(face_vertex_indices) if face_vertex_indices else tuple()
            )
            mesh_hash = hashlib.md5(str(mesh_data).encode()).hexdigest()
            
            mesh_hashes[mesh_hash].append(mesh_prim)
        
        # Return groups of duplicates (groups with more than one mesh)
        duplicates = []
        for mesh_group in mesh_hashes.values():
            if len(mesh_group) > 1:
                duplicates.append(mesh_group)
        
        return duplicates
    
    def _find_high_poly_meshes(self, meshes: list) -> list:
        """Find meshes with high polygon counts."""
        high_poly = []
        
        for mesh_prim in meshes:
            mesh = UsdGeom.Mesh(mesh_prim)
            face_vertex_counts = mesh.GetFaceVertexCountsAttr().Get()
            
            if face_vertex_counts:
                polygon_count = len(face_vertex_counts)
                if polygon_count > self.high_poly_threshold:
                    high_poly.append({
                        "prim": mesh_prim,
                        "polygons": polygon_count,
                        "path": str(mesh_prim.GetPath())
                    })
        
        return sorted(high_poly, key=lambda x: x["polygons"], reverse=True)
    
    def _find_hidden_geometry(self, stage: Usd.Stage) -> list:
        """Find geometry that is hidden (visibility = hidden)."""
        hidden = []
        
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Imageable):
                imageable = UsdGeom.Imageable(prim)
                visibility = imageable.GetVisibilityAttr().Get()
                if visibility == "hidden":
                    hidden.append(prim)
        
        return hidden
    
    def _find_material_issues(self, stage: Usd.Stage) -> list:
        """Find material assignment issues."""
        issues = []
        
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Mesh):
                mesh = UsdGeom.Mesh(prim)
                binding_api = UsdShade.MaterialBindingAPI(mesh)
                
                # Check for missing material assignments
                material = binding_api.GetDirectBinding().GetMaterial()
                if not material:
                    issues.append({
                        "type": "missing_material",
                        "prim": prim,
                        "path": str(prim.GetPath())
                    })
        
        return issues
    
    def get_statistics(self, stage: Usd.Stage) -> dict:
        """Get comprehensive statistics about the scene."""
        stats = {
            "total_prims": 0,
            "mesh_prims": 0,
            "material_prims": 0,
            "total_polygons": 0,
            "total_vertices": 0,
            "total_materials": 0,
            "instances": 0,
            "references": 0,
            "estimated_memory_mb": 0.0
        }
        
        total_vertices = 0
        total_polygons = 0
        
        for prim in stage.Traverse():
            stats["total_prims"] += 1
            
            if prim.IsA(UsdGeom.Mesh):
                stats["mesh_prims"] += 1
                mesh = UsdGeom.Mesh(prim)
                
                points = mesh.GetPointsAttr().Get()
                face_vertex_counts = mesh.GetFaceVertexCountsAttr().Get()
                
                if points:
                    total_vertices += len(points)
                if face_vertex_counts:
                    total_polygons += len(face_vertex_counts)
            
            elif prim.IsA(UsdShade.Material):
                stats["material_prims"] += 1
            
            if prim.IsInstance():
                stats["instances"] += 1
            
            if prim.HasAuthoredReferences():
                stats["references"] += 1
        
        stats["total_vertices"] = total_vertices
        stats["total_polygons"] = total_polygons
        stats["total_materials"] = stats["material_prims"]
        
        # Rough memory estimate (vertices * 12 bytes + overhead)
        stats["estimated_memory_mb"] = (total_vertices * 12) / (1024 * 1024)
        
        return stats

