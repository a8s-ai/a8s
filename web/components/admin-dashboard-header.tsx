'use client';

import { SidebarToggle } from '@/components/sidebar-toggle';
import { Button } from '@/components/ui/button';
import { memo } from 'react';
import { UserRoundPlus } from 'lucide-react';

function PureAdminDashboardHeader() {
  return (
    <header className="flex sticky top-0 bg-background py-1.5 items-center px-2 md:px-2 gap-2">
      <SidebarToggle />

      <h1 className="order-2 md:order-1 md:px-2 px-2 md:h-fit ml-auto md:ml-0 font-semibold">
        Admin Dashboard
      </h1>

      <Button className="bg-zinc-900 dark:bg-zinc-100 hover:bg-zinc-800 dark:hover:bg-zinc-200 text-zinc-50 dark:text-zinc-900 hidden md:flex py-1.5 px-4 h-fit md:h-[34px] order-4 md:ml-auto">
        <UserRoundPlus className="size-4" />
        Add new user
      </Button>
    </header>
  );
}

export const AdminDashboardHeader = memo(PureAdminDashboardHeader);
