import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Input } from './input'

describe('Input Component', () => {
  describe('Rendering', () => {
    it('should render input element', () => {
      render(<Input />)
      expect(screen.getByRole('textbox')).toBeInTheDocument()
    })

    it('should render with placeholder', () => {
      render(<Input placeholder="Enter text..." />)
      expect(screen.getByPlaceholderText('Enter text...')).toBeInTheDocument()
    })

    it('should render with value', () => {
      render(<Input value="test value" />)
      expect(screen.getByDisplayValue('test value')).toBeInTheDocument()
    })

    it('should render with custom className', () => {
      render(<Input className="custom-input" />)
      expect(screen.getByRole('textbox')).toHaveClass('custom-input')
    })
  })

  describe('User Input', () => {
    it('should accept text input', async () => {
      render(<Input />)
      const input = screen.getByRole('textbox')
      
      await userEvent.type(input, 'Hello World')
      expect(input).toHaveValue('Hello World')
    })

    it('should clear on backspace', async () => {
      render(<Input defaultValue="test" />)
      const input = screen.getByDisplayValue('test')
      
      await userEvent.clear(input)
      expect(input).toHaveValue('')
    })

    it('should handle rapid typing', async () => {
      render(<Input />)
      const input = screen.getByRole('textbox')
      
      await userEvent.type(input, 'quick')
      expect(input).toHaveValue('quick')
    })
  })

  describe('Disabled State', () => {
    it('should be disabled when disabled prop is true', () => {
      render(<Input disabled />)
      expect(screen.getByRole('textbox')).toBeDisabled()
    })

    it('should not accept input when disabled', async () => {
      render(<Input disabled placeholder="Can't type" />)
      const input = screen.getByPlaceholderText("Can't type")
      
      await userEvent.type(input, 'text')
      expect(input).toHaveValue('')
    })
  })

  describe('Events', () => {
    it('should call onChange when typing', async () => {
      const handleChange = vi.fn()
      render(<Input onChange={handleChange} />)
      
      await userEvent.type(screen.getByRole('textbox'), 'a')
      expect(handleChange).toHaveBeenCalled()
    })

    it('should call onFocus when focused', () => {
      const handleFocus = vi.fn()
      render(<Input onFocus={handleFocus} />)
      
      screen.getByRole('textbox').focus()
      expect(handleFocus).toHaveBeenCalledTimes(1)
    })

    it('should call onBlur when blurred', () => {
      const handleBlur = vi.fn()
      render(<Input onBlur={handleBlur} />)
      
      const input = screen.getByRole('textbox')
      input.focus()
      input.blur()
      expect(handleBlur).toHaveBeenCalledTimes(1)
    })
  })

  describe('Types', () => {
    it('should render email type', () => {
      render(<Input type="email" />)
      expect(screen.getByRole('textbox')).toHaveAttribute('type', 'email')
    })

    it('should render password type', () => {
      render(<Input type="password" />)
      expect(document.querySelector('input[type="password"]')).toBeInTheDocument()
    })

    it('should render number type', () => {
      render(<Input type="number" />)
      expect(screen.getByRole('spinbutton')).toBeInTheDocument()
    })

    it('should render date type', () => {
      render(<Input type="date" />)
      expect(document.querySelector('input[type="date"]')).toBeInTheDocument()
    })

    it('should render time type', () => {
      render(<Input type="time" />)
      expect(document.querySelector('input[type="time"]')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('should accept aria-label', () => {
      render(<Input aria-label="Search input" />)
      expect(screen.getByLabelText('Search input')).toBeInTheDocument()
    })

    it('should accept aria-describedby', () => {
      render(
        <>
          <Input aria-describedby="description" />
          <span id="description">Helper text</span>
        </>
      )
      expect(screen.getByRole('textbox')).toHaveAttribute('aria-describedby', 'description')
    })

    it('should accept aria-invalid', () => {
      render(<Input aria-invalid="true" />)
      expect(screen.getByRole('textbox')).toHaveAttribute('aria-invalid', 'true')
    })
  })

  describe('Styling Classes', () => {
    it('should have flex class', () => {
      render(<Input />)
      expect(screen.getByRole('textbox')).toHaveClass('flex')
    })

    it('should have h-10 class by default', () => {
      render(<Input />)
      expect(screen.getByRole('textbox')).toHaveClass('h-10')
    })

    it('should have rounded-md class', () => {
      render(<Input />)
      expect(screen.getByRole('textbox')).toHaveClass('rounded-md')
    })

    it('should have w-full class', () => {
      render(<Input />)
      expect(screen.getByRole('textbox')).toHaveClass('w-full')
    })
  })
})
