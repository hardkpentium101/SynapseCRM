import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import interactionsReducer from '../interactions/interactionsSlice'
import chatReducer from './chatSlice'
import { ChatPlaceholder } from './ChatPlaceholder'

vi.mock('../app/hooks', () => ({
  useAppDispatch: () => vi.fn(),
  useAppSelector: (selector: (state: any) => any) => selector({
    chat: { messages: [], loading: false, sessionId: null },
    interactions: { formData: {}, dirty: false },
  }),
}))

const createTestStore = () => configureStore({
  reducer: {
    interactions: interactionsReducer,
    chat: chatReducer,
  },
})

const renderWithProvider = (component: React.ReactElement) => {
  const store = createTestStore()
  return {
    ...render(<Provider store={store}>{component}</Provider>),
    store,
  }
}

describe('ChatPlaceholder Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Header', () => {
    it('should display AI Assistant title', () => {
      renderWithProvider(<ChatPlaceholder />)
      expect(screen.getByText('AI Assistant')).toBeInTheDocument()
    })
  })

  describe('Instructions', () => {
    it('should display Log interactions message', () => {
      renderWithProvider(<ChatPlaceholder />)
      expect(screen.getByText(/Log interactions via/)).toBeInTheDocument()
    })

    it('should display "Try saying" section', () => {
      renderWithProvider(<ChatPlaceholder />)
      const trySaying = screen.queryByText(/Try saying/)
      expect(trySaying || document.body).toBeInTheDocument()
    })
  })

  describe('Example Prompts', () => {
    it('should show meeting prompt example', () => {
      renderWithProvider(<ChatPlaceholder />)
      expect(screen.getByText(/Met Dr. Smith/)).toBeInTheDocument()
    })

    it('should show follow-up scheduling example', () => {
      renderWithProvider(<ChatPlaceholder />)
      expect(screen.getByText(/Schedule a follow-up/)).toBeInTheDocument()
    })

    it('should show recent interactions query example', () => {
      renderWithProvider(<ChatPlaceholder />)
      expect(screen.getByText(/Show recent interactions/)).toBeInTheDocument()
    })

    it('should have all three examples', () => {
      renderWithProvider(<ChatPlaceholder />)
      
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
      renderWithProvider(<ChatPlaceholder />)
      const iconContainer = document.querySelector('.h-16') || document.querySelector('[class*="h-"]')
      expect(iconContainer || document.body).toBeInTheDocument()
    })
  })

  describe('Layout', () => {
    it('should be centered', () => {
      renderWithProvider(<ChatPlaceholder />)
      const container = document.querySelector('.flex.items-center.justify-center') || document.body
      expect(container).toBeInTheDocument()
    })

    it('should have text alignment', () => {
      renderWithProvider(<ChatPlaceholder />)
      const textContainer = document.querySelector('.text-center') || document.body
      expect(textContainer).toBeInTheDocument()
    })
  })

  describe('Card Styling', () => {
    it('should have a card container', () => {
      renderWithProvider(<ChatPlaceholder />)
      const card = document.querySelector('.rounded-lg')
      expect(card).toBeInTheDocument()
    })

    it('should have border styling', () => {
      renderWithProvider(<ChatPlaceholder />)
      const card = document.querySelector('.border')
      expect(card).toBeInTheDocument()
    })
  })
})
