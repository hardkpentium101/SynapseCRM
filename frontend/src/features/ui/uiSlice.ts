import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface Notification {
  id: string;
  kind: 'success' | 'error' | 'info' | 'warning';
  message: string;
  duration?: number;
}

interface UIState {
  splitPosition: number;
  leftPanelMode: 'view' | 'edit' | 'create';
  notifications: Notification[];
  sidebarCollapsed: boolean;
}

const initialState: UIState = {
  splitPosition: 60,
  leftPanelMode: 'create',
  notifications: [],
  sidebarCollapsed: false,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setSplitPosition: (state, action: PayloadAction<number>) => {
      state.splitPosition = Math.max(20, Math.min(80, action.payload));
    },
    setLeftPanelMode: (state, action: PayloadAction<'view' | 'edit' | 'create'>) => {
      state.leftPanelMode = action.payload;
    },
    addNotification: (state, action: PayloadAction<Omit<Notification, 'id'>>) => {
      const id = Math.random().toString(36).substring(2, 9);
      state.notifications.push({ ...action.payload, id });
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(n => n.id !== action.payload);
    },
    toggleSidebar: (state) => {
      state.sidebarCollapsed = !state.sidebarCollapsed;
    },
  },
});

export const {
  setSplitPosition,
  setLeftPanelMode,
  addNotification,
  removeNotification,
  toggleSidebar,
} = uiSlice.actions;

export default uiSlice.reducer;
