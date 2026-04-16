import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { SplitPane } from './SplitPane'

describe('SplitPane', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    document.body.innerHTML = ''
  })

  const leftContent = <div data-testid="left-panel">Left Panel Content</div>
  const rightContent = <div data-testid="right-panel">Right Panel Content</div>

  it('renders both panels', () => {
    render(<SplitPane left={leftContent} right={rightContent} />)

    expect(screen.getByTestId('left-panel')).toBeInTheDocument()
    expect(screen.getByTestId('right-panel')).toBeInTheDocument()
  })

  it('renders with custom initial position', () => {
    render(<SplitPane left={leftContent} right={rightContent} initialPosition={50} />)
    
    const leftPanel = screen.getByTestId('left-panel').parentElement
    expect(leftPanel).toBeInTheDocument()
  })

  it('renders children correctly', () => {
    render(
      <SplitPane 
        left={<div>Custom Left</div>} 
        right={<div>Custom Right</div>} 
      />
    )

    expect(screen.getByText('Custom Left')).toBeInTheDocument()
    expect(screen.getByText('Custom Right')).toBeInTheDocument()
  })
})
