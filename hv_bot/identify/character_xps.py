from PIL import Image


def get_xps_from_xp_bar_image(xp_bar_image: Image):
    XP_BAR_LEFT = 60
    XP_BAR_WIDTH = 418
    XP_BAR_HEIGHT = 16
    XP_BAR_HORIZONTAL_PADDING = 5
    XP_BAR_VERTICAL_PADDING = 6

    # TODO it seems that there are some marginal errors to actual num

    HP_BAR_TOP = 0
    MP_BAR_TOP = 16
    SP_BAR_TOP = 32
    DP_BAR_TOP = 48

    XP_BAR_TOPS = [HP_BAR_TOP, MP_BAR_TOP, SP_BAR_TOP, DP_BAR_TOP]
    xps = []
    for xp_bar_top in XP_BAR_TOPS:
        xp_bar_box = (XP_BAR_LEFT, xp_bar_top, XP_BAR_LEFT + XP_BAR_WIDTH, xp_bar_top + XP_BAR_HEIGHT)
        xp_bar_box_image = xp_bar_image.crop(xp_bar_box)
        # xp_bar_box_image.show()
        rgb_image = xp_bar_box_image.convert("RGB")

        total_xp = XP_BAR_WIDTH - 2 * XP_BAR_HORIZONTAL_PADDING
        current_xp = 0
        # threshold: HP:230/580; MP:460/610; SP: 450/610
        for x in range(0 + XP_BAR_HORIZONTAL_PADDING, XP_BAR_WIDTH - XP_BAR_HORIZONTAL_PADDING):
            r, g, b = rgb_image.getpixel((x, XP_BAR_VERTICAL_PADDING))
            # print(r, g, b)
            total_bright = r + g + b
            if total_bright >= 500:
                break
            current_xp += 1
        xp = current_xp / total_xp
        xps.append(xp)
    # the return list contains only float between [0, 1]
    return xps


def crop_xp_bar_image(fullscreen_image: Image):  # TODO private function
    XP_BAR_BOX_LEFT = 87
    XP_BAR_BOX_TOP = 74
    XP_BAR_BOX_WIDTH = 500
    XP_BAR_BOX_HEIGHT = 65

    box = [
        XP_BAR_BOX_LEFT,
        XP_BAR_BOX_TOP,
        XP_BAR_BOX_LEFT + XP_BAR_BOX_WIDTH,
        XP_BAR_BOX_TOP + XP_BAR_BOX_HEIGHT
    ]

    xp_bar_image = fullscreen_image.crop(box)
    return xp_bar_image
