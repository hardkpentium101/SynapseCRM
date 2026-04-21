import { describe, it, expect, vi, beforeEach } from 'vitest'
import { configureStore } from '@reduxjs/toolkit'
import interactionsReducer, { setFormData, setHCP, addMaterial } from './interactionsSlice'
import type { HCP, Material } from '../../types'

vi.mock('../../services/api', () => ({
  api: {
    chat: vi.fn(),
    getHcp: vi.fn(),
    getMaterial: vi.fn(),
  },
}))

describe('Chat Response Form Update', () => {
  let store: ReturnType<typeof configureStore>

  beforeEach(() => {
    store = configureStore({
      reducer: {
        interactions: interactionsReducer,
      },
    })
  })

  describe('setHCP action', () => {
    it('should set hcp_id and hcp object in formData', () => {
      const mockHCP: HCP = {
        id: 'hcp-123',
        name: 'Dr. Priya Sharma',
        specialty: 'Oncology',
        institution: 'Apollo Hospital',
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

      store.dispatch(setHCP(mockHCP))

      const state = store.getState().interactions
      expect(state.formData.hcpId).toBe('hcp-123')
      expect(state.formData.hcp).toEqual(mockHCP)
      expect(state.dirty).toBe(true)
    })
  })

  describe('addMaterial action', () => {
    it('should add material to formData.materials array', () => {
      const mockMaterial: Material = {
        id: 'mat-456',
        name: 'Neuroplus Brochure',
        type: 'pdf',
        createdAt: '2024-01-01',
      }

      store.dispatch(addMaterial(mockMaterial))

      const state = store.getState().interactions
      expect(state.formData.materials).toHaveLength(1)
      expect(state.formData.materials?.[0]).toEqual(mockMaterial)
      expect(state.dirty).toBe(true)
    })

    it('should append materials if array already has items', () => {
      const material1: Material = {
        id: 'mat-001',
        name: 'Neuroplus Brochure',
        type: 'pdf',
        createdAt: '2024-01-01',
      }
      const material2: Material = {
        id: 'mat-002',
        name: 'OncoBoost Sample',
        type: 'physical',
        createdAt: '2024-01-01',
      }

      store.dispatch(addMaterial(material1))
      store.dispatch(addMaterial(material2))

      const state = store.getState().interactions
      expect(state.formData.materials).toHaveLength(2)
      expect(state.formData.materials?.[0].id).toBe('mat-001')
      expect(state.formData.materials?.[1].id).toBe('mat-002')
    })
  })

  describe('setFormData action', () => {
    it('should merge partial interaction data into formData', () => {
      const partialData = {
        topics: 'Oncoboost efficacy discussion',
        sentiment: 'positive' as const,
        attendees: ['rajesh'],
      }

      store.dispatch(setFormData(partialData))

      const state = store.getState().interactions
      expect(state.formData.topics).toBe('Oncoboost efficacy discussion')
      expect(state.formData.sentiment).toBe('positive')
      expect(state.formData.attendees).toEqual(['rajesh'])
      expect(state.dirty).toBe(true)
    })

    it('should merge multiple fields at once', () => {
      store.dispatch(setFormData({
        type: 'meeting',
        outcome: 'Follow up next week',
      }))

      const state = store.getState().interactions
      expect(state.formData.type).toBe('meeting')
      expect(state.formData.outcome).toBe('Follow up next week')
    })
  })

  describe('full chat response simulation', () => {
    it('should update form with HCP, materials, and interaction fields', async () => {
      const { api } = await import('../../services/api')

      const mockHCP: HCP = {
        id: 'hcp-123',
        name: 'Dr. Sharma',
        specialty: 'Oncology',
        institution: 'Apollo',
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }
      const mockMaterial: Material = {
        id: 'mat-neuroplus',
        name: 'Neuroplus',
        type: 'pdf',
        createdAt: '2024-01-01',
      }

      vi.mocked(api.getHcp).mockResolvedValueOnce(mockHCP)
      vi.mocked(api.getMaterial).mockResolvedValueOnce(mockMaterial)

      const mockResponse = {
        message: 'Logged your interaction with Dr. Sharma',
        session_id: 'session-123',
        success: true,
        interaction: {
          hcp_id: 'hcp-123',
          type: 'meeting',
          date_time: '2024-01-15T12:00',
          topics: ['oncoboost efficacy'],
          sentiment: 'positive',
          attendees: ['rajesh'],
          materials: ['mat-neuroplus'],
        },
      }

      vi.mocked(api.chat).mockResolvedValueOnce(mockResponse)

      // Simulate the chat response handling (what happens in ChatPlaceholder)
      if (mockResponse.interaction) {
        const interactionData = mockResponse.interaction

        if (interactionData.hcp_id) {
          const hcp = await (api as any).getHcp(interactionData.hcp_id)
          store.dispatch(setHCP(hcp))
        }

        if (interactionData.materials && Array.isArray(interactionData.materials)) {
          for (const materialId of interactionData.materials) {
            const material = await (api as any).getMaterial(materialId)
            store.dispatch(addMaterial(material))
          }
        }

        const { hcp_id, materials, ...formFields } = interactionData
        store.dispatch(setFormData({
          ...formFields,
          hcpId: interactionData.hcp_id || (interactionData as any).hcpId,
        }))
      }

      const state = store.getState().interactions

      expect(state.formData.hcpId).toBe('hcp-123')
      expect(state.formData.hcp?.name).toBe('Dr. Sharma')
      expect(state.formData.materials).toHaveLength(1)
      expect(state.formData.materials?.[0].name).toBe('Neuroplus')
      expect(state.formData.topics).toEqual(['oncoboost efficacy'])
      expect(state.formData.sentiment).toBe('positive')
      expect(state.formData.attendees).toEqual(['rajesh'])
    })
  })
})