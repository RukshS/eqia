import { Metadata } from 'next';
<<<<<<< HEAD
import SigninForm from '@/components/auth/SigninForm';
=======
import SigninForm from '@/app/auth/SigninForm';
>>>>>>> 5c5bad20bbe98aa0de4283e9c096c1d9a2c741fd

export const metadata: Metadata = {
  title: 'Sign In - EQIA',
  description: 'Sign in to your EQIA account',
};

export default function SigninPage() {
  return <SigninForm />;
}
