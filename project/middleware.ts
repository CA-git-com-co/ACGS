import { NextRequest, NextResponse } from 'next/server';
import { getToken } from 'next-auth/jwt';

const protectedRoutes = ['/governance', '/constitutional', '/admin'];

const publicRoutes = ['/', '/login', '/about', '/contact'];

export async function middleware(req: NextRequest) {
  const path = req.nextUrl.pathname;

  // Skip middleware for API routes, static files, and Next.js internals
  if (
    path.startsWith('/api/') ||
    path.startsWith('/_next/') ||
    path.startsWith('/favicon.ico') ||
    path.includes('.')
  ) {
    return NextResponse.next();
  }

  const isProtectedRoute = protectedRoutes.some(
    route => path === route || path.startsWith(`${route}/`)
  );

  const isPublicRoute = publicRoutes.some(route => path === route || path.startsWith(`${route}/`));

  const token = await getToken({ req });

  // Redirect to login if accessing protected route without session
  if (isProtectedRoute && !token) {
    const url = new URL('/login', req.url);
    url.searchParams.set('callbackUrl', encodeURI(req.url));
    return NextResponse.redirect(url);
  }

  // Redirect to dashboard if accessing login with session
  if (path === '/login' && token) {
    return NextResponse.redirect(new URL('/governance/dashboard', req.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
