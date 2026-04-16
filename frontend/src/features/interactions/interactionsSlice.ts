import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Interaction, HCP, Sentiment, Material, Sample, FollowUp } from '../../types';
import { api } from '../../services/api';

interface InteractionsState {
  items: Interaction[];
  activeId: string | null;
  activeInteraction: Interaction | null;
  formData: Partial<Interaction>;
  dirty: boolean;
  loading: boolean;
  saving: boolean;
  error: string | null;
}

const initialFormData: Partial<Interaction> = {
  type: 'meeting',
  dateTime: new Date().toISOString().slice(0, 16),
  attendees: [],
  topics: '',
  sentiment: undefined,
  outcome: '',
};

const initialState: InteractionsState = {
  items: [],
  activeId: null,
  activeInteraction: null,
  formData: initialFormData,
  dirty: false,
  loading: false,
  saving: false,
  error: null,
};

export const fetchInteractions = createAsyncThunk(
  'interactions/fetchAll',
  async (filters: { hcpId?: string } | undefined, { rejectWithValue }) => {
    try {
      return await api.getInteractions(filters);
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

export const fetchInteraction = createAsyncThunk(
  'interactions/fetchOne',
  async (id: string, { rejectWithValue }) => {
    try {
      return await api.getInteraction(id);
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

export const createInteraction = createAsyncThunk(
  'interactions/create',
  async (data: Partial<Interaction>, { rejectWithValue }) => {
    try {
      return await api.createInteraction(data);
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

export const updateInteraction = createAsyncThunk(
  'interactions/update',
  async ({ id, data }: { id: string; data: Partial<Interaction> }, { rejectWithValue }) => {
    try {
      return await api.updateInteraction(id, data);
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

const interactionsSlice = createSlice({
  name: 'interactions',
  initialState,
  reducers: {
    setActiveInteraction: (state, action: PayloadAction<string | null>) => {
      state.activeId = action.payload;
      state.activeInteraction = action.payload 
        ? state.items.find(i => i.id === action.payload) || null 
        : null;
      state.formData = state.activeInteraction 
        ? { ...state.activeInteraction }
        : { ...initialFormData, dateTime: new Date().toISOString().slice(0, 16) };
      state.dirty = false;
    },
    updateFormField: (state, action: PayloadAction<{ field: string; value: unknown }>) => {
      const { field, value } = action.payload;
      (state.formData as Record<string, unknown>)[field] = value;
      state.dirty = true;
    },
    setFormData: (state, action: PayloadAction<Partial<Interaction>>) => {
      state.formData = { ...state.formData, ...action.payload };
      state.dirty = true;
    },
    setHCP: (state, action: PayloadAction<HCP>) => {
      state.formData.hcpId = action.payload.id;
      state.formData.hcp = action.payload;
      state.dirty = true;
    },
    setSentiment: (state, action: PayloadAction<Sentiment>) => {
      state.formData.sentiment = action.payload;
      state.dirty = true;
    },
    addAttendee: (state, action: PayloadAction<string>) => {
      if (!state.formData.attendees) {
        state.formData.attendees = [];
      }
      state.formData.attendees.push(action.payload);
      state.dirty = true;
    },
    removeAttendee: (state, action: PayloadAction<number>) => {
      if (state.formData.attendees) {
        state.formData.attendees.splice(action.payload, 1);
        state.dirty = true;
      }
    },
    addMaterial: (state, action: PayloadAction<Material>) => {
      if (!state.formData.materials) {
        state.formData.materials = [];
      }
      state.formData.materials.push(action.payload);
      state.dirty = true;
    },
    removeMaterial: (state, action: PayloadAction<string>) => {
      if (state.formData.materials) {
        state.formData.materials = state.formData.materials.filter(m => m.id !== action.payload);
        state.dirty = true;
      }
    },
    addSample: (state, action: PayloadAction<Sample>) => {
      if (!state.formData.samples) {
        state.formData.samples = [];
      }
      state.formData.samples.push(action.payload);
      state.dirty = true;
    },
    removeSample: (state, action: PayloadAction<string>) => {
      if (state.formData.samples) {
        state.formData.samples = state.formData.samples.filter(s => s.id !== action.payload);
        state.dirty = true;
      }
    },
    addFollowUp: (state, action: PayloadAction<FollowUp>) => {
      if (!state.formData.followUps) {
        state.formData.followUps = [];
      }
      state.formData.followUps.push(action.payload);
      state.dirty = true;
    },
    removeFollowUp: (state, action: PayloadAction<string>) => {
      if (state.formData.followUps) {
        state.formData.followUps = state.formData.followUps.filter(f => f.id !== action.payload);
        state.dirty = true;
      }
    },
    resetForm: (state) => {
      state.formData = { ...initialFormData, dateTime: new Date().toISOString().slice(0, 16) };
      state.activeId = null;
      state.activeInteraction = null;
      state.dirty = false;
    },
    clearDirty: (state) => {
      state.dirty = false;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchInteractions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchInteractions.fulfilled, (state, action: PayloadAction<Interaction[]>) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(fetchInteraction.fulfilled, (state, action: PayloadAction<Interaction>) => {
        state.activeInteraction = action.payload;
        state.formData = { ...action.payload };
        state.dirty = false;
      })
      .addCase(createInteraction.pending, (state) => {
        state.saving = true;
      })
      .addCase(createInteraction.fulfilled, (state, action: PayloadAction<Interaction>) => {
        state.saving = false;
        state.items.push(action.payload);
        state.activeId = action.payload.id;
        state.activeInteraction = action.payload;
        state.formData = { ...action.payload };
        state.dirty = false;
      })
      .addCase(createInteraction.rejected, (state, action) => {
        state.saving = false;
        state.error = action.payload as string;
      })
      .addCase(updateInteraction.pending, (state) => {
        state.saving = true;
      })
      .addCase(updateInteraction.fulfilled, (state, action: PayloadAction<Interaction>) => {
        state.saving = false;
        const index = state.items.findIndex(i => i.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = action.payload;
        }
        state.activeInteraction = action.payload;
        state.formData = { ...action.payload };
        state.dirty = false;
      })
      .addCase(updateInteraction.rejected, (state, action) => {
        state.saving = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  setActiveInteraction,
  updateFormField,
  setFormData,
  setHCP,
  setSentiment,
  addAttendee,
  removeAttendee,
  addMaterial,
  removeMaterial,
  addSample,
  removeSample,
  addFollowUp,
  removeFollowUp,
  resetForm,
  clearDirty,
} = interactionsSlice.actions;

export default interactionsSlice.reducer;
