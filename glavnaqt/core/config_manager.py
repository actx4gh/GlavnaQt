def all_configurations():
    return [
        [],
        ["left"],
        ["right"],
        ["top"],
        ["bottom"],
        ["left", "right"],
        ["left", "top"],
        ["left", "bottom"],
        ["right", "top"],
        ["right", "bottom"],
        ["top", "bottom"],
        ["left", "right", "top"],
        ["left", "right", "bottom"],
        ["left", "top", "bottom"],
        ["right", "top", "bottom"],
        ["left", "right", "top", "bottom"]
    ]
