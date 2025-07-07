import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

# Create figure and axis
fig, ax = plt.subplots(1, 1, figsize=(16, 12))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Define colors for different layers
colors = {
    'constitutional': '#e1f5fe',
    'multiagent': '#f3e5f5', 
    'knowledge': '#e8f5e8',
    'external': '#fff3e0',
    'compliance': '#ffebee'
}

# Define box positions and text
boxes = {
    'client': (5, 9, 'Client\nRequest', 'external'),
    'gateway': (5, 8, 'API\nGateway', 'external'),
    'cai': (5, 7, 'Constitutional AI\nService :8001', 'constitutional'),
    'is': (7.5, 7, 'Integrity\nService :8002', 'constitutional'),
    'hash': (8.5, 8, 'Constitutional Hash\ncdd01ef066bc6cf2', 'compliance'),
    'mac': (5, 5.5, 'Multi-Agent\nCoordinator :8008', 'multiagent'),
    'wa1': (2.5, 4, 'Worker\nAgent 1 :8009', 'multiagent'),
    'wa2': (5, 4, 'Worker\nAgent 2 :8009', 'multiagent'),
    'wa3': (7.5, 4, 'Worker\nAgent N :8009', 'multiagent'),
    'bb': (5, 2.5, 'Blackboard\nService :8010', 'knowledge'),
    'auditdb': (7.5, 2.5, 'Audit\nDatabase', 'knowledge'),
    'mcp': (2.5, 7, 'MCP Aggregator\n:3000', 'external'),
    'tools': (1, 7, 'External Tools\nContext7, Sequential', 'external')
}

# Draw boxes
box_objects = {}
for name, (x, y, text, style) in boxes.items():
    # Create fancy box
    if name == 'auditdb':
        # Draw cylinder for database
        box = patches.Ellipse((x, y+0.15), 1.5, 0.3, facecolor=colors[style], 
                             edgecolor='green', linewidth=2)
        ax.add_patch(box)
        box = patches.Rectangle((x-0.75, y-0.5), 1.5, 0.65, facecolor=colors[style], 
                               edgecolor='green', linewidth=2)
        ax.add_patch(box)
        box = patches.Ellipse((x, y-0.5), 1.5, 0.3, facecolor=colors[style], 
                             edgecolor='green', linewidth=2)
        ax.add_patch(box)
    else:
        linewidth = 3 if style == 'compliance' else 2
        edge_color = {'constitutional': 'blue', 'multiagent': 'purple', 
                     'knowledge': 'green', 'external': 'orange', 'compliance': 'red'}[style]
        
        box = FancyBboxPatch((x-0.75, y-0.4), 1.5, 0.8, 
                            boxstyle="round,pad=0.05",
                            facecolor=colors[style], 
                            edgecolor=edge_color, 
                            linewidth=linewidth)
        ax.add_patch(box)
    
    # Add text
    ax.text(x, y, text, ha='center', va='center', fontsize=8, fontweight='bold')
    box_objects[name] = (x, y)

# Define connections with labels
connections = [
    ('client', 'gateway', ''),
    ('gateway', 'cai', ''),
    ('cai', 'mac', 'Constitutional Hash\ncdd01ef066bc6cf2'),
    ('cai', 'is', 'Compliance\nValidation'),
    ('mac', 'wa1', 'Task Assignment\n+ Hash Validation'),
    ('mac', 'wa2', 'Task Assignment\n+ Hash Validation'),
    ('mac', 'wa3', 'Task Assignment\n+ Hash Validation'),
    ('wa1', 'bb', 'Knowledge Sharing\n+ Compliance Check'),
    ('wa2', 'bb', ''),
    ('wa3', 'bb', 'Knowledge Sharing\n+ Compliance Check'),
    ('mac', 'bb', 'State Management\n+ Hash Validation'),
    ('wa1', 'is', 'Compliance\nReport'),
    ('wa2', 'is', 'Compliance\nReport'),
    ('wa3', 'is', 'Compliance\nReport'),
    ('is', 'auditdb', 'Audit Log'),
    ('bb', 'auditdb', 'Knowledge Log'),
    ('tools', 'mcp', ''),
    ('mcp', 'cai', ''),
    ('mcp', 'mac', ''),
    ('mac', 'cai', 'Aggregated Response\n+ Hash Validation'),
    ('cai', 'gateway', 'Constitutional\nResponse'),
    ('gateway', 'client', '')
]

# Draw connections
for start, end, label in connections:
    x1, y1 = box_objects[start]
    x2, y2 = box_objects[end]
    
    # Create arrow
    arrow = ConnectionPatch((x1, y1), (x2, y2), "data", "data",
                           arrowstyle="->", shrinkA=30, shrinkB=30,
                           mutation_scale=20, fc="black", ec="black", linewidth=1.5)
    ax.add_patch(arrow)
    
    # Add label if provided
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        # Offset label slightly to avoid overlap with arrow
        offset_x = 0.3 if x2 > x1 else -0.3
        offset_y = 0.2 if y2 > y1 else -0.2
        ax.text(mid_x + offset_x, mid_y + offset_y, label, ha='center', va='center', 
                fontsize=6, bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))

# Add dashed compliance check arrows
compliance_checks = [
    ('cai', 'is', 'Pre-execution\nCompliance Check'),
    ('mac', 'is', 'Runtime\nCompliance Check'),
]

for start, end, label in compliance_checks:
    x1, y1 = box_objects[start]
    x2, y2 = box_objects[end]
    
    arrow = ConnectionPatch((x1, y1), (x2, y2), "data", "data",
                           arrowstyle="->", shrinkA=30, shrinkB=30,
                           mutation_scale=20, fc="red", ec="red", 
                           linewidth=1.5, linestyle='--', alpha=0.7)
    ax.add_patch(arrow)

# Add title
ax.text(5, 9.7, 'ACGS Production Architecture', ha='center', va='center', 
        fontsize=16, fontweight='bold')

# Add layer labels
ax.text(0.5, 8.5, 'External\nInterface', ha='center', va='center', 
        fontsize=10, fontweight='bold', color='orange', rotation=90)
ax.text(0.5, 7, 'Constitutional\nCompliance', ha='center', va='center', 
        fontsize=10, fontweight='bold', color='blue', rotation=90)
ax.text(0.5, 5, 'Multi-Agent\nCoordination', ha='center', va='center', 
        fontsize=10, fontweight='bold', color='purple', rotation=90)
ax.text(0.5, 3, 'Knowledge\nManagement', ha='center', va='center', 
        fontsize=10, fontweight='bold', color='green', rotation=90)

# Save the figure
plt.tight_layout()
plt.savefig('figures/production_architecture.svg', format='svg', dpi=300, bbox_inches='tight')
plt.savefig('figures/production_architecture.pdf', format='pdf', dpi=300, bbox_inches='tight')

print("Production architecture diagram saved as SVG and PDF")
plt.close()
