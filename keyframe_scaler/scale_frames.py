import maya.cmds as mc

# Scaling of frames based on selection pivoting from the first or the last selected frame

def main (scale_factor=1, are_selected_frames=True, is_vertical=True, is_first=True):
    """
    :param scale_factor: the amount we are scaling by.
    :return:
    """
    anim_curve_info_dict = _get_all_keyframe_info(are_selected_frames=are_selected_frames, is_first=is_first)
    if not anim_curve_info_dict:
        return
    for anim_curve, keyframe_info in anim_curve_info_dict.iteritems():
        time_pivot = keyframe_info[0]
        value_pivot = keyframe_info[1]
        keyframe_indices = keyframe_info[2]

        for i in range(1, len(keyframe_indices)):
            if is_vertical:
                # In case we are scaling vertically, the values will be changed.
                value = mc.keyframe(anim_curve, query=True,
                                    valueChange=True, index=(keyframe_indices[i], keyframe_indices[i]))[0]
                new_value = (value-value_pivot)*scale_factor
                if new_value == 0:
                    pass

                mc.keyframe(anim_curve, edit=True,
                            valueChange=value_pivot+new_value,
                            index=(keyframe_indices[i], keyframe_indices[i]))
            else:
                # In case we are scaling horizontally, the times will be changed.
                time = mc.keyframe(anim_curve, query=True,
                                    timeChange=True,
                                    index=(keyframe_indices[i], keyframe_indices[i]))[0]

                new_value = time_pivot+(time-time_pivot)*scale_factor
                try:
                    mc.keyframe(anim_curve, edit=True,
                                timeChange=new_value,
                                index=(keyframe_indices[i], keyframe_indices[i]))
                except RuntimeError:
                    # keyframes can't go past the point where they have the same time
                    pass


def _get_all_keyframe_info (are_selected_frames=True, is_first=True):
    """
    :param is_first: determines whether keyframes are scaled after the first or before last.
    :param are_selected_frames: whether to scale all keyframes or only selected ones
    """
    anim_curve_info_dict = {}
    anim_curves = mc.keyframe(q=True, selected=True, name=True)
    if not anim_curves:
        mc.warning("Please select at least one animation curve.")
        return
    for anim_curve in anim_curves:
        anim_curve_info_dict[anim_curve] = _get_single_curve_info(anim_curve, are_selected_frames, is_first)
    return anim_curve_info_dict


def _get_single_curve_info(anim_curve, are_selected_frames, is_first):
    """
    :param anim_curve:  The name of a curve that we are getting info from. ex: Object_translateX
    :return: time_pivot (time of either first or last frame), value_pivot (value of either first or
    last frame), selected_indices (indices
    """
    selected_frame_times = mc.keyframe(anim_curve, q=True, selected=True, timeChange=True)
    selected_frame_values = mc.keyframe(anim_curve, q=True, selected=True, valueChange=True)
    selected_indices = mc.keyframe(anim_curve, q=True, selected=True, indexValue=True)
    all_indices = mc.keyframe(anim_curve, q=True, indexValue=True)

    # Calculating values based on provided parameters and selected keyframes
    #
    if is_first:
        time_pivot = selected_frame_times[0]
        value_pivot = selected_frame_values[0]
        index_start = selected_indices[0]
        if not are_selected_frames:
            selected_indices = all_indices[index_start:]

    else:
        time_pivot = selected_frame_times[-1]
        value_pivot = selected_frame_values[-1]
        index_start = selected_indices[-1]
        if not are_selected_frames:
            selected_indices = all_indices[:index_start]+[index_start]
            selected_indices.reverse()

    return time_pivot, value_pivot, selected_indices