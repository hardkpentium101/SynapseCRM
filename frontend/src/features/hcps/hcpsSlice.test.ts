import { describe, it, expect, beforeEach } from 'vitest'
import { configureStore } from '@reduxjs/toolkit'
import hcpsReducer, {
  setActiveHCP,
  clearSearch,
} from '../../features/hcps/hcpsSlice'

describe('hcpsSlice', () => {
  let store: ReturnType<typeof configureStore>

  const mockHcps = [
    {
      id: '1',
      name: 'Dr. Priya Sharma',
      specialty: 'Oncology',
      institution: 'Tata Memorial Hospital',
      email: 'priya@tata.org',
      phone: '+91 98765 43210',
      createdAt: '2025-01-01T00:00:00Z',
      updatedAt: '2025-01-01T00:00:00Z',
    },
    {
      id: '2',
      name: 'Dr. Rajesh Kumar',
      specialty: 'Cardiology',
      institution: 'AIIMS Delhi',
      email: 'rajesh@aiims.ac.in',
      createdAt: '2025-01-01T00:00:00Z',
      updatedAt: '2025-01-01T00:00:00Z',
    },
  ]

  beforeEach(() => {
    store = configureStore({
      reducer: { hcps: hcpsReducer },
    })
  })

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const state = store.getState().hcps
      expect(state.items).toEqual([])
      expect(state.searchResults).toEqual([])
      expect(state.activeId).toBeNull()
      expect(state.activeHCP).toBeNull()
      expect(state.loading).toBe(false)
      expect(state.error).toBeNull()
    })
  })

  describe('setActiveHCP action', () => {
    it('should set active HCP when valid id provided', () => {
      store = configureStore({
        reducer: { hcps: hcpsReducer },
        preloadedState: {
          hcps: {
            items: mockHcps,
            searchResults: [],
            activeId: null,
            activeHCP: null,
            loading: false,
            error: null,
          },
        },
      })

      store.dispatch(setActiveHCP('1'))
      const state = store.getState().hcps

      expect(state.activeId).toBe('1')
      expect(state.activeHCP).toEqual(mockHcps[0])
    })

    it('should clear active HCP when null provided', () => {
      store = configureStore({
        reducer: { hcps: hcpsReducer },
        preloadedState: {
          hcps: {
            items: mockHcps,
            searchResults: [],
            activeId: '1',
            activeHCP: mockHcps[0],
            loading: false,
            error: null,
          },
        },
      })

      store.dispatch(setActiveHCP(null))
      const state = store.getState().hcps

      expect(state.activeId).toBeNull()
      expect(state.activeHCP).toBeNull()
    })
  })

  describe('clearSearch action', () => {
    it('should clear search results', () => {
      store = configureStore({
        reducer: { hcps: hcpsReducer },
        preloadedState: {
          hcps: {
            items: [],
            searchResults: mockHcps,
            activeId: null,
            activeHCP: null,
            loading: false,
            error: null,
          },
        },
      })

      store.dispatch(clearSearch())
      expect(store.getState().hcps.searchResults).toEqual([])
    })
  })
})
