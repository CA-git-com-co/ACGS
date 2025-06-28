import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import AccessibilityUtils from '@/lib/accessibility';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

describe('Application Accessibility Tests', () => {
  describe('Accessibility Utilities', () => {
    it('should generate unique IDs', () => {
      const id1 = AccessibilityUtils.generateId();
      const id2 = AccessibilityUtils.generateId();

      expect(id1).toMatch(/^acgs-[a-z0-9]{9}$/);
      expect(id2).toMatch(/^acgs-[a-z0-9]{9}$/);
      expect(id1).not.toBe(id2);
    });

    it('should generate IDs with custom prefix', () => {
      const id = AccessibilityUtils.generateId('test');
      expect(id).toMatch(/^test-[a-z0-9]{9}$/);
    });

    it('should announce to screen reader', () => {
      // Mock DOM methods
      const createElement = jest.spyOn(document, 'createElement');
      const appendChild = jest.spyOn(document.body, 'appendChild');
      const removeChild = jest.spyOn(document.body, 'removeChild');

      AccessibilityUtils.announceToScreenReader('Test message');

      expect(createElement).toHaveBeenCalledWith('div');
      expect(appendChild).toHaveBeenCalled();

      // Check that element has correct attributes
      const announcerElement = appendChild.mock.calls[0][0] as HTMLElement;
      expect(announcerElement.getAttribute('aria-live')).toBe('polite');
      expect(announcerElement.getAttribute('aria-atomic')).toBe('true');
      expect(announcerElement.textContent).toBe('Test message');

      // Clean up
      createElement.mockRestore();
      appendChild.mockRestore();
      removeChild.mockRestore();
    });
  });

  describe('FocusManager', () => {
    let focusManager: InstanceType<typeof AccessibilityUtils.FocusManager>;
    let mockElement: HTMLElement;

    beforeEach(() => {
      focusManager = new AccessibilityUtils.FocusManager();
      mockElement = document.createElement('div');
      mockElement.innerHTML = `
        <button>First</button>
        <input type="text" />
        <button>Last</button>
      `;
      document.body.appendChild(mockElement);
    });

    afterEach(() => {
      document.body.removeChild(mockElement);
    });

    it('should save and restore focus', () => {
      const activeElement = document.createElement('button');
      activeElement.focus = jest.fn();
      Object.defineProperty(document, 'activeElement', {
        value: activeElement,
        configurable: true,
      });

      focusManager.saveFocus();
      focusManager.restoreFocus();

      expect(activeElement.focus).toHaveBeenCalled();
    });

    it('should trap focus within container', () => {
      const buttons = mockElement.querySelectorAll('button');
      const input = mockElement.querySelector('input');

      // Mock focus methods
      buttons.forEach(button => {
        button.focus = jest.fn();
      });
      if (input) input.focus = jest.fn();

      focusManager.trapFocus(mockElement);

      // First focusable element should be focused
      expect(buttons[0].focus).toHaveBeenCalled();
    });
  });

  describe('KeyboardNavigation', () => {
    let container: HTMLElement;

    beforeEach(() => {
      container = document.createElement('div');
      container.innerHTML = `
        <button>Button 1</button>
        <button>Button 2</button>
        <button disabled>Disabled Button</button>
        <button>Button 3</button>
      `;
      document.body.appendChild(container);
    });

    afterEach(() => {
      document.body.removeChild(container);
    });

    it('should identify focusable elements', () => {
      const buttons = container.querySelectorAll('button');
      const enabledButtons = Array.from(buttons).filter(btn => !btn.disabled);
      const disabledButton = container.querySelector('button[disabled]') as HTMLElement;

      expect(
        AccessibilityUtils.KeyboardNavigation.isFocusable(enabledButtons[0] as HTMLElement)
      ).toBe(true);
      expect(AccessibilityUtils.KeyboardNavigation.isFocusable(disabledButton)).toBe(false);
    });

    it('should get all focusable elements', () => {
      const focusableElements =
        AccessibilityUtils.KeyboardNavigation.getFocusableElements(container);
      expect(focusableElements).toHaveLength(3); // Disabled button should not be included
    });

    it('should handle arrow navigation', () => {
      const buttons = Array.from(
        container.querySelectorAll('button:not([disabled])')
      ) as HTMLElement[];
      buttons.forEach(btn => {
        btn.focus = jest.fn();
      });

      const downEvent = new KeyboardEvent('keydown', { key: 'ArrowDown' });
      const upEvent = new KeyboardEvent('keydown', { key: 'ArrowUp' });

      // Test moving down
      let currentIndex = AccessibilityUtils.KeyboardNavigation.handleArrowNavigation(
        downEvent,
        buttons,
        0,
        'vertical'
      );
      expect(currentIndex).toBe(1);

      // Test moving up
      currentIndex = AccessibilityUtils.KeyboardNavigation.handleArrowNavigation(
        upEvent,
        buttons,
        1,
        'vertical'
      );
      expect(currentIndex).toBe(0);
    });
  });

  describe('AriaUtils', () => {
    let element: HTMLElement;

    beforeEach(() => {
      element = document.createElement('button');
    });

    it('should set expanded state', () => {
      AccessibilityUtils.AriaUtils.setExpanded(element, true);
      expect(element.getAttribute('aria-expanded')).toBe('true');

      AccessibilityUtils.AriaUtils.setExpanded(element, false);
      expect(element.getAttribute('aria-expanded')).toBe('false');
    });

    it('should set selected state', () => {
      AccessibilityUtils.AriaUtils.setSelected(element, true);
      expect(element.getAttribute('aria-selected')).toBe('true');
    });

    it('should set pressed state', () => {
      AccessibilityUtils.AriaUtils.setPressed(element, true);
      expect(element.getAttribute('aria-pressed')).toBe('true');
    });

    it('should set live region', () => {
      AccessibilityUtils.AriaUtils.setLiveRegion(element, 'assertive');
      expect(element.getAttribute('aria-live')).toBe('assertive');
      expect(element.getAttribute('aria-atomic')).toBe('true');
    });

    it('should associate with description', () => {
      const description = document.createElement('div');
      description.textContent = 'This is a description';

      AccessibilityUtils.AriaUtils.associateWithDescription(element, description);

      expect(description.id).toBeTruthy();
      expect(element.getAttribute('aria-describedby')).toBe(description.id);
    });
  });

  describe('ContrastUtils', () => {
    it('should calculate relative luminance', () => {
      // Test white
      const whiteLuminance = AccessibilityUtils.ContrastUtils.getRelativeLuminance(255, 255, 255);
      expect(whiteLuminance).toBeCloseTo(1, 2);

      // Test black
      const blackLuminance = AccessibilityUtils.ContrastUtils.getRelativeLuminance(0, 0, 0);
      expect(blackLuminance).toBeCloseTo(0, 2);
    });

    it('should calculate contrast ratio', () => {
      const whiteToBlackRatio = AccessibilityUtils.ContrastUtils.getContrastRatio(
        [255, 255, 255],
        [0, 0, 0]
      );
      expect(whiteToBlackRatio).toBeCloseTo(21, 0); // Maximum contrast ratio
    });

    it('should check WCAG compliance', () => {
      // High contrast should pass AA
      expect(AccessibilityUtils.ContrastUtils.meetsWCAGStandards(7, 'AA')).toBe(true);

      // Low contrast should fail AA
      expect(AccessibilityUtils.ContrastUtils.meetsWCAGStandards(3, 'AA')).toBe(false);

      // Medium contrast should pass AA for large text
      expect(AccessibilityUtils.ContrastUtils.meetsWCAGStandards(3.5, 'AA', 'large')).toBe(true);
    });
  });

  describe('MotionUtils', () => {
    it('should detect reduced motion preference', () => {
      // Mock matchMedia
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: jest.fn().mockImplementation(query => ({
          matches: query === '(prefers-reduced-motion: reduce)',
          media: query,
          onchange: null,
          addListener: jest.fn(),
          removeListener: jest.fn(),
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
          dispatchEvent: jest.fn(),
        })),
      });

      expect(AccessibilityUtils.MotionUtils.prefersReducedMotion()).toBe(true);
    });

    it('should return safe animation duration', () => {
      // Mock reduced motion preference
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: jest.fn().mockImplementation(query => ({
          matches: query === '(prefers-reduced-motion: reduce)',
        })),
      });

      const safeDuration = AccessibilityUtils.MotionUtils.getSafeAnimationDuration(1000);
      expect(safeDuration).toBe(300); // Should be reduced
    });
  });

  describe('Global CSS Classes', () => {
    it('should apply sr-only styles correctly', () => {
      const { container } = render(<span className="sr-only">Hidden text</span>);
      const element = container.querySelector('.sr-only');

      expect(element).toBeInTheDocument();
      expect(element).toHaveClass('sr-only');
    });

    it('should apply focus styles correctly', () => {
      const { container } = render(<button className="focus-visible-enhanced">Focus me</button>);
      const button = container.querySelector('button');

      expect(button).toHaveClass('focus-visible-enhanced');
    });
  });
});
