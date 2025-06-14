# OS-Style Governance Dashboard

A modern, minimalist governance dashboard built with Next.js 14, TypeScript, and Tailwind CSS. This application provides an intuitive interface for managing organizational policies, proposals, and voting processes with an OS-inspired design.

## 🚀 Features

- **OS-Style Interface**: Clean, minimalist design inspired by modern operating systems
- **Drag & Drop Dashboard**: Customizable dashboard with draggable cards
- **Global Command Palette**: Quick access to actions via ⌘K/Ctrl+K shortcut
- **Dark/Light Theme**: Automatic theme switching with persistent storage
- **Responsive Design**: Fully responsive across all device sizes
- **Accessibility First**: WCAG 2.1 AA compliant with keyboard navigation
- **TypeScript**: Full type safety throughout the application
- **Modern Tech Stack**: Next.js 14, React 18, Tailwind CSS

## 🛠 Technology Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Drag & Drop**: @dnd-kit
- **Icons**: Lucide React
- **Command Interface**: cmdk
- **Animations**: Framer Motion

## 📦 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd governance-dashboard-nextjs
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🎨 Design System

### Colors
- **Base**: White (`#FFFFFF`), Light Gray (`#F5F7FA`), Dark Gray (`#1F2937`)
- **Primary Accent**: Blue (`#3B82F6`)
- **Status**: Success (`#10B981`), Warning (`#F59E0B`), Error (`#EF4444`)

### Typography
- **Font**: Inter with fallbacks
- **Scale**: Caption (12px), Body (14px), Subheading (16px), Heading (20px), Large Heading (24px)

### Spacing
- Based on 4px grid system (4px, 8px, 16px, 24px, etc.)

## 🚀 Key Features

### Command Palette
Press `⌘K` (Mac) or `Ctrl+K` (Windows/Linux) to open the global command palette for quick actions:
- Create new policies and proposals
- Navigate to different sections
- Search across the application

### Draggable Dashboard
Customize your dashboard by dragging and dropping cards to rearrange the layout. Your preferences are automatically saved.

### Theme System
Toggle between light and dark themes using the theme toggle in the header. Your preference is saved locally.

### Responsive Navigation
- Collapsible sidebar on desktop
- Mobile-optimized navigation
- Keyboard-accessible navigation

## 📁 Project Structure

```
governance-dashboard-nextjs/
├── app/                    # Next.js 14 App Router
│   ├── (dashboard)/       # Dashboard layout group
│   │   ├── page.tsx       # Home dashboard
│   │   ├── policies/      # Policies section
│   │   ├── governance/    # Governance section
│   │   └── settings/      # Settings section
│   ├── globals.css        # Global styles
│   └── layout.tsx         # Root layout
├── components/            # React components
│   ├── ui/               # Reusable UI components
│   ├── layout/           # Layout components
│   └── dashboard/        # Dashboard-specific components
├── hooks/                # Custom React hooks
├── lib/                  # Utility functions
├── types/                # TypeScript type definitions
└── public/               # Static assets
```

## 🧩 Component Architecture

### UI Components
- **Button**: Flexible button component with variants
- **Input**: Form input with validation support
- **Card**: Draggable content cards with header/content sections

### Layout Components
- **Sidebar**: Collapsible navigation sidebar
- **CommandBar**: Global command palette
- **ThemeToggle**: Dark/light mode toggle

### Hooks
- **useKeyboard**: Handle keyboard shortcuts
- **useLocalStorage**: Persistent local storage

## 🔧 Customization

### Adding New Routes
1. Create a new page in the `app/(dashboard)` directory
2. Add the route to the sidebar navigation in `components/layout/Sidebar.tsx`

### Creating New Components
Follow the established patterns:
- Use TypeScript interfaces for props
- Include accessibility attributes
- Support both light and dark themes
- Use the established design tokens

### Adding Commands
Add new commands to the command palette in `components/layout/CommandBar.tsx`:

```typescript
{
  id: 'new-command',
  label: 'My New Command',
  icon: <Icon className="h-4 w-4" />,
  keywords: ['keyword1', 'keyword2'],
  onSelect: () => handleAction(),
}
```

## 🔐 Accessibility

- Semantic HTML structure
- ARIA labels and roles
- Keyboard navigation support
- Focus management
- Screen reader compatibility
- High contrast mode support
- Reduced motion support

## 📱 Responsive Design

- Mobile-first approach
- Breakpoints: 640px, 768px, 1024px, 1280px
- Touch-friendly interface
- Optimized for all screen sizes

## 🚀 Performance

- Next.js 14 optimization
- Code splitting by route
- Optimized images and fonts
- Minimal bundle size
- Fast development builds

## 🧪 Development

### Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler

### Code Quality
- ESLint with Next.js configuration
- TypeScript strict mode
- Consistent code formatting
- Component documentation

## 🤝 Contributing

1. Follow the established code style
2. Ensure TypeScript types are properly defined
3. Test across different browsers and devices
4. Maintain accessibility standards
5. Update documentation as needed

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.