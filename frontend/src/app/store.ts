import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../features/auth/authSlice';
import hcpsReducer from '../features/hcps/hcpsSlice';
import interactionsReducer from '../features/interactions/interactionsSlice';
import materialsReducer from '../features/materials/materialsSlice';
import samplesReducer from '../features/samples/samplesSlice';
import followUpsReducer from '../features/followUps/followUpsSlice';
import uiReducer from '../features/ui/uiSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    hcps: hcpsReducer,
    interactions: interactionsReducer,
    materials: materialsReducer,
    samples: samplesReducer,
    followUps: followUpsReducer,
    ui: uiReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
