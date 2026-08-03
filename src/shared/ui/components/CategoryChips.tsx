'use client';

import { useState } from 'react';

interface CategoryChipProps {
  label: string;
  value: string;
  isSelected: boolean;
  onClick: () => void;
}

const CategoryChip: React.FC<CategoryChipProps> = ({ 
  label, 
  value, 
  isSelected, 
  onClick 
}) => {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-full text-sm font-medium transition duration-300 ${
        isSelected 
          ? 'bg-teal-600 text-white shadow-md' 
          : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
      }`}
    >
      {label}
    </button>
  );
};

interface CategoryChipsProps {
  onCitySelect: (city: string) => void;
  selectedCity: string;
}

export const CategoryChips: React.FC<CategoryChipsProps> = ({ 
  onCitySelect, 
  selectedCity 
}) => {
  const [chips] = useState([
    { label: 'Veterinaria', value: 'veterinary' },
    { label: 'Estética', value: 'grooming' },
    { label: 'Urgencias', value: 'emergency' },
    { label: 'Todos', value: '' }
  ]);
  
  const cities = [
    { label: 'Madrid', value: 'madrid' },
    { label: 'Barcelona', value: 'barcelona' },
    { label: 'Valencia', value: 'valencia' },
    { label: 'Sevilla', value: 'sevilla' },
    { label: 'Zaragoza', value: 'zaragoza' }
  ];

  const handleCityClick = (cityValue: string) => {
    onCitySelect(cityValue);
  };

  return (
    <div className="flex flex-wrap justify-center gap-3">
      {/* Category Chips */}
      <div className="flex flex-wrap justify-center gap-3 mb-6">
        {chips.map((chip) => (
          <CategoryChip
            key={chip.value}
            label={chip.label}
            value={chip.value}
            isSelected={selectedCity === chip.value}
            onClick={() => handleCityClick(chip.value)}
          />
        ))}
      </div>
      
      {/* City Filters */}
      <div className="flex flex-wrap justify-center gap-3">
        {cities.map((city) => (
          <CategoryChip
            key={city.value}
            label={city.label}
            value={city.value}
            isSelected={selectedCity === city.value}
            onClick={() => handleCityClick(city.value)}
          />
        ))}
      </div>
    </div>
  );
};