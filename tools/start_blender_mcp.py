import bpy
import addon_utils
addon_utils.enable('blender_mcp', default_set=True, persistent=True)
prefs = bpy.context.preferences.addons['blender_mcp'].preferences
prefs.telemetry_consent = False
bpy.ops.wm.save_userpref()
print('BLENDER_MCP_READY', bpy.app.version_string, flush=True)
