import React from 'react';
import { motion } from 'framer-motion';
import PropTypes from 'prop-types';

export const StatsCard = ({
  title,
  value,
  icon: Icon,
  color,
  trend,
  description,
}) => {
  const colorClasses = {
    purple: 'bg-purple-500',
    green: 'bg-green-500',
    red: 'bg-red-500',
    blue: 'bg-blue-500',
  };

  const textColorClasses = {
    purple: 'text-purple-600 dark:text-purple-400',
    green: 'text-green-600 dark:text-green-400',
    red: 'text-red-600 dark:text-red-400',
    blue: 'text-blue-600 dark:text-blue-400',
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
    >
      <div className="flex items-center">
        <div className={`flex-shrink-0 p-3 rounded-lg ${colorClasses[color]} bg-opacity-10`}>
          <Icon className={`h-6 w-6 ${textColorClasses[color]}`} />
        </div>
        <div className="ml-4 flex-1">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {title}
          </p>
          <div className="flex items-baseline">
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {value.toLocaleString()}
            </p>
            {trend && (
              <span className="ml-2 text-sm font-medium text-green-600 dark:text-green-400">
                {trend}
              </span>
            )}
          </div>
          {description && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {description}
            </p>
          )}
        </div>
      </div>
    </motion.div>
  );
};

StatsCard.propTypes = {
  title: PropTypes.string.isRequired,
  value: PropTypes.number.isRequired,
  icon: PropTypes.elementType.isRequired,
  color: PropTypes.oneOf(['purple', 'green', 'red', 'blue']).isRequired,
  trend: PropTypes.string,
  description: PropTypes.string,
};
