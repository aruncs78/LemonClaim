'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Shield, Zap, MessageCircle, CreditCard, CheckCircle, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

const features = [
  { icon: <Zap className="w-6 h-6" />, title: 'Instant Quotes', description: 'Get covered in minutes with AI-powered quotes.' },
  { icon: <MessageCircle className="w-6 h-6" />, title: 'Maya AI Assistant', description: 'File claims through friendly conversation.' },
  { icon: <Shield className="w-6 h-6" />, title: 'Complete Coverage', description: 'Home, renters, auto, life, and pet insurance.' },
  { icon: <CreditCard className="w-6 h-6" />, title: 'Fast Payouts', description: 'Get paid in minutes for approved claims.' },
];

const insuranceTypes = [
  { name: 'Home', emoji: '🏠', price: 'from $25/mo' },
  { name: 'Renters', emoji: '🏢', price: 'from $5/mo' },
  { name: 'Auto', emoji: '🚗', price: 'from $50/mo' },
  { name: 'Life', emoji: '❤️', price: 'from $9/mo' },
  { name: 'Pet', emoji: '🐕', price: 'from $12/mo' },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full gradient-primary flex items-center justify-center">
                <span className="text-white font-bold">L</span>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">LemonClaim</span>
            </Link>
            <div className="flex items-center space-x-4">
              <Link href="/login"><Button variant="ghost">Log in</Button></Link>
              <Link href="/register"><Button>Get Started</Button></Link>
            </div>
          </div>
        </div>
      </nav>

      <section className="pt-32 pb-20 px-4 gradient-hero text-white">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-5xl lg:text-6xl font-bold mb-6">Insurance that's<br /><span className="text-white/90">actually simple</span></h1>
            <p className="text-xl text-white/80 mb-8 max-w-lg mx-auto">Get covered in minutes. File claims through AI chat. Receive payouts instantly.</p>
            <div className="flex justify-center gap-4">
              <Link href="/register"><Button size="lg" className="bg-white text-primary hover:bg-white/90">Get Your Quote <ArrowRight className="ml-2 w-5 h-5" /></Button></Link>
            </div>
            <div className="flex justify-center items-center gap-6 mt-8 text-white/70">
              <div className="flex items-center gap-2"><CheckCircle className="w-5 h-5" /><span>No hidden fees</span></div>
              <div className="flex items-center gap-2"><CheckCircle className="w-5 h-5" /><span>Cancel anytime</span></div>
            </div>
          </motion.div>
        </div>
      </section>

      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-bold text-gray-900 mb-12 text-center">Coverage for everything you love</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {insuranceTypes.map((type) => (
              <div key={type.name} className="bg-white rounded-2xl border-2 border-gray-100 p-6 text-center hover:border-primary hover:shadow-lg transition-all cursor-pointer">
                <span className="text-4xl">{type.emoji}</span>
                <h3 className="font-semibold text-gray-900 mt-3">{type.name}</h3>
                <p className="text-primary font-medium mt-1">{type.price}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 px-4 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-bold text-gray-900 mb-12 text-center">Why choose LemonClaim?</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature) => (
              <div key={feature.title} className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className="w-12 h-12 rounded-xl gradient-primary flex items-center justify-center text-white mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 px-4 gradient-hero text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to get started?</h2>
          <p className="text-xl text-white/80 mb-8">Join over 500,000 happy customers who trust LemonClaim.</p>
          <Link href="/register"><Button size="lg" className="bg-white text-primary hover:bg-white/90">Get Your Free Quote <ArrowRight className="ml-2 w-5 h-5" /></Button></Link>
        </div>
      </section>

      <footer className="bg-gray-900 text-white py-12 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-gray-400">© 2024 LemonClaim Insurance. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
