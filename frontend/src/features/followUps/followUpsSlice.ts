import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { FollowUp } from '../../types';
import { api } from '../../services/api';

interface FollowUpsState {
  suggestions: FollowUp[];
}

const initialState: FollowUpsState = {
  suggestions: [],
};

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
  },
  extraReducers: (builder) => {
    builder
      .addCase(createFollowUp.fulfilled, (state, action: PayloadAction<FollowUp>) => {
        state.suggestions = state.suggestions.filter(s => s.id !== action.payload.id);
      });
  },
});

export const { addSuggestion, removeSuggestion } = followUpsSlice.actions;
export default followUpsSlice.reducer;
