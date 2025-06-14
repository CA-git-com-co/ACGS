import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { ThemeToggle } from '@/components/layout/ThemeToggle'

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-large-heading font-bold text-gray-900 dark:text-gray-100">
          Settings
        </h1>
        <p className="text-body text-gray-500 dark:text-gray-400 mt-1">
          Manage your account settings and preferences
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              label="Full Name"
              placeholder="Enter your full name"
              defaultValue="John Doe"
            />
            <Input
              label="Email Address"
              type="email"
              placeholder="Enter your email"
              defaultValue="john.doe@example.com"
            />
            <Input
              label="Organization"
              placeholder="Enter your organization"
              defaultValue="Example Corp"
            />
            <Button>Save Changes</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Preferences</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-body font-medium">Theme</p>
                <p className="text-caption text-gray-500 dark:text-gray-400">
                  Choose your preferred theme
                </p>
              </div>
              <ThemeToggle />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <p className="text-body font-medium">Email Notifications</p>
                <p className="text-caption text-gray-500 dark:text-gray-400">
                  Receive updates about governance activities
                </p>
              </div>
              <input
                type="checkbox"
                defaultChecked
                className="rounded border-gray-300 text-accent-primary focus:ring-accent-primary"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="text-body font-medium">Auto-save Drafts</p>
                <p className="text-caption text-gray-500 dark:text-gray-400">
                  Automatically save policy and proposal drafts
                </p>
              </div>
              <input
                type="checkbox"
                defaultChecked
                className="rounded border-gray-300 text-accent-primary focus:ring-accent-primary"
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Security</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              label="Current Password"
              type="password"
              placeholder="Enter current password"
            />
            <Input
              label="New Password"
              type="password"
              placeholder="Enter new password"
            />
            <Input
              label="Confirm New Password"
              type="password"
              placeholder="Confirm new password"
            />
            <Button variant="outline">Change Password</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Keyboard Shortcuts</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-body">Open Command Palette</span>
              <kbd className="px-2 py-1 text-caption bg-gray-100 dark:bg-gray-700 rounded border">
                ⌘K
              </kbd>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-body">Create New Policy</span>
              <kbd className="px-2 py-1 text-caption bg-gray-100 dark:bg-gray-700 rounded border">
                ⌘N
              </kbd>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-body">Search</span>
              <kbd className="px-2 py-1 text-caption bg-gray-100 dark:bg-gray-700 rounded border">
                ⌘F
              </kbd>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}