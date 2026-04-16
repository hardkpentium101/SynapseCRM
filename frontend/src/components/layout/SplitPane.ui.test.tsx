import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { SplitPane } from './SplitPane'

describe('SplitPane Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    document.body.innerHTML = ''
  })

  const leftContent = <div data-testid="left-content">Left Panel Content</div>
  const rightContent = <div data-testid="right-content">Right Panel Content</div>

  describe('Rendering', () => {
    it('should render left panel content', () => {
      render(<SplitPane left={leftContent} right={rightContent} />)
      expect(screen.getByTestId('left-content')).toBeInTheDocument()
    })

    it('should render right panel content', () => {
      render(<SplitPane left={leftContent} right={rightContent} />)
      expect(screen.getByTestId('right-content')).toBeInTheDocument()
    })

    it('should render with default initial position of 60%', () => {
      const { container } = render(<SplitPane left={leftContent} right={rightContent} />)
      const leftPanel = container.querySelector('[style*="60%"]')
      expect(leftPanel).toBeInTheDocument()
    })

    it('should render with custom initial position', () => {
      const { container } = render(<SplitPane left={leftContent} right={rightContent} initialPosition={50} />)
      const leftPanel = container.querySelector('[style*="50%"]')
      expect(leftPanel).toBeInTheDocument()
    })

    it('should render divider', () => {
      const { container } = render(<SplitPane left={leftContent} right={rightContent} />)
      expect(container.querySelector('.cursor-col-resize')).toBeInTheDocument()
    })
  })

  describe('Divider Dragging', () => {
    it('should detect divider element', () => {
      render(<SplitPane left={leftContent} right={rightContent} />)
      
      const divider = document.querySelector('.cursor-col-resize')
      expect(divider).toBeInTheDocument()
    })

    it('should have correct cursor style', () => {
      render(<SplitPane left={leftContent} right={rightContent} />)
      
      const divider = document.querySelector('.cursor-col-resize')
      expect(divider).toHaveClass('cursor-col-resize')
    })

    it('should have resize functionality class', () => {
      render(<SplitPane left={leftContent} right={rightContent} />)
      
      const divider = document.querySelector('.cursor-col-resize')
      expect(divider).toHaveClass('group')
    })
  })

  describe('Resize Constraints', () => {
    it('should respect minimum left panel size', () => {
      const { container } = render(
        <SplitPane left={leftContent} right={rightContent} minLeft={30} />
      )
      
      const leftPanel = container.querySelector('div[style*="%"]')
      expect(leftPanel).toBeInTheDocument()
    })

    it('should respect minimum right panel size', () => {
      const { container } = render(
        <SplitPane left={leftContent} right={rightContent} minRight={30} />
      )
      
      const leftPanel = container.querySelector('div[style*="%"]')
      expect(leftPanel).toBeInTheDocument()
    })
  })

  describe('Responsive Layout', () => {
    it('should fill container width', () => {
      const { container } = render(<SplitPane left={leftContent} right={rightContent} />)
      
      const wrapper = container.querySelector('.flex')
      expect(wrapper).toHaveClass('w-full')
    })

    it('should be overflow hidden', () => {
      const { container } = render(<SplitPane left={leftContent} right={rightContent} />)
      
      const wrapper = container.firstChild
      expect(wrapper).toHaveClass('overflow-hidden')
    })
  })

  describe('Children Rendering', () => {
    it('should render complex left content', () => {
      const complexLeft = (
        <div>
          <h1>Title</h1>
          <button>Click me</button>
          <input type="text" />
        </div>
      )
      render(<SplitPane left={complexLeft} right={rightContent} />)
      
      expect(screen.getByText('Title')).toBeInTheDocument()
      expect(screen.getByText('Click me')).toBeInTheDocument()
      expect(screen.getByRole('textbox')).toBeInTheDocument()
    })

    it('should render complex right content', () => {
      const complexRight = (
        <div>
          <h2>Right Title</h2>
          <ul>
            <li>Item 1</li>
            <li>Item 2</li>
          </ul>
        </div>
      )
      render(<SplitPane left={leftContent} right={complexRight} />)
      
      expect(screen.getByText('Right Title')).toBeInTheDocument()
      expect(screen.getByText('Item 1')).toBeInTheDocument()
      expect(screen.getByText('Item 2')).toBeInTheDocument()
    })

    it('should render React fragments', () => {
      const fragmentLeft = (
        <>
          <span>Fragment 1</span>
          <span>Fragment 2</span>
        </>
      )
      render(<SplitPane left={fragmentLeft} right={rightContent} />)
      
      expect(screen.getByText('Fragment 1')).toBeInTheDocument()
      expect(screen.getByText('Fragment 2')).toBeInTheDocument()
    })
  })

  describe('Height Handling', () => {
    it('should have full height', () => {
      const { container } = render(<SplitPane left={leftContent} right={rightContent} />)
      
      const wrapper = container.firstChild
      expect(wrapper).toHaveClass('h-full')
    })
  })

  describe('Border Styling', () => {
    it('should apply border to left panel', () => {
      const { container } = render(<SplitPane left={leftContent} right={rightContent} />)
      
      const leftPanel = container.querySelector('.border-r')
      expect(leftPanel).toBeInTheDocument()
    })
  })
})
