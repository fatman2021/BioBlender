from html.parser import *
from math import *
from smtplib import *
from urllib.request import *

import bpy
from bpy import *
from mathutils import *

from .BioBlender2 import *

bl_info = {
    "name": "BioBlender 2.0",
    "author": "SciVis, IFC-CNR",
    "version": (2, 0),
    "blender": (2, 6, 8, 0),
    "location": "Properties Window > Scene",
    "description": "BioBlender 2.0",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "http://bioblender.eu/?page_id=665",
    "category": "Add Mesh",
}

# ==================================================================================================================
# ==================================================================================================================
# ==================================================================================================================

# ==================================================================================================================
# ==================================================================================================================
# ==================================================================================================================


# ===== REGISTER = START ================================================
def register():
    bpy.utils.register_module(__name__)  # @UndefinedVariable


def unregister():
    bpy.utils.unregister_module(__name__)  # @UndefinedVariable


if __name__ == "__main__":
    register()
# ===== REGISTER = END ================================================
