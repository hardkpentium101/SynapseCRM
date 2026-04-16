import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { HCP } from '../../types';
import { api } from '../../services/api';

interface HCPsState {
  items: HCP[];
  searchResults: HCP[];
  activeId: string | null;
  activeHCP: HCP | null;
  loading: boolean;
  error: string | null;
}

const initialState: HCPsState = {
  items: [],
  searchResults: [],
  activeId: null,
  activeHCP: null,
  loading: false,
  error: null,
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

export const fetchHCP = createAsyncThunk(
  'hcps/fetchOne',
  async (id: string, { rejectWithValue }) => {
    try {
      return await api.getHcp(id);
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

export const createHCP = createAsyncThunk(
  'hcps/create',
  async (data: Partial<HCP>, { rejectWithValue }) => {
    try {
      return await api.createHcp(data);
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

export const updateHCP = createAsyncThunk(
  'hcps/update',
  async ({ id, data }: { id: string; data: Partial<HCP> }, { rejectWithValue }) => {
    try {
      return await api.updateHcp(id, data);
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

const hcpsSlice = createSlice({
  name: 'hcps',
  initialState,
  reducers: {
    setActiveHCP: (state, action: PayloadAction<string | null>) => {
      state.activeId = action.payload;
      state.activeHCP = action.payload ? state.items.find(h => h.id === action.payload) || null : null;
    },
    clearSearch: (state) => {
      state.searchResults = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchHCPs.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchHCPs.fulfilled, (state, action: PayloadAction<HCP[]>) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchHCPs.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(searchHCPs.fulfilled, (state, action: PayloadAction<HCP[]>) => {
        state.searchResults = action.payload;
      })
      .addCase(fetchHCP.fulfilled, (state, action: PayloadAction<HCP>) => {
        state.activeHCP = action.payload;
      })
      .addCase(createHCP.fulfilled, (state, action: PayloadAction<HCP>) => {
        state.items.push(action.payload);
      })
      .addCase(updateHCP.fulfilled, (state, action: PayloadAction<HCP>) => {
        const index = state.items.findIndex(h => h.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = action.payload;
        }
      });
  },
});

export const { setActiveHCP, clearSearch } = hcpsSlice.actions;
export default hcpsSlice.reducer;
