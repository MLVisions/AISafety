"""
AI Safety Website Icon Generator
Clean, professional icons for navigation using matplotlib
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to prevent popups
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, Circle
import os

# Website color scheme (matching plot_generator.py)
COLORS = {
    'primary_blue': '#0a1f44',
    'medium_blue': '#1e4a80', 
    'accent_blue': '#295da0',
    'light_blue': '#4da3d8',
    'bright_blue': '#66c2ff',
    'background': '#f5f8fc',
    'text_dark': '#2c3e50',
    'text_light': '#6a7aa2',
    'success_green': '#27ae60',
    'warning_orange': '#f39c12',
    'error_red': '#e74c3c',
    'neutral_gray': '#95a5a6'
}

def setup_icon_style():
    """Configure matplotlib for clean icon generation with transparency"""
    plt.rcParams.update({
        'figure.facecolor': 'none',  # Transparent figure
        'axes.facecolor': 'none'     # Transparent axes
    })

def generate_page_icons():
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
            'color': COLORS['accent_blue'],
            'type': 'neural_network'
        },
        'economy_icon.png': {
            'title': 'Economy & Policy', 
            'color': COLORS['success_green'],
            'type': 'trend_chart'
        },
        'society_icon.png': {
            'title': 'Society & Mental Health',
            'color': COLORS['warning_orange'], 
            'type': 'people_group'
        },
        'privacy_icon.png': {
            'title': 'Privacy & Security',
            'color': COLORS['error_red'],
            'type': 'security_shield'
        },
        'action_icon.png': {
            'title': 'What We Can Do Now',
            'color': COLORS['bright_blue'],
            'type': 'action_arrow'
        }
    }
    
    for filename, config in icons.items():
        # Larger figure size for bigger icons
        fig, ax = plt.subplots(figsize=(4, 4), dpi=300)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Remove background circle - make it fully transparent
        # Just draw the icon directly without background
        
        # Generate icon based on type
        if config['type'] == 'home_house':
            # Home icon - simple house shape
            # House base (rectangle)
            house_base = Rectangle((3.5, 3.5), 3, 2.5, color=config['color'], alpha=0.8)
            ax.add_patch(house_base)
            # House roof (triangle)
            roof_x = [3.2, 5, 6.8]
            roof_y = [6, 7.5, 6]
            ax.fill(roof_x, roof_y, color=config['color'], alpha=0.85)
            # Door
            door = Rectangle((4.6, 3.5), 0.8, 1.5, color='white', alpha=0.9)
            ax.add_patch(door)
            # Door handle
            ax.scatter(5.2, 4.2, s=30, c=config['color'], alpha=0.8, zorder=10)
            
        elif config['type'] == 'neural_network':
            # AI/Tech icon - connected nodes representing neural network
            nodes = [(3.5, 7), (6.5, 7), (3, 5), (7, 5), (5, 3)]
            # Draw connections first (behind nodes)
            connections = [(0, 2), (1, 3), (2, 4), (3, 4), (0, 1), (2, 3)]
            for start, end in connections:
                x1, y1 = nodes[start]
                x2, y2 = nodes[end]
                ax.plot([x1, x2], [y1, y2], color=config['color'], alpha=0.7, linewidth=3)
            # Draw nodes on top
            for x, y in nodes:
                ax.scatter(x, y, s=300, c=config['color'], alpha=0.9, zorder=10, edgecolors='white', linewidth=2)
                
        elif config['type'] == 'trend_chart':
            # Economy icon - upward trending bar chart
            x_positions = [3, 4.5, 6, 7.5]
            heights = [2.5, 3.8, 5.2, 6.5]
            bar_width = 0.8
            for i, (x, h) in enumerate(zip(x_positions, heights)):
                bar = Rectangle((x - bar_width/2, 5 - h/2), bar_width, h, 
                              color=config['color'], alpha=0.8)
                ax.add_patch(bar)
            # Add trend line
            trend_x = np.array(x_positions)
            trend_y = np.array([5 - h/2 + h for h in heights])
            ax.plot(trend_x, trend_y, color=config['color'], linewidth=3, alpha=0.9, linestyle='--')
            
        elif config['type'] == 'people_group':
            # Society icon - group of people figures
            people_positions = [(3.5, 5.5), (5, 5.5), (6.5, 5.5)]
            for x, y in people_positions:
                # Head
                head = Circle((x, y + 1.2), 0.35, color=config['color'], alpha=0.85)
                ax.add_patch(head)
                # Body
                body = Rectangle((x-0.25, y-0.8), 0.5, 1.8, color=config['color'], alpha=0.85)
                ax.add_patch(body)
            # Add heart symbol above center figure
            heart_x, heart_y = 5, 7.8
            ax.plot([heart_x-0.2, heart_x, heart_x+0.2], [heart_y-0.2, heart_y, heart_y-0.2], 
                   color=config['color'], linewidth=4, alpha=0.8)
                
        elif config['type'] == 'security_shield':
            # Privacy/Security icon - shield with lock
            shield_x = [5, 3.8, 3.8, 5, 6.2, 6.2, 5]
            shield_y = [7.5, 6.5, 4, 2.5, 4, 6.5, 7.5]
            ax.fill(shield_x, shield_y, color=config['color'], alpha=0.85, edgecolor='white', linewidth=2)
            # Lock symbol inside shield
            lock_body = Rectangle((4.4, 4.8), 1.2, 1, color='white', alpha=0.95)
            ax.add_patch(lock_body)
            lock_shackle = Circle((5, 5.9), 0.25, fill=False, edgecolor='white', linewidth=3)
            ax.add_patch(lock_shackle)
            
        elif config['type'] == 'action_arrow':
            # Action icon - forward arrow with checkmark
            # Arrow pointing forward/up
            arrow_body = Rectangle((4, 4.5), 2, 0.8, color=config['color'], alpha=0.8)
            ax.add_patch(arrow_body)
            # Arrow head (triangle)
            arrow_head_x = [6, 7.2, 6]
            arrow_head_y = [5.7, 4.9, 4.1]
            ax.fill(arrow_head_x, arrow_head_y, color=config['color'], alpha=0.8)
            # Checkmark
            check_x = [2.5, 3.2, 4.5]
            check_y = [5.2, 4.5, 6.8]
            ax.plot(check_x, check_y, color=config['color'], linewidth=4, alpha=0.9)
        
        # Save icon with transparent background
        save_path = f'docs/images/{filename}'
        plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                   facecolor='none', edgecolor='none', pad_inches=0.05,
                   transparent=True)
        plt.close()
        print(f"✅ Generated {filename}")

def generate_all_icons():
    """Generate all navigation icons"""
    print("🎨 Generating navigation icons...")
    print("=" * 40)
    generate_page_icons()
    print("✅ All icons generated successfully!")

if __name__ == "__main__":
    generate_all_icons()