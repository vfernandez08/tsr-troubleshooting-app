// recommendations.js – rule‑based suggestion engine for your Tier‑1 eero tool
// Replace the AI assistant with this richer rule set.
// -----------------------------------------------------------------------------

const rules = [
  // ───────────────────── New eero setup issues ─────────────────────────────
  {
    when: { newEero: true, speedBucket: 'sub100' },
    solutions: [
      'Allow 10-15 minutes for eero optimization to complete.',
      'Verify eero gateway is properly connected to ONT via Ethernet.',
      'Check eero app for any setup warnings or firmware updates.'
    ]
  },

  // ───────────────────── SSID change issues ────────────────────────────────
  {
    when: { ssidChanged: true },
    solutions: [
      'Have customer forget the old WiFi network on their device.',
      'Reconnect to the new network name with updated password.',
      'Clear device WiFi cache if connection issues persist.'
    ]
  },

  // ───────────────────── Device flapping issues ────────────────────────────
  {
    when: { event: 'deviceFlapping' },
    solutions: [
      'Check device power saving settings that may disconnect WiFi.',
      'Test device closer to eero to rule out weak signal.',
      'Temporarily disable band steering to isolate 2.4/5 GHz issues.'
    ]
  },

  // ───────────────────── DFS radar interference ────────────────────────────
  {
    when: { dfsHits: true },
    solutions: [
      'Allow 1-2 minutes for automatic channel re-selection.',
      'Relocate eero away from potential radar sources (airports, weather stations).',
      'Consider disabling DFS channels in eero app if interference persists.'
    ]
  },

  // ───────────────────── Poor signal strength ──────────────────────────────
  {
    when: { rssi: 'low', speedBucket: 'sub100' },
    solutions: [
      'Move device closer to eero gateway for testing.',
      'Add eero extender if coverage area is too large.',
      'Check for physical obstructions blocking WiFi signal.'
    ]
  },

  // ───────────────────── 2.4 GHz only devices ──────────────────────────────
  {
    when: { deviceBandCap: '2.4_only', speedBucket: 'sub50' },
    solutions: [
      'Enable Legacy Mode for older 2.4 GHz-only devices.',
      'Check for microwave ovens, baby monitors causing interference.',
      'Enable Legacy Mode for 2.4 GHz-only devices if needed.'
    ]
  },

  // ───────────────────── General slow speeds ───────────────────────────────
  {
    when: { speedBucket: 'sub100' },
    solutions: [
      'Power cycle both ONT and eero gateway.',
      'Test wired connection directly to confirm upstream speeds.',
      'Check for background downloads or streaming on other devices.'
    ]
  }
];

// -----------------------------------------------------------------------------
// De‑duplicate fixes across multiple matched rules and return them.
function getRecommendations(selections) {
  const matchedSolutions = rules
    .filter(rule => Object.entries(rule.when).every(([k, v]) => selections[k] === v))
    .flatMap(rule => rule.solutions);

  return [...new Set(matchedSolutions)];
}

// -----------------------------------------------------------------------------
// Generate recommendations based on Step 4 and Step 5 data
function generateRecommendationsFromSteps(step4Data, step5Data) {
  const selections = {};

  // Parse Step 4 (Wi-Fi Environment Check) data
  if (step4Data && step4Data.eero_only_wifi === 'yes') {
    selections.connectionType = 'wifi';
  }

  if (step4Data && step4Data.new_router === 'yes_24h') {
    selections.newEero = true;
  }

  if (step4Data && step4Data.ssid_same_as_old === 'no') {
    selections.ssidChanged = true;
  }

  // Parse Step 5 (Event Stream Analysis) data  
  if (step5Data && step5Data.selected_events) {
    const events = step5Data.selected_events;
    if (events.includes('gateway_offline')) {
      selections.event = 'gatewayOffline';
    }
    if (events.includes('user_device_removed') || events.includes('user_device_connected')) {
      selections.event = 'deviceFlapping';
    }
    if (events.includes('dfs_strike_detected')) {
      selections.dfsHits = true;
    }
  }

  // Parse speed and band information
  if (step5Data && step5Data.device_band_capability) {
    selections.deviceBandCap = step5Data.device_band_capability;
  }

  // Parse speed bucket from speed test data
  if (step5Data && step5Data.speed_before) {
    const speed = parseInt(step5Data.speed_before);
    if (speed < 50) {
      selections.speedBucket = 'sub50';
    } else if (speed < 100) {
      selections.speedBucket = 'sub100';
    } else if (speed < 300) {
      selections.speedBucket = 'sub300';
    } else {
      selections.speedBucket = 'good';
    }
  }

  // Signal strength
  if (step5Data && (step5Data.signal_strength === 'poor' || step5Data.signal_strength === 'weak')) {
    selections.rssi = 'low';
  } else if (step4Data && step4Data.eero_only_wifi === 'yes') {
    selections.rssi = 'good';
  }

  return getRecommendations(selections);
}

// Make functions available globally
window.RecommendationEngine = {
  getRecommendations,
  generateRecommendationsFromSteps
};