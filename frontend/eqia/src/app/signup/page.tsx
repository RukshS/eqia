import { Metadata } from 'next';
import SignupForm from '@/components/auth/SignupForm';

export const metadata: Metadata = {
  title: 'Sign Up - EQIA',
  description: 'Create your EQIA account to get started',
};

export default function SignupPage() {
  return <SignupForm />;
}
