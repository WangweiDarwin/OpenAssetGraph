import React, { useEffect, useRef, useState } from 'react';
import G6, { Graph, Node, Edge } from '@antv/g6';
import { Spin } from 'antd';

interface TopologyNode {
  id: string;
  label: string;
  type: string;
  properties?: Record<string, any>;
}

interface TopologyEdge {
  source: string;
  target: string;
  type: string;
  properties?: Record<string, any>;
}

interface TopologyGraphProps {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  onNodeClick?: (node: TopologyNode) => void;
  onNodeDoubleClick?: (node: TopologyNode) => void;
}

const nodeTypeColors: Record<string, string> = {
  Database: '#10b981',
  Service: '#3b82f6',
  API: '#8b5cf6',
  FrontendApp: '#f59e0b',
  Table: '#6b7280',
  Library: '#ec4899',
  Component: '#06b6d4',
};

const TopologyGraph: React.FC<TopologyGraphProps> = ({
  nodes,
  edges,
  onNodeClick,
  onNodeDoubleClick,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const graphRef = useRef<Graph | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!containerRef.current || nodes.length === 0) return;

    const width = containerRef.current.offsetWidth;
    const height = containerRef.current.offsetHeight;

    if (graphRef.current) {
      graphRef.current.destroy();
    }

    const graph = new G6.Graph({
      container: containerRef.current,
      width,
      height,
      modes: {
        default: ['drag-canvas', 'zoom-canvas', 'drag-node'],
      },
      layout: {
        type: 'force',
        preventOverlap: true,
        nodeSize: 80,
        linkDistance: 180,
        nodeStrength: -400,
        edgeStrength: 0.1,
        gravity: 80,
      },
      defaultNode: {
        type: 'rect',
        size: [120, 50],
        style: {
          fill: '#ffffff',
          stroke: '#e2e8f0',
          lineWidth: 2,
          radius: 8,
        },
        labelCfg: {
          style: {
            fill: '#1e293b',
            fontSize: 12,
            fontWeight: 500,
          },
          position: 'center',
        },
      },
      defaultEdge: {
        type: 'quadratic',
        style: {
          stroke: '#cbd5e1',
          lineWidth: 1.5,
          endArrow: {
            path: G6.Arrow.triangle(6, 8, 0),
            fill: '#94a3b8',
          },
        },
      },
      nodeStateStyles: {
        hover: {
          fill: '#f0f7ff',
          stroke: '#0066cc',
          lineWidth: 2,
          shadowColor: 'rgba(0, 102, 204, 0.15)',
          shadowBlur: 10,
        },
        selected: {
          fill: '#f0f7ff',
          stroke: '#0066cc',
          lineWidth: 2,
          shadowColor: 'rgba(0, 102, 204, 0.25)',
          shadowBlur: 15,
        },
      },
      edgeStateStyles: {
        hover: {
          stroke: '#0066cc',
          lineWidth: 2,
        },
      },
    });

    const g6Nodes = nodes.map((node) => {
      const label = node.label.length > 14 ? node.label.substring(0, 14) + '...' : node.label;
      return {
        id: node.id,
        label: label,
        type: 'rect',
        size: [Math.max(100, label.length * 9 + 20), 36],
        style: {
          fill: '#ffffff',
          stroke: nodeTypeColors[node.type] || '#6b7280',
          lineWidth: 2,
          radius: 6,
          shadowColor: 'rgba(0, 0, 0, 0.08)',
          shadowBlur: 4,
          shadowOffsetX: 0,
          shadowOffsetY: 2,
        },
        labelCfg: {
          style: {
            fill: '#1e293b',
            fontSize: 12,
            fontWeight: 500,
          },
          position: 'center',
        },
        nodeData: node,
      };
    });

    const g6Edges = edges.map((edge, index) => ({
      id: `edge-${index}`,
      source: edge.source,
      target: edge.target,
      type: 'quadratic',
      style: {
        stroke: '#cbd5e1',
        lineWidth: 1.5,
        endArrow: {
          path: G6.Arrow.triangle(5, 6, 0),
          fill: '#94a3b8',
        },
      },
      label: edge.type,
      labelCfg: {
        style: {
          fill: '#64748b',
          fontSize: 10,
          background: {
            fill: '#ffffff',
            padding: [2, 4, 2, 4],
            radius: 4,
          },
        },
        refY: 8,
      },
      edgeData: edge,
    }));

    graph.data({
      nodes: g6Nodes,
      edges: g6Edges,
    });

    graph.on('node:mouseenter', (e) => {
      graph.setItemState(e.item as Node, 'hover', true);
    });

    graph.on('node:mouseleave', (e) => {
      graph.setItemState(e.item as Node, 'hover', false);
    });

    graph.on('node:click', (e) => {
      const model = e.item?.getModel();
      if (model && onNodeClick) {
        onNodeClick((model as any).nodeData);
      }
      graph.getNodes().forEach((node) => {
        graph.setItemState(node, 'selected', false);
      });
      graph.setItemState(e.item as Node, 'selected', true);
    });

    graph.on('node:dblclick', (e) => {
      const model = e.item?.getModel();
      if (model && onNodeDoubleClick) {
        onNodeDoubleClick((model as any).nodeData);
      }
    });

    graph.on('edge:mouseenter', (e) => {
      graph.setItemState(e.item as Edge, 'hover', true);
    });

    graph.on('edge:mouseleave', (e) => {
      graph.setItemState(e.item as Edge, 'hover', false);
    });

    graph.render();
    graphRef.current = graph;
    setLoading(false);

    setTimeout(() => {
      if (graphRef.current) {
        graphRef.current.fitView(20);
      }
    }, 100);

    const handleResize = () => {
      if (containerRef.current && graphRef.current) {
        graphRef.current.changeSize(
          containerRef.current.offsetWidth,
          containerRef.current.offsetHeight
        );
        graphRef.current.fitCenter();
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (graphRef.current) {
        graphRef.current.destroy();
      }
    };
  }, [nodes, edges, onNodeClick, onNodeDoubleClick]);

  if (nodes.length === 0) {
    return (
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        height: '100%',
        color: 'var(--text-secondary)'
      }}>
        <p>No topology data available</p>
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      {loading && (
        <div style={{ 
          position: 'absolute', 
          top: '50%', 
          left: '50%', 
          transform: 'translate(-50%, -50%)' 
        }}>
          <Spin />
        </div>
      )}
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
    </div>
  );
};

export default TopologyGraph;
