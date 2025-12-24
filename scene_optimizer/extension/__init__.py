"""
Scene Optimizer Extension for NVIDIA Omniverse
Analyzes and optimizes USD scenes for improved performance.
"""

import omni.ext
import omni.ui as ui
from .scene_optimizer import SceneOptimizerWindow


class SceneOptimizerExtension(omni.ext.IExt):
    """Main extension class."""
    
    def on_startup(self, ext_id):
        """Called when extension is loaded."""
        self._window = SceneOptimizerWindow()
        print("[Scene Optimizer] Extension loaded successfully")
    
    def on_shutdown(self):
        """Called when extension is unloaded."""
        if hasattr(self, "_window"):
            self._window.destroy()
        print("[Scene Optimizer] Extension unloaded")

