import { NextRequest, NextResponse } from 'next/server';

interface SignupRequestBody {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
}

export async function POST(request: NextRequest) {
  try {
    const body: SignupRequestBody = await request.json();
    const { firstName, lastName, email, password } = body;

    // Basic validation
    if (!firstName || !lastName || !email || !password) {
      return NextResponse.json(
        { message: 'All fields are required' },
        { status: 400 }
      );
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { message: 'Invalid email format' },
        { status: 400 }
      );
    }

    // Password validation
    if (password.length < 8) {
      return NextResponse.json(
        { message: 'Password must be at least 8 characters long' },
        { status: 400 }
      );
    }

    // Mock check for existing user
    if (email === 'test@example.com') {
      return NextResponse.json(
        { message: 'User with this email already exists' },
        { status: 409 }
      );
    }

    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Mock successful user creation
    const mockUser = {
      id: Date.now().toString(),
      firstName,
      lastName,
      email,
      createdAt: new Date().toISOString(),
    };

    console.log('Mock user created:', mockUser);

    // In a real application, you would:
    // 1. Hash the password
    // 2. Save user to database
    // 3. Send verification email
    // 4. Create session/JWT token

    return NextResponse.json(
      {
        message: 'Account created successfully',
        user: {
          id: mockUser.id,
          firstName: mockUser.firstName,
          lastName: mockUser.lastName,
          email: mockUser.email,
        },
      },
      { status: 201 }
    );
  } catch (error) {
    console.error('Signup error:', error);
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}
