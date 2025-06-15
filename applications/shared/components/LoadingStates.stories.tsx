import type { Meta, StoryObj } from '@storybook/react';
import { 
  Spinner, 
  Skeleton, 
  Progress, 
  LoadingOverlay, 
  CardSkeleton, 
  TableSkeleton, 
  FormSkeleton, 
  LoadingButton, 
  TimeoutLoader 
} from './LoadingStates';

/**
 * Loading States Components for ACGS-PGP Framework
 * 
 * These components provide consistent loading experiences across the application,
 * supporting various use cases from quick spinners to complex skeleton loaders.
 * All components integrate with the ACGS service architecture and follow
 * constitutional governance design patterns.
 */

// Spinner Stories
const spinnerMeta: Meta<typeof Spinner> = {
  title: 'Components/Loading/Spinner',
  component: Spinner,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'Basic spinner component for quick loading states. Used throughout ACGS services for API calls and data fetching.'
      }
    }
  },
  tags: ['autodocs'],
  argTypes: {
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg', 'xl'],
      description: 'Size of the spinner'
    },
    color: {
      control: 'select',
      options: ['blue', 'green', 'yellow', 'red', 'gray', 'indigo'],
      description: 'Color theme of the spinner'
    },
    showText: {
      control: 'boolean',
      description: 'Whether to show loading text'
    },
    text: {
      control: 'text',
      description: 'Loading text to display'
    }
  }
};

export default spinnerMeta;
type SpinnerStory = StoryObj<typeof spinnerMeta>;

export const Default: SpinnerStory = {
  args: {
    size: 'md',
    color: 'blue',
    showText: false
  }
};

export const WithText: SpinnerStory = {
  args: {
    size: 'lg',
    color: 'blue',
    showText: true,
    text: 'Loading constitutional principles...'
  }
};

export const Small: SpinnerStory = {
  args: {
    size: 'sm',
    color: 'gray'
  }
};

export const Large: SpinnerStory = {
  args: {
    size: 'xl',
    color: 'indigo',
    showText: true,
    text: 'Synthesizing governance policies...'
  }
};

export const AllColors: SpinnerStory = {
  render: () => (
    <div className="flex gap-4 items-center">
      <Spinner size="md" color="blue" />
      <Spinner size="md" color="green" />
      <Spinner size="md" color="yellow" />
      <Spinner size="md" color="red" />
      <Spinner size="md" color="gray" />
      <Spinner size="md" color="indigo" />
    </div>
  )
};

// Skeleton Stories
const skeletonMeta: Meta<typeof Skeleton> = {
  title: 'Components/Loading/Skeleton',
  component: Skeleton,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'Skeleton loader for content placeholders. Provides visual feedback while data is loading from ACGS services.'
      }
    }
  },
  tags: ['autodocs']
};

export const SkeletonDefault: StoryObj<typeof skeletonMeta> = {
  args: {
    width: '200px',
    height: '20px'
  }
};

export const SkeletonMultiLine: StoryObj<typeof skeletonMeta> = {
  args: {
    lines: 3,
    height: '16px'
  }
};

export const SkeletonRounded: StoryObj<typeof skeletonMeta> = {
  args: {
    width: '60px',
    height: '60px',
    rounded: true
  }
};

// Progress Stories
const progressMeta: Meta<typeof Progress> = {
  title: 'Components/Loading/Progress',
  component: Progress,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'Progress indicator for multi-step operations like policy synthesis or compliance validation.'
      }
    }
  },
  tags: ['autodocs']
};

export const ProgressDefault: StoryObj<typeof progressMeta> = {
  args: {
    progress: 65,
    label: 'Policy Synthesis Progress'
  }
};

export const ProgressWithoutLabel: StoryObj<typeof progressMeta> = {
  args: {
    progress: 40,
    showPercentage: false
  }
};

export const ProgressColors: StoryObj<typeof progressMeta> = {
  render: () => (
    <div className="space-y-4 w-80">
      <Progress progress={25} color="blue" label="AC Service Connection" />
      <Progress progress={50} color="green" label="GS Policy Synthesis" />
      <Progress progress={75} color="yellow" label="PGC Compliance Check" />
      <Progress progress={90} color="red" label="Critical Validation" />
      <Progress progress={100} color="indigo" label="Complete" />
    </div>
  )
};

// LoadingButton Stories
const loadingButtonMeta: Meta<typeof LoadingButton> = {
  title: 'Components/Loading/LoadingButton',
  component: LoadingButton,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'Button component with integrated loading state. Used for form submissions and API calls to ACGS services.'
      }
    }
  },
  tags: ['autodocs']
};

export const LoadingButtonDefault: StoryObj<typeof loadingButtonMeta> = {
  args: {
    isLoading: false,
    children: 'Submit Principle',
    className: 'px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700'
  }
};

export const LoadingButtonActive: StoryObj<typeof loadingButtonMeta> = {
  args: {
    isLoading: true,
    loadingText: 'Creating principle...',
    children: 'Submit Principle',
    className: 'px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700'
  }
};

// Card Skeleton Stories
const cardSkeletonMeta: Meta<typeof CardSkeleton> = {
  title: 'Components/Loading/CardSkeleton',
  component: CardSkeleton,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'Skeleton loader for card components. Used while loading principles, policies, or other governance data.'
      }
    }
  },
  tags: ['autodocs']
};

export const CardSkeletonDefault: StoryObj<typeof cardSkeletonMeta> = {};

export const CardSkeletonGrid: StoryObj<typeof cardSkeletonMeta> = {
  render: () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-6xl">
      <CardSkeleton />
      <CardSkeleton />
      <CardSkeleton />
      <CardSkeleton />
      <CardSkeleton />
      <CardSkeleton />
    </div>
  )
};

// Table Skeleton Stories
const tableSkeletonMeta: Meta<typeof TableSkeleton> = {
  title: 'Components/Loading/TableSkeleton',
  component: TableSkeleton,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'Skeleton loader for table components. Used for governance data tables and analytics views.'
      }
    }
  },
  tags: ['autodocs']
};

export const TableSkeletonDefault: StoryObj<typeof tableSkeletonMeta> = {
  args: {
    rows: 5,
    columns: 4
  }
};

export const TableSkeletonLarge: StoryObj<typeof tableSkeletonMeta> = {
  args: {
    rows: 10,
    columns: 6
  }
};

// Loading Overlay Stories
const loadingOverlayMeta: Meta<typeof LoadingOverlay> = {
  title: 'Components/Loading/LoadingOverlay',
  component: LoadingOverlay,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'Overlay component that shows loading state over existing content. Used for form submissions and data updates.'
      }
    }
  },
  tags: ['autodocs']
};

export const LoadingOverlayDefault: StoryObj<typeof loadingOverlayMeta> = {
  args: {
    isLoading: true,
    children: (
      <div className="p-8 bg-white border rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Constitutional Principle</h3>
        <p className="text-gray-600 mb-4">
          This is some content that will be overlaid with a loading state when the component is processing.
        </p>
        <button className="px-4 py-2 bg-blue-600 text-white rounded">
          Edit Principle
        </button>
      </div>
    )
  }
};

export const LoadingOverlayNotLoading: StoryObj<typeof loadingOverlayMeta> = {
  args: {
    isLoading: false,
    children: (
      <div className="p-8 bg-white border rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Constitutional Principle</h3>
        <p className="text-gray-600 mb-4">
          This content is fully interactive when not in loading state.
        </p>
        <button className="px-4 py-2 bg-blue-600 text-white rounded">
          Edit Principle
        </button>
      </div>
    )
  }
};
