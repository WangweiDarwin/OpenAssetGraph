const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export interface TopologyNode {
  id: string;
  label: string;
  type: string;
  properties?: Record<string, any>;
  x?: number;
  y?: number;
}

export interface TopologyEdge {
  source: string;
  target: string;
  type: string;
  properties?: Record<string, any>;
}

export interface TopologyData {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  node_count: number;
  edge_count: number;
}

export interface SearchResult {
  id: string;
  label: string;
  type: string;
  properties?: Record<string, any>;
  score?: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  count: number;
}

export interface NodeRelationship {
  id: string;
  type: string;
  source: string;
  target: string;
  properties?: Record<string, any>;
}

export interface PathResponse {
  start_node_id: string;
  end_node_id: string;
  path: string[];
  path_length: number;
}

export interface TopologyStats {
  total_nodes: number;
  total_edges: number;
  node_types: Record<string, number>;
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ApiError(response.status, errorData.detail || 'Request failed');
  }

  return response.json();
}

export const topologyApi = {
  async getTopology(nodeTypes?: string[], limit: number = 100): Promise<TopologyData> {
    const params = new URLSearchParams();
    params.set('limit', limit.toString());
    
    if (nodeTypes && nodeTypes.length > 0) {
      params.set('node_types', nodeTypes.join(','));
    }
    
    return fetchApi<TopologyData>(`/api/topology?${params.toString()}`);
  },

  async searchNodes(query: string, nodeTypes?: string[], limit: number = 50): Promise<SearchResponse> {
    const params = new URLSearchParams();
    params.set('q', query);
    params.set('limit', limit.toString());
    
    if (nodeTypes && nodeTypes.length > 0) {
      params.set('node_types', nodeTypes.join(','));
    }
    
    return fetchApi<SearchResponse>(`/api/topology/search?${params.toString()}`);
  },

  async getNode(nodeId: string): Promise<TopologyNode> {
    return fetchApi<TopologyNode>(`/api/topology/nodes/${encodeURIComponent(nodeId)}`);
  },

  async findPath(startNodeId: string, endNodeId: string, maxDepth: number = 5): Promise<PathResponse> {
    const params = new URLSearchParams();
    params.set('start', startNodeId);
    params.set('end', endNodeId);
    params.set('max_depth', maxDepth.toString());
    
    return fetchApi<PathResponse>(`/api/topology/path?${params.toString()}`);
  },

  async getNodeRelationships(
    nodeId: string, 
    relationshipType?: string, 
    direction: 'both' | 'incoming' | 'outgoing' = 'both'
  ): Promise<{ node_id: string; relationships: NodeRelationship[]; count: number }> {
    const params = new URLSearchParams();
    params.set('direction', direction);
    
    if (relationshipType) {
      params.set('relationship_type', relationshipType);
    }
    
    return fetchApi(`/api/topology/nodes/${encodeURIComponent(nodeId)}/relationships?${params.toString()}`);
  },

  async getStats(): Promise<TopologyStats> {
    return fetchApi<TopologyStats>('/api/topology/stats');
  },
};

export const scanApi = {
  async scanDatabase(config: {
    host: string;
    port: number;
    database: string;
    user: string;
    password: string;
    schema?: string;
  }): Promise<{ task_id: string; status: string }> {
    return fetchApi('/api/scan/database', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  },

  async scanCode(path: string): Promise<{ task_id: string; status: string }> {
    return fetchApi('/api/scan/code', {
      method: 'POST',
      body: JSON.stringify({ path }),
    });
  },

  async getScanStatus(taskId: string): Promise<{
    task_id: string;
    status: string;
    progress?: number;
    result?: any;
    error?: string;
  }> {
    return fetchApi(`/api/scan/status/${taskId}`);
  },

  async getScanHistory(): Promise<Array<{
    task_id: string;
    type: string;
    status: string;
    created_at: string;
  }>> {
    return fetchApi('/api/scan/history');
  },
};

export { ApiError };
