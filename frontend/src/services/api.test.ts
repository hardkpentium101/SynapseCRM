import { describe, it, expect, beforeEach, vi } from 'vitest'
import { api } from './api'

global.fetch = vi.fn()

describe('api service', () => {
  const mockFetch = global.fetch as ReturnType<typeof vi.fn>

  beforeEach(() => {
    vi.clearAllMocks()
    api.setToken(null)
  })

  describe('setToken', () => {
    it('should set and clear token', () => {
      api.setToken('test-token')
      expect(api).toBeDefined()
      
      api.setToken(null)
      expect(api).toBeDefined()
    })
  })

  describe('login', () => {
    it('should set token on successful login', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          user: { id: '1', email: 'test@test.com', name: 'Test', role: 'rep' },
          access_token: 'token123',
          refresh_token: 'refresh123',
        }),
      })

      const result = await api.login({ email: 'test@test.com', password: 'test123' })

      expect(result.tokens.accessToken).toBe('token123')
      expect(result.tokens.refreshToken).toBe('refresh123')
      expect(result.user.email).toBe('test@test.com')
    })

    it('should throw error on failed login', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Invalid credentials' }),
      })

      await expect(api.login({ email: 'test@test.com', password: 'wrong' }))
        .rejects.toThrow('Invalid credentials')
    })
  })

  describe('hcps', () => {
    it('should fetch all hcps', async () => {
      const mockHcps = [
        { id: '1', name: 'Dr. Sharma', specialty: 'Oncology' },
        { id: '2', name: 'Dr. Kumar', specialty: 'Cardiology' },
      ]

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockHcps,
      })

      const result = await api.getHcps()
      expect(result).toEqual(mockHcps)
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/hcps'),
        expect.any(Object)
      )
    })

    it('should search hcps with query param', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      })

      await api.getHcps('Sharma')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('search=Sharma'),
        expect.any(Object)
      )
    })

    it('should include auth token when set', async () => {
      api.setToken('test-token')
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      })

      await api.getHcps()

      const call = mockFetch.mock.calls[0]
      const headers = call[1]?.headers as Record<string, string>
      expect(headers?.Authorization).toContain('test-token')
    })
  })

  describe('interactions', () => {
    it('should fetch interactions with filters', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      })

      await api.getInteractions({ hcpId: 'hcp-1', userId: 'user-1' })

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('hcp_id=hcp-1'),
        expect.any(Object)
      )
    })

    it('should create interaction', async () => {
      const newInteraction = {
        hcpId: 'hcp-1',
        type: 'meeting',
        dateTime: '2025-04-16T10:00:00',
        attendees: [],
        topics: 'Test topic',
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ...newInteraction, id: 'int-1' }),
      })

      const result = await api.createInteraction(newInteraction)
      expect(result.id).toBe('int-1')
    })
  })
})
