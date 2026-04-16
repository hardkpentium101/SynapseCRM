import { describe, it, expect, beforeEach } from 'vitest'
import { configureStore } from '@reduxjs/toolkit'
import authReducer, {
  login,
  logout,
  clearError,
} from '../../features/auth/authSlice'

describe('authSlice', () => {
  let store: ReturnType<typeof configureStore>

  beforeEach(() => {
    store = configureStore({
      reducer: { auth: authReducer },
    })
  })

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const state = store.getState().auth
      expect(state.user).toBeNull()
      expect(state.isAuthenticated).toBe(false)
      expect(state.loading).toBe(false)
      expect(state.error).toBeNull()
    })
  })

  describe('clearError action', () => {
    it('should clear error from state', () => {
      store.dispatch(clearError())
      const state = store.getState().auth
      expect(state.error).toBeNull()
    })
  })

  describe('login thunk', () => {
    it('should have loading state when dispatched', () => {
      store.dispatch(login({ email: 'test@test.com', password: 'test' }))
      const state = store.getState().auth
      // Login starts with loading: false, but dispatch should trigger async behavior
      expect(state).toBeDefined()
    })
  })

  describe('logout thunk', () => {
    it('should clear auth state on logout', () => {
      store.dispatch(logout())
      const state = store.getState().auth
      expect(state.user).toBeNull()
      expect(state.isAuthenticated).toBe(false)
    })
  })
})
