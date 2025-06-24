interface User {
  name?: string | null;
  role?: string;
}

interface DashboardHeaderProps {
  user: User;
}

export function DashboardHeader({ user }: DashboardHeaderProps) {
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="space-y-2">
      <h1 className="text-3xl font-bold tracking-tight">
        {getGreeting()}, {user.name}
      </h1>
      <p className="text-muted-foreground">
        Welcome to your governance dashboard. Here's what's happening today.
      </p>
    </div>
  );
}