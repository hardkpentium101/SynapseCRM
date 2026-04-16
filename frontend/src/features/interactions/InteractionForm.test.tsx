import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
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

const createStore = () => configureStore({
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
    hcps: { items: [], searchResults: [], activeId: null, activeHCP: null, loading: false, error: null },
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
    materials: { items: [], loading: false, error: null },
    samples: { items: [], searchResults: [], loading: false, error: null },
    followUps: { items: [], suggestions: [], loading: false, error: null },
    ui: { splitPosition: 60, leftPanelMode: 'create', notifications: [], sidebarCollapsed: false },
  },
})

describe('InteractionForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the form with all sections', () => {
    const store = createStore()
    render(
      <Provider store={store}>
        <InteractionForm />
      </Provider>
    )

    expect(screen.getByText('Basic Details')).toBeInTheDocument()
    expect(screen.getByText('Discussion & Notes')).toBeInTheDocument()
    expect(screen.getByText('Materials & Samples')).toBeInTheDocument()
    expect(screen.getByText('Sentiment & Outcomes')).toBeInTheDocument()
    expect(screen.getByText('Follow-ups')).toBeInTheDocument()
  })

  it('renders New Interaction button', () => {
    const store = createStore()
    render(
      <Provider store={store}>
        <InteractionForm />
      </Provider>
    )

    expect(screen.getByText('New Interaction')).toBeInTheDocument()
  })

  it('renders sentiment selector buttons', () => {
    const store = createStore()
    render(
      <Provider store={store}>
        <InteractionForm />
      </Provider>
    )

    expect(screen.getByText('Positive')).toBeInTheDocument()
    expect(screen.getByText('Neutral')).toBeInTheDocument()
    expect(screen.getByText('Negative')).toBeInTheDocument()
  })

  it('renders Save button', () => {
    const store = createStore()
    render(
      <Provider store={store}>
        <InteractionForm />
      </Provider>
    )

    expect(screen.getByText('Save')).toBeInTheDocument()
  })

  it('disables Save when no HCP selected', () => {
    const store = createStore()
    render(
      <Provider store={store}>
        <InteractionForm />
      </Provider>
    )

    const saveButton = screen.getByText('Save').closest('button')
    expect(saveButton).toBeDisabled()
  })

  it('renders Dictate and Summarize buttons', () => {
    const store = createStore()
    render(
      <Provider store={store}>
        <InteractionForm />
      </Provider>
    )

    expect(screen.getByText('Dictate')).toBeInTheDocument()
    expect(screen.getByText('Summarize from Voice Note')).toBeInTheDocument()
  })

  it('shows AI Suggested Follow-ups section', () => {
    const store = createStore()
    render(
      <Provider store={store}>
        <InteractionForm />
      </Provider>
    )

    expect(screen.getByText('AI Suggested Follow-ups')).toBeInTheDocument()
  })
})
