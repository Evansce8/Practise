import svgwrite
import os

def parse_points(point_string):
    # This helper function converts "0,-160 -20,-120" into [(0,-160), (-20,-120)]
    points = []
    pairs = point_string.split()
    for pair in pairs:
        x, y = pair.split(',')
        points.append((float(x), float(y)))
    return points

def create_lso_gold_logo():
    # 1. Setup the Canvas
    folder_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(folder_path, 'LSO_Gold_Logo.svg')

    dwg = svgwrite.Drawing(file_path, width='600px', height='600px')
    
    # 2. Premium Dark Background
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill="#0a0a0a"))

    # 3. Define the Gold Color Palette
    gold_color = "#d4af37"
    light_gold = "#fceabb"
    dark_gold = "#b8860b"

    # 4. Center Group
    logo_group = dwg.g(transform="translate(300, 300)")

    # --- OUTER RING ---
    logo_group.add(dwg.circle(center=(0, 0), r=250, fill="none", stroke=gold_color, stroke_width="6"))
    logo_group.add(dwg.circle(center=(0, 0), r=235, fill="none", stroke=dark_gold, stroke_width="1"))

    # --- THE CROWN (Top) ---
    crown_points_str = "0,-160 -20,-120 -40,-150 -60,-110 -80,-140 -100,-100 -80,-80 80,-80 100,-100 80,-140 60,-110 40,-150 20,-120"
    crown_points = parse_points(crown_points_str)
    logo_group.add(dwg.polygon(points=crown_points, fill=gold_color))
    
    # Crown base bar
    logo_group.add(dwg.rect(insert=(-80, -80), size=(160, 15), fill=dark_gold))

    # --- THE TEXT "L.S.O" ---
    text = dwg.text("", x=[0], y=[40], 
                    font_family="'Times New Roman', serif", 
                    font_size="160", 
                    font_weight="bold", 
                    text_anchor="middle", 
                    letter_spacing="10")
    
    text.add(dwg.tspan("L", fill=gold_color))
    text.add(dwg.tspan(".", fill=light_gold))
    text.add(dwg.tspan("S", fill=gold_color))
    text.add(dwg.tspan(".", fill=light_gold))
    text.add(dwg.tspan("O", fill=gold_color))
    
    logo_group.add(text)

    # --- THE MOUNTAINS (Bottom) ---
    mountain_points_str = "-120,140 -60,70 0,110 60,50 120,140"
    mountain_points = parse_points(mountain_points_str)
    logo_group.add(dwg.polygon(points=mountain_points, fill="none", stroke=gold_color, stroke_width="4", stroke_linejoin="round"))
    
    # Snow caps
    cap1 = parse_points("-60,70 -45,85 -75,85")
    cap2 = parse_points("60,50 75,65 45,65")
    logo_group.add(dwg.polygon(points=cap1, fill=light_gold))
    logo_group.add(dwg.polygon(points=cap2, fill=light_gold))

    # --- TAGLINE ---
    tagline = dwg.text("DREAM  •  PLAN  •  DO", x=[0], y=[200], 
                       font_family="Helvetica, Arial, sans-serif", 
                       font_size="18", 
                       font_weight="300", 
                       text_anchor="middle", 
                       letter_spacing="6",
                       fill=light_gold)
    logo_group.add(tagline)

    # Underline for tagline
    logo_group.add(dwg.line(start=(-150, 220), end=(150, 220), stroke=gold_color, stroke_width="2"))

    dwg.add(logo_group)
    dwg.save()
    print("Success! Your luxury logo has been created at:")
    print(file_path)

if __name__ == "__main__":
    create_lso_gold_logo()