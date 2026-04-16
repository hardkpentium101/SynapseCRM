import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { FollowUp } from '../../types';
import { api } from '../../services/api';

interface FollowUpsState {
  items: FollowUp[];
  suggestions: FollowUp[];
  loading: boolean;
  error: string | null;
}

const initialState: FollowUpsState = {
  items: [],
  suggestions: [],
  loading: false,
  error: null,
};

export const fetchFollowUps = createAsyncThunk(
  'followUps/fetchAll',
  async (interactionId: string | undefined, { rejectWithValue }) => {
    try {
      return await api.getFollowUps(interactionId);
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

export const createFollowUp = createAsyncThunk(
  'followUps/create',
  async (data: Partial<FollowUp>, { rejectWithValue }) => {
    try {
      return await api.createFollowUp(data);
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

export const updateFollowUp = createAsyncThunk(
  'followUps/update',
  async ({ id, data }: { id: string; data: Partial<FollowUp> }, { rejectWithValue }) => {
    try {
      return await api.updateFollowUp(id, data);
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

export const deleteFollowUp = createAsyncThunk(
  'followUps/delete',
  async (id: string, { rejectWithValue }) => {
    try {
      await api.deleteFollowUp(id);
      return id;
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

const followUpsSlice = createSlice({
  name: 'followUps',
  initialState,
  reducers: {
    addSuggestion: (state, action: PayloadAction<FollowUp>) => {
      state.suggestions.push(action.payload);
    },
    removeSuggestion: (state, action: PayloadAction<string>) => {
      state.suggestions = state.suggestions.filter(s => s.id !== action.payload);
    },
    clearSuggestions: (state) => {
      state.suggestions = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchFollowUps.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchFollowUps.fulfilled, (state, action: PayloadAction<FollowUp[]>) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchFollowUps.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(createFollowUp.fulfilled, (state, action: PayloadAction<FollowUp>) => {
        state.items.push(action.payload);
        state.suggestions = state.suggestions.filter(s => s.id !== action.payload.id);
      })
      .addCase(updateFollowUp.fulfilled, (state, action: PayloadAction<FollowUp>) => {
        const index = state.items.findIndex(f => f.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = action.payload;
        }
      })
      .addCase(deleteFollowUp.fulfilled, (state, action: PayloadAction<string>) => {
        state.items = state.items.filter(f => f.id !== action.payload);
      });
  },
});

export const { addSuggestion, removeSuggestion, clearSuggestions } = followUpsSlice.actions;
export default followUpsSlice.reducer;
