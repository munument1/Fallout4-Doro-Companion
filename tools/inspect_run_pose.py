import bpy
bpy.ops.wm.open_mainfile(filepath=r'D:\Codex_Trans\Fo4 modding\build\Doro_FO4_roundtrip_QA.blend')
r=next(o for o in bpy.data.objects if o.type=='ARMATURE' and o.animation_data and o.animation_data.action)
for f in [1,6,11]:
 bpy.context.scene.frame_set(f)
 print('FRAME',f,flush=True)
 for n in ['COM','SPINE1','SPINE2','Ribcage','HEAD','LLeg_Front_Thigh','LLeg_Front_Knee','LLeg_Front_Ankle']:
  b=r.pose.bones[n];print(n,'loc',[round(x,2) for x in b.head],'deltaAngles',[round(x*57.3,1) for x in (b.matrix@b.bone.matrix_local.inverted()).to_euler()],flush=True)
