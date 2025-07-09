#!/usr/bin/env python3
"""
ACGS Documentation Relationship Graph Generator
Constitutional Hash: cdd01ef066bc6cf2

This tool generates interactive visualizations of documentation relationships including:
- Interactive HTML graph visualizations
- Force-directed network layouts
- Hierarchical dependency trees
- Topic clustering analysis
- Cross-reference strength mapping
- Constitutional compliance visualization
- Orphaned document detection
"""

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Import our advanced analyzer
try:
    from advanced_cross_reference_analyzer import (
        CONSTITUTIONAL_HASH,
        DOCS_DIR,
        REPO_ROOT,
        AdvancedCrossReferenceAnalyzer,
    )
except ImportError:
    # Fallback if running standalone
    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
    REPO_ROOT = Path(__file__).parent.parent.parent
    DOCS_DIR = REPO_ROOT / "docs"


class DocumentationRelationshipGraphGenerator:
    """Generates interactive documentation relationship graphs."""

    def __init__(self):
        self.analyzer = None
        self.graph_data = None

    def load_analysis_data(
        self, analysis_file: Optional[Path] = None
    ) -> dict[str, Any]:
        """Load analysis data from file or run fresh analysis."""
        if analysis_file and analysis_file.exists():
            print(f"📊 Loading analysis data from {analysis_file}")
            with open(analysis_file) as f:
                return json.load(f)
        else:
            print("🔍 Running fresh cross-reference analysis...")
            from advanced_cross_reference_analyzer import AdvancedCrossReferenceAnalyzer

            self.analyzer = AdvancedCrossReferenceAnalyzer()
            return self.analyzer.run_comprehensive_analysis(max_workers=4)

    def generate_force_directed_graph(self, analysis_data: dict[str, Any]) -> str:
        """Generate force-directed interactive HTML graph."""
        dependency_graph = analysis_data["dependency_graph"]
        nodes = dependency_graph["nodes"]
        edges = dependency_graph["edges"]

        # Create node categories for coloring
        node_categories = self._categorize_nodes(nodes)

        # Build HTML with D3.js visualization
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ACGS Documentation Relationship Graph</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1e1e1e;
            color: #ffffff;
        }}

        .header {{
            text-align: center;
            margin-bottom: 20px;
        }}

        .controls {{
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}

        .control-group {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}

        label {{
            font-size: 14px;
            color: #cccccc;
        }}

        input, select {{
            padding: 5px;
            border: 1px solid #444;
            border-radius: 4px;
            background: #2a2a2a;
            color: #ffffff;
        }}

        .graph-container {{
            width: 100%;
            height: 80vh;
            border: 1px solid #444;
            border-radius: 8px;
            background: #252525;
            position: relative;
        }}

        .tooltip {{
            position: absolute;
            padding: 10px;
            background: rgba(0, 0, 0, 0.9);
            border: 1px solid #666;
            border-radius: 6px;
            pointer-events: none;
            font-size: 12px;
            max-width: 300px;
            z-index: 1000;
        }}

        .stats {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.8);
            padding: 10px;
            border-radius: 6px;
            font-size: 12px;
            border: 1px solid #444;
        }}

        .legend {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.8);
            padding: 10px;
            border-radius: 6px;
            font-size: 12px;
            border: 1px solid #444;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }}

        .legend-color {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}

        .node {{
            cursor: pointer;
            stroke: #fff;
            stroke-width: 1.5px;
        }}

        .node:hover {{
            stroke-width: 3px;
        }}

        .link {{
            stroke: #999;
            stroke-opacity: 0.6;
        }}

        .link.highlighted {{
            stroke: #ff6b6b;
            stroke-width: 3px;
            stroke-opacity: 1;
        }}

        .node.highlighted {{
            stroke: #ff6b6b;
            stroke-width: 4px;
        }}

        .constitutional-compliant {{
            box-shadow: 0 0 10px #4ecdc4;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔗 ACGS Documentation Relationship Graph</h1>
        <p>Constitutional Hash: <code>{CONSTITUTIONAL_HASH}</code></p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="controls">
        <div class="control-group">
            <label for="nodeSize">Node Size:</label>
            <input type="range" id="nodeSize" min="3" max="15" value="8" />
        </div>
        <div class="control-group">
            <label for="linkDistance">Link Distance:</label>
            <input type="range" id="linkDistance" min="30" max="200" value="80" />
        </div>
        <div class="control-group">
            <label for="chargeStrength">Charge Strength:</label>
            <input type="range" id="chargeStrength" min="-500" max="-50" value="-200" />
        </div>
        <div class="control-group">
            <label for="filterCategory">Filter Category:</label>
            <select id="filterCategory">
                <option value="all">All Documents</option>
                <option value="api">API Documentation</option>
                <option value="architecture">Architecture</option>
                <option value="deployment">Deployment</option>
                <option value="configuration">Configuration</option>
                <option value="security">Security</option>
                <option value="operations">Operations</option>
                <option value="training">Training</option>
                <option value="workflows">Workflows</option>
                <option value="orphaned">Orphaned</option>
                <option value="non_compliant">Non-Compliant</option>
            </select>
        </div>
        <div class="control-group">
            <label for="showLabels">Show Labels:</label>
            <input type="checkbox" id="showLabels" checked />
        </div>
    </div>

    <div class="graph-container">
        <svg id="graph"></svg>
        <div class="tooltip" id="tooltip" style="opacity: 0;"></div>

        <div class="stats" id="stats">
            <div><strong>Graph Statistics</strong></div>
            <div>Total Documents: {len(nodes)}</div>
            <div>Total Links: {len(edges)}</div>
            <div>Connected Components: {dependency_graph['metrics']['connected_components']}</div>
            <div>Orphaned Documents: {dependency_graph['metrics']['orphaned_documents']}</div>
            <div>Avg Degree: {dependency_graph['metrics']['average_degree']:.1f}</div>
        </div>

        <div class="legend" id="legend">
            <div><strong>Document Categories</strong></div>
            <div class="legend-item">
                <div class="legend-color" style="background: #4ecdc4;"></div>
                <span>API Documentation</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #45b7d1;"></div>
                <span>Architecture</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #f39c12;"></div>
                <span>Deployment</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #e74c3c;"></div>
                <span>Security</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #9b59b6;"></div>
                <span>Operations</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #2ecc71;"></div>
                <span>Configuration</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #95a5a6;"></div>
                <span>Other</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #34495e;"></div>
                <span>Orphaned</span>
            </div>
        </div>
    </div>

    <script>
        // Data
        const nodes = {json.dumps(nodes, indent=8)};
        const links = {json.dumps(edges, indent=8)};
        const nodeCategories = {json.dumps(node_categories, indent=8)};

        // Color mapping
        const colorMap = {{
            'api': '#4ecdc4',
            'architecture': '#45b7d1',
            'deployment': '#f39c12',
            'security': '#e74c3c',
            'operations': '#9b59b6',
            'configuration': '#2ecc71',
            'training': '#ffb347',
            'workflows': '#dda0dd',
            'other': '#95a5a6',
            'orphaned': '#34495e'
        }};

        // SVG setup
        const svg = d3.select('#graph');
        const container = d3.select('.graph-container');
        const tooltip = d3.select('#tooltip');

        function updateGraph() {{
            // Clear existing graph
            svg.selectAll('*').remove();

            const containerRect = container.node().getBoundingClientRect();
            const width = containerRect.width - 2;
            const height = containerRect.height - 2;

            svg.attr('width', width).attr('height', height);

            // Filter nodes and links based on category
            const filterCategory = d3.select('#filterCategory').property('value');

            let filteredNodes = nodes;
            let filteredLinks = links;

            if (filterCategory !== 'all') {{
                const nodeIds = new Set();

                if (filterCategory === 'orphaned') {{
                    filteredNodes = nodes.filter(d => d.degree === 0);
                }} else if (filterCategory === 'non_compliant') {{
                    filteredNodes = nodes.filter(d => !d.constitutional_hash);
                }} else {{
                    filteredNodes = nodes.filter(d => nodeCategories[d.id] === filterCategory);
                }}

                filteredNodes.forEach(d => nodeIds.add(d.id));
                filteredLinks = links.filter(d => nodeIds.has(d.source) && nodeIds.has(d.target));
            }}

            // Create a copy of nodes for D3 simulation
            const graphNodes = filteredNodes.map(d => ({{...d}}));
            const graphLinks = filteredLinks.map(d => ({{...d}}));

            // Get control values
            const nodeSize = +d3.select('#nodeSize').property('value');
            const linkDistance = +d3.select('#linkDistance').property('value');
            const chargeStrength = +d3.select('#chargeStrength').property('value');
            const showLabels = d3.select('#showLabels').property('checked');

            // Simulation
            const simulation = d3.forceSimulation(graphNodes)
                .force('link', d3.forceLink(graphLinks).id(d => d.id).distance(linkDistance))
                .force('charge', d3.forceManyBody().strength(chargeStrength))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('collision', d3.forceCollide().radius(nodeSize + 2));

            // Create links
            const link = svg.append('g')
                .attr('class', 'links')
                .selectAll('line')
                .data(graphLinks)
                .enter().append('line')
                .attr('class', 'link')
                .style('stroke-width', d => Math.sqrt(d.confidence * 3))
                .style('stroke', d => {{
                    const typeColors = {{
                        'api': '#4ecdc4',
                        'semantic': '#45b7d1',
                        'config': '#f39c12',
                        'direct': '#95a5a6'
                    }};
                    return typeColors[d.type] || '#999';
                }});

            // Create nodes
            const node = svg.append('g')
                .attr('class', 'nodes')
                .selectAll('circle')
                .data(graphNodes)
                .enter().append('circle')
                .attr('class', 'node')
                .attr('r', d => nodeSize + (d.degree * 0.5))
                .style('fill', d => colorMap[nodeCategories[d.id]] || colorMap['other'])
                .style('stroke', d => d.constitutional_hash ? '#4ecdc4' : '#666')
                .style('stroke-width', d => d.constitutional_hash ? '2px' : '1px')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));

            // Add labels
            let labels;
            if (showLabels) {{
                labels = svg.append('g')
                    .attr('class', 'labels')
                    .selectAll('text')
                    .data(graphNodes)
                    .enter().append('text')
                    .text(d => d.id.split('/').pop().replace('.md', ''))
                    .style('font-size', '10px')
                    .style('fill', '#ffffff')
                    .style('text-anchor', 'middle')
                    .style('pointer-events', 'none')
                    .style('font-weight', d => d.constitutional_hash ? 'bold' : 'normal');
            }}

            // Tooltip interactions
            node.on('mouseover', function(event, d) {{
                d3.select(this).classed('highlighted', true);

                // Highlight connected links
                link.classed('highlighted', l => l.source.id === d.id || l.target.id === d.id);

                // Show tooltip
                const content = `
                    <strong>${{d.title || d.id}}</strong><br/>
                    <em>File:</em> ${{d.id}}<br/>
                    <em>Category:</em> ${{nodeCategories[d.id]}}<br/>
                    <em>Connections:</em> ${{d.degree}}<br/>
                    <em>Topics:</em> ${{d.topics.slice(0, 5).join(', ')}}...<br/>
                    <em>Constitutional Hash:</em> ${{d.constitutional_hash ? '✅' : '❌'}}<br/>
                    <em>API Endpoints:</em> ${{d.api_endpoints.length}}
                `;

                tooltip.html(content)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 10) + 'px')
                    .transition().duration(200)
                    .style('opacity', 1);
            }})
            .on('mouseout', function(event, d) {{
                d3.select(this).classed('highlighted', false);
                link.classed('highlighted', false);

                tooltip.transition().duration(200)
                    .style('opacity', 0);
            }})
            .on('click', function(event, d) {{
                // Open document in new tab (if this were a real web server)
                console.log('Open document:', d.id);
            }});

            // Update positions
            simulation.on('tick', () => {{
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);

                node
                    .attr('cx', d => d.x)
                    .attr('cy', d => d.y);

                if (labels) {{
                    labels
                        .attr('x', d => d.x)
                        .attr('y', d => d.y + 4);
                }}
            }});

            function dragstarted(event, d) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }}

            function dragged(event, d) {{
                d.fx = event.x;
                d.fy = event.y;
            }}

            function dragended(event, d) {{
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }}
        }}

        // Initialize graph
        updateGraph();

        // Event listeners for controls
        d3.selectAll('#nodeSize, #linkDistance, #chargeStrength, #filterCategory, #showLabels')
            .on('input change', updateGraph);

        // Window resize
        window.addEventListener('resize', () => {{
            setTimeout(updateGraph, 100);
        }});
    </script>
</body>
</html>"""

        return html_content

    def _categorize_nodes(self, nodes: list[dict[str, Any]]) -> dict[str, str]:
        """Categorize nodes based on their file paths."""
        categories = {}

        for node in nodes:
            file_path = node["id"].lower()

            if node["degree"] == 0:
                category = "orphaned"
            elif "/api/" in file_path:
                category = "api"
            elif "/architecture/" in file_path:
                category = "architecture"
            elif "/deployment/" in file_path:
                category = "deployment"
            elif "/security/" in file_path:
                category = "security"
            elif "/operations/" in file_path:
                category = "operations"
            elif "/configuration/" in file_path or "config" in file_path:
                category = "configuration"
            elif "/training/" in file_path:
                category = "training"
            elif "/workflows/" in file_path:
                category = "workflows"
            else:
                category = "other"

            categories[node["id"]] = category

        return categories

    def generate_hierarchical_tree(self, analysis_data: dict[str, Any]) -> str:
        """Generate hierarchical tree visualization."""
        dependency_graph = analysis_data["dependency_graph"]

        # Build hierarchy based on directory structure
        hierarchy = self._build_file_hierarchy(dependency_graph["nodes"])

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ACGS Documentation Hierarchy</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1e1e1e;
            color: #ffffff;
        }}

        .header {{
            text-align: center;
            margin-bottom: 20px;
        }}

        .tree-container {{
            width: 100%;
            height: 80vh;
            border: 1px solid #444;
            border-radius: 8px;
            background: #252525;
            overflow: auto;
        }}

        .node {{
            cursor: pointer;
        }}

        .node circle {{
            fill: #fff;
            stroke: steelblue;
            stroke-width: 1.5px;
        }}

        .node.constitutional circle {{
            stroke: #4ecdc4;
            stroke-width: 3px;
        }}

        .node text {{
            font: 12px sans-serif;
            fill: #ffffff;
        }}

        .link {{
            fill: none;
            stroke: #ccc;
            stroke-width: 1.5px;
        }}

        .tooltip {{
            position: absolute;
            padding: 10px;
            background: rgba(0, 0, 0, 0.9);
            border: 1px solid #666;
            border-radius: 6px;
            pointer-events: none;
            font-size: 12px;
            max-width: 300px;
            z-index: 1000;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌳 ACGS Documentation Hierarchy</h1>
        <p>Constitutional Hash: <code>{CONSTITUTIONAL_HASH}</code></p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="tree-container">
        <svg id="tree"></svg>
        <div class="tooltip" id="tooltip" style="opacity: 0;"></div>
    </div>

    <script>
        const treeData = {json.dumps(hierarchy, indent=8)};

        const margin = {{top: 20, right: 120, bottom: 20, left: 120}};
        const width = 1200 - margin.right - margin.left;
        const height = 800 - margin.top - margin.bottom;

        const svg = d3.select('#tree')
            .attr('width', width + margin.right + margin.left)
            .attr('height', height + margin.top + margin.bottom);

        const g = svg.append('g')
            .attr('transform', `translate(${{margin.left}},${{margin.top}})`);

        const tree = d3.tree().size([height, width]);
        const tooltip = d3.select('#tooltip');

        const root = d3.hierarchy(treeData, d => d.children);
        tree(root);

        const link = g.selectAll('.link')
            .data(root.descendants().slice(1))
            .enter().append('path')
            .attr('class', 'link')
            .attr('d', d => {{
                return `M${{d.y}},${{d.x}}C${{(d.y + d.parent.y) / 2}},${{d.x}} ${{(d.y + d.parent.y) / 2}},${{d.parent.x}} ${{d.parent.y}},${{d.parent.x}}`;
            }});

        const node = g.selectAll('.node')
            .data(root.descendants())
            .enter().append('g')
            .attr('class', d => `node ${{d.data.constitutional_hash ? 'constitutional' : ''}}`)
            .attr('transform', d => `translate(${{d.y}},${{d.x}})`);

        node.append('circle')
            .attr('r', 4.5)
            .style('fill', d => {{
                if (d.data.type === 'directory') return '#4ecdc4';
                if (d.data.constitutional_hash) return '#2ecc71';
                return '#95a5a6';
            }});

        node.append('text')
            .attr('dy', '.35em')
            .attr('x', d => d.children || d._children ? -13 : 13)
            .style('text-anchor', d => d.children || d._children ? 'end' : 'start')
            .text(d => d.data.name);

        node.on('mouseover', function(event, d) {{
            if (d.data.type === 'file') {{
                const content = `
                    <strong>${{d.data.name}}</strong><br/>
                    <em>Path:</em> ${{d.data.path}}<br/>
                    <em>Degree:</em> ${{d.data.degree || 0}}<br/>
                    <em>Constitutional Hash:</em> ${{d.data.constitutional_hash ? '✅' : '❌'}}<br/>
                    <em>Topics:</em> ${{(d.data.topics || []).slice(0, 3).join(', ')}}
                `;

                tooltip.html(content)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 10) + 'px')
                    .transition().duration(200)
                    .style('opacity', 1);
            }}
        }})
        .on('mouseout', function() {{
            tooltip.transition().duration(200)
                .style('opacity', 0);
        }});
    </script>
</body>
</html>"""

        return html_content

    def _build_file_hierarchy(self, nodes: list[dict[str, Any]]) -> dict[str, Any]:
        """Build hierarchical structure from file paths."""
        root = {"name": "docs", "type": "directory", "children": []}

        for node in nodes:
            parts = node["id"].split("/")
            current = root

            # Navigate/create directory structure
            for i, part in enumerate(parts[:-1]):  # Exclude filename
                found = False
                for child in current.get("children", []):
                    if child["name"] == part and child["type"] == "directory":
                        current = child
                        found = True
                        break

                if not found:
                    new_dir = {"name": part, "type": "directory", "children": []}
                    current.setdefault("children", []).append(new_dir)
                    current = new_dir

            # Add file
            filename = parts[-1]
            file_node = {
                "name": filename,
                "type": "file",
                "path": node["id"],
                "degree": node["degree"],
                "constitutional_hash": node["constitutional_hash"],
                "topics": node["topics"],
            }
            current.setdefault("children", []).append(file_node)

        return root

    def generate_topic_clusters(self, analysis_data: dict[str, Any]) -> str:
        """Generate topic clustering visualization."""
        # Analyze topic clusters
        topic_clusters = self._analyze_topic_clusters(analysis_data)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ACGS Documentation Topic Clusters</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1e1e1e;
            color: #ffffff;
        }}

        .header {{
            text-align: center;
            margin-bottom: 20px;
        }}

        .cluster-container {{
            width: 100%;
            height: 80vh;
            border: 1px solid #444;
            border-radius: 8px;
            background: #252525;
        }}

        .cluster {{
            stroke: #fff;
            stroke-width: 1px;
            fill-opacity: 0.3;
        }}

        .node {{
            stroke: #fff;
            stroke-width: 1px;
            cursor: pointer;
        }}

        .tooltip {{
            position: absolute;
            padding: 10px;
            background: rgba(0, 0, 0, 0.9);
            border: 1px solid #666;
            border-radius: 6px;
            pointer-events: none;
            font-size: 12px;
            max-width: 300px;
            z-index: 1000;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 ACGS Documentation Topic Clusters</h1>
        <p>Constitutional Hash: <code>{CONSTITUTIONAL_HASH}</code></p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="cluster-container">
        <svg id="clusters"></svg>
        <div class="tooltip" id="tooltip" style="opacity: 0;"></div>
    </div>

    <script>
        const clusterData = {json.dumps(topic_clusters, indent=8)};

        const width = 1200;
        const height = 800;

        const svg = d3.select('#clusters')
            .attr('width', width)
            .attr('height', height);

        const tooltip = d3.select('#tooltip');

        // Color scale for clusters
        const color = d3.scaleOrdinal(d3.schemeCategory10);

        // Pack layout for clusters
        const pack = d3.pack()
            .size([width - 4, height - 4])
            .padding(3);

        const root = d3.hierarchy({{children: clusterData}})
            .sum(d => d.documents ? d.documents.length : 1)
            .sort((a, b) => b.value - a.value);

        pack(root);

        const leaf = svg.selectAll('.cluster')
            .data(root.leaves())
            .enter().append('g')
            .attr('class', 'cluster')
            .attr('transform', d => `translate(${{d.x}},${{d.y}})`);

        leaf.append('circle')
            .attr('r', d => d.r)
            .style('fill', (d, i) => color(i))
            .style('fill-opacity', 0.3)
            .style('stroke', '#fff')
            .style('stroke-width', 2);

        leaf.append('text')
            .attr('text-anchor', 'middle')
            .attr('dy', '0.3em')
            .style('font-size', d => Math.min(d.r / 3, 12) + 'px')
            .style('fill', '#ffffff')
            .style('font-weight', 'bold')
            .text(d => d.data.topic);

        // Add document nodes within clusters
        leaf.each(function(d) {{
            const g = d3.select(this);
            const clusterRadius = d.r;
            const documents = d.data.documents || [];

            if (documents.length > 1) {{
                const docRadius = Math.min(clusterRadius / 4, 8);
                const angleStep = (2 * Math.PI) / documents.length;
                const ringRadius = clusterRadius * 0.6;

                documents.forEach((doc, i) => {{
                    const angle = i * angleStep;
                    const x = Math.cos(angle) * ringRadius;
                    const y = Math.sin(angle) * ringRadius;

                    g.append('circle')
                        .attr('class', 'node')
                        .attr('cx', x)
                        .attr('cy', y)
                        .attr('r', docRadius)
                        .style('fill', doc.constitutional_hash ? '#4ecdc4' : '#95a5a6')
                        .on('mouseover', function(event) {{
                            const content = `
                                <strong>${{doc.title || doc.id}}</strong><br/>
                                <em>File:</em> ${{doc.id}}<br/>
                                <em>Topic:</em> ${{d.data.topic}}<br/>
                                <em>Constitutional Hash:</em> ${{doc.constitutional_hash ? '✅' : '❌'}}
                            `;

                            tooltip.html(content)
                                .style('left', (event.pageX + 10) + 'px')
                                .style('top', (event.pageY - 10) + 'px')
                                .transition().duration(200)
                                .style('opacity', 1);
                        }})
                        .on('mouseout', function() {{
                            tooltip.transition().duration(200)
                                .style('opacity', 0);
                        }});
                }});
            }}
        }});

        // Cluster hover effects
        leaf.on('mouseover', function(event, d) {{
            if (!event.target.classList.contains('node')) {{
                const content = `
                    <strong>Topic: ${{d.data.topic}}</strong><br/>
                    <em>Documents:</em> ${{d.data.documents.length}}<br/>
                    <em>Strength:</em> ${{d.data.strength.toFixed(2)}}<br/>
                    <em>Files:</em><br/>
                    ${{d.data.documents.slice(0, 5).map(doc => `• ${{doc.id.split('/').pop()}}`).join('<br/>')}}
                    ${{d.data.documents.length > 5 ? '<br/>...' : ''}}
                `;

                tooltip.html(content)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 10) + 'px')
                    .transition().duration(200)
                    .style('opacity', 1);
            }}
        }})
        .on('mouseout', function(event) {{
            if (!event.target.classList.contains('node')) {{
                tooltip.transition().duration(200)
                    .style('opacity', 0);
            }}
        }});
    </script>
</body>
</html>"""

        return html_content

    def _analyze_topic_clusters(
        self, analysis_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Analyze and cluster documents by topics."""
        nodes = analysis_data["dependency_graph"]["nodes"]

        # Build topic to documents mapping
        topic_docs = defaultdict(list)

        for node in nodes:
            for topic in node["topics"]:
                if len(topic) > 3:  # Filter out short/common words
                    topic_docs[topic].append(node)

        # Create clusters for topics with multiple documents
        clusters = []
        for topic, docs in topic_docs.items():
            if len(docs) >= 2:  # At least 2 documents share this topic
                cluster = {
                    "topic": topic,
                    "documents": docs,
                    "strength": len(docs) / len(nodes),  # Relative strength
                    "constitutional_compliance": sum(
                        1 for doc in docs if doc["constitutional_hash"]
                    )
                    / len(docs),
                }
                clusters.append(cluster)

        # Sort by strength and return top clusters
        clusters.sort(key=lambda x: x["strength"], reverse=True)
        return clusters[:20]  # Top 20 clusters

    def generate_compliance_heatmap(self, analysis_data: dict[str, Any]) -> str:
        """Generate constitutional compliance heatmap."""
        nodes = analysis_data["dependency_graph"]["nodes"]

        # Build directory compliance stats
        dir_stats = self._calculate_directory_compliance(nodes)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ACGS Constitutional Compliance Heatmap</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1e1e1e;
            color: #ffffff;
        }}

        .header {{
            text-align: center;
            margin-bottom: 20px;
        }}

        .heatmap-container {{
            width: 100%;
            height: 80vh;
            border: 1px solid #444;
            border-radius: 8px;
            background: #252525;
            padding: 20px;
        }}

        .cell {{
            stroke: #333;
            stroke-width: 1px;
            cursor: pointer;
        }}

        .cell:hover {{
            stroke: #fff;
            stroke-width: 2px;
        }}

        .tooltip {{
            position: absolute;
            padding: 10px;
            background: rgba(0, 0, 0, 0.9);
            border: 1px solid #666;
            border-radius: 6px;
            pointer-events: none;
            font-size: 12px;
            max-width: 300px;
            z-index: 1000;
        }}

        .legend {{
            margin-top: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}

        .legend-scale {{
            display: flex;
            border: 1px solid #666;
        }}

        .legend-cell {{
            width: 20px;
            height: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 ACGS Constitutional Compliance Heatmap</h1>
        <p>Constitutional Hash: <code>{CONSTITUTIONAL_HASH}</code></p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="heatmap-container">
        <svg id="heatmap"></svg>
        <div class="tooltip" id="tooltip" style="opacity: 0;"></div>

        <div class="legend">
            <span>Compliance Rate:</span>
            <div class="legend-scale" id="legend-scale"></div>
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
        </div>
    </div>

    <script>
        const dirStats = {json.dumps(dir_stats, indent=8)};

        const margin = {{top: 50, right: 50, bottom: 100, left: 150}};
        const cellSize = 30;
        const width = Object.keys(dirStats).length * cellSize + margin.left + margin.right;
        const height = 400 + margin.top + margin.bottom;

        const svg = d3.select('#heatmap')
            .attr('width', width)
            .attr('height', height);

        const g = svg.append('g')
            .attr('transform', `translate(${{margin.left}},${{margin.top}})`);

        const tooltip = d3.select('#tooltip');

        // Color scale
        const colorScale = d3.scaleSequential(d3.interpolateRdYlGn)
            .domain([0, 1]);

        // Create legend
        const legendScale = d3.select('#legend-scale');
        for (let i = 0; i <= 10; i++) {{
            legendScale.append('div')
                .attr('class', 'legend-cell')
                .style('background-color', colorScale(i / 10));
        }}

        // Directory names
        const directories = Object.keys(dirStats);

        // X scale
        const xScale = d3.scaleBand()
            .domain(directories)
            .range([0, directories.length * cellSize])
            .padding(0.1);

        // Y positions for different metrics
        const metrics = ['compliance_rate', 'total_docs', 'compliant_docs'];
        const metricLabels = {{
            'compliance_rate': 'Compliance Rate',
            'total_docs': 'Total Documents',
            'compliant_docs': 'Compliant Documents'
        }};

        // Create cells
        directories.forEach((dir, i) => {{
            const x = i * cellSize;

            // Compliance rate cell
            g.append('rect')
                .attr('class', 'cell')
                .attr('x', x)
                .attr('y', 0)
                .attr('width', cellSize - 1)
                .attr('height', cellSize - 1)
                .style('fill', colorScale(dirStats[dir].compliance_rate))
                .on('mouseover', function(event) {{
                    const content = `
                        <strong>${{dir}}</strong><br/>
                        <em>Compliance Rate:</em> ${{(dirStats[dir].compliance_rate * 100).toFixed(1)}}%<br/>
                        <em>Compliant Docs:</em> ${{dirStats[dir].compliant_docs}}/${{dirStats[dir].total_docs}}<br/>
                        <em>Non-Compliant Files:</em><br/>
                        ${{dirStats[dir].non_compliant_files.slice(0, 5).map(f => `• ${{f}}`).join('<br/>')}}
                        ${{dirStats[dir].non_compliant_files.length > 5 ? '<br/>...' : ''}}
                    `;

                    tooltip.html(content)
                        .style('left', (event.pageX + 10) + 'px')
                        .style('top', (event.pageY - 10) + 'px')
                        .transition().duration(200)
                        .style('opacity', 1);
                }})
                .on('mouseout', function() {{
                    tooltip.transition().duration(200)
                        .style('opacity', 0);
                }});
        }});

        // Add directory labels
        g.selectAll('.dir-label')
            .data(directories)
            .enter().append('text')
            .attr('class', 'dir-label')
            .attr('x', (d, i) => i * cellSize + cellSize / 2)
            .attr('y', cellSize + 15)
            .attr('text-anchor', 'middle')
            .style('font-size', '10px')
            .style('fill', '#ffffff')
            .text(d => d)
            .attr('transform', (d, i) => `rotate(-45, ${{i * cellSize + cellSize / 2}}, ${{cellSize + 15}})`);

        // Add title
        g.append('text')
            .attr('x', (directories.length * cellSize) / 2)
            .attr('y', -20)
            .attr('text-anchor', 'middle')
            .style('font-size', '16px')
            .style('font-weight', 'bold')
            .style('fill', '#ffffff')
            .text('Constitutional Compliance by Directory');
    </script>
</body>
</html>"""

        return html_content

    def _calculate_directory_compliance(
        self, nodes: list[dict[str, Any]]
    ) -> dict[str, dict[str, Any]]:
        """Calculate constitutional compliance statistics by directory."""
        dir_stats = defaultdict(
            lambda: {
                "total_docs": 0,
                "compliant_docs": 0,
                "compliance_rate": 0.0,
                "non_compliant_files": [],
            }
        )

        for node in nodes:
            # Get directory from file path
            path_parts = node["id"].split("/")
            if len(path_parts) > 1:
                directory = path_parts[1] if path_parts[0] == "docs" else path_parts[0]
            else:
                directory = "root"

            dir_stats[directory]["total_docs"] += 1

            if node["constitutional_hash"]:
                dir_stats[directory]["compliant_docs"] += 1
            else:
                dir_stats[directory]["non_compliant_files"].append(
                    node["id"].split("/")[-1]
                )

        # Calculate compliance rates
        for directory, stats in dir_stats.items():
            if stats["total_docs"] > 0:
                stats["compliance_rate"] = stats["compliant_docs"] / stats["total_docs"]

        return dict(dir_stats)

    def generate_all_visualizations(self, output_dir: Path) -> dict[str, Path]:
        """Generate all visualization types."""
        print("🎨 ACGS Documentation Relationship Graph Generator")
        print("=" * 60)
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"Output Directory: {output_dir}")
        print()

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load analysis data
        analysis_data = self.load_analysis_data()

        generated_files = {}

        # Generate force-directed graph
        print("🔗 Generating force-directed relationship graph...")
        force_graph_html = self.generate_force_directed_graph(analysis_data)
        force_graph_file = output_dir / "force_directed_graph.html"
        with open(force_graph_file, "w") as f:
            f.write(force_graph_html)
        generated_files["force_directed"] = force_graph_file
        print(f"✅ Generated: {force_graph_file}")

        # Generate hierarchical tree
        print("🌳 Generating hierarchical tree...")
        tree_html = self.generate_hierarchical_tree(analysis_data)
        tree_file = output_dir / "hierarchical_tree.html"
        with open(tree_file, "w") as f:
            f.write(tree_html)
        generated_files["hierarchical"] = tree_file
        print(f"✅ Generated: {tree_file}")

        # Generate topic clusters
        print("🔍 Generating topic clusters...")
        clusters_html = self.generate_topic_clusters(analysis_data)
        clusters_file = output_dir / "topic_clusters.html"
        with open(clusters_file, "w") as f:
            f.write(clusters_html)
        generated_files["clusters"] = clusters_file
        print(f"✅ Generated: {clusters_file}")

        # Generate compliance heatmap
        print("📊 Generating compliance heatmap...")
        heatmap_html = self.generate_compliance_heatmap(analysis_data)
        heatmap_file = output_dir / "compliance_heatmap.html"
        with open(heatmap_file, "w") as f:
            f.write(heatmap_html)
        generated_files["heatmap"] = heatmap_file
        print(f"✅ Generated: {heatmap_file}")

        # Generate summary index
        print("📋 Generating visualization index...")
        index_html = self._generate_index(generated_files, analysis_data)
        index_file = output_dir / "index.html"
        with open(index_file, "w") as f:
            f.write(index_html)
        generated_files["index"] = index_file
        print(f"✅ Generated: {index_file}")

        print()
        print("=" * 60)
        print("🎉 All visualizations generated successfully!")
        print(f"📁 Open {index_file} in your browser to view all visualizations")
        print(f"🔗 Constitutional Hash: {CONSTITUTIONAL_HASH}")

        return generated_files

    def _generate_index(
        self, generated_files: dict[str, Path], analysis_data: dict[str, Any]
    ) -> str:
        """Generate index page linking to all visualizations."""
        summary = analysis_data["summary"]

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ACGS Documentation Relationship Visualizations</title>
    <style>
        body {{
            margin: 0;
            padding: 40px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1e1e1e;
            color: #ffffff;
            line-height: 1.6;
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .stat-card {{
            background: #2a2a2a;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #444;
            text-align: center;
        }}

        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #4ecdc4;
        }}

        .stat-label {{
            color: #cccccc;
            margin-top: 5px;
        }}

        .visualizations {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}

        .viz-card {{
            background: #2a2a2a;
            border-radius: 8px;
            border: 1px solid #444;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .viz-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(78, 205, 196, 0.3);
        }}

        .viz-image {{
            width: 100%;
            height: 200px;
            background: #333;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3em;
            color: #666;
        }}

        .viz-content {{
            padding: 20px;
        }}

        .viz-title {{
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #4ecdc4;
        }}

        .viz-description {{
            color: #cccccc;
            margin-bottom: 15px;
        }}

        .viz-button {{
            display: inline-block;
            background: #4ecdc4;
            color: #1e1e1e;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: background 0.2s;
        }}

        .viz-button:hover {{
            background: #45b7d1;
        }}

        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #444;
            color: #888;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔗 ACGS Documentation Relationship Visualizations</h1>
        <p>Constitutional Hash: <code>{CONSTITUTIONAL_HASH}</code></p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{summary['total_documents']}</div>
            <div class="stat-label">Total Documents</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{summary['total_cross_references']}</div>
            <div class="stat-label">Cross-References</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{summary['semantic_relationships']}</div>
            <div class="stat-label">Semantic Relationships</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{summary['total_issues']}</div>
            <div class="stat-label">Total Issues</div>
        </div>
    </div>

    <div class="visualizations">
        <div class="viz-card">
            <div class="viz-image">🔗</div>
            <div class="viz-content">
                <div class="viz-title">Force-Directed Network</div>
                <div class="viz-description">
                    Interactive network graph showing document relationships with force-directed layout.
                    Explore connections, filter by categories, and discover relationship patterns.
                </div>
                <a href="force_directed_graph.html" class="viz-button">View Network</a>
            </div>
        </div>

        <div class="viz-card">
            <div class="viz-image">🌳</div>
            <div class="viz-content">
                <div class="viz-title">Hierarchical Tree</div>
                <div class="viz-description">
                    Tree visualization showing the hierarchical structure of documentation
                    organized by directory structure and constitutional compliance.
                </div>
                <a href="hierarchical_tree.html" class="viz-button">View Tree</a>
            </div>
        </div>

        <div class="viz-card">
            <div class="viz-image">🔍</div>
            <div class="viz-content">
                <div class="viz-title">Topic Clusters</div>
                <div class="viz-description">
                    Clustering visualization showing documents grouped by shared topics and themes.
                    Discover content relationships and identify documentation gaps.
                </div>
                <a href="topic_clusters.html" class="viz-button">View Clusters</a>
            </div>
        </div>

        <div class="viz-card">
            <div class="viz-image">📊</div>
            <div class="viz-content">
                <div class="viz-title">Compliance Heatmap</div>
                <div class="viz-description">
                    Heatmap showing constitutional compliance rates across different documentation
                    directories. Identify areas needing compliance attention.
                </div>
                <a href="compliance_heatmap.html" class="viz-button">View Heatmap</a>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>Generated by ACGS Documentation Relationship Graph Generator</p>
        <p>Constitutional Hash: <code>{CONSTITUTIONAL_HASH}</code> ✅</p>
    </div>
</body>
</html>"""


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="ACGS Documentation Relationship Graph Generator"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "visualization_output",
        help="Output directory for visualizations",
    )
    parser.add_argument("--analysis", type=Path, help="Path to analysis JSON file")

    args = parser.parse_args()

    generator = DocumentationRelationshipGraphGenerator()
    generated_files = generator.generate_all_visualizations(args.output)

    print(f"\n📁 All visualizations saved to: {args.output}")
    print(f"🌐 Open {generated_files['index']} in your browser to explore!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
