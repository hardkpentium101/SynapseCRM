import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { ChatMessage } from '../../types';

interface ChatState {
  messages: (ChatMessage & { responseLog?: ResponseLog })[];
  loading: boolean;
  sessionId: string | null;
}

interface ResponseLog {
  intent: string;
  entitiesSet: { field: string; value: string }[];
  materialsAdded: string[];
  suggestionsAdded: string[];
}

interface AssistantMsg {
  role: 'assistant';
  content: string;
  responseLog?: ResponseLog;
}

const initialState: ChatState = {
  messages: [],
  loading: false,
  sessionId: null,
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addUserMessage(state, action: PayloadAction<string>) {
      state.messages.push({ role: 'user', content: action.payload });
    },
    addAssistantMessage(state, action: PayloadAction<AssistantMsg>) {
      state.messages.push(action.payload);
    },
    setLoading(state, action: PayloadAction<boolean>) {
      state.loading = action.payload;
    },
    setSessionId(state, action: PayloadAction<string>) {
      state.sessionId = action.payload;
    },
    clearMessages(state) {
      state.messages = [];
      state.sessionId = null;
    },
    addFollowUpAction(state, action: PayloadAction<{ description: string; status: 'approved' | 'declined' }>) {
      state.messages.push({
        role: 'assistant',
        content: action.payload.status === 'approved'
          ? `✅ Follow-up created: ${action.payload.description}`
          : `❌ Follow-up declined: ${action.payload.description}`,
      });
    },
  },
});

export const {
  addUserMessage,
  addAssistantMessage,
  setLoading,
  setSessionId,
  clearMessages,
  addFollowUpAction,
} = chatSlice.actions;

export default chatSlice.reducer;
