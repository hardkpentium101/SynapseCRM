import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Sample } from '../../types';
import { api } from '../../services/api';

interface SamplesState {
  searchResults: Sample[];
}

const initialState: SamplesState = {
  searchResults: [],
};

export const fetchSamples = createAsyncThunk(
  'samples/fetchAll',
  async (interactionId: string | undefined, { rejectWithValue }) => {
    try {
      return await api.getSamples(interactionId);
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

export const searchSamples = createAsyncThunk(
  'samples/search',
  async (query: string, { rejectWithValue }) => {
    try {
      const items = await api.getSamples();
      if (!query) return items;
      const lower = query.toLowerCase();
      return items.filter(
        (s) =>
          s.productName.toLowerCase().includes(lower) ||
          s.lotNumber?.toLowerCase().includes(lower)
      );
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

const samplesSlice = createSlice({
  name: 'samples',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchSamples.fulfilled, (state, action: PayloadAction<Sample[]>) => {
        state.searchResults = action.payload;
      })
      .addCase(searchSamples.fulfilled, (state, action: PayloadAction<Sample[]>) => {
        state.searchResults = action.payload;
      });
  },
});

export default samplesSlice.reducer;
