'use client';

import { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search } from 'lucide-react';
import type { User } from '@/lib/db/schema';
import { formatDate } from '@/lib/utils';

interface TableProps {
  users: User[];
  totalUsers: number;
  isLoading: boolean;
  page: number;
  limit: number;
  pageCount: number;
  onPageChange: (page: number) => void;
}

export function AdminDashboardTable({
  users,
  totalUsers,
  isLoading,
  page,
  limit,
  pageCount,
  onPageChange,
}: TableProps) {
  const [searchQuery, setSearchQuery] = useState('');
  return (
    <div className="space-y-4 px-2">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold">All users ({totalUsers})</h2>
        <div className="relative">
          <Search className="absolute left-2 top-2.5 size-4 text-muted-foreground" />
          <Input
            placeholder="Search users..."
            className="pl-8 rounded-lg h-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Table */}
      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead>Email</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Created On</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={3} className="text-center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : (
              users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell className="font-medium">{user.email}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">{user.role}</Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {formatDate(user.createdAt)}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex justify-between items-center">
        <div className="text-sm text-muted-foreground">
          Showing {(page - 1) * limit + 1} to{' '}
          {Math.min(page * limit, totalUsers)} of {totalUsers} users
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            className="rounded-lg h-8"
            onClick={() => onPageChange(Math.max(1, page - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            className="rounded-lg h-8"
            onClick={() => onPageChange(page + 1)}
            disabled={page >= pageCount}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}
