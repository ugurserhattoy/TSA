def button_style(color_set=None, width=None):
    """
    Defines button's default style and colors

    Args:
        color_set -> "lblue", "blue", "red"
        width     -> For fixed width enter a number or auto width
    """
    width_str = "" if width is None else f"min-width: {width}px;\nmax-width: {width}px;"
    # color_set = 0: bgcolor, 1: hover bgcolor, 2: pressed bgcolor
    match color_set:
        case None:  # Default color set
            color_set = ["#707070", "#4C4B4B", "#868686"]
        case "lblue":  # Light Blue
            color_set = ["#2980b9", "#13649b", "#3396d8"]
        case "blue":  # Blue
            color_set = ["#0A4872", "#083B5D", "#0F6198"]
        case "red":  # Red
            color_set = ["#c0392b", "#a93226", "#e74c3c"]

    return f"""
        QPushButton {{
            background-color: {color_set[0]};
            color: white;
            border-radius: 6px;
            font-size: 14px;
            padding: 6px 24px;
            {width_str}
        }}
        QPushButton:hover {{
            background-color: {color_set[1]};
        }}
        QPushButton:pressed {{
            background-color: {color_set[2]};
        }}
    """
