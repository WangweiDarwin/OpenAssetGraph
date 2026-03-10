import React, { useEffect, useRef, useState } from 'react';
import G6, { Graph, TreeGraph } from '@antv/g6';

interface TopologyNode {
  id: string;
  label: string;
  type: string;
  properties?: Record<string, any>;
  x?: number;
  y?: number;
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
  width?: number;
  height?: number;
}

const TopologyGraph: React.FC<TopologyGraphProps> = ({
  nodes,
  edges,
  onNodeClick,
  onNodeDoubleClick,
  width = 800,
  height = 600,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const graphRef = useRef<Graph | null>(null);
  const [selectedNode, setSelectedNode] = useState<TopologyNode | null>(null);

  const getNodeColor = (type: string): string => {
    const colorMap: Record<string, string> = {
      Database: '#1890ff',
      Table: '#52c41a',
      Column: '#faad14',
      Service: '#722ed1',
      API: '#eb2f96',
      FrontendApp: '#13c2c2',
      Component: '#fa8c16',
    };
    return colorMap[type] || '#8c8c8c';
  };

  const getNodeIcon = (type: string): string => {
    const iconMap: Record<string, string> = {
      Database: '🗄️',
      Table: '📊',
      Column: '📝',
      Service: '⚙️',
      API: '🔌',
      FrontendApp: '🖥️',
      Component: '🧩',
    };
    return iconMap[type] || '📦';
  };

  useEffect(() => {
    if (!containerRef.current) return;

    const graph = new G6.Graph({
      container: containerRef.current,
      width,
      height,
      modes: {
        default: [
          'drag-canvas',
          'zoom-canvas',
          'drag-node',
          {
            type: 'tooltip',
            formatText: (model: any) => {
              return `${model.label}\nType: ${model.type}`;
            },
            offset: 10,
          },
        ],
      },
      layout: {
        type: 'force',
        preventOverlap: true,
        linkDistance: 150,
        nodeStrength: -50,
        edgeStrength: 0.1,
        nodeSize: 60,
      },
      defaultNode: {
        size: [60, 60],
        style: {
          fill: '#C6E5FF',
          stroke: '#5B8FF9',
          lineWidth: 2,
        },
        labelCfg: {
          style: {
            fill: '#000000',
            fontSize: 12,
          },
          position: 'bottom',
        },
      },
      defaultEdge: {
        style: {
          stroke: '#b5b5b5',
          lineWidth: 2,
          endArrow: {
            path: G6.Arrow.triangle(8, 10, 0),
            fill: '#b5b5b5',
          },
        },
      },
      nodeStateStyles: {
        selected: {
          stroke: '#f00',
          lineWidth: 3,
        },
        hover: {
          fill: '#f0f0f0',
        },
      },
      edgeStateStyles: {
        hover: {
          stroke: '#1890ff',
          lineWidth: 3,
        },
      },
    });

    graphRef.current = graph;

    graph.on('node:click', (evt: any) => {
      const { item } = evt;
      const model = item.getModel();
      
      if (selectedNode) {
        graph.setItemState(selectedNode.id, 'selected', false);
      }
      
      graph.setItemState(item, 'selected', true);
      setSelectedNode(model);
      
      if (onNodeClick) {
        onNodeClick(model);
      }
    });

    graph.on('node:dblclick', (evt: any) => {
      const { item } = evt;
      const model = item.getModel();
      
      if (onNodeDoubleClick) {
        onNodeDoubleClick(model);
      }
    });

    graph.on('node:mouseenter', (evt: any) => {
      const { item } = evt;
      graph.setItemState(item, 'hover', true);
    });

    graph.on('node:mouseleave', (evt: any) => {
      const { item } = evt;
      graph.setItemState(item, 'hover', false);
    });

    graph.on('edge:mouseenter', (evt: any) => {
      const { item } = evt;
      graph.setItemState(item, 'hover', true);
    });

    graph.on('edge:mouseleave', (evt: any) => {
      const { item } = evt;
      graph.setItemState(item, 'hover', false);
    });

    return () => {
      if (graph) {
        graph.destroy();
      }
    };
  }, [width, height, onNodeClick, onNodeDoubleClick, selectedNode]);

  useEffect(() => {
    if (!graphRef.current || !nodes.length) return;

    const graph = graphRef.current;

    const g6Nodes = nodes.map((node) => ({
      id: node.id,
      label: node.label,
      type: 'circle',
      style: {
        fill: getNodeColor(node.type),
        stroke: getNodeColor(node.type),
        lineWidth: 2,
      },
      labelCfg: {
        style: {
          fill: '#000000',
          fontSize: 12,
          fontWeight: 'bold',
        },
        position: 'bottom',
        offset: 10,
      },
      ...node,
    }));

    const g6Edges = edges.map((edge, index) => ({
      id: `edge-${index}`,
      source: edge.source,
      target: edge.target,
      label: edge.type,
      style: {
        stroke: '#b5b5b5',
        lineWidth: 2,
        endArrow: {
          path: G6.Arrow.triangle(8, 10, 0),
          fill: '#b5b5b5',
        },
      },
      labelCfg: {
        style: {
          fill: '#666666',
          fontSize: 10,
        },
        refY: 5,
      },
    }));

    graph.changeData({
      nodes: g6Nodes,
      edges: g6Edges,
    });

    graph.layout();
  }, [nodes, edges]);

  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        height: '100%',
        border: '1px solid #d9d9d9',
        borderRadius: '4px',
        overflow: 'hidden',
      }}
    />
  );
};

export default TopologyGraph;
