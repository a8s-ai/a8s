import 'next-auth';
import type { DefaultSession, User as NextAuthUser } from 'next-auth';

declare module 'next-auth' {
  interface Session extends DefaultSession {
    user: NextAuthUser & {
      role: 'user' | 'admin';
    };
  }

  interface User extends NextAuthUser {
    role: 'user' | 'admin';
  }
}
