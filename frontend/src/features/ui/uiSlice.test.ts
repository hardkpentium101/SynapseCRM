import { describe, it, expect, beforeEach } from 'vitest'
import { configureStore } from '@reduxjs/toolkit'
import uiReducer, {
  setSplitPosition,
  setLeftPanelMode,
  addNotification,
  removeNotification,
  toggleSidebar,
} from '../../features/ui/uiSlice'

describe('uiSlice', () => {
  let store: ReturnType<typeof configureStore>

  beforeEach(() => {
    store = configureStore({
      reducer: { ui: uiReducer },
    })
  })

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const state = store.getState().ui
      expect(state.splitPosition).toBe(60)
      expect(state.leftPanelMode).toBe('create')
      expect(state.notifications).toEqual([])
      expect(state.sidebarCollapsed).toBe(false)
    })
  })

  describe('setSplitPosition action', () => {
    it('should set split position within bounds', () => {
      store.dispatch(setSplitPosition(50))
      expect(store.getState().ui.splitPosition).toBe(50)
    })

    it('should clamp to minimum (20%)', () => {
      store.dispatch(setSplitPosition(10))
      expect(store.getState().ui.splitPosition).toBe(20)
    })

    it('should clamp to maximum (80%)', () => {
      store.dispatch(setSplitPosition(90))
      expect(store.getState().ui.splitPosition).toBe(80)
    })
  })

  describe('setLeftPanelMode action', () => {
    it('should set to view mode', () => {
      store.dispatch(setLeftPanelMode('view'))
      expect(store.getState().ui.leftPanelMode).toBe('view')
    })

    it('should set to edit mode', () => {
      store.dispatch(setLeftPanelMode('edit'))
      expect(store.getState().ui.leftPanelMode).toBe('edit')
    })

    it('should set to create mode', () => {
      store.dispatch(setLeftPanelMode('create'))
      expect(store.getState().ui.leftPanelMode).toBe('create')
    })
  })

  describe('notifications', () => {
    it('should add notification with generated id', () => {
      store.dispatch(addNotification({ kind: 'success', message: 'Saved!' }))
      const notifications = store.getState().ui.notifications

      expect(notifications).toHaveLength(1)
      expect(notifications[0].message).toBe('Saved!')
      expect(notifications[0].kind).toBe('success')
      expect(notifications[0].id).toBeDefined()
    })

    it('should add multiple notifications', () => {
      store.dispatch(addNotification({ kind: 'success', message: 'First' }))
      store.dispatch(addNotification({ kind: 'error', message: 'Second' }))
      store.dispatch(addNotification({ kind: 'info', message: 'Third' }))

      expect(store.getState().ui.notifications).toHaveLength(3)
    })

    it('should remove notification by id', () => {
      store.dispatch(addNotification({ kind: 'success', message: 'To remove' }))
      const id = store.getState().ui.notifications[0].id

      store.dispatch(removeNotification(id))
      expect(store.getState().ui.notifications).toHaveLength(0)
    })
  })

  describe('toggleSidebar action', () => {
    it('should toggle sidebar state', () => {
      expect(store.getState().ui.sidebarCollapsed).toBe(false)
      
      store.dispatch(toggleSidebar())
      expect(store.getState().ui.sidebarCollapsed).toBe(true)
      
      store.dispatch(toggleSidebar())
      expect(store.getState().ui.sidebarCollapsed).toBe(false)
    })
  })
})
