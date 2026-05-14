import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { HCP } from '../../types';
import { api } from '../../services/api';

interface HCPsState {
  searchResults: HCP[];
}

const initialState: HCPsState = {
  searchResults: [],
};

export const fetchHCPs = createAsyncThunk(
  'hcps/fetchAll',
  async (_, { rejectWithValue }) => {
    try {
      return await api.getHcps();
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

export const searchHCPs = createAsyncThunk(
  'hcps/search',
  async (query: string, { rejectWithValue }) => {
    try {
      return await api.getHcps(query);
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

const hcpsSlice = createSlice({
  name: 'hcps',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(searchHCPs.fulfilled, (state, action: PayloadAction<HCP[]>) => {
        state.searchResults = action.payload;
      })
      .addCase(fetchHCPs.fulfilled, (state, action: PayloadAction<HCP[]>) => {
        state.searchResults = action.payload;
      });
  },
});

export default hcpsSlice.reducer;
