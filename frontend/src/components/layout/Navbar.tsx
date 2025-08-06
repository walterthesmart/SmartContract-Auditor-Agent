'use client';

import { useState } from 'react';
import Image from 'next/image';
import { Menu, X, Shield, FileText, Award, BookOpen, ExternalLink } from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavbarProps {
  readonly activeSection: string;
  readonly onSectionChange: (section: string) => void;
}

const navigationItems = [
  { id: 'dashboard', label: 'Dashboard', icon: Shield },
  { id: 'reports', label: 'Reports', icon: FileText },
  { id: 'nfts', label: 'NFT Certificates', icon: Award },
  { id: 'tutorial', label: 'Tutorial', icon: BookOpen },
];

export function Navbar({ activeSection, onSectionChange }: NavbarProps): JSX.Element {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const handleSectionChange = (sectionId: string) => {
    onSectionChange(sectionId);
    setIsMobileMenuOpen(false);
  };

  const openApiDocs = (): void => {
    window.open(`${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'}/docs`, '_blank');
  };

  return (
    <nav className="sticky top-0 z-50 border-b border-dark-700 bg-dark-800/80 backdrop-blur-md">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-3">
            <div className="relative h-8 w-8">
              <Image
                src="/assets/images/logo.png"
                alt="HederaAuditAI Logo"
                width={32}
                height={32}
                className="rounded-md"
                onError={(e) => {
                  e.currentTarget.style.display = 'none';
                }}
              />
            </div>
            <h1 className="text-xl font-bold text-gradient">
              HederaAuditAI
            </h1>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleSectionChange(item.id)}
                    className={cn(
                      'flex items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                      activeSection === item.id
                        ? 'bg-primary-600/20 text-primary-400'
                        : 'text-dark-300 hover:bg-dark-700 hover:text-white'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </button>
                );
              })}
              <button
                onClick={openApiDocs}
                className="flex items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium text-dark-300 transition-colors hover:bg-dark-700 hover:text-white"
              >
                <ExternalLink className="h-4 w-4" />
                <span>API Docs</span>
              </button>
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={toggleMobileMenu}
              className="inline-flex items-center justify-center rounded-md p-2 text-dark-400 hover:bg-dark-700 hover:text-white focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
              aria-expanded="false"
            >
              <span className="sr-only">Open main menu</span>
              {isMobileMenuOpen ? (
                <X className="block h-6 w-6" aria-hidden="true" />
              ) : (
                <Menu className="block h-6 w-6" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden">
          <div className="space-y-1 border-t border-dark-700 bg-dark-800 px-2 pb-3 pt-2 sm:px-3">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => handleSectionChange(item.id)}
                  className={cn(
                    'flex w-full items-center space-x-2 rounded-lg px-3 py-2 text-base font-medium transition-colors',
                    activeSection === item.id
                      ? 'bg-primary-600/20 text-primary-400'
                      : 'text-dark-300 hover:bg-dark-700 hover:text-white'
                  )}
                >
                  <Icon className="h-5 w-5" />
                  <span>{item.label}</span>
                </button>
              );
            })}
            <button
              onClick={openApiDocs}
              className="flex w-full items-center space-x-2 rounded-lg px-3 py-2 text-base font-medium text-dark-300 transition-colors hover:bg-dark-700 hover:text-white"
            >
              <ExternalLink className="h-5 w-5" />
              <span>API Docs</span>
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}
