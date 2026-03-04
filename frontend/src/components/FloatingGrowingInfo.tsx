import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

interface GrowingInfo {
  native_region?: string[];
  climate_zones?: string[];
  hardiness_zones?: string;
  light_requirement?: string;
  water_needs?: string;
  soil_preference?: string;
  ph_range?: string;
  growing_season?: string[];
  mature_height?: string;
  mature_spread?: string;
  growth_rate?: string;
}

interface FloatingGrowingInfoProps {
  isOpen: boolean;
  onClose: () => void;
  growingInfo: GrowingInfo;
  flowerName: string;
}

export default function FloatingGrowingInfo({
  isOpen,
  onClose,
  growingInfo,
  flowerName
}: FloatingGrowingInfoProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-40"
          />

          {/* Floating Panel */}
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.95 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="fixed bottom-0 left-0 right-0 md:bottom-8 md:left-1/2 md:-translate-x-1/2 md:max-w-2xl bg-white rounded-t-2xl md:rounded-2xl shadow-2xl z-50 max-h-[80vh] overflow-y-auto"
          >
            {/* Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between rounded-t-2xl">
              <div>
                <h3 className="text-lg font-bold text-[#2D5016]">
                  Growing Information
                </h3>
                <p className="text-sm text-gray-600">{flowerName}</p>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              >
                <X className="w-5 h-5 text-gray-600" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              {/* Native Region */}
              {growingInfo.native_region && growingInfo.native_region.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 }}
                  className="space-y-2"
                >
                  <h4 className="font-semibold text-gray-800 flex items-center gap-2">
                    <span className="text-xl">📍</span>
                    Native Region
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {growingInfo.native_region.map((region, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-[#E8B4B8] text-[#2D5016] rounded-full text-sm"
                      >
                        {region}
                      </span>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Climate & Hardiness */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
                className="space-y-3"
              >
                <h4 className="font-semibold text-gray-800 flex items-center gap-2">
                  <span className="text-xl">🌍</span>
                  Where It Grows
                </h4>
                <div className="ml-7 space-y-2 text-gray-700">
                  {growingInfo.climate_zones && growingInfo.climate_zones.length > 0 && (
                    <p className="flex items-start gap-2">
                      <span className="font-medium min-w-[100px]">Climate:</span>
                      <span>{growingInfo.climate_zones.join(', ')}</span>
                    </p>
                  )}
                  {growingInfo.hardiness_zones && (
                    <p className="flex items-start gap-2">
                      <span className="font-medium min-w-[100px]">Hardiness:</span>
                      <span>USDA Zones {growingInfo.hardiness_zones}</span>
                    </p>
                  )}
                </div>
              </motion.div>

              {/* Growing Conditions */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
                className="space-y-3"
              >
                <h4 className="font-semibold text-gray-800 flex items-center gap-2">
                  <span className="text-xl">🌱</span>
                  Growing Conditions
                </h4>
                <div className="ml-7 space-y-2 text-gray-700">
                  {growingInfo.light_requirement && (
                    <p className="flex items-start gap-2">
                      <span className="font-medium min-w-[100px]">Light:</span>
                      <span>{growingInfo.light_requirement}</span>
                    </p>
                  )}
                  {growingInfo.water_needs && (
                    <p className="flex items-start gap-2">
                      <span className="font-medium min-w-[100px]">Water:</span>
                      <span>{growingInfo.water_needs}</span>
                    </p>
                  )}
                  {growingInfo.soil_preference && (
                    <p className="flex items-start gap-2">
                      <span className="font-medium min-w-[100px]">Soil:</span>
                      <span>{growingInfo.soil_preference}</span>
                    </p>
                  )}
                  {growingInfo.ph_range && (
                    <p className="flex items-start gap-2">
                      <span className="font-medium min-w-[100px]">pH:</span>
                      <span>{growingInfo.ph_range}</span>
                    </p>
                  )}
                </div>
              </motion.div>

              {/* Growth Information */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 }}
                className="space-y-3"
              >
                <h4 className="font-semibold text-gray-800 flex items-center gap-2">
                  <span className="text-xl">📏</span>
                  Size & Growth
                </h4>
                <div className="ml-7 space-y-2 text-gray-700">
                  {growingInfo.mature_height && (
                    <p className="flex items-start gap-2">
                      <span className="font-medium min-w-[100px]">Height:</span>
                      <span>{growingInfo.mature_height}</span>
                    </p>
                  )}
                  {growingInfo.mature_spread && (
                    <p className="flex items-start gap-2">
                      <span className="font-medium min-w-[100px]">Spread:</span>
                      <span>{growingInfo.mature_spread}</span>
                    </p>
                  )}
                  {growingInfo.growth_rate && (
                    <p className="flex items-start gap-2">
                      <span className="font-medium min-w-[100px]">Growth:</span>
                      <span>{growingInfo.growth_rate}</span>
                    </p>
                  )}
                </div>
              </motion.div>

              {/* Bloom Season */}
              {growingInfo.growing_season && growingInfo.growing_season.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 }}
                  className="space-y-2"
                >
                  <h4 className="font-semibold text-gray-800 flex items-center gap-2">
                    <span className="text-xl">🌸</span>
                    Growing Season
                  </h4>
                  <div className="ml-7">
                    <p className="text-gray-700">
                      {growingInfo.growing_season.join(', ')}
                    </p>
                  </div>
                </motion.div>
              )}
            </div>

            {/* Footer */}
            <div className="sticky bottom-0 bg-gray-50 px-6 py-4 border-t border-gray-200 rounded-b-2xl">
              <button
                onClick={onClose}
                className="w-full bg-[#2D5016] text-white py-3 rounded-lg font-semibold hover:bg-[#1f3a0f] transition-colors"
              >
                Close
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}