import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import { InteractionForm } from './InteractionForm'
import authReducer from '../auth/authSlice'
import hcpsReducer from '../hcps/hcpsSlice'
import interactionsReducer from './interactionsSlice'
import materialsReducer from '../materials/materialsSlice'
import samplesReducer from '../samples/samplesSlice'
import followUpsReducer from '../followUps/followUpsSlice'
import uiReducer from '../ui/uiSlice'
import { setHCP, addMaterial } from './interactionsSlice'
import type { HCP, Material } from '../../types'

const mockHCP: HCP = {
  id: 'hcp-1',
  name: 'Dr. Priya Sharma',
  specialty: 'Oncology',
  institution: 'Tata Memorial Hospital',
  email: 'priya@tata.org',
  createdAt: '2025-01-01T00:00:00Z',
  updatedAt: '2025-01-01T00:00:00Z',
}

const mockMaterial: Material = {
  id: 'mat-1',
  name: 'OncoBoost Brochure',
  type: 'pdf',
  description: 'Phase III data',
  createdAt: '2025-01-01T00:00:00Z',
}

const createStore = (preloadedState = {}) => configureStore({
  reducer: {
    auth: authReducer,
    hcps: hcpsReducer,
    interactions: interactionsReducer,
    materials: materialsReducer,
    samples: samplesReducer,
    followUps: followUpsReducer,
    ui: uiReducer,
  },
  preloadedState: {
    auth: {
      user: { id: '1', email: 'rep@pharma.com', name: 'John Smith', role: 'rep' },
      isAuthenticated: true,
      loading: false,
      error: null,
    },
    hcps: { items: [mockHCP], searchResults: [], activeId: null, activeHCP: null, loading: false, error: null },
    interactions: {
      items: [],
      activeId: null,
      activeInteraction: null,
      formData: { type: 'meeting', dateTime: '', attendees: [], topics: '', sentiment: undefined, outcome: '' },
      dirty: false,
      loading: false,
      saving: false,
      error: null,
    },
    materials: { items: [mockMaterial], loading: false, error: null },
    samples: { items: [], searchResults: [], loading: false, error: null },
    followUps: { items: [], suggestions: [], loading: false, error: null },
    ui: { splitPosition: 60, leftPanelMode: 'create', notifications: [], sidebarCollapsed: false },
    ...preloadedState,
  },
})

describe('InteractionForm UI Functionality', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('HCP Selection', () => {
    it('should render HCP search input', () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      const hcpInput = screen.getByPlaceholderText('Search HCP...')
      expect(hcpInput).toBeInTheDocument()
    })

    it('should display HCP info after selection', async () => {
      const store = createStore()
      store.dispatch(setHCP(mockHCP))
      
      render(<Provider store={store}><InteractionForm /></Provider>)

      await waitFor(() => {
        expect(screen.getByDisplayValue('Dr. Priya Sharma')).toBeInTheDocument()
      })
    })
  })

  describe('Interaction Type Dropdown', () => {
    it('should have Meeting as default', () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      const select = screen.getByRole('combobox')
      expect(select).toHaveValue('meeting')
    })

    it('should change interaction type', async () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      const select = screen.getByRole('combobox')
      await userEvent.selectOptions(select, 'call')

      expect(select).toHaveValue('call')
    })
  })

  describe('Date and Time Inputs', () => {
    it('should render date input', () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      const dateInput = document.querySelector('input[type="date"]')
      expect(dateInput).toBeInTheDocument()
    })

    it('should render time input', () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      const timeInput = document.querySelector('input[type="time"]')
      expect(timeInput).toBeInTheDocument()
    })
  })

  describe('Attendees Management', () => {
    it('should add attendee when pressing Enter', async () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      const input = screen.getByPlaceholderText('Add attendee')
      await userEvent.type(input, 'Dr. John')
      fireEvent.keyDown(input, { key: 'Enter' })

      await waitFor(() => {
        expect(screen.getByText('Dr. John')).toBeInTheDocument()
      })
    })

    it('should add attendee when clicking button', async () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      const input = screen.getByPlaceholderText('Add attendee')
      const addButton = screen.getByRole('button', { name: '' }).closest('button')

      await userEvent.type(input, 'Dr. Jane')
      if (addButton) {
        await userEvent.click(addButton)
      }

      await waitFor(() => {
        expect(screen.getByText('Dr. Jane')).toBeInTheDocument()
      })
    })

    it('should remove attendee when clicking X', async () => {
      const store = createStore({
        interactions: {
          items: [],
          activeId: null,
          activeInteraction: null,
          formData: { type: 'meeting', dateTime: '', attendees: ['Dr. John'], topics: '', sentiment: undefined, outcome: '' },
          dirty: false,
          loading: false,
          saving: false,
          error: null,
        },
      })
      render(<Provider store={store}><InteractionForm /></Provider>)

      const removeButton = screen.getByText('Dr. John').parentElement?.querySelector('button')
      if (removeButton) {
        await userEvent.click(removeButton)
      }

      await waitFor(() => {
        expect(screen.queryByText('Dr. John')).not.toBeInTheDocument()
      })
    })
  })

  describe('Topics & Notes Textarea', () => {
    it('should accept topic input', async () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      const textarea = screen.getByPlaceholderText('Enter topics discussed...')
      await userEvent.type(textarea, 'Discussed OncoBoost efficacy')

      expect(textarea).toHaveValue('Discussed OncoBoost efficacy')
    })

    it('should update Redux state on input', async () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      const textarea = screen.getByPlaceholderText('Enter topics discussed...')
      await userEvent.type(textarea, 'New topic')

      expect(store.getState().interactions.formData.topics).toBe('New topic')
    })
  })

  describe('Sentiment Selection', () => {
    it('should have Positive button', () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      expect(screen.getByText('Positive')).toBeInTheDocument()
    })

    it('should have Neutral button', () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      expect(screen.getByText('Neutral')).toBeInTheDocument()
    })

    it('should have Negative button', () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      expect(screen.getByText('Negative')).toBeInTheDocument()
    })

    it('should update sentiment in Redux on click', async () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      await userEvent.click(screen.getByText('Positive'))

      expect(store.getState().interactions.formData.sentiment).toBe('positive')
    })

    it('should mark state as dirty when sentiment changes', async () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      await userEvent.click(screen.getByText('Negative'))

      expect(store.getState().interactions.dirty).toBe(true)
    })
  })

  describe('Outcomes Textarea', () => {
    it('should accept outcome input', async () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      const textarea = screen.getByPlaceholderText('Key agreements or results of the meeting...')
      await userEvent.type(textarea, 'Patient interested in clinical trial')

      expect(textarea).toHaveValue('Patient interested in clinical trial')
    })
  })

  describe('New Interaction Button', () => {
    it('should reset form when clicked', async () => {
      const store = createStore({
        interactions: {
          items: [],
          activeId: null,
          activeInteraction: null,
          formData: { 
            type: 'call', 
            dateTime: '2025-04-16T10:00', 
            attendees: ['Dr. John'],
            topics: 'Some topic',
            sentiment: 'positive',
            outcome: 'Good outcome',
          },
          dirty: true,
          loading: false,
          saving: false,
          error: null,
        },
      })
      render(<Provider store={store}><InteractionForm /></Provider>)

      await userEvent.click(screen.getByText('New Interaction'))
      expect(screen.getByText('Start New')).toBeInTheDocument()
      await userEvent.click(screen.getByText('Start New'))

      expect(store.getState().interactions.formData.topics).toBe('')
      expect(store.getState().interactions.formData.sentiment).toBeUndefined()
      expect(store.getState().interactions.dirty).toBe(false)
    })
  })

  describe('Save Button', () => {
    it('should be disabled when no HCP selected', () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      const saveButton = screen.getByText('Save').closest('button')
      expect(saveButton).toBeDisabled()
    })

    it('should be enabled when HCP is selected', async () => {
      const store = createStore()
      store.dispatch(setHCP(mockHCP))
      
      render(<Provider store={store}><InteractionForm /></Provider>)

      const saveButton = screen.getByText('Save').closest('button')
      expect(saveButton).not.toBeDisabled()
    })
  })

  describe('Dirty State Indicator', () => {
    it('should show unsaved changes badge when dirty', () => {
      const store = createStore({
        interactions: {
          items: [],
          activeId: null,
          activeInteraction: null,
          formData: { type: 'meeting', dateTime: '', attendees: [], topics: 'Changed', sentiment: undefined, outcome: '' },
          dirty: true,
          loading: false,
          saving: false,
          error: null,
        },
      })
      render(<Provider store={store}><InteractionForm /></Provider>)

      expect(screen.getByText('Unsaved changes')).toBeInTheDocument()
    })

    it('should not show badge when clean', () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      expect(screen.queryByText('Unsaved changes')).not.toBeInTheDocument()
    })
  })

  describe('Dictate Button', () => {
    it('should render Dictate button', () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      expect(screen.getByText('Dictate')).toBeInTheDocument()
    })
  })

  describe('AI Summarize Button', () => {
    it('should render Summarize from Voice Note button', () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      expect(screen.getByText('Summarize from Voice Note')).toBeInTheDocument()
    })
  })

  describe('Materials Section', () => {
    it('should show "No materials added" when empty', () => {
      const store = createStore({
        materials: { items: [], loading: false, error: null },
      })
      render(<Provider store={store}><InteractionForm /></Provider>)

      expect(screen.getByText('No materials added')).toBeInTheDocument()
    })

    it('should add material to form', async () => {
      const store = createStore()
      store.dispatch(addMaterial(mockMaterial))
      
      render(<Provider store={store}><InteractionForm /></Provider>)

      await waitFor(() => {
        expect(screen.getByText('OncoBoost Brochure')).toBeInTheDocument()
      })
    })
  })

  describe('Samples Section', () => {
    it('should show "No samples added" when empty', () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      expect(screen.getByText('No samples added')).toBeInTheDocument()
    })

    it('should have sample search input', () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      expect(screen.getByPlaceholderText('Search sample...')).toBeInTheDocument()
    })
  })

  describe('Follow-ups Section', () => {
    it('should show AI suggestion placeholder when no suggestions', () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      expect(screen.getByText('AI suggestions will appear here based on interaction context')).toBeInTheDocument()
    })

    it('should have manual follow-up textarea', () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      expect(screen.getByPlaceholderText('Enter next steps...')).toBeInTheDocument()
    })
  })

  describe('Form Card Sections', () => {
    it('should render all section headers', () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      expect(screen.getByText('Basic Details')).toBeInTheDocument()
      expect(screen.getByText('Discussion & Notes')).toBeInTheDocument()
      expect(screen.getByText('Materials & Samples')).toBeInTheDocument()
      expect(screen.getByText('Sentiment & Outcomes')).toBeInTheDocument()
      expect(screen.getByText('Follow-ups')).toBeInTheDocument()
    })
  })

  describe('User Info Display', () => {
    it('should show logged in user name', () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      expect(screen.getByDisplayValue('John Smith')).toBeInTheDocument()
    })
  })

  describe('Cancel Button', () => {
    it('should be disabled when no changes', () => {
      const store = createStore()
      render(<Provider store={store}><InteractionForm /></Provider>)

      const cancelButton = screen.getByText('Cancel').closest('button')
      expect(cancelButton).toBeDisabled()
    })

    it('should be enabled when dirty', () => {
      const store = createStore({
        interactions: {
          items: [],
          activeId: null,
          activeInteraction: null,
          formData: { type: 'meeting', dateTime: '', attendees: [], topics: 'Changed', sentiment: undefined, outcome: '' },
          dirty: true,
          loading: false,
          saving: false,
          error: null,
        },
      })
      render(<Provider store={store}><InteractionForm /></Provider>)

      const cancelButton = screen.getByText('Cancel').closest('button')
      expect(cancelButton).not.toBeDisabled()
    })
  })
})
