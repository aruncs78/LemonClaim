'use client';

import { useEffect, useState } from 'react';
import { Shield, FileText, DollarSign, Bell } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { userApi } from '@/lib/api';

export default function DashboardPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    userApi.getDashboard().then(setData).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" /></div>;

  const stats = [
    { label: 'Active Policies', value: data?.summary?.active_policies || 0, icon: Shield, color: 'text-blue-500' },
    { label: 'Pending Claims', value: data?.summary?.pending_claims || 0, icon: FileText, color: 'text-orange-500' },
    { label: 'Total Coverage', value: `$${(data?.summary?.total_coverage || 0).toLocaleString()}`, icon: DollarSign, color: 'text-green-500' },
    { label: 'Notifications', value: data?.summary?.unread_notifications || 0, icon: Bell, color: 'text-purple-500' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Welcome back, {data?.user?.full_name?.split(' ')[0] || 'User'}!</h1>
        <p className="text-gray-600 mt-1">Here's an overview of your insurance coverage.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">{stat.label}</p>
                  <p className="text-2xl font-bold mt-1">{stat.value}</p>
                </div>
                <div className={`p-3 rounded-full bg-gray-100 ${stat.color}`}>
                  <stat.icon className="w-6 h-6" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle>Recent Policies</CardTitle></CardHeader>
          <CardContent>
            {data?.recent_policies?.length > 0 ? (
              <div className="space-y-4">
                {data.recent_policies.map((policy: any) => (
                  <div key={policy.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium">{policy.policy_type?.replace('_', ' ')?.toUpperCase()}</p>
                      <p className="text-sm text-gray-500">{policy.policy_number}</p>
                    </div>
                    <span className="px-3 py-1 text-xs rounded-full bg-green-100 text-green-800">{policy.status}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No policies yet. Get your first quote!</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Recent Payments</CardTitle></CardHeader>
          <CardContent>
            {data?.recent_payments?.length > 0 ? (
              <div className="space-y-4">
                {data.recent_payments.map((payment: any) => (
                  <div key={payment.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium">${Number(payment.amount).toFixed(2)}</p>
                      <p className="text-sm text-gray-500">{payment.description}</p>
                    </div>
                    <span className={`px-3 py-1 text-xs rounded-full ${payment.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>{payment.status}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No payments yet.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
