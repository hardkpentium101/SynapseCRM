import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Material } from '../../types';
import { api } from '../../services/api';

interface MaterialsState {
  items: Material[];
  searchResults: Material[];
  loading: boolean;
  error: string | null;
}

const initialState: MaterialsState = {
  items: [],
  searchResults: [],
  loading: false,
  error: null,
};

export const fetchMaterials = createAsyncThunk(
  'materials/fetchAll',
  async (_, { rejectWithValue }) => {
    try {
      return await api.getMaterials();
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

export const searchMaterials = createAsyncThunk(
  'materials/search',
  async (query: string, { rejectWithValue }) => {
    try {
      return await api.getMaterials(query);
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

const materialsSlice = createSlice({
  name: 'materials',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchMaterials.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchMaterials.fulfilled, (state, action: PayloadAction<Material[]>) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchMaterials.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(searchMaterials.pending, (state) => {
        state.searchResults = [];
      })
      .addCase(searchMaterials.fulfilled, (state, action: PayloadAction<Material[]>) => {
        state.searchResults = action.payload;
      });
  },
});

export default materialsSlice.reducer;
