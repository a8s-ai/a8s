import { auth } from '@/app/(auth)/auth';
import {
  getUser,
  getUsersCount,
  getUsersWithPagination,
} from '@/lib/db/queries';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const page = Number.parseInt(searchParams.get('page') || '1', 10);
  const limit = Number.parseInt(searchParams.get('limit') || '10', 10);

  const session = await auth();

  if (!session?.user || !session.user.email) {
    return new Response('Unauthorized', { status: 401 });
  }

  const [user] = await getUser(session.user.email);

  if (user.role !== 'admin') {
    return new Response('Forbidden', { status: 403 });
  }

  try {
    const [users, totalUsers] = await Promise.all([
      getUsersWithPagination({ page, limit }),
      getUsersCount(),
    ]);

    return Response.json({
      users,
      meta: {
        total: totalUsers,
        page,
        limit,
        pageCount: Math.ceil(totalUsers / limit),
      },
    });
  } catch (error) {
    console.error('Error in users API:', error);
    return new Response('Internal Server Error', { status: 500 });
  }
}
