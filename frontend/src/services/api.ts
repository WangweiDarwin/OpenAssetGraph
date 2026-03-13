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

export interface ScanResult {
  status: string;
  nodes_added: number;
  edges_added: number;
  message: string;
  project_id?: string;
}

export interface ChatMessage {
  role: string;
  content: string;
}

export interface ChatResponse {
  response: string;
  model: string;
  usage: Record<string, any>;
  context_summary?: string;
  referenced_projects?: string[];
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(endpoint, {
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

export const api = {
  async checkHealth(): Promise<{ status: string }> {
    try {
      const response = await fetch('/api/topology/stats');
      if (response.ok) {
        return { status: 'ok' };
      }
      return { status: 'error' };
    } catch {
      return { status: 'error' };
    }
  },

  async getProjects(): Promise<{ projects: string[] }> {
    return fetchApi<{ projects: string[] }>('/api/projects');
  },

  async getProjectStats(projectName: string): Promise<{
    node_count: number;
    edge_count: number;
    last_scanned: string;
    node_types: Record<string, number>;
  }> {
    return fetchApi(`/api/projects/${projectName}/stats`);
  },

  async deleteProject(projectName: string): Promise<{ status: string; message: string }> {
    return fetchApi<{ status: string; message: string }>(`/api/scan/project/${projectName}`, {
      method: 'DELETE',
    });
  },
};

export const topologyApi = {
  async getTopology(nodeTypes?: string[], limit: number = 100): Promise<TopologyData> {
    const params = new URLSearchParams();
    params.set('limit', limit.toString());
    
    if (nodeTypes && nodeTypes.length > 0) {
      params.set('node_types', nodeTypes.join(','));
    }
    
    return fetchApi<TopologyData>(`/api/topology?${params.toString()}`);
  },

  async getProjects(): Promise<any[]> {
    return fetchApi<any[]>('/api/topology/projects');
  },

  async switchProject(projectId: string): Promise<void> {
    await fetchApi(`/api/topology/projects/${projectId}/switch`, { method: 'POST' });
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
  async scanGitHub(repoUrl: string, branch: string = 'main', scanType: string = 'architecture'): Promise<ScanResult> {
    return fetchApi<ScanResult>('/api/scan/github', {
      method: 'POST',
      body: JSON.stringify({ repo_url: repoUrl, branch, scan_type: scanType }),
    });
  },

  async addManualNodes(nodes: any[], edges?: any[]): Promise<ScanResult> {
    return fetchApi<ScanResult>('/api/scan/manual', {
      method: 'POST',
      body: JSON.stringify({ nodes, edges }),
    });
  },

  async clearTopology(): Promise<{ status: string; message: string }> {
    return fetchApi<{ status: string; message: string }>('/api/scan/clear', { method: 'POST' });
  },

  async deleteProject(projectName: string): Promise<{ status: string; message: string; nodes_deleted: number }> {
    return fetchApi(`/api/scan/project/${projectName}`, { method: 'DELETE' });
  },

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

export const chatApi = {
  async sendMessage(message: string, conversationHistory?: ChatMessage[]): Promise<ChatResponse> {
    return fetchApi<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        conversation_history: conversationHistory || [],
      }),
    });
  },

  async testConnection(): Promise<any> {
    return fetchApi('/api/chat/test');
  },
};

export { ApiError };
