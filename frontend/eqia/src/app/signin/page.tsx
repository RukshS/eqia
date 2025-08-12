import { Metadata } from 'next';
import SigninForm from '@/components/auth/SigninForm';

export const metadata: Metadata = {
  title: 'Sign In - EQIA',
  description: 'Sign in to your EQIA account',
};

export default function SigninPage() {
  return <SigninForm />;
}
