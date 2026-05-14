import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from './button'

describe('Button Component', () => {
  describe('Rendering', () => {
    it('should render button with text', () => {
      render(<Button>Click me</Button>)
      expect(screen.getByText('Click me')).toBeInTheDocument()
    })

    it('should render as default variant', () => {
      const { container } = render(<Button>Default</Button>)
      expect(container.querySelector('button')).toBeInTheDocument()
    })

    it('should render with custom className', () => {
      render(<Button className="custom-class">Custom</Button>)
      const button = screen.getByText('Custom')
      expect(button).toHaveClass('custom-class')
    })
  })

  describe('Variants', () => {
    it('should render default variant', () => {
      render(<Button variant="default">Default</Button>)
      expect(screen.getByText('Default')).toBeInTheDocument()
    })

    it('should render destructive variant', () => {
      render(<Button variant="destructive">Delete</Button>)
      expect(screen.getByText('Delete')).toBeInTheDocument()
    })

    it('should render outline variant', () => {
      render(<Button variant="outline">Outline</Button>)
      expect(screen.getByText('Outline')).toBeInTheDocument()
    })

    it('should render secondary variant', () => {
      render(<Button variant="secondary">Secondary</Button>)
      expect(screen.getByText('Secondary')).toBeInTheDocument()
    })

    it('should render ghost variant', () => {
      render(<Button variant="ghost">Ghost</Button>)
      expect(screen.getByText('Ghost')).toBeInTheDocument()
    })

    it('should render link variant', () => {
      render(<Button variant="link">Link</Button>)
      expect(screen.getByText('Link')).toBeInTheDocument()
    })
  })

  describe('Sizes', () => {
    it('should render default size', () => {
      render(<Button size="default">Default Size</Button>)
      expect(screen.getByText('Default Size')).toBeInTheDocument()
    })

    it('should render small size', () => {
      render(<Button size="sm">Small</Button>)
      expect(screen.getByText('Small')).toBeInTheDocument()
    })

    it('should render large size', () => {
      render(<Button size="lg">Large</Button>)
      expect(screen.getByText('Large')).toBeInTheDocument()
    })

    it('should render icon size', () => {
      render(<Button size="icon">🔍</Button>)
      expect(screen.getByText('🔍')).toBeInTheDocument()
    })
  })

  describe('Disabled State', () => {
    it('should be disabled when disabled prop is true', () => {
      render(<Button disabled>Disabled</Button>)
      expect(screen.getByText('Disabled')).toBeDisabled()
    })

    it('should not respond to clicks when disabled', async () => {
      const handleClick = vi.fn()
      render(<Button disabled onClick={handleClick}>Disabled</Button>)
      
      await userEvent.click(screen.getByText('Disabled'))
      expect(handleClick).not.toHaveBeenCalled()
    })
  })

  describe('Click Handling', () => {
    it('should call onClick when clicked', async () => {
      const handleClick = vi.fn()
      render(<Button onClick={handleClick}>Click me</Button>)
      
      await userEvent.click(screen.getByText('Click me'))
      expect(handleClick).toHaveBeenCalledTimes(1)
    })

    it('should not call onClick when disabled', async () => {
      const handleClick = vi.fn()
      render(<Button disabled onClick={handleClick}>Can't click</Button>)
      
      await userEvent.click(screen.getByText("Can't click"))
      expect(handleClick).not.toHaveBeenCalled()
    })
  })

  describe('Icon Support', () => {
    it('should render with icon', () => {
      render(<Button>🔍 Search</Button>)
      expect(screen.getByText('🔍 Search')).toBeInTheDocument()
    })

    it('should render with icon component', () => {
      render(<Button>➕ Add</Button>)
      expect(screen.getByText('➕ Add')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('should be focusable', () => {
      render(<Button>Focusable</Button>)
      const button = screen.getByText('Focusable')
      button.focus()
      expect(document.activeElement).toBe(button)
    })

    it('should accept type attribute', () => {
      render(<Button type="submit">Submit</Button>)
      expect(screen.getByText('Submit')).toHaveAttribute('type', 'submit')
    })

    it('should be rendered as button element', () => {
      render(<Button>Button</Button>)
      expect(screen.getByText('Button').tagName).toBe('BUTTON')
    })
  })

  describe('Styling', () => {
    it('should apply inline-flex class', () => {
      render(<Button>Flex</Button>)
      const button = screen.getByText('Flex')
      expect(button).toHaveClass('inline-flex')
    })

    it('should apply items-center class', () => {
      render(<Button>Centered</Button>)
      const button = screen.getByText('Centered')
      expect(button).toHaveClass('items-center')
    })

    it('should apply justify-center class', () => {
      render(<Button>Justify</Button>)
      const button = screen.getByText('Justify')
      expect(button).toHaveClass('justify-center')
    })
  })
})
