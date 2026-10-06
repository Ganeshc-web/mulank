"""Display-only helpers (kept out of luck_engine.py so the engine stays UI-free)."""
COLOUR_HEX = {
    "Gold": "#d4af37", "Yellow": "#f4d03f", "Orange": "#e67e22", "Black": "#2c3e50", "Dark blue": "#1a365d",
    "White": "#ffffff", "Cream": "#fff8dc", "Green": "#2ecc71", "Violet": "#8e44ad", "Purple": "#9b59b6",
    "Mauve": "#c39bd3", "Dark grey": "#5d6d7e", "Electric blue": "#1e90ff", "Grey": "#95a5a6", "Red": "#e74c3c",
    "Crimson": "#c0392b", "Light green": "#82e0aa", "Light grey": "#d5d8dc", "Very dark shades": "#1c1c1c",
    "Light blue": "#7ec8e3", "Pink": "#ff8da1", "Pale yellow": "#f9e79f", "Dark shades": "#2e2e2e",
    "Bright yellow": "#f1c40f",
}


def swatch_html(names) -> str:
    names = (names,) if isinstance(names, str) else names
    chips = []
    for n in names:
        hx = COLOUR_HEX.get(n, "#cccccc")
        chips.append(
            '<span style="display:inline-flex;align-items:center;gap:6px;margin:0 12px 8px 0">'
            f'<span style="width:18px;height:18px;border-radius:4px;background:{hx};border:1px solid #999;'
            f'display:inline-block"></span>{n}</span>')
    return "".join(chips)