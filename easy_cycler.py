import maya.cmds as mc

# Duplicates animation on selected objects a specified amount of times.
# Simulates a behaviour of post infinity curve, but with keyframes applied to the continuation of a curve


def copy_anim_curve(anim_curve, prev_idx, frames, values, tangent_infos):
    """
    Duplicate keyframes and tangent weights for a single animation curve
    """
    new_frames, new_values = get_new_curve_data(frames, values)
    for i in range(len(new_frames)):
        mc.setKeyframe(anim_curve, time=new_frames[i], value=new_values[i])

    # for tangent values first copy the out value
    first_tangent_info = tangent_infos[0]
    last_tangent_info = tangent_infos[-1]
    mc.keyTangent(anim_curve,
                  index=(prev_idx, prev_idx),
                  inAngle=last_tangent_info[0],
                  outAngle=first_tangent_info[1],
                  inWeight=last_tangent_info[2],
                  outWeight=first_tangent_info[3],
                  inTangentType=last_tangent_info[4],
                  outTangentType=first_tangent_info[5])
    for i in range(1,len(tangent_infos)):
        tangent_info = tangent_infos[i]
        mc.keyTangent(anim_curve,
                      index=(prev_idx+i, prev_idx+i),
                      inAngle=tangent_info[0],
                      outAngle=tangent_info[1],
                      inWeight=tangent_info[2],
                      outWeight=tangent_info[3],
                      inTangentType=tangent_info[4],
                      outTangentType=tangent_info[5])
    return new_frames, new_values


def get_new_curve_data(frames, values):
    new_frames = generate_new_vals(frames)
    new_values = generate_new_vals(values)
    return new_frames, new_values


def generate_new_vals(original_vals=None):
    """
    Generate values on the duplicated curve based on the previous one
    """
    prev_val = original_vals[-1]
    new_vals = []
    for i in range(1, len(original_vals)):
        prev_val = prev_val+(original_vals[i]-original_vals[i-1])
        new_vals.append(prev_val)
    return new_vals


def get_curve_data(anim_curve):
    """
    Get info on keyframes, their values and tangent infos
    :param anim_curve:
    :return:
    """
    keyframe_times = mc.keyframe(anim_curve, q=True, timeChange=True)
    keyframe_values = mc.keyframe(anim_curve, q=True, valueChange=True)
    tangent_infos = []
    if not keyframe_times or not keyframe_values:
        return None, None, None
    for i in range(len(keyframe_times)):
        tangent_infos.append(mc.keyTangent(anim_curve,
                                           index=(i, i),
                                           query=True,
                                           inAngle=True,
                                           outAngle=True,
                                           inWeight=True,
                                           outWeight=True,
                                           inTangentType=True,
                                           outTangentType=True))
    return keyframe_times, keyframe_values, tangent_infos


def main(num_of_loops=1):
    selected_objs = mc.ls(sl=True)
    if not selected_objs:
        mc.warning("Please select controllers to copy")
    for obj in selected_objs:
        print ("obj ", obj)
        anim_curves = mc.listConnections(obj, t="animCurve")
        if not anim_curves:
            continue
        for anim_curve in anim_curves:
            if not anim_curve:
                continue
            frames, values, tangent_infos = get_curve_data(anim_curve)
            if not frames or not values or not tangent_infos:
                continue
            for i in range(0, num_of_loops):
                prev_idx = (len(frames)-1)*(i+1) # increase index depending on the loop number
                new_frames, new_values = copy_anim_curve(anim_curve, prev_idx, frames, values, tangent_infos)
                frames = frames[-1:]+new_frames
                values = values[-1:]+new_values

