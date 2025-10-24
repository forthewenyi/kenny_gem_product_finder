import { TierLevel } from '@/types'

interface TierBadgeProps {
  tier: TierLevel
  size?: 'sm' | 'md' | 'lg'
}

const tierConfig = {
  good: {
    label: 'GOOD',
    stars: '⭐',
    bgColor: 'bg-tier-good',
    textColor: 'text-white',
    description: '$20-80, 2-5 years',
  },
  better: {
    label: 'BETTER',
    stars: '⭐⭐',
    bgColor: 'bg-tier-better',
    textColor: 'text-white',
    description: '$80-200, 8-15 years',
  },
  best: {
    label: 'BEST',
    stars: '⭐⭐⭐',
    bgColor: 'bg-tier-best',
    textColor: 'text-white',
    description: '$200-600+, 15-30+ years',
  },
}

export default function TierBadge({ tier, size = 'md' }: TierBadgeProps) {
  const config = tierConfig[tier]

  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2',
  }

  return (
    <div
      className={`inline-flex items-center gap-1 rounded-full font-semibold ${config.bgColor} ${config.textColor} ${sizeClasses[size]}`}
    >
      <span>{config.stars}</span>
      <span>{config.label}</span>
    </div>
  )
}
