import { describe, it, expect } from 'vitest'
import type {
  User,
  HCP,
  Interaction,
  Material,
  Sample,
  FollowUp,
  UserRole,
  Sentiment,
  InteractionType,
} from './index'

describe('types', () => {
  describe('User', () => {
    it('should have required fields', () => {
      const user: User = {
        id: '1',
        email: 'test@test.com',
        name: 'Test User',
        role: 'rep',
        createdAt: '2025-01-01T00:00:00Z',
        updatedAt: '2025-01-01T00:00:00Z',
      }

      expect(user.id).toBe('1')
      expect(user.email).toBe('test@test.com')
      expect(user.role).toBe('rep')
    })

    it('should allow optional territory', () => {
      const user: User = {
        id: '1',
        email: 'test@test.com',
        name: 'Test User',
        role: 'rep',
        territory: 'North India',
        createdAt: '2025-01-01T00:00:00Z',
        updatedAt: '2025-01-01T00:00:00Z',
      }

      expect(user.territory).toBe('North India')
    })
  })

  describe('HCP', () => {
    it('should have required fields', () => {
      const hcp: HCP = {
        id: '1',
        name: 'Dr. Sharma',
        createdAt: '2025-01-01T00:00:00Z',
        updatedAt: '2025-01-01T00:00:00Z',
      }

      expect(hcp.name).toBe('Dr. Sharma')
      expect(hcp.specialty).toBeUndefined()
    })
  })

  describe('Interaction', () => {
    it('should have required fields', () => {
      const interaction: Interaction = {
        id: '1',
        hcpId: 'hcp-1',
        userId: 'user-1',
        type: 'meeting',
        dateTime: '2025-04-16T10:00:00Z',
        attendees: [],
        topics: 'Test topic',
        createdAt: '2025-01-01T00:00:00Z',
        updatedAt: '2025-01-01T00:00:00Z',
      }

      expect(interaction.type).toBe('meeting')
      expect(interaction.attendees).toEqual([])
    })

    it('should allow optional sentiment', () => {
      const interaction: Interaction = {
        id: '1',
        hcpId: 'hcp-1',
        userId: 'user-1',
        type: 'meeting',
        dateTime: '2025-04-16T10:00:00Z',
        attendees: [],
        topics: 'Test',
        sentiment: 'positive',
        createdAt: '2025-01-01T00:00:00Z',
        updatedAt: '2025-01-01T00:00:00Z',
      }

      expect(interaction.sentiment).toBe('positive')
    })
  })

  describe('enums', () => {
    it('should have valid UserRole values', () => {
      const roles: UserRole[] = ['rep', 'manager', 'admin']
      roles.forEach(role => expect(typeof role).toBe('string'))
    })

    it('should have valid Sentiment values', () => {
      const sentiments: Sentiment[] = ['positive', 'neutral', 'negative']
      sentiments.forEach(s => expect(typeof s).toBe('string'))
    })

    it('should have valid InteractionType values', () => {
      const types: InteractionType[] = ['meeting', 'call', 'conference', 'email']
      types.forEach(type => expect(typeof type).toBe('string'))
    })
  })

  describe('Material', () => {
    it('should have required fields', () => {
      const material: Material = {
        id: '1',
        name: 'Brochure',
        type: 'pdf',
        createdAt: '2025-01-01T00:00:00Z',
      }

      expect(material.name).toBe('Brochure')
      expect(material.type).toBe('pdf')
    })
  })

  describe('Sample', () => {
    it('should have required fields', () => {
      const sample: Sample = {
        id: '1',
        productName: 'OncoBoost',
        quantity: 10,
        createdAt: '2025-01-01T00:00:00Z',
      }

      expect(sample.productName).toBe('OncoBoost')
      expect(sample.quantity).toBe(10)
    })
  })

  describe('FollowUp', () => {
    it('should have required fields', () => {
      const followUp: FollowUp = {
        id: '1',
        type: 'follow_up_meeting',
        description: 'Schedule follow-up in 2 weeks',
        status: 'pending',
        aiGenerated: false,
        createdAt: '2025-01-01T00:00:00Z',
        updatedAt: '2025-01-01T00:00:00Z',
      }

      expect(followUp.type).toBe('follow_up_meeting')
      expect(followUp.aiGenerated).toBe(false)
    })
  })
})
