import maya.cmds as mc

def main (is_first=True, are_selected_frames=True, scale_amount=1, is_vertical=True):
    """
    Scales all selected keyframes.
    :param is_first: determines whether keyframes are scaled after the first or before last.
    :param are_selected_frames: whether to scale all keyframes or only selected ones
    :param scale_amount: how much to scale by
    """
    anim_curves = mc.keyframe(q=True, selected=True, name=True)
    if not anim_curves:
        mc.warning("Please select at least one animation curve.")
        return
    for anim_curve in anim_curves:
        scale_frames_on_curve(anim_curve, is_first, are_selected_frames, scale_amount, is_vertical=is_vertical)

def scale_frames_on_curve(anim_curve, is_first=True, are_selected_frames=True,
                          scale_amount=1, is_vertical=True):
    """
    Scales keyframes on a specific anim_curve based on selected ones.
    :param anim_curve: the name of the animation curve where selected keys are placed.
    :param is_first: determines whether keyframes are scaled after the first or before last.
    :param are_selected_frames: whether to scale all keyframes or only selected ones
    :param scale_amount: how much to scale by
    """
    selected_frame_times = mc.keyframe(anim_curve, q=True, selected=True, timeChange=True)
    selected_frame_values = mc.keyframe(anim_curve, q=True, selected=True, valueChange=True)
    all_times = mc.keyframe(anim_curve, q=True, timeChange=True)

    if is_first:
        time_pivot = selected_frame_times[0]
        value_pivot = selected_frame_values[0]
        time_start = selected_frame_times[0]
        time_end = selected_frame_times[-1]
        if not are_selected_frames:
            time_end = all_times[-1]

    else:
        time_start = selected_frame_times[-1]
        time_pivot = selected_frame_times[-1]
        value_pivot = selected_frame_values[-1]
        time_end = selected_frame_times[0]
        if not are_selected_frames:
            time_end = all_times[0]

    if is_vertical:
        mc.scaleKey(anim_curve, time=(time_start, time_end),
                    timePivot=time_pivot, valuePivot=value_pivot,
                    valueScale=scale_amount)
    else:
        mc.scaleKey(anim_curve, time=(time_start, time_end),
                    timePivot=time_pivot, valuePivot=value_pivot,
                    timeScale=scale_amount)



    