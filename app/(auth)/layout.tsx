import { ClientSessionProvider } from '@/components/session-provider';
import { auth } from './auth';

export default async function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await auth();

  return (
    <ClientSessionProvider session={session}>{children}</ClientSessionProvider>
  );
}