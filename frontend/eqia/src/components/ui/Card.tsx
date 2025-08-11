import { HTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, title, description, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'rounded-lg border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800',
          className
        )}
        {...props}
      >
        {(title || description) && (
          <div className="p-6 pb-4">
            {title && (
              <h3 className="text-lg font-semibold leading-none tracking-tight text-gray-900 dark:text-white">
                {title}
              </h3>
            )}
            {description && (
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                {description}
              </p>
            )}
          </div>
        )}
        <div className={title || description ? 'px-6 pb-6' : 'p-6'}>
          {children}
        </div>
      </div>
    );
  }
);

Card.displayName = 'Card';

export default Card;
