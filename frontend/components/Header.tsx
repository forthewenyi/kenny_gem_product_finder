'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import NavigationDropdown from './NavigationDropdown'
import { getPopularSearches, trackSearch, type PopularSearchItem } from '@/lib/api'

interface HeaderProps {
  onNavigate?: (category: string) => void
  onSearch?: (query: string) => void
}

export default function Header({ onNavigate, onSearch }: HeaderProps) {
  const router = useRouter()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [expandedMobileCategory, setExpandedMobileCategory] = useState<string | null>(null)
  const [isLoggingOut, setIsLoggingOut] = useState(false)

  // Categories with dropdowns
  const dropdownCategories = [
    { id: 'cookware', label: 'COOKWARE' },
    { id: 'knives', label: 'KNIVES' },
    { id: 'bakeware', label: 'BAKEWARE' },
  ] as const

  const handleCategoryClick = (categoryId: string) => {
    // Toggle the category expansion in mobile
    if (expandedMobileCategory === categoryId) {
      setExpandedMobileCategory(null)
    } else {
      setExpandedMobileCategory(categoryId)
    }
  }

  const handleDropdownSearch = (query: string, category: string) => {
    if (onSearch) {
      onSearch(query)
    }
    setMobileMenuOpen(false) // Close mobile menu after search
    setExpandedMobileCategory(null)
  }

  const handleLogout = async () => {
    if (isLoggingOut) return

    setIsLoggingOut(true)
    try {
      const response = await fetch('/api/auth/logout', {
        method: 'POST',
      })

      if (response.ok) {
        router.push('/login')
        router.refresh()
      }
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      setIsLoggingOut(false)
    }
  }

  return (
    <>
      <header className="sticky top-0 bg-white border-b border-gray-200 px-4 md:px-10 py-4 md:py-5 flex justify-between items-center z-50">
        {/* Left side: Logo + Navigation */}
        <div className="flex items-center gap-4 md:gap-10">
          {/* Logo */}
          <div className="flex items-center gap-2 text-base md:text-xl font-bold uppercase tracking-wider">
            <span>⛏️</span>
            <span className="hidden sm:inline">KENNY GEM FINDER</span>
            <span className="sm:hidden">KENNY</span>
          </div>

          {/* Desktop Navigation with Dropdowns */}
          <nav className="hidden md:flex gap-6">
            {dropdownCategories.map((category) => (
              <NavigationDropdown
                key={category.id}
                category={category.id}
                label={category.label}
                onSearch={handleDropdownSearch}
              />
            ))}
          </nav>
        </div>

        {/* Right side: Mobile Menu + Cart Icon + Logout */}
        <div className="flex items-center gap-4">
          {/* Mobile Menu Button */}
          <button
            className="md:hidden text-2xl"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? '✕' : '☰'}
          </button>

          {/* Cart Icon */}
          <div className="text-xl cursor-pointer">
            🛒
          </div>

          {/* Logout Button */}
          <button
            onClick={handleLogout}
            disabled={isLoggingOut}
            className="text-[11px] uppercase tracking-wide text-[#79786c] hover:text-black transition-colors disabled:opacity-50"
            aria-label="Logout"
          >
            {isLoggingOut ? 'Logging out...' : 'Logout'}
          </button>
        </div>
      </header>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed top-[57px] left-0 right-0 bg-white border-b border-gray-200 shadow-xl z-40 animate-slideDown max-h-[80vh] overflow-y-auto">
          <nav className="flex flex-col py-2">
            {dropdownCategories.map((category) => (
              <MobileCategorySection
                key={category.id}
                category={category.id}
                label={category.label}
                isExpanded={expandedMobileCategory === category.id}
                onToggle={() => handleCategoryClick(category.id)}
                onItemSelect={(term: string) => {
                  trackSearch(term, category.id)
                  handleDropdownSearch(term, category.id)
                }}
              />
            ))}
          </nav>
        </div>
      )}
    </>
  )
}

// Mobile Category Section Component
interface MobileCategorySectionProps {
  category: string
  label: string
  isExpanded: boolean
  onToggle: () => void
  onItemSelect: (term: string) => void
}

function MobileCategorySection({ category, label, isExpanded, onToggle, onItemSelect }: MobileCategorySectionProps) {
  // Fetch popular searches when expanded
  const { data, isLoading } = useQuery({
    queryKey: ['popular-searches', category],
    queryFn: () => getPopularSearches(category),
    enabled: isExpanded,
    staleTime: 1000 * 60 * 60, // Cache for 1 hour
  })

  return (
    <div className="border-b border-gray-100 last:border-b-0">
      {/* Category Header */}
      <button
        onClick={onToggle}
        className="w-full text-left px-5 py-3 text-[11px] uppercase tracking-wide text-black hover:bg-[#f8f8f8] transition-colors flex items-center justify-between"
      >
        <span>{label}</span>
        <span className="text-base">{isExpanded ? '−' : '+'}</span>
      </button>

      {/* Expanded Popular Items */}
      {isExpanded && (
        <div className="bg-[#f8f8f8] py-1">
          {isLoading && (
            <div className="px-8 py-2 text-[10px] text-[#79786c] uppercase tracking-wide">
              Loading...
            </div>
          )}

          {!isLoading && data?.items && data.items.length === 0 && (
            <div className="px-8 py-2 text-[10px] text-[#79786c] uppercase tracking-wide">
              No popular searches yet
            </div>
          )}

          {!isLoading && data?.items && data.items.length > 0 && (
            <ul>
              {data.items.map((item: PopularSearchItem, idx: number) => (
                <li key={idx}>
                  <button
                    onClick={() => onItemSelect(item.term)}
                    className="w-full text-left px-8 py-2 text-[10px] hover:bg-white transition-colors"
                  >
                    <span className="text-black uppercase tracking-wide">
                      {item.term}
                    </span>
                    <span className="ml-2 text-[9px] text-[#79786c]">
                      ({item.count})
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
