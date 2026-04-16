import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Sample } from '../../types';
import { api } from '../../services/api';

interface SamplesState {
  items: Sample[];
  searchResults: Sample[];
  loading: boolean;
  error: string | null;
}

const initialState: SamplesState = {
  items: [],
  searchResults: [],
  loading: false,
  error: null,
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

export const createSample = createAsyncThunk(
  'samples/create',
  async (data: Partial<Sample>, { rejectWithValue }) => {
    try {
      return await api.createSample(data);
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

export const deleteSample = createAsyncThunk(
  'samples/delete',
  async (id: string, { rejectWithValue }) => {
    try {
      await api.deleteSample(id);
      return id;
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
      .addCase(fetchSamples.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchSamples.fulfilled, (state, action: PayloadAction<Sample[]>) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchSamples.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(createSample.fulfilled, (state, action: PayloadAction<Sample>) => {
        state.items.push(action.payload);
      })
      .addCase(deleteSample.fulfilled, (state, action: PayloadAction<string>) => {
        state.items = state.items.filter(s => s.id !== action.payload);
      })
      .addCase(searchSamples.pending, (state) => {
        state.loading = true;
      })
      .addCase(searchSamples.fulfilled, (state, action: PayloadAction<Sample[]>) => {
        state.loading = false;
        state.searchResults = action.payload;
      })
      .addCase(searchSamples.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export default samplesSlice.reducer;
