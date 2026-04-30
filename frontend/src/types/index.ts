export type UserRole = 'rep' | 'manager' | 'admin';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  territory?: string;
  createdAt: string;
  updatedAt: string;
}

export interface HCP {
  id: string;
  name: string;
  specialty?: string;
  institution?: string;
  email?: string;
  phone?: string;
  notes?: string;
  createdBy?: string;
  createdAt?: string;
  updatedAt?: string;
}

export type InteractionType = 'meeting' | 'call' | 'conference' | 'email';
export type Sentiment = 'positive' | 'neutral' | 'negative';

export interface Interaction {
  id: string;
  hcpId: string;
  hcp?: HCP;
  userId: string;
  type: InteractionType;
  dateTime: string;
  attendees: string[];
  topics: string;
  sentiment?: Sentiment;
  outcome?: string;
  voiceNoteUrl?: string;
  materials?: Material[];
  samples?: Sample[];
  followUps?: FollowUp[];
  createdAt: string;
  updatedAt: string;
}

export type MaterialType = 'pdf' | 'physical' | 'digital';

export interface Material {
  id: string;
  name: string;
  type: MaterialType;
  description?: string;
  fileUrl?: string;
  createdAt: string;
}

export interface Sample {
  id: string;
  interactionId?: string;
  productName: string;
  lotNumber?: string;
  quantity: number;
  createdAt: string;
}

export type FollowUpType = 'follow_up_meeting' | 'send_material' | 'sample_request' | 'call' | 'other';
export type FollowUpStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';

export interface FollowUp {
  id: string;
  interactionId?: string;
  type: FollowUpType;
  description: string;
  status: FollowUpStatus;
  dueDate?: string;
  assigneeId?: string;
  assignee?: User;
  createdBy?: string;
  aiGenerated: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface InteractionMaterial {
  interactionId: string;
  materialId: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatResponse {
  message: string;
  intent: string;
  entities: Record<string, unknown>;
  sessionId: string;
  success: boolean;
  error?: string;
  interaction?: Interaction;
  aiSuggestions?: Array<{ id?: string; description: string; type?: string; dueInDays?: number; dueDate?: string; priority?: string }>;
}
