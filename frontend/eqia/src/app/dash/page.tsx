import dynamic from 'next/dynamic';

// Import the client Dashboard component dynamically to ensure proper SSR handling
const Dashboard = dynamic(() => import('./dashboard'), { ssr: false });

export const metadata = {
  title: 'Dashboard - EQIA',
  description: 'Environmental Quality Monitoring Dashboard',
};

export default function DashboardPage() {
  return <Dashboard />;
}
