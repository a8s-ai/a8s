import { auth } from '@/app/(auth)/auth';
import { redirect } from 'next/navigation';
import { AdminDashboard } from '@/components/admin-dashboard';

export default async function AdminDashboardPage() {
  const session = await auth();

  if (!session || session.user?.role !== 'admin') {
    redirect('/');
  }

  return <AdminDashboard />;
}
