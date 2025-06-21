import React from 'react';
import { Link } from 'react-router-dom';

interface FooterProps {
  className?: string;
}

interface FooterLink {
  path: string;
  label: string;
  external?: boolean;
}

const Footer: React.FC<FooterProps> = ({ className = '' }) => {
  const currentYear = new Date().getFullYear();

  const footerLinks: FooterLink[] = [
    { path: '/docs', label: 'Documentation' },
    { path: '/privacy', label: 'Privacy Policy' },
    { path: '/terms', label: 'Terms of Service' },
    { path: '/about', label: 'About' },
    { path: '/contact', label: 'Contact' }
  ];

  const socialLinks: FooterLink[] = [
    { path: 'https://github.com/CA-git-com-co/ACGS', label: 'GitHub', external: true },
    { path: 'https://twitter.com/acgs-pgp', label: 'Twitter', external: true },
    { path: 'https://discord.gg/acgs-pgp', label: 'Discord', external: true }
  ];

  const renderLink = (link: FooterLink) => {
    if (link.external) {
      return (
        <a
          key={link.path}
          href={link.path}
          target="_blank"
          rel="noopener noreferrer"
          className="text-gray-300 hover:text-white text-sm transition-colors duration-200"
        >
          {link.label}
        </a>
      );
    }

    return (
      <Link
        key={link.path}
        to={link.path}
        className="text-gray-300 hover:text-white text-sm transition-colors duration-200"
      >
        {link.label}
      </Link>
    );
  };

  return (
    <footer className={`bg-gray-800 text-white ${className}`}>
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Section */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center mb-4">
              <span className="text-2xl mr-2">🏛️</span>
              <h3 className="text-lg font-bold">ACGS-PGP Framework</h3>
            </div>
            <p className="text-gray-300 text-sm leading-relaxed mb-4">
              Artificial Constitution and Self-Synthesizing Prompt Governance Compiler - A
              comprehensive framework for constitutional governance systems with real-time
              compliance validation and democratic policy synthesis.
            </p>
            <div className="flex items-center space-x-2 text-sm text-gray-400">
              <span>🔗</span>
              <span>Powered by Solana Blockchain</span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-sm font-semibold text-gray-200 uppercase tracking-wider mb-4">
              Quick Links
            </h4>
            <div className="space-y-2">{footerLinks.map(renderLink)}</div>
          </div>

          {/* Community */}
          <div>
            <h4 className="text-sm font-semibold text-gray-200 uppercase tracking-wider mb-4">
              Community
            </h4>
            <div className="space-y-2">{socialLinks.map(renderLink)}</div>
            <div className="mt-4">
              <h5 className="text-sm font-medium text-gray-300 mb-2">System Status</h5>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-xs text-gray-400">All systems operational</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="mt-8 pt-8 border-t border-gray-700">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-sm text-gray-300">
              © {currentYear} ACGS-PGP Framework. All rights reserved.
            </div>

            <div className="flex items-center space-x-4 mt-4 md:mt-0">
              <div className="text-xs text-gray-400">Version 1.0.0</div>
              <div className="text-xs text-gray-400">Constitution Hash: cdd01ef066bc6cf2</div>
            </div>
          </div>

          <div className="mt-4 text-center">
            <p className="text-xs text-gray-400">
              Built with ❤️ for transparent and democratic governance systems
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
