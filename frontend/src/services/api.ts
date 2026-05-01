import type {
  User, HCP, Interaction, Material, Sample, FollowUp,
  AuthTokens, LoginCredentials
} from '../types';
import camelcaseKeys from 'camelcase-keys';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

class ApiService {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    
    if (options.headers) {
      const customHeaders = options.headers as Record<string, string>;
      Object.assign(headers, customHeaders);
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      throw new Error(error.detail || 'An error occurred');
    }

    const data = await response.json();
    return camelcaseKeys(data, { deep: true }) as T;
  }

  // Auth
  async login(credentials: LoginCredentials): Promise<{ user: User; tokens: AuthTokens }> {
    const response = await this.request<{ user: User; accessToken: string; refreshToken: string }>(
      '/auth/login',
      { method: 'POST', body: JSON.stringify(credentials) }
    );
    this.token = response.accessToken;
    return {
      user: response.user || { id: '', email: credentials.email, name: '', role: 'rep' },
      tokens: { accessToken: response.accessToken, refreshToken: response.refreshToken }
    };
  }

  async getMe(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  // HCPs
  async getHcps(search?: string): Promise<HCP[]> {
    const params = search ? `?search=${encodeURIComponent(search)}` : '';
    return this.request<HCP[]>(`/hcps${params}`);
  }

  async getHcp(id: string): Promise<HCP> {
    return this.request<HCP>(`/hcps/${id}`);
  }

  async createHcp(data: Partial<HCP>): Promise<HCP> {
    return this.request<HCP>('/hcps', { method: 'POST', body: JSON.stringify(data) });
  }

  async updateHcp(id: string, data: Partial<HCP>): Promise<HCP> {
    return this.request<HCP>(`/hcps/${id}`, { method: 'PUT', body: JSON.stringify(data) });
  }

  async deleteHcp(id: string): Promise<void> {
    return this.request<void>(`/hcps/${id}`, { method: 'DELETE' });
  }

  // Interactions
  async getInteractions(filters?: { hcpId?: string; userId?: string }): Promise<Interaction[]> {
    const params = new URLSearchParams();
    if (filters?.hcpId) params.set('hcp_id', filters.hcpId);
    if (filters?.userId) params.set('user_id', filters.userId);
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.request<Interaction[]>(`/interactions${query}`);
  }

  async getInteraction(id: string): Promise<Interaction> {
    return this.request<Interaction>(`/interactions/${id}`);
  }

  async createInteraction(data: Record<string, unknown>): Promise<Interaction> {
    const snakeData = this.toSnakeCase(data);
    return this.request<Interaction>('/interactions', { method: 'POST', body: JSON.stringify(snakeData) });
  }

  async updateInteraction(id: string, data: Partial<Interaction>): Promise<Interaction> {
    const snakeData = this.toSnakeCase(data);
    return this.request<Interaction>(`/interactions/${id}`, { method: 'PUT', body: JSON.stringify(snakeData) });
  }

  private toSnakeCase(obj: Record<string, unknown>): Record<string, unknown> {
    const result: Record<string, unknown> = {};
    for (const key in obj) {
      const snakeKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
      const value = obj[key];
      if (Array.isArray(value)) {
        result[snakeKey] = value.map(item => 
          typeof item === 'object' && item !== null 
            ? this.toSnakeCase(item as Record<string, unknown>) 
            : item
        );
      } else if (typeof value === 'object' && value !== null) {
        result[snakeKey] = this.toSnakeCase(value as Record<string, unknown>);
      } else {
        result[snakeKey] = value;
      }
    }
    return result;
  }

  async deleteInteraction(id: string): Promise<void> {
    return this.request<void>(`/interactions/${id}`, { method: 'DELETE' });
  }

  // Materials
  async getMaterials(search?: string): Promise<Material[]> {
    const params = search ? `?search=${encodeURIComponent(search)}` : '';
    return this.request<Material[]>(`/materials${params}`);
  }

  async getMaterial(id: string): Promise<Material> {
    return this.request<Material>(`/materials/${id}`);
  }

  async createMaterial(data: Partial<Material>): Promise<Material> {
    return this.request<Material>('/materials', { method: 'POST', body: JSON.stringify(data) });
  }

  // Samples
  async getSamples(interactionId?: string): Promise<Sample[]> {
    const params = interactionId ? `?interaction_id=${interactionId}` : '';
    return this.request<Sample[]>(`/samples${params}`);
  }

  async createSample(data: Partial<Sample>): Promise<Sample> {
    return this.request<Sample>('/samples', { method: 'POST', body: JSON.stringify(data) });
  }

  async deleteSample(id: string): Promise<void> {
    return this.request<void>(`/samples/${id}`, { method: 'DELETE' });
  }

  // Follow-ups
  async getFollowUps(interactionId?: string): Promise<FollowUp[]> {
    const params = interactionId ? `?interaction_id=${interactionId}` : '';
    return this.request<FollowUp[]>(`/follow-ups${params}`);
  }

  async createFollowUp(data: Partial<FollowUp>): Promise<FollowUp> {
    const snakeData = this.toSnakeCase(data);
    return this.request<FollowUp>('/follow-ups', { method: 'POST', body: JSON.stringify(snakeData) });
  }

  async updateFollowUp(id: string, data: Partial<FollowUp>): Promise<FollowUp> {
    return this.request<FollowUp>(`/follow-ups/${id}`, { method: 'PUT', body: JSON.stringify(data) });
  }

  async deleteFollowUp(id: string): Promise<void> {
    return this.request<void>(`/follow-ups/${id}`, { method: 'DELETE' });
  }

  // Chat
  async chat(message: string, sessionId?: string, userId?: string, formData?: Record<string, unknown>): Promise<{
    message: string;
    intent: string;
    entities: Record<string, unknown>;
    session_id: string;
    success: boolean;
    error?: string;
    interaction?: {
      hcpId?: string;
      hcp_id?: string;
      hcpName?: string;
      hcp_name?: string;
      hcpSpecialty?: string;
      hcp_specialty?: string;
      hcpInstitution?: string;
      hcp_institution?: string;
      type: string;
      dateTime?: string;
      date_time?: string;
      topics?: string[];
      attendees?: string[];
      sentiment?: string;
      outcome?: string;
      notes?: string;
      status?: string;
      message?: string;
      materials?: Array<string | { id: string; name: string; type: string; description?: string }>;
    };
    aiSuggestions?: Array<{ id?: string; description: string; type?: string; dueInDays?: number; dueDate?: string; priority?: string }>;
  }> {
    return this.request<{
      message: string;
      intent: string;
      entities: Record<string, unknown>;
      session_id: string;
      success: boolean;
      error?: string;
      interaction?: {
        hcpId?: string;
        hcp_id?: string;
        hcpName?: string;
        hcp_name?: string;
        hcpSpecialty?: string;
        hcp_specialty?: string;
        hcpInstitution?: string;
        hcp_institution?: string;
        type: string;
        dateTime?: string;
        date_time?: string;
        topics?: string[];
        attendees?: string[];
        sentiment?: string;
        outcome?: string;
        notes?: string;
        status?: string;
        message?: string;
      materials?: Array<string | { id: string; name: string; type: string; description?: string }>;
      };
    aiSuggestions?: Array<{ id?: string; description: string; type?: string; dueInDays?: number; dueDate?: string; priority?: string }>;
    }>('/agent/chat', {
      method: 'POST',
      body: JSON.stringify({ message, session_id: sessionId, user_id: userId, form_data: formData }),
    });
  }

  async getChatHistory(sessionId: string, limit = 20): Promise<{ messages: unknown[]; count: number }> {
    return this.request<{ messages: unknown[]; count: number }>(`/agent/history/${sessionId}?limit=${limit}`);
  }

  async getSessionEntities(sessionId: string): Promise<{ entities: Record<string, unknown> }> {
    return this.request<{ entities: Record<string, unknown> }>(`/agent/session/${sessionId}/entities`);
  }
}

export const api = new ApiService();
