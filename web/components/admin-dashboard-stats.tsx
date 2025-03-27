'use client';

import { Card } from '@/components/ui/card';
import type { User } from '@/lib/db/schema';

interface StatsProps {
  users: User[];
  totalUsers: number;
}

export function AdminDashboardStats({ users, totalUsers }: StatsProps) {
  const stats = [
    { title: 'Total Users', count: totalUsers, type: 'total' },
    {
      title: 'Admins',
      count: users.filter((u) => u.role === 'admin').length,
      type: 'admin',
    },
    { title: 'Active Users', count: totalUsers, type: 'active' },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {stats.map((stat) => (
        <Card key={stat.type} className="p-4">
          <div className="flex flex-col gap-1">
            <h3 className="text-sm font-medium text-muted-foreground">
              {stat.title}
            </h3>
            <p className="text-2xl font-bold">{stat.count.toLocaleString()}</p>
          </div>
        </Card>
      ))}
    </div>
  );
}
