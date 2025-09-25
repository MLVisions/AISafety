"""
AI Safety Website Icon Generator
Clean, professional icons for navigation using matplotlib
"""

import matplotlib

matplotlib.use('Agg')  # Use non-interactive backend to prevent popups

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle

# Website color scheme - cohesive blue theme with complementary accents
COLORS = {
    'primary_blue': '#0a1f44',
    'medium_blue': '#1e4a80',
    'accent_blue': '#295da0',
    'light_blue': '#4da3d8',
    'bright_blue': '#66c2ff',
    'soft_cyan': '#7dd3fc',
    'mint_green': '#10b981',
    'warm_amber': '#f59e0b',
    'soft_purple': '#8b5cf6',
    'coral_pink': '#f97316',
    'white': '#ffffff',
    'light_gray': '#e2e8f0'
}

def setup_icon_style() -> None:
    """Configure matplotlib for clean icon generation with transparency"""
    plt.rcParams.update({
        'figure.facecolor': 'none',  # Transparent figure
        'axes.facecolor': 'none'     # Transparent axes
    })

def generate_page_icons() -> None:
    """Generate clean, professional icons for each main page"""
    setup_icon_style()

    icons = {
        'home_icon.png': {
            'title': 'Home',
            'color': COLORS['primary_blue'],
            'type': 'home_house'
        },
        'ai_icon.png': {
            'title': 'AI & Technology',
            'color': COLORS['soft_cyan'],
            'type': 'neural_network'
        },
        'economy_icon.png': {
            'title': 'Economy & Policy',
            'color': COLORS['mint_green'],
            'type': 'trend_chart'
        },
        'society_icon.png': {
            'title': 'Society & Mental Health',
            'color': COLORS['soft_purple'],
            'type': 'people_group'
        },
        'privacy_icon.png': {
            'title': 'Privacy & Security',
            'color': COLORS['coral_pink'],
            'type': 'security_shield'
        },
        'action_icon.png': {
            'title': 'What We Can Do Now',
            'color': COLORS['warm_amber'],
            'type': 'action_arrow'
        }
    }

    for filename, config in icons.items():
        # Much larger figure size for bigger, more proportional icons
        fig, ax = plt.subplots(figsize=(8, 8), dpi=300)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

        # Set equal aspect ratio to prevent horizontal compression
        ax.set_aspect('equal')

        # Generate icon based on type with improved sizing and proportions
        if config['type'] == 'home_house':
            # Home icon - improved house shape with better proportions
            # House base (rectangle) - wider and taller
            house_base = Rectangle((2.5, 2.5), 5, 4, color=config['color'], alpha=0.85)
            ax.add_patch(house_base)
            # House roof (triangle) - properly proportioned
            roof_x = [2, 5, 8]
            roof_y = [6.5, 8.5, 6.5]
            ax.fill(roof_x, roof_y, color=config['color'], alpha=0.9)
            # Door - larger and proportional
            door = Rectangle((4.2, 2.5), 1.6, 2.8, color=COLORS['white'], alpha=0.95)
            ax.add_patch(door)
            # Door handle - larger
            ax.scatter(5.4, 3.8, s=80, c=config['color'], alpha=0.9, zorder=10)
            # Windows - add for more detail
            window1 = Rectangle((3, 4.8), 1, 1, color=COLORS['white'], alpha=0.95)
            window2 = Rectangle((6, 4.8), 1, 1, color=COLORS['white'], alpha=0.95)
            ax.add_patch(window1)
            ax.add_patch(window2)

        elif config['type'] == 'neural_network':
            # AI/Tech icon - improved neural network with better proportions
            nodes = [(2.5, 7.5), (7.5, 7.5), (2, 5), (8, 5), (5, 2.5)]
            # Draw connections first (behind nodes) - thicker lines
            connections = [(0, 2), (1, 3), (2, 4), (3, 4), (0, 1), (2, 3), (0, 4), (1, 4)]
            for start, end in connections:
                x1, y1 = nodes[start]
                x2, y2 = nodes[end]
                ax.plot([x1, x2], [y1, y2], color=config['color'], alpha=0.6, linewidth=4)
            # Draw nodes on top - larger and more prominent
            for x, y in nodes:
                ax.scatter(x, y, s=500, c=config['color'], alpha=0.9, zorder=10,
                          edgecolors=COLORS['white'], linewidth=3)

        elif config['type'] == 'trend_chart':
            # Economy icon - improved bar chart with better proportions
            x_positions = [2.5, 4, 5.5, 7]
            heights = [2.5, 4, 5.5, 7]
            bar_width = 1
            for _, (x, h) in enumerate(zip(x_positions, heights, strict=False)):
                bar = Rectangle((x - bar_width/2, 2), bar_width, h,
                              color=config['color'], alpha=0.85)
                ax.add_patch(bar)
            # Add trend arrow - more prominent
            ax.annotate('', xy=(8.5, 8.5), xytext=(2, 2.5),
                       arrowprops={'arrowstyle': '->', 'lw': 4, 'color': config['color'], 'alpha': 0.8})

        elif config['type'] == 'people_group':
            # Society icon - improved people figures with better proportions
            people_positions = [(2.5, 5), (5, 5), (7.5, 5)]
            for x, y in people_positions:
                # Head - larger
                head = Circle((x, y + 2), 0.6, color=config['color'], alpha=0.9)
                ax.add_patch(head)
                # Body - wider and taller
                body = Rectangle((x-0.5, y-1.5), 1, 3, color=config['color'], alpha=0.9)
                ax.add_patch(body)
            # Add connection symbol above - heart/connection
            # Draw a connecting arc above center figure
            ax.plot([3.5, 5, 6.5], [8, 8.5, 8], color=config['color'], linewidth=5, alpha=0.8)
            # Add small circles/dots for connection
            for hx in [3.5, 5, 6.5]:
                ax.scatter(hx, 8 if hx != 5 else 8.5, s=120, c=config['color'],
                          alpha=0.9, marker='o')

        elif config['type'] == 'security_shield':
            # Privacy/Security icon - improved shield with better proportions
            shield_x = [5, 2.5, 2.5, 5, 7.5, 7.5, 5]
            shield_y = [8.5, 7, 3, 1.5, 3, 7, 8.5]
            ax.fill(shield_x, shield_y, color=config['color'], alpha=0.9,
                   edgecolor=COLORS['white'], linewidth=3)
            # Lock symbol inside shield - larger and more detailed
            lock_body = Rectangle((3.8, 4), 2.4, 2, color=COLORS['white'], alpha=0.95)
            ax.add_patch(lock_body)
            # Lock shackle - larger
            lock_shackle = Circle((5, 6.5), 0.5, fill=False, edgecolor=COLORS['white'], linewidth=4)
            ax.add_patch(lock_shackle)
            # Add keyhole detail
            ax.scatter(5, 4.8, s=100, c=config['color'], alpha=0.9, marker='o')

        elif config['type'] == 'action_arrow':
            # Action icon - improved arrow with better proportions
            # Main arrow body - larger
            arrow_body = Rectangle((2.5, 4), 4, 2, color=config['color'], alpha=0.85)
            ax.add_patch(arrow_body)
            # Arrow head - larger triangle
            arrow_head_x = [6.5, 8.5, 6.5]
            arrow_head_y = [6.5, 5, 3.5]
            ax.fill(arrow_head_x, arrow_head_y, color=config['color'], alpha=0.85)
            # Add action burst/star around arrow
            star_angles = np.linspace(0, 2*np.pi, 8)
            for angle in star_angles:
                x_star = 5.5 + 2.5 * np.cos(angle)
                y_star = 5 + 2.5 * np.sin(angle)
                ax.plot([5.5, x_star], [5, y_star], color=config['color'],
                       linewidth=3, alpha=0.6)

        # Save icon with transparent background - higher quality
        save_path = f'docs/images/{filename}'
        plt.savefig(save_path, dpi=300, bbox_inches='tight',
                   facecolor='none', edgecolor='none', pad_inches=0.1,
                   transparent=True, format='png')
        plt.close()
        print(f"✅ Generated {filename} - larger size with improved proportions")

def generate_all_icons() -> None:
    """Generate all navigation icons"""
    generate_page_icons()
    print("✅ All icons generated successfully!")

if __name__ == "__main__":
    generate_all_icons()
