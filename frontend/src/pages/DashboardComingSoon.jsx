import { BarChart3, TrendingUp, Users, Calendar } from 'lucide-react';

export default function ComingSoonSplash() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full text-center">

        {/* Main Content */}
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Dashboard Coming Soon
        </h1>
        
        <p className="text-xl text-gray-600 mb-8 max-w-lg mx-auto">
          We're building something amazing for you. Your comprehensive analytics dashboard will be ready soon.
        </p>
      </div>
    </div>
  );
}