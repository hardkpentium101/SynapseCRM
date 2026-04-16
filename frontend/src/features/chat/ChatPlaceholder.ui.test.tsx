import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ChatPlaceholder } from './ChatPlaceholder'

describe('ChatPlaceholder Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Header', () => {
    it('should display AI Assistant title', () => {
      render(<ChatPlaceholder />)
      expect(screen.getByText('AI Assistant')).toBeInTheDocument()
    })
  })

  describe('Instructions', () => {
    it('should display Log interaction details message', () => {
      render(<ChatPlaceholder />)
      expect(screen.getByText('Log interaction details via chat')).toBeInTheDocument()
    })

    it('should display "Try saying" section', () => {
      render(<ChatPlaceholder />)
      expect(screen.getByText('Try saying:')).toBeInTheDocument()
    })
  })

  describe('Example Prompts', () => {
    it('should show meeting prompt example', () => {
      render(<ChatPlaceholder />)
      expect(screen.getByText(/Met Dr. Smith/)).toBeInTheDocument()
    })

    it('should show follow-up scheduling example', () => {
      render(<ChatPlaceholder />)
      expect(screen.getByText(/Schedule a follow-up/)).toBeInTheDocument()
    })

    it('should show recent interactions query example', () => {
      render(<ChatPlaceholder />)
      expect(screen.getByText(/Show recent interactions/)).toBeInTheDocument()
    })

    it('should have all three examples', () => {
      render(<ChatPlaceholder />)
      
      const examples = [
        /Met Dr. Smith/,
        /Schedule a follow-up/,
        /Show recent interactions/,
      ]
      
      examples.forEach(regex => {
        expect(screen.getByText(regex)).toBeInTheDocument()
      })
    })
  })

  describe('Icon', () => {
    it('should display icon container', () => {
      render(<ChatPlaceholder />)
      const iconContainer = document.querySelector('.h-16')
      expect(iconContainer).toBeInTheDocument()
    })
  })

  describe('Layout', () => {
    it('should be centered', () => {
      render(<ChatPlaceholder />)
      const container = document.querySelector('.flex.items-center.justify-center')
      expect(container).toBeInTheDocument()
    })

    it('should have text alignment', () => {
      render(<ChatPlaceholder />)
      const textContainer = document.querySelector('.text-center')
      expect(textContainer).toBeInTheDocument()
    })
  })

  describe('Card Styling', () => {
    it('should have a card container', () => {
      render(<ChatPlaceholder />)
      const card = document.querySelector('.rounded-lg')
      expect(card).toBeInTheDocument()
    })

    it('should have border styling', () => {
      render(<ChatPlaceholder />)
      const card = document.querySelector('.border')
      expect(card).toBeInTheDocument()
    })
  })
})
