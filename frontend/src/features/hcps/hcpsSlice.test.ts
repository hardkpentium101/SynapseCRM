import { describe, it, expect, beforeEach } from 'vitest'
import { configureStore } from '@reduxjs/toolkit'
import hcpsReducer from '../../features/hcps/hcpsSlice'

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

  it('should have correct initial state', () => {
    const state = store.getState().hcps
    expect(state.searchResults).toEqual([])
  })
})
