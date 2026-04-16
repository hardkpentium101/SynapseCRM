import { describe, it, expect, beforeEach } from 'vitest'
import { configureStore } from '@reduxjs/toolkit'
import interactionsReducer, {
  setActiveInteraction,
  updateFormField,
  setFormData,
  setSentiment,
  addAttendee,
  removeAttendee,
  addMaterial,
  removeMaterial,
  resetForm,
  clearDirty,
} from '../../features/interactions/interactionsSlice'
import type { Interaction, InteractionType } from '../../types'

describe('interactionsSlice', () => {
  let store: ReturnType<typeof configureStore>

  const mockInteraction: Interaction = {
    id: 'int-1',
    hcpId: 'hcp-1',
    hcp: {
      id: 'hcp-1',
      name: 'Dr. Priya Sharma',
      specialty: 'Oncology',
      institution: 'Tata Memorial Hospital',
      createdAt: '2025-01-01T00:00:00Z',
      updatedAt: '2025-01-01T00:00:00Z',
    },
    userId: 'user-1',
    type: 'meeting',
    dateTime: '2025-04-16T10:00:00Z',
    attendees: ['Dr. John'],
    topics: 'Discussed OncoBoost efficacy',
    sentiment: 'positive',
    outcome: 'Patient interested in clinical trial',
    materials: [],
    samples: [],
    followUps: [],
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-01-01T00:00:00Z',
  }

  const mockMaterial = {
    id: 'mat-1',
    name: 'OncoBoost Brochure',
    type: 'pdf' as const,
    description: 'Phase III clinical trial data',
    createdAt: '2025-01-01T00:00:00Z',
  }

  beforeEach(() => {
    store = configureStore({
      reducer: { interactions: interactionsReducer },
    })
  })

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const state = store.getState().interactions
      expect(state.items).toEqual([])
      expect(state.activeId).toBeNull()
      expect(state.activeInteraction).toBeNull()
      expect(state.formData.type).toBe('meeting')
      expect(state.formData.attendees).toEqual([])
      expect(state.dirty).toBe(false)
    })
  })

  describe('setActiveInteraction action', () => {
    it('should set active interaction and populate form data', () => {
      store = configureStore({
        reducer: { interactions: interactionsReducer },
        preloadedState: {
          interactions: {
            items: [mockInteraction],
            activeId: null,
            activeInteraction: null,
            formData: { type: 'meeting', dateTime: '', attendees: [], topics: '', sentiment: undefined, outcome: '' },
            dirty: false,
            loading: false,
            saving: false,
            error: null,
          },
        },
      })

      store.dispatch(setActiveInteraction('int-1'))
      const state = store.getState().interactions

      expect(state.activeId).toBe('int-1')
      expect(state.activeInteraction).toEqual(mockInteraction)
      expect(state.formData.hcpId).toBe('hcp-1')
      expect(state.formData.topics).toBe('Discussed OncoBoost efficacy')
      expect(state.dirty).toBe(false)
    })
  })

  describe('updateFormField action', () => {
    it('should update field and set dirty flag', () => {
      store.dispatch(updateFormField({ field: 'topics', value: 'New topic' }))
      const state = store.getState().interactions

      expect(state.formData.topics).toBe('New topic')
      expect(state.dirty).toBe(true)
    })
  })

  describe('setFormData action', () => {
    it('should merge form data and set dirty flag', () => {
      store.dispatch(setFormData({ topics: 'AI extracted topic', sentiment: 'positive' as const }))
      const state = store.getState().interactions

      expect(state.formData.topics).toBe('AI extracted topic')
      expect(state.formData.sentiment).toBe('positive')
      expect(state.dirty).toBe(true)
    })
  })

  describe('setSentiment action', () => {
    it('should set sentiment and mark dirty', () => {
      store.dispatch(setSentiment('positive'))
      expect(store.getState().interactions.formData.sentiment).toBe('positive')
      expect(store.getState().interactions.dirty).toBe(true)
    })
  })

  describe('attendees management', () => {
    it('should add attendee', () => {
      store.dispatch(addAttendee('Dr. John'))
      expect(store.getState().interactions.formData.attendees).toContain('Dr. John')
      expect(store.getState().interactions.dirty).toBe(true)
    })

    it('should remove attendee', () => {
      store = configureStore({
        reducer: { interactions: interactionsReducer },
        preloadedState: {
          interactions: {
            items: [],
            activeId: null,
            activeInteraction: null,
            formData: { type: 'meeting', dateTime: '', attendees: ['Dr. John', 'Dr. Jane'], topics: '', sentiment: undefined, outcome: '' },
            dirty: false,
            loading: false,
            saving: false,
            error: null,
          },
        },
      })

      store.dispatch(removeAttendee(0))
      expect(store.getState().interactions.formData.attendees).toEqual(['Dr. Jane'])
      expect(store.getState().interactions.dirty).toBe(true)
    })
  })

  describe('materials management', () => {
    it('should add material', () => {
      store.dispatch(addMaterial(mockMaterial))
      expect(store.getState().interactions.formData.materials).toContainEqual(mockMaterial)
      expect(store.getState().interactions.dirty).toBe(true)
    })

    it('should remove material', () => {
      store = configureStore({
        reducer: { interactions: interactionsReducer },
        preloadedState: {
          interactions: {
            items: [],
            activeId: null,
            activeInteraction: null,
            formData: { type: 'meeting', dateTime: '', attendees: [], topics: '', sentiment: undefined, outcome: '', materials: [mockMaterial] },
            dirty: false,
            loading: false,
            saving: false,
            error: null,
          },
        },
      })

      store.dispatch(removeMaterial('mat-1'))
      expect(store.getState().interactions.formData.materials).toEqual([])
      expect(store.getState().interactions.dirty).toBe(true)
    })
  })

  describe('resetForm action', () => {
    it('should reset form to initial state', () => {
      store = configureStore({
        reducer: { interactions: interactionsReducer },
        preloadedState: {
          interactions: {
            items: [mockInteraction],
            activeId: 'int-1',
            activeInteraction: mockInteraction,
            formData: { ...mockInteraction, topics: 'Modified topic' },
            dirty: true,
            loading: false,
            saving: false,
            error: null,
          },
        },
      })

      store.dispatch(resetForm())
      const state = store.getState().interactions

      expect(state.activeId).toBeNull()
      expect(state.activeInteraction).toBeNull()
      expect(state.formData.type).toBe('meeting')
      expect(state.formData.topics).toBe('')
      expect(state.dirty).toBe(false)
    })
  })

  describe('clearDirty action', () => {
    it('should clear dirty flag', () => {
      store = configureStore({
        reducer: { interactions: interactionsReducer },
        preloadedState: {
          interactions: {
            items: [],
            activeId: null,
            activeInteraction: null,
            formData: { type: 'meeting' as InteractionType, dateTime: '', attendees: [], topics: 'dirty', sentiment: undefined, outcome: '' },
            dirty: true,
            loading: false,
            saving: false,
            error: null,
          },
        },
      })

      store.dispatch(clearDirty())
      expect(store.getState().interactions.dirty).toBe(false)
    })
  })
})
