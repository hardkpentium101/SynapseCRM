import { describe, it, expect, vi } from 'vitest'
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
      expect(screen.getByText(/Try saying/)).toBeInTheDocument()
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
