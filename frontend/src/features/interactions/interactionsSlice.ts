import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Interaction, HCP, Sentiment, Material, Sample } from '../../types';
import { api } from '../../services/api';

interface InteractionsState {
  formData: Partial<Interaction>;
  sessionId: string | null;
  dirty: boolean;
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
  formData: initialFormData,
  sessionId: null,
  dirty: false,
};

export const loadSessionEntities = createAsyncThunk(
  'interactions/loadSessionEntities',
  async (sessionId: string, { rejectWithValue }) => {
    try {
      const response = await api.getSessionEntities(sessionId);
      return { sessionId, entities: response.entities };
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

export const createInteraction = createAsyncThunk(
  'interactions/create',
  async (data: { hcpId: string; type: string; dateTime: string; topics?: string; sentiment?: Sentiment; outcome?: string; attendees?: string[]; materialIds?: string[]; samples?: Array<{ product_name: string; lot_number?: string; quantity: number }> }, { rejectWithValue }) => {
    try {
      return await api.createInteraction(data);
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

const interactionsSlice = createSlice({
  name: 'interactions',
  initialState,
  reducers: {
    updateFormField: (state, action: PayloadAction<{ field: string; value: unknown }>) => {
      const { field, value } = action.payload;
      (state.formData as Record<string, unknown>)[field] = value;
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
    resetForm: (state) => {
      state.formData = { ...initialFormData, dateTime: new Date().toISOString().slice(0, 16) };
      state.dirty = false;
    },
    setSessionId: (state, action: PayloadAction<string | null>) => {
      state.sessionId = action.payload;
    },
    clearDirty: (state) => {
      state.dirty = false;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loadSessionEntities.fulfilled, (state, action) => {
        const { sessionId, entities } = action.payload;
        state.sessionId = sessionId;
        if (entities.hcp_id) {
          const hcpData: HCP = {
            id: entities.hcp_id as string,
            name: (entities.hcp_name as string) || '',
            specialty: (entities.hcp_specialty as string) || '',
            institution: (entities.hcp_institution as string) || '',
          };
          state.formData.hcpId = entities.hcp_id as string;
          state.formData.hcp = hcpData;
        }
        if (entities.date_time) {
          state.formData.dateTime = entities.date_time as string;
        }
        if (entities.type) {
          state.formData.type = entities.type as Interaction['type'];
        }
        if (entities.topics) {
          const topicsVal = entities.topics;
          state.formData.topics = Array.isArray(topicsVal)
            ? topicsVal.join(', ')
            : String(topicsVal);
        }
        if (entities.sentiment) {
          state.formData.sentiment = entities.sentiment as Sentiment;
        }
        if (entities.outcome) {
          state.formData.outcome = entities.outcome as string;
        }
      })
      .addCase(createInteraction.fulfilled, (state, action: PayloadAction<Interaction>) => {
        state.formData = { ...action.payload };
        state.dirty = false;
      });
  },
});

export const {
  updateFormField,
  setHCP,
  setSentiment,
  addAttendee,
  removeAttendee,
  addMaterial,
  removeMaterial,
  addSample,
  removeSample,
  resetForm,
  setSessionId,
  clearDirty,
} = interactionsSlice.actions;

export default interactionsSlice.reducer;
