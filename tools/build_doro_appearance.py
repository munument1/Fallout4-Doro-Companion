import bpy, math, json
from mathutils import Vector
from pathlib import Path

OUT=Path(r'D:\Codex_Trans\Fo4 modding\doro')
OUT.mkdir(exist_ok=True)
scene=bpy.context.scene
for o in list(scene.objects):
    o.hide_render=True
    o.hide_set(True)
col=bpy.data.collections.new('DORO • model v01')
scene.collection.children.link(col)
def move(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o)
    return o
def mat(name,color,rough=.4):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough
    return m
white=mat('Doro porcelain white',(.92,.90,.87));pink=mat('Doro strawberry pink',(.77,.24,.45));pinklight=mat('Doro soft pink highlight',(.94,.39,.60))
ink=mat('Doro warm ink',(.035,.017,.035));purple=mat('Doro violet',(.32,.12,.60));lavender=mat('Doro lavender',(.65,.40,.82));ribbon=mat('Doro ribbon plum',(.24,.09,.36));blush=mat('Doro cheek blush',(.96,.53,.65));mouth=mat('Doro mouth inside',(.23,.025,.07));tongue=mat('Doro tongue',(.94,.31,.48));shine=mat('Doro eye highlights',(1,1,1),.2)
parts=[]
def uv(name,loc,scale,material,seg=48,rings=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=loc)
    o=move(bpy.context.object);o.name=name;o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    for p in o.data.polygons:p.use_smooth=True
    parts.append(o);return o
def stroke(name,points,radius,material):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=16;cu.bevel_depth=radius;cu.bevel_resolution=4
    sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for p,co in zip(sp.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,cu);col.objects.link(o);cu.materials.append(material);parts.append(o);return o
def lock(name,coords,widths,depths,material):
    # Rounded, tapered ribbon of hair; cross-sections remain in the X/Y plane.
    verts=[];faces=[];n=16
    for (x,y,z),w,d in zip(coords,widths,depths):
        for j in range(n):
            a=j*2*math.pi/n;verts.append((x+w*math.cos(a),y+d*math.sin(a),z))
    for i in range(len(coords)-1):
        for j in range(n):a=i*n+j;b=i*n+(j+1)%n;faces.append((a,b,b+n,a+n))
    faces.extend([tuple(reversed(range(n))),tuple((len(coords)-1)*n+j for j in range(n))])
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(material)
    for f in me.polygons:f.use_smooth=True
    sub=o.modifiers.new('Soft sculpted hair','SUBSURF');sub.levels=2;sub.render_levels=2;parts.append(o);return o

body=uv('Doro Body',(0,-34,56),(43,66,37),white)
bodybits=[body]
for side,x in [('L',-1),('R',1)]:
    bodybits.append(uv('Front leg '+side,(x*31,10,29),(16,20,29),white))
    bodybits.append(uv('Rear leg '+side,(x*27,-76,27),(15,19,27),white))
bpy.ops.object.select_all(action='DESELECT')
for o in bodybits:o.select_set(True)
bpy.context.view_layer.objects.active=body;bpy.ops.object.join()
rem=body.modifiers.new('Continuous body surface','REMESH');rem.mode='VOXEL';rem.voxel_size=1.6;bpy.ops.object.modifier_apply(modifier=rem.name)
sm=body.modifiers.new('Smooth body junctions','SMOOTH');sm.factor=1.2;sm.iterations=6;bpy.ops.object.modifier_apply(modifier=sm.name)
for p in body.data.polygons:p.use_smooth=True
head=uv('Doro Face',(0,39,82),(46,32,37),white)
cap=uv('Hair back volume',(0,30,94),(49,33,42),pink)
# Face remains in front of the cap; three overlapping sculpted fringe pieces.
lock('Fringe center',[(-7,40,130),(-5,57,126),(-3,68,114),(-2,72,100),(0,73,93)],[5,14,15,10,.3],[3,7,8,6,.3],pink)
lock('Fringe left',[(-15,36,130),(-23,51,127),(-28,65,115),(-29,71,104),(-23,72,101)],[4,12,13,8,.3],[2,7,8,5,.3],pink)
lock('Fringe right',[(8,38,132),(18,55,126),(23,66,114),(26,71,103),(30,70,100)],[4,14,12,7,.3],[2,8,7,5,.3],pink)
for s in [-1,1]:
    lock('Long side lock '+str(s),[(s*24,33,129),(s*39,42,117),(s*46,48,96),(s*47,48,74),(s*43,51,58),(s*33,56,52)],[4,11,11,10,7,.2],[3,12,13,11,7,.2],pink)
    lock('Outer swept lock '+str(s),[(s*30,23,124),(s*45,27,108),(s*51,30,83),(s*49,34,62),(s*39,38,50)],[3,9,8,7,.2],[2,9,9,6,.2],pink)
bun=uv('Side rose bun',(-45,17,124),(20,18,21),pinklight)
for i in range(3):
    x=-55+i*8
    stroke('Bun sculpt seam '+str(i),[(x,31,137),(x+3,35,128),(x+4,34,116)],.65,pink)
uv('Ribbon knot',(-48,20,102),(5,5,5),ribbon)
for s in [-1,1]:
    o=uv('Ribbon bow '+str(s),(-48+s*9,19,100),(10,4,6),ribbon);o.rotation_euler[1]=s*.4
    lock('Ribbon tail '+str(s),[(-48+s*3,20,101),(-48+s*6,20,93),(-48+s*9,20,83)],[3,4,3],[2,2,1],ribbon)

def fy(x,z):
    return 39+32*math.sqrt(max(.03,1-(x/46)**2-((z-82)/37)**2))
for x in [-18,18]:
    z=83;y=fy(x,z)
    uv('Eye outline '+str(x),(x,y+.7,z),(10.1,2.1,13.8),ink)
    uv('Eye violet '+str(x),(x,y+2.1,z),(8.6,1.3,12.2),purple)
    uv('Eye lavender lower '+str(x),(x,y+2.7,z-4.6),(7.7,.8,6.4),lavender)
    uv('Eye sparkle '+str(x),(x-2.8,y+3.4,z+6.5),(2.5,.8,3),shine,32,20)
    stroke('Eyebrow '+str(x),[(x-8,fy(x-8,99)+1.6,99),(x-1,fy(x-1,102)+1.6,102),(x+6,fy(x+6,100)+1.6,100)],1.15,ink)
    uv('Cheek '+str(x),(x*1.42,fy(x*1.42,70)+.3,70),(6.5,.65,3.2),blush)
# A shallow mouth cavity and tongue, with independent upper/lower geometry.
uv('Mouth outline',(0,fy(0,68)+.7,67),(5.4,1.5,7.4),ink)
uv('Mouth cavity',(0,fy(0,68)+1.6,67),(4.2,.8,6.2),mouth)
uv('Tongue',(0,fy(0,68)+2.3,64),(3.1,.45,3.1),tongue)
stroke('Omega upper lip',[(-6,fy(-6,73)+2,73),(-4,fy(-4,71)+2,71),(-1,fy(-1,72)+2,72),(0,fy(0,74)+2,74),(2,fy(2,71)+2,71),(5,fy(5,72)+2,72),(6,fy(6,74)+2,74)],.85,ink)
uv('Tiny tail',(0,-96,67),(11,13,10),white)

# Studio presentation, independent from the game asset collection.
studio=bpy.data.collections.new('STUDIO • preview only');scene.collection.children.link(studio)
def studio_move(o):
    for c in list(o.users_collection):c.objects.unlink(o)
    studio.objects.link(o)
floor=mat('Studio lilac',(.12,.10,.17),.75)
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-2));ground=bpy.context.object;ground.name='Studio floor';ground.data.materials.append(floor);studio_move(ground)
def aim(o,point):o.rotation_euler=(Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,size in [('Key',(130,160,260),1600000,180),('Fill',(-170,100,150),1100000,160),('Rim',(0,-180,230),1900000,140)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);studio.objects.link(o);o.location=loc;aim(o,(0,0,65))
data=bpy.data.cameras.new('Doro presentation');cam=bpy.data.objects.new('Doro presentation',data);studio.objects.link(cam);scene.camera=cam;data.type='ORTHO';data.ortho_scale=255
scene.render.engine='CYCLES';scene.cycles.samples=32
scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world.color=(.25,.25,.25);scene.view_settings.view_transform='AgX'
cam.location=(230,310,185);aim(cam,(0,-17,69))
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'doro_three_quarter.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Doro_appearance_v01.blend'))
bpy.ops.render.render(write_still=True)
cam.location=(0,360,115);aim(cam,(0,0,70));scene.render.filepath=str(OUT/'doro_front.png');bpy.ops.render.render(write_still=True)
cam.location=(360,0,120);aim(cam,(0,-15,70));scene.render.filepath=str(OUT/'doro_side.png');bpy.ops.render.render(write_still=True)
cam.location=(230,310,185);aim(cam,(0,-17,69));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Doro_appearance_v01.blend'))
print('DORO_MODEL_DONE',len(col.objects),'objects')
