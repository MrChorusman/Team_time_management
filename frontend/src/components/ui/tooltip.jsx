import { useState } from 'react'
import { cn } from '@/lib/utils.js'

const Tooltip = ({ children, content, className }) => {
  const [show, setShow] = useState(false)

  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
      >
        {children}
      </div>
      {show && (
        <div className={cn(
          "absolute z-50 px-3 py-2 text-sm font-medium text-white bg-gray-900 dark:bg-gray-700 rounded-lg shadow-lg",
          "bottom-full left-1/2 transform -translate-x-1/2 mb-2",
          "whitespace-nowrap",
          "before:content-[''] before:absolute before:top-full before:left-1/2 before:transform before:-translate-x-1/2",
          "before:border-4 before:border-transparent before:border-t-gray-900 dark:before:border-t-gray-700",
          className
        )}>
          {content}
        </div>
      )}
    </div>
  )
}

export { Tooltip }
