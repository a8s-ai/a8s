'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { fetcher } from '@/lib/utils';
import type { User } from '@/lib/db/schema';
import { AdminDashboardHeader } from '@/components/admin-dashboard-header';
import { AdminDashboardStats } from '@/components/admin-dashboard-stats';
import { AdminDashboardTable } from '@/components/admin-dashboard-table';

interface PaginatedUsers {
  users: User[];
  meta: {
    total: number;
    page: number;
    limit: number;
    pageCount: number;
  };
}

export function AdminDashboard() {
  const [page, setPage] = useState(1);
  const [limit] = useState(10);

  const {
    data: usersData,
    isLoading,
    error,
  } = useSWR<PaginatedUsers>(`/api/users?page=${page}&limit=${limit}`, fetcher);

  if (error) {
    return <div className="p-6">Failed to load users</div>;
  }

  return (
    <div className="flex flex-col min-w-0 h-dvh bg-background">
      <AdminDashboardHeader />
      <div className="p-2 space-y-6">
        <AdminDashboardStats
          users={usersData?.users ?? []}
          totalUsers={usersData?.meta.total ?? 0}
        />
        <AdminDashboardTable
          users={usersData?.users ?? []}
          totalUsers={usersData?.meta.total ?? 0}
          isLoading={isLoading}
          page={page}
          limit={limit}
          pageCount={usersData?.meta.pageCount ?? 0}
          onPageChange={setPage}
        />
      </div>
    </div>
  );
}
