'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X, ChevronLeft, ChevronRight } from 'lucide-react';
import { useResponsive } from '@/hooks/useResponsive';
import { cn } from '@/lib/utils';

interface ResponsiveLayoutProps {
  navbar: React.ReactNode;
  sidebar: React.ReactNode;
  children: React.ReactNode;
}

export function ResponsiveLayout({ navbar, sidebar, children }: ResponsiveLayoutProps) {
  const { isMobile, isTablet } = useResponsive();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
  const toggleCollapse = () => setSidebarCollapsed(!sidebarCollapsed);

  // Mobile layout
  if (isMobile) {
    return (
      <div className="flex h-screen flex-col overflow-hidden">
        {/* Mobile Navbar */}
        <div className="relative z-50">
          {navbar}
        </div>

        {/* Mobile Content */}
        <div className="relative flex flex-1 overflow-hidden">
          {/* Main Content */}
          <main className="flex-1 overflow-auto">
            <div className="p-4">
              {children}
            </div>
          </main>

          {/* Mobile Sidebar Overlay */}
          <AnimatePresence>
            {sidebarOpen && (
              <>
                {/* Backdrop */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="absolute inset-0 z-40 bg-black/50"
                  onClick={() => setSidebarOpen(false)}
                />

                {/* Sidebar */}
                <motion.div
                  initial={{ x: '100%' }}
                  animate={{ x: 0 }}
                  exit={{ x: '100%' }}
                  transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                  className="absolute right-0 top-0 z-50 h-full w-80 max-w-[80vw] overflow-auto bg-dark-800 shadow-xl"
                >
                  {/* Close Button */}
                  <div className="flex items-center justify-between border-b border-dark-700 p-4">
                    <h3 className="text-lg font-semibold text-white">Dashboard</h3>
                    <button
                      onClick={() => setSidebarOpen(false)}
                      className="rounded-lg p-2 text-dark-400 hover:bg-dark-700 hover:text-white"
                    >
                      <X className="h-5 w-5" />
                    </button>
                  </div>
                  
                  <div className="p-4">
                    {sidebar}
                  </div>
                </motion.div>
              </>
            )}
          </AnimatePresence>

          {/* Mobile Sidebar Toggle */}
          <button
            onClick={toggleSidebar}
            className="fixed bottom-6 right-6 z-30 rounded-full bg-primary-600 p-3 text-white shadow-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-dark-900"
          >
            <Menu className="h-6 w-6" />
          </button>
        </div>
      </div>
    );
  }

  // Tablet layout
  if (isTablet) {
    return (
      <div className="flex h-screen flex-col overflow-hidden">
        {/* Navbar */}
        <div className="relative z-40">
          {navbar}
        </div>

        {/* Content */}
        <div className="flex flex-1 overflow-hidden">
          {/* Main Content */}
          <main className="flex-1 overflow-auto">
            <div className="p-6">
              {children}
            </div>
          </main>

          {/* Tablet Sidebar */}
          <AnimatePresence>
            {sidebarOpen && (
              <motion.aside
                initial={{ width: 0, opacity: 0 }}
                animate={{ width: 384, opacity: 1 }}
                exit={{ width: 0, opacity: 0 }}
                transition={{ duration: 0.3, ease: 'easeInOut' }}
                className="border-l border-dark-700 bg-dark-800/50 backdrop-blur-sm overflow-hidden"
              >
                <div className="h-full overflow-auto p-6">
                  {sidebar}
                </div>
              </motion.aside>
            )}
          </AnimatePresence>

          {/* Tablet Sidebar Toggle */}
          <button
            onClick={toggleSidebar}
            className={cn(
              'fixed right-4 top-1/2 z-30 -translate-y-1/2 rounded-l-lg bg-dark-700 p-2 text-dark-300 shadow-lg transition-all hover:bg-dark-600 hover:text-white',
              sidebarOpen ? 'translate-x-0' : 'translate-x-1'
            )}
          >
            {sidebarOpen ? (
              <ChevronRight className="h-5 w-5" />
            ) : (
              <ChevronLeft className="h-5 w-5" />
            )}
          </button>
        </div>
      </div>
    );
  }

  // Desktop layout
  return (
    <div className="flex h-screen flex-col overflow-hidden">
      {/* Navbar */}
      <div className="relative z-40">
        {navbar}
      </div>

      {/* Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          <div className="p-8">
            {children}
          </div>
        </main>

        {/* Desktop Sidebar */}
        <motion.aside
          animate={{
            width: sidebarCollapsed ? 60 : 384,
          }}
          transition={{ duration: 0.3, ease: 'easeInOut' }}
          className="border-l border-dark-700 bg-dark-800/30 backdrop-blur-sm"
        >
          {/* Collapse Toggle */}
          <div className="flex items-center justify-between border-b border-dark-700 p-4">
            {!sidebarCollapsed && (
              <h3 className="text-lg font-semibold text-white">Dashboard</h3>
            )}
            <button
              onClick={toggleCollapse}
              className="rounded-lg p-2 text-dark-400 hover:bg-dark-700 hover:text-white"
            >
              {sidebarCollapsed ? (
                <ChevronLeft className="h-5 w-5" />
              ) : (
                <ChevronRight className="h-5 w-5" />
              )}
            </button>
          </div>

          {/* Sidebar Content */}
          <div className="h-full overflow-auto">
            {sidebarCollapsed ? (
              <div className="p-2">
                {/* Collapsed sidebar content - could show icons only */}
                <div className="space-y-2">
                  <div className="h-8 w-8 rounded bg-dark-700" />
                  <div className="h-8 w-8 rounded bg-dark-700" />
                  <div className="h-8 w-8 rounded bg-dark-700" />
                </div>
              </div>
            ) : (
              <div className="p-6">
                {sidebar}
              </div>
            )}
          </div>
        </motion.aside>
      </div>
    </div>
  );
}
