# Accessibility Guidelines for ACGS

## Overview

The Autonomous Constitutional Governance System (ACGS) is committed to providing
an inclusive and accessible experience for all users, including those with
disabilities. This document outlines our accessibility standards, implementation
guidelines, and testing procedures.

## Standards and Compliance

### WCAG 2.1 AA Compliance

We strive to meet
[Web Content Accessibility Guidelines (WCAG) 2.1 Level AA](https://www.w3.org/WAI/WCAG21/quickref/)
standards. This includes:

- **Perceivable**: Information and UI components must be presentable to users in
  ways they can perceive
- **Operable**: UI components and navigation must be operable
- **Understandable**: Information and the operation of UI must be understandable
- **Robust**: Content must be robust enough for interpretation by assistive
  technologies

## Implementation Guidelines

### 1. Semantic HTML

Always use semantic HTML elements that provide meaning and structure:

```tsx
// ✅ Good - Semantic elements
<header role="banner">
  <nav role="navigation" aria-label="Main navigation">
    <h1>ACGS</h1>
  </nav>
</header>

<main id="main-content">
  <article>
    <h2>Policy Proposal</h2>
  </article>
</main>

// ❌ Avoid - Non-semantic divs
<div className="header">
  <div className="nav">
    <div className="title">ACGS</div>
  </div>
</div>
```

### 2. ARIA Labels and Roles

Use ARIA attributes to enhance accessibility when semantic HTML isn't
sufficient:

```tsx
// Button with descriptive label
<Button aria-label="Open user menu for John Doe">
  <Avatar />
</Button>

// Form with proper associations
<FormLabel htmlFor="policy-title">Policy Title</FormLabel>
<FormControl>
  <Input
    id="policy-title"
    aria-describedby="title-description"
    aria-invalid={hasError}
  />
</FormControl>
<FormDescription id="title-description">
  Enter a clear, descriptive title for your policy proposal
</FormDescription>
```

### 3. Keyboard Navigation

Ensure all interactive elements are keyboard accessible:

- All interactive elements must be focusable with Tab
- Use logical tab order
- Provide visible focus indicators
- Support standard keyboard shortcuts (Enter, Space, Arrow keys)

```tsx
// Example: Custom component with keyboard support
const CustomButton = ({ onClick, children, ...props }) => {
  const handleKeyDown = event => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onClick(event);
    }
  };

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={handleKeyDown}
      className="focus-visible:ring-2"
      {...props}
    >
      {children}
    </div>
  );
};
```

### 4. Color and Contrast

- Maintain WCAG AA contrast ratios (4.5:1 for normal text, 3:1 for large text)
- Don't rely solely on color to convey information
- Support both light and dark themes

```tsx
// Use semantic color classes that adapt to themes
<Button variant="destructive">Delete</Button> // Uses semantic red
<Alert className="border-destructive">Error message</Alert>
```

### 5. Images and Media

Provide appropriate alternative text:

```tsx
// Decorative images
<Shield className="h-8 w-8" aria-hidden="true" />

// Informative images
<img src="/chart.png" alt="Policy approval rates over time showing 85% increase" />

// Complex images
<img
  src="/governance-flow.png"
  alt="Governance flow diagram"
  aria-describedby="flow-description"
/>
<div id="flow-description">
  The governance process starts with proposal submission...
</div>
```

### 6. Forms

Create accessible forms with proper labeling and error handling:

```tsx
const PolicyForm = () => {
  return (
    <Form>
      <FormField name="title">
        <FormItem>
          <FormLabel>Policy Title *</FormLabel>
          <FormControl>
            <Input placeholder="Enter policy title" />
          </FormControl>
          <FormDescription>
            Provide a clear, descriptive title for your policy proposal
          </FormDescription>
          <FormMessage />
        </FormItem>
      </FormField>
    </Form>
  );
};
```

## Component-Specific Guidelines

### Navigation

- Use skip links for quick navigation
- Provide clear navigation landmarks
- Use descriptive link text

```tsx
// Skip links
<SkipLink href="#main-content">Skip to main content</SkipLink>
<SkipLink href="#navigation">Skip to navigation</SkipLink>

// Navigation structure
<nav role="navigation" aria-label="Main navigation">
  <ul>
    <li><a href="/dashboard">Dashboard</a></li>
    <li><a href="/policies">Policies</a></li>
  </ul>
</nav>
```

### Tables

Make data tables accessible with proper headers and captions:

```tsx
<Table>
  <TableCaption>Recent policy proposals and their status</TableCaption>
  <TableHeader>
    <TableRow>
      <TableHead scope="col">Title</TableHead>
      <TableHead scope="col">Status</TableHead>
      <TableHead scope="col">Date</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>Climate Action Plan</TableCell>
      <TableCell>Under Review</TableCell>
      <TableCell>2024-01-15</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

### Modals and Dialogs

Implement proper focus management:

```tsx
const PolicyDialog = () => {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Create Policy</Button>
      </DialogTrigger>
      <DialogContent
        aria-labelledby="dialog-title"
        aria-describedby="dialog-description"
      >
        <DialogHeader>
          <DialogTitle id="dialog-title">Create New Policy</DialogTitle>
          <DialogDescription id="dialog-description">
            Fill out the form below to create a new policy proposal.
          </DialogDescription>
        </DialogHeader>
        {/* Form content */}
      </DialogContent>
    </Dialog>
  );
};
```

## Testing Guidelines

### Automated Testing

We use several tools for automated accessibility testing:

1. **ESLint with jsx-a11y**: Catches accessibility issues during development
2. **jest-axe**: Automated accessibility testing in unit tests
3. **@axe-core/react**: Runtime accessibility checking in development

```bash
# Run accessibility-specific tests
npm run test:a11y

# Run accessibility linting
npm run lint:a11y
```

### Manual Testing

#### Keyboard Testing

1. Navigate through the entire interface using only the keyboard
2. Ensure all interactive elements are reachable with Tab
3. Verify logical tab order
4. Test that all functionality is available via keyboard

#### Screen Reader Testing

Test with popular screen readers:

- **NVDA** (Windows)
- **JAWS** (Windows)
- **VoiceOver** (macOS)
- **Orca** (Linux)

#### Visual Testing

1. Test with browser zoom up to 400%
2. Verify color contrast ratios
3. Test without color (simulate color blindness)
4. Ensure content is readable with custom fonts and colors

### Testing Checklist

- [ ] All images have appropriate alt text
- [ ] Form fields have associated labels
- [ ] Error messages are properly announced
- [ ] Focus indicators are visible and clear
- [ ] Color contrast meets WCAG AA standards
- [ ] Page structure uses proper heading hierarchy
- [ ] Skip links are present and functional
- [ ] ARIA attributes are used correctly
- [ ] Keyboard navigation works throughout the app
- [ ] Screen reader announcements are appropriate

## Tools and Resources

### Development Tools

- **ESLint Plugin**: `eslint-plugin-jsx-a11y`
- **Testing**: `jest-axe`, `@axe-core/react`
- **Browser Extensions**: axe DevTools, WAVE
- **Color Contrast**: WebAIM Contrast Checker

### Documentation

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
- [MDN Accessibility Documentation](https://developer.mozilla.org/en-US/docs/Web/Accessibility)

## Getting Help

For accessibility questions or issues:

1. Check this documentation
2. Review WCAG guidelines
3. Test with automated tools
4. Conduct manual testing
5. Consult the team accessibility expert

## Continuous Improvement

Accessibility is an ongoing process. We:

- Regularly audit the application for accessibility issues
- Stay updated with the latest WCAG guidelines
- Incorporate user feedback from people with disabilities
- Train team members on accessibility best practices
- Update this documentation as we learn and improve

Remember: Accessibility benefits everyone, not just users with disabilities. By
following these guidelines, we create a better user experience for all ACGS
users.
