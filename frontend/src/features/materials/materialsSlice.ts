import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Material } from '../../types';
import { api } from '../../services/api';

interface MaterialsState {
  items: Material[];
  searchResults: Material[];
}

const initialState: MaterialsState = {
  items: [],
  searchResults: [],
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
      .addCase(fetchMaterials.fulfilled, (state, action: PayloadAction<Material[]>) => {
        state.items = action.payload;
      })
      .addCase(searchMaterials.fulfilled, (state, action: PayloadAction<Material[]>) => {
        state.searchResults = action.payload;
      });
  },
});

export default materialsSlice.reducer;
