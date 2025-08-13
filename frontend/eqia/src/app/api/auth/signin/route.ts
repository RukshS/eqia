import { NextRequest, NextResponse } from 'next/server';

interface SigninRequestBody {
  email: string;
  password: string;
}

export async function POST(request: NextRequest) {
  try {
    const body: SigninRequestBody = await request.json();
    const { email, password } = body;

    if (!email || !password) {
      return NextResponse.json({ message: 'Email and password are required' }, { status: 400 });
    }

    // Mock authentication
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json({ message: 'Invalid email format' }, { status: 400 });
    }

    // Simulate a simple credential check
    const isValid = password.length >= 8;
    await new Promise((r) => setTimeout(r, 800));

    if (!isValid) {
      return NextResponse.json({ message: 'Invalid credentials' }, { status: 401 });
    }

    // In a real app, create a session/JWT here
    return NextResponse.json({ message: 'Signed in', user: { email } }, { status: 200 });
  } catch (error) {
    console.error('Signin error:', error);
    return NextResponse.json({ message: 'Internal server error' }, { status: 500 });
  }
}
