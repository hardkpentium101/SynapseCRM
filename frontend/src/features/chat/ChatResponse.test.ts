import { describe, it, expect, vi, beforeEach } from 'vitest'
import { configureStore } from '@reduxjs/toolkit'
import interactionsReducer, { setHCP, addMaterial, updateFormField } from '../interactions/interactionsSlice'
import followUpsReducer, { addSuggestion } from '../followUps/followUpsSlice'
import type { HCP, Material, FollowUp } from '../../types'

describe('ChatPlaceholder — material and suggestion handling', () => {
  let store: ReturnType<typeof configureStore>

  beforeEach(() => {
    store = configureStore({
      reducer: {
        interactions: interactionsReducer,
        followUps: followUpsReducer,
      },
    })
  })

  describe('setHCP from interaction data (reference pattern)', () => {
    it('should handle camelCase hcpId', () => {
      const interactionData = {
        hcpId: 'hcp-123',
        hcpName: 'Dr. Priya Sharma',
        hcpSpecialty: 'Oncology',
        hcpInstitution: 'Apollo Hospital',
      }

      if (interactionData.hcpId || (interactionData as any).hcp_id) {
        const hcpObj: HCP = {
          id: interactionData.hcpId || (interactionData as any).hcp_id || '',
          name: interactionData.hcpName || (interactionData as any).hcp_name || '',
          specialty: interactionData.hcpSpecialty || (interactionData as any).hcp_specialty || '',
          institution: interactionData.hcpInstitution || (interactionData as any).hcp_institution || '',
        }
        store.dispatch(setHCP(hcpObj))
      }

      const state = store.getState().interactions
      expect(state.formData.hcpId).toBe('hcp-123')
      expect(state.formData.hcp?.name).toBe('Dr. Priya Sharma')
      expect(state.formData.hcp?.specialty).toBe('Oncology')
      expect(state.formData.hcp?.institution).toBe('Apollo Hospital')
    })

    it('should handle snake_case hcp_id', () => {
      const interactionData = {
        hcp_id: 'hcp-456',
        hcp_name: 'Dr. Kumar',
        hcp_specialty: 'Cardiology',
        hcp_institution: 'Max Hospital',
      }

      if (interactionData.hcpId || (interactionData as any).hcp_id) {
        const hcpObj: HCP = {
          id: interactionData.hcpId || (interactionData as any).hcp_id || '',
          name: interactionData.hcpName || (interactionData as any).hcp_name || '',
          specialty: interactionData.hcpSpecialty || (interactionData as any).hcp_specialty || '',
          institution: interactionData.hcpInstitution || (interactionData as any).hcp_institution || '',
        }
        store.dispatch(setHCP(hcpObj))
      }

      const state = store.getState().interactions
      expect(state.formData.hcpId).toBe('hcp-456')
      expect(state.formData.hcp?.name).toBe('Dr. Kumar')
    })
  })

  describe('materials from interaction data (backend returns string names)', () => {
    it('should add material from string name', () => {
      const interactionData = {
        hcpId: 'hcp-123',
        hcpName: 'Dr. Sharma',
        type: 'meeting',
        materials: ['NeuroPlus Clinical Summary'],
      }

      if (interactionData.materials && Array.isArray(interactionData.materials)) {
        for (const mat of interactionData.materials) {
          if (mat && typeof mat === 'string' && mat.trim()) {
            const material: Material = {
              id: `mat-${crypto.randomUUID()}`,
              name: mat,
              type: 'pdf',
              createdAt: new Date().toISOString(),
            }
            store.dispatch(addMaterial(material))
          } else if (mat && typeof mat === 'object' && mat.id) {
            const material: Material = {
              id: mat.id,
              name: mat.name,
              type: (mat.type as Material['type']) || 'pdf',
              description: mat.description,
              createdAt: new Date().toISOString(),
            }
            store.dispatch(addMaterial(material))
          }
        }
      }

      const state = store.getState().interactions
      expect(state.formData.materials).toHaveLength(1)
      expect(state.formData.materials?.[0].name).toBe('NeuroPlus Clinical Summary')
      expect(state.formData.materials?.[0].type).toBe('pdf')
      expect(state.formData.materials?.[0].id).toMatch(/^mat-/)
      expect(state.dirty).toBe(true)
    })

    it('should add multiple material string names', () => {
      const interactionData = {
        hcpId: 'hcp-123',
        materials: ['NeuroPlus Clinical Summary', 'OncoBoost Phase III Brochure', 'CardioProtect Sample Kit'],
      }

      if (interactionData.materials && Array.isArray(interactionData.materials)) {
        for (const mat of interactionData.materials) {
          if (mat && typeof mat === 'string' && mat.trim()) {
            const material: Material = {
              id: `mat-${crypto.randomUUID()}`,
              name: mat,
              type: 'pdf',
              createdAt: new Date().toISOString(),
            }
            store.dispatch(addMaterial(material))
          } else if (mat && typeof mat === 'object' && mat.id) {
            const material: Material = {
              id: mat.id,
              name: mat.name,
              type: (mat.type as Material['type']) || 'pdf',
              description: mat.description,
              createdAt: new Date().toISOString(),
            }
            store.dispatch(addMaterial(material))
          }
        }
      }

      const state = store.getState().interactions
      expect(state.formData.materials).toHaveLength(3)
      expect(state.formData.materials?.[0].name).toBe('NeuroPlus Clinical Summary')
      expect(state.formData.materials?.[1].name).toBe('OncoBoost Phase III Brochure')
      expect(state.formData.materials?.[2].name).toBe('CardioProtect Sample Kit')
    })

    it('should skip empty or whitespace-only material strings', () => {
      const interactionData = {
        hcpId: 'hcp-123',
        materials: ['NeuroPlus', '', '   ', undefined, null],
      }

      if (interactionData.materials && Array.isArray(interactionData.materials)) {
        for (const mat of interactionData.materials) {
          if (mat && typeof mat === 'string' && mat.trim()) {
            store.dispatch(addMaterial({
              id: `mat-${crypto.randomUUID()}`,
              name: mat,
              type: 'pdf',
              createdAt: new Date().toISOString(),
            }))
          } else if (mat && typeof mat === 'object' && (mat as any).id) {
            store.dispatch(addMaterial({
              id: (mat as any).id,
              name: (mat as any).name,
              type: ((mat as any).type as Material['type']) || 'pdf',
              createdAt: new Date().toISOString(),
            }))
          }
        }
      }

      const state = store.getState().interactions
      expect(state.formData.materials).toHaveLength(1)
      expect(state.formData.materials?.[0].name).toBe('NeuroPlus')
    })

    it('should handle empty materials array', () => {
      const interactionData = {
        hcpId: 'hcp-123',
        materials: [],
      }

      if (interactionData.materials && Array.isArray(interactionData.materials)) {
        for (const mat of interactionData.materials) {
          if (mat && typeof mat === 'string' && mat.trim()) {
            store.dispatch(addMaterial({
              id: `mat-${crypto.randomUUID()}`,
              name: mat,
              type: 'pdf',
              createdAt: new Date().toISOString(),
            }))
          } else if (mat && typeof mat === 'object' && (mat as any).id) {
            store.dispatch(addMaterial({
              id: (mat as any).id,
              name: (mat as any).name,
              type: ((mat as any).type as Material['type']) || 'pdf',
              createdAt: new Date().toISOString(),
            }))
          }
        }
      }

      const state = store.getState().interactions
      expect(state.formData.materials).toBeUndefined()
    })

    it('should handle missing materials field', () => {
      const interactionData = {
        hcpId: 'hcp-123',
        type: 'meeting',
      }

      if (interactionData.materials && Array.isArray(interactionData.materials)) {
        for (const mat of interactionData.materials) {
          if (mat && typeof mat === 'string' && mat.trim()) {
            store.dispatch(addMaterial({
              id: `mat-${crypto.randomUUID()}`,
              name: mat,
              type: 'pdf',
              createdAt: new Date().toISOString(),
            }))
          } else if (mat && typeof mat === 'object' && (mat as any).id) {
            store.dispatch(addMaterial({
              id: (mat as any).id,
              name: (mat as any).name,
              type: ((mat as any).type as Material['type']) || 'pdf',
              createdAt: new Date().toISOString(),
            }))
          }
        }
      }

      const state = store.getState().interactions
      expect(state.formData.materials).toBeUndefined()
    })

    it('should still handle object materials (fallback)', () => {
      const interactionData = {
        hcpId: 'hcp-123',
        materials: [
          { id: 'mat-001', name: 'NeuroPlus Clinical Summary', type: 'pdf', description: 'Summary' },
        ],
      }

      if (interactionData.materials && Array.isArray(interactionData.materials)) {
        for (const mat of interactionData.materials) {
          if (mat && typeof mat === 'string' && mat.trim()) {
            store.dispatch(addMaterial({
              id: `mat-${crypto.randomUUID()}`,
              name: mat,
              type: 'pdf',
              createdAt: new Date().toISOString(),
            }))
          } else if (mat && typeof mat === 'object' && (mat as any).id) {
            store.dispatch(addMaterial({
              id: (mat as any).id,
              name: (mat as any).name,
              type: ((mat as any).type as Material['type']) || 'pdf',
              description: (mat as any).description,
              createdAt: new Date().toISOString(),
            }))
          }
        }
      }

      const state = store.getState().interactions
      expect(state.formData.materials).toHaveLength(1)
      expect(state.formData.materials?.[0].id).toBe('mat-001')
      expect(state.formData.materials?.[0].name).toBe('NeuroPlus Clinical Summary')
      expect(state.formData.materials?.[0].description).toBe('Summary')
    })

    it('should handle mixed string and object materials', () => {
      const interactionData = {
        hcpId: 'hcp-123',
        materials: [
          'NeuroPlus Clinical Summary',
          { id: 'mat-002', name: 'OncoBoost Brochure', type: 'pdf' },
        ],
      }

      if (interactionData.materials && Array.isArray(interactionData.materials)) {
        for (const mat of interactionData.materials) {
          if (mat && typeof mat === 'string' && mat.trim()) {
            store.dispatch(addMaterial({
              id: `mat-${crypto.randomUUID()}`,
              name: mat,
              type: 'pdf',
              createdAt: new Date().toISOString(),
            }))
          } else if (mat && typeof mat === 'object' && (mat as any).id) {
            store.dispatch(addMaterial({
              id: (mat as any).id,
              name: (mat as any).name,
              type: ((mat as any).type as Material['type']) || 'pdf',
              createdAt: new Date().toISOString(),
            }))
          }
        }
      }

      const state = store.getState().interactions
      expect(state.formData.materials).toHaveLength(2)
      expect(state.formData.materials?.[0].name).toBe('NeuroPlus Clinical Summary')
      expect(state.formData.materials?.[1].id).toBe('mat-002')
    })
  })

  describe('AI suggestions from chat response (camelCase after camelcase-keys)', () => {
    it('should convert dueInDays to dueDate and dispatch suggestion', () => {
      const mockSuggestions = [
        { type: 'call', description: 'Follow up on efficacy data discussed', dueInDays: 7, priority: 'high' },
      ]

      for (const suggestion of mockSuggestions) {
        if (suggestion && suggestion.description) {
          const dueDate = suggestion.dueDate
            ? suggestion.dueDate
            : suggestion.dueInDays
              ? new Date(Date.now() + suggestion.dueInDays * 86400000).toISOString()
              : undefined

          const typeMap: Record<string, FollowUp['type']> = {
            call: 'call',
            meeting: 'follow_up_meeting',
            email: 'other',
            sendMaterial: 'send_material',
            send_material: 'send_material',
            sampleRequest: 'sample_request',
            sample_request: 'sample_request',
          }

          const followUp: FollowUp = {
            id: suggestion.id || crypto.randomUUID(),
            description: suggestion.description,
            type: typeMap[suggestion.type || ''] || 'other',
            status: 'pending',
            aiGenerated: true,
            dueDate,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          }
          store.dispatch(addSuggestion(followUp))
        }
      }

      const state = store.getState().followUps
      expect(state.suggestions).toHaveLength(1)
      expect(state.suggestions[0].description).toBe('Follow up on efficacy data discussed')
      expect(state.suggestions[0].type).toBe('call')
      expect(state.suggestions[0].status).toBe('pending')
      expect(state.suggestions[0].aiGenerated).toBe(true)
      expect(state.suggestions[0].dueDate).toBeDefined()

      const dueDate = new Date(state.suggestions[0].dueDate!)
      const expectedDate = new Date(Date.now() + 7 * 86400000)
      expect(Math.abs(dueDate.getTime() - expectedDate.getTime())).toBeLessThan(2000)
    })

    it('should handle explicit dueDate string', () => {
      const mockSuggestions = [
        { type: 'meeting', description: 'Schedule follow-up meeting', dueDate: '2024-02-01T10:00:00Z' },
      ]

      for (const suggestion of mockSuggestions) {
        if (suggestion && suggestion.description) {
          const dueDate = suggestion.dueDate
            ? suggestion.dueDate
            : suggestion.dueInDays
              ? new Date(Date.now() + suggestion.dueInDays * 86400000).toISOString()
              : undefined

          const typeMap: Record<string, FollowUp['type']> = {
            call: 'call',
            meeting: 'follow_up_meeting',
            email: 'other',
            sendMaterial: 'send_material',
            send_material: 'send_material',
            sampleRequest: 'sample_request',
            sample_request: 'sample_request',
          }

          const followUp: FollowUp = {
            id: suggestion.id || crypto.randomUUID(),
            description: suggestion.description,
            type: typeMap[suggestion.type || ''] || 'other',
            status: 'pending',
            aiGenerated: true,
            dueDate,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          }
          store.dispatch(addSuggestion(followUp))
        }
      }

      const state = store.getState().followUps
      expect(state.suggestions[0].dueDate).toBe('2024-02-01T10:00:00Z')
    })

    it('should map camelCase and snake_case suggestion types to FollowUp types', () => {
      const mockSuggestions = [
        { type: 'call', description: 'Call follow-up', dueInDays: 3 },
        { type: 'meeting', description: 'Meeting follow-up', dueInDays: 14 },
        { type: 'email', description: 'Email follow-up', dueInDays: 1 },
        { type: 'sendMaterial', description: 'Send materials (camelCase)', dueInDays: 2 },
        { type: 'send_material', description: 'Send materials (snake_case)', dueInDays: 2 },
        { type: 'sampleRequest', description: 'Request samples (camelCase)', dueInDays: 5 },
        { type: 'sample_request', description: 'Request samples (snake_case)', dueInDays: 5 },
        { type: 'unknown_type', description: 'Unknown type', dueInDays: 7 },
        { description: 'No type field' },
      ]

      const typeMap: Record<string, FollowUp['type']> = {
        call: 'call',
        meeting: 'follow_up_meeting',
        email: 'other',
        sendMaterial: 'send_material',
        send_material: 'send_material',
        sampleRequest: 'sample_request',
        sample_request: 'sample_request',
      }

      for (const suggestion of mockSuggestions) {
        if (suggestion && suggestion.description) {
          const dueDate = suggestion.dueInDays
            ? new Date(Date.now() + suggestion.dueInDays * 86400000).toISOString()
            : undefined

          const followUp: FollowUp = {
            id: suggestion.id || crypto.randomUUID(),
            description: suggestion.description,
            type: typeMap[suggestion.type || ''] || 'other',
            status: 'pending',
            aiGenerated: true,
            dueDate,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          }
          store.dispatch(addSuggestion(followUp))
        }
      }

      const state = store.getState().followUps
      expect(state.suggestions).toHaveLength(9)
      expect(state.suggestions[0].type).toBe('call')
      expect(state.suggestions[1].type).toBe('follow_up_meeting')
      expect(state.suggestions[2].type).toBe('other')
      expect(state.suggestions[3].type).toBe('send_material')
      expect(state.suggestions[4].type).toBe('send_material')
      expect(state.suggestions[5].type).toBe('sample_request')
      expect(state.suggestions[6].type).toBe('sample_request')
      expect(state.suggestions[7].type).toBe('other')
      expect(state.suggestions[8].type).toBe('other')
    })

    it('should handle multiple suggestions', () => {
      const mockSuggestions = [
        { type: 'call', description: 'Follow up call', dueInDays: 3, priority: 'high' },
        { type: 'meeting', description: 'Follow up meeting', dueInDays: 14, priority: 'medium' },
      ]

      const typeMap: Record<string, FollowUp['type']> = {
        call: 'call',
        meeting: 'follow_up_meeting',
        email: 'other',
        sendMaterial: 'send_material',
        send_material: 'send_material',
        sampleRequest: 'sample_request',
        sample_request: 'sample_request',
      }

      for (const suggestion of mockSuggestions) {
        if (suggestion && suggestion.description) {
          const dueDate = suggestion.dueInDays
            ? new Date(Date.now() + suggestion.dueInDays * 86400000).toISOString()
            : undefined

          const followUp: FollowUp = {
            id: suggestion.id || crypto.randomUUID(),
            description: suggestion.description,
            type: typeMap[suggestion.type || ''] || 'other',
            status: 'pending',
            aiGenerated: true,
            dueDate,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          }
          store.dispatch(addSuggestion(followUp))
        }
      }

      const state = store.getState().followUps
      expect(state.suggestions).toHaveLength(2)
    })

    it('should skip suggestions without description', () => {
      const mockSuggestions = [
        { type: 'call', description: 'Valid suggestion', dueInDays: 7 },
        { type: 'call' },
        { type: 'call', description: '' },
        null,
      ]

      const typeMap: Record<string, FollowUp['type']> = {
        call: 'call',
        meeting: 'follow_up_meeting',
        email: 'other',
        sendMaterial: 'send_material',
        send_material: 'send_material',
        sampleRequest: 'sample_request',
        sample_request: 'sample_request',
      }

      for (const suggestion of mockSuggestions as any[]) {
        if (suggestion && suggestion.description) {
          const dueDate = suggestion.dueInDays
            ? new Date(Date.now() + suggestion.dueInDays * 86400000).toISOString()
            : undefined

          const followUp: FollowUp = {
            id: suggestion.id || crypto.randomUUID(),
            description: suggestion.description,
            type: typeMap[suggestion.type || ''] || 'other',
            status: 'pending',
            aiGenerated: true,
            dueDate,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          }
          store.dispatch(addSuggestion(followUp))
        }
      }

      const state = store.getState().followUps
      expect(state.suggestions).toHaveLength(1)
      expect(state.suggestions[0].description).toBe('Valid suggestion')
    })
  })

  describe('full chat response — materials (string names) + suggestions (camelCase) + HCP combined', () => {
    it('should process complete camelCase chat response after camelcase-keys', () => {
      const mockResponse = {
        message: 'Interaction logged for Dr. Sharma',
        sessionId: 'session-123',
        success: true,
        interaction: {
          hcpId: 'hcp-123',
          hcpName: 'Dr. Priya Sharma',
          hcpSpecialty: 'Oncology',
          hcpInstitution: 'Apollo Hospital',
          type: 'meeting',
          dateTime: '2024-01-15T12:00:00Z',
          topics: ['oncoboost efficacy', 'clinical trials'],
          sentiment: 'positive',
          attendees: ['rajesh'],
          outcome: 'Positive engagement',
          notes: 'HCP interested in Phase III data',
          materials: ['NeuroPlus Clinical Summary', 'OncoBoost Phase III Brochure'],
        },
        aiSuggestions: [
          { type: 'call', description: 'Follow up on efficacy data', dueInDays: 7, priority: 'high' },
          { type: 'meeting', description: 'Schedule Phase III data review', dueInDays: 14, priority: 'medium' },
          { type: 'sendMaterial', description: 'Send additional materials', dueInDays: 3, priority: 'low' },
        ],
      }

      const interactionData = mockResponse.interaction

      if (interactionData.hcpId || (interactionData as any).hcp_id) {
        const hcpObj: HCP = {
          id: interactionData.hcpId || (interactionData as any).hcp_id || '',
          name: interactionData.hcpName || (interactionData as any).hcp_name || '',
          specialty: interactionData.hcpSpecialty || (interactionData as any).hcp_specialty || '',
          institution: interactionData.hcpInstitution || (interactionData as any).hcp_institution || '',
        }
        store.dispatch(setHCP(hcpObj))
      }

      if (interactionData.dateTime || (interactionData as any).date_time) {
        store.dispatch(updateFormField({ field: 'dateTime', value: interactionData.dateTime || (interactionData as any).date_time }))
      }

      if (interactionData.type) {
        store.dispatch(updateFormField({ field: 'type', value: interactionData.type }))
      }

      if (interactionData.topics && Array.isArray(interactionData.topics) && interactionData.topics.length > 0) {
        store.dispatch(updateFormField({ field: 'topics', value: interactionData.topics.join(', ') }))
      }

      if (interactionData.attendees && Array.isArray(interactionData.attendees)) {
        store.dispatch(updateFormField({ field: 'attendees', value: interactionData.attendees }))
      }

      if (interactionData.sentiment) {
        store.dispatch(updateFormField({ field: 'sentiment', value: interactionData.sentiment }))
      }

      if (interactionData.outcome) {
        store.dispatch(updateFormField({ field: 'outcome', value: interactionData.outcome }))
      }

      if (interactionData.notes) {
        store.dispatch(updateFormField({ field: 'notes', value: interactionData.notes }))
      }

      if (interactionData.materials && Array.isArray(interactionData.materials)) {
        for (const mat of interactionData.materials) {
          if (mat && typeof mat === 'string' && mat.trim()) {
            const material: Material = {
              id: `mat-${crypto.randomUUID()}`,
              name: mat,
              type: 'pdf',
              createdAt: new Date().toISOString(),
            }
            store.dispatch(addMaterial(material))
          } else if (mat && typeof mat === 'object' && (mat as any).id) {
            const material: Material = {
              id: (mat as any).id,
              name: (mat as any).name,
              type: ((mat as any).type as Material['type']) || 'pdf',
              description: (mat as any).description,
              createdAt: new Date().toISOString(),
            }
            store.dispatch(addMaterial(material))
          }
        }
      }

      if (mockResponse.aiSuggestions && Array.isArray(mockResponse.aiSuggestions)) {
        for (const suggestion of mockResponse.aiSuggestions) {
          if (suggestion && suggestion.description) {
            const dueDate = suggestion.dueDate
              ? suggestion.dueDate
              : suggestion.dueInDays
                ? new Date(Date.now() + suggestion.dueInDays * 86400000).toISOString()
                : undefined

            const typeMap: Record<string, FollowUp['type']> = {
              call: 'call',
              meeting: 'follow_up_meeting',
              email: 'other',
              sendMaterial: 'send_material',
              send_material: 'send_material',
              sampleRequest: 'sample_request',
              sample_request: 'sample_request',
            }

            const followUp: FollowUp = {
              id: suggestion.id || crypto.randomUUID(),
              description: suggestion.description,
              type: typeMap[suggestion.type || ''] || 'other',
              status: 'pending',
              aiGenerated: true,
              dueDate,
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
            }
            store.dispatch(addSuggestion(followUp))
          }
        }
      }

      const interactionsState = store.getState().interactions
      const followUpsState = store.getState().followUps

      expect(interactionsState.formData.hcpId).toBe('hcp-123')
      expect(interactionsState.formData.hcp?.name).toBe('Dr. Priya Sharma')
      expect(interactionsState.formData.type).toBe('meeting')
      expect(interactionsState.formData.sentiment).toBe('positive')
      expect(interactionsState.formData.outcome).toBe('Positive engagement')
      expect(interactionsState.formData.materials).toHaveLength(2)
      expect(interactionsState.formData.materials?.[0].name).toBe('NeuroPlus Clinical Summary')
      expect(interactionsState.formData.materials?.[1].name).toBe('OncoBoost Phase III Brochure')
      expect(interactionsState.dirty).toBe(true)

      expect(followUpsState.suggestions).toHaveLength(3)
      expect(followUpsState.suggestions[0].description).toBe('Follow up on efficacy data')
      expect(followUpsState.suggestions[0].type).toBe('call')
      expect(followUpsState.suggestions[1].description).toBe('Schedule Phase III data review')
      expect(followUpsState.suggestions[1].type).toBe('follow_up_meeting')
      expect(followUpsState.suggestions[2].description).toBe('Send additional materials')
      expect(followUpsState.suggestions[2].type).toBe('send_material')
    })
  })
})
