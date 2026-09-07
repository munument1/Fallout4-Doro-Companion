import bpy, addon_utils
bpy.utils.refresh_script_paths()
addon_utils.enable('io_scene_nifly', default_set=True, persistent=True)
print('IMPORT_PROPERTIES',[(p.identifier,p.type) for p in bpy.ops.import_scene.pynifly.get_rna_type().properties])
