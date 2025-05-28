
// recommendations.js – rule‑based suggestion engine for your Tier‑1 eero tool
// Replace the AI assistant with this richer rule set.
// -----------------------------------------------------------------------------

const rules = [
  // ───────────────────────── Wi‑Fi signal / RSSI ────────────────────────────
  {
    when: { connectionType: 'wifi', rssi: 'low' },
    solutions: [
      'Have the customer move the device closer to the nearest eero.',
      'Relocate an eero or add another node midway to boost mesh coverage.',
      'Remove metal/mirrored obstacles that can attenuate 5–6 GHz signal.'
    ]
  },

  // ───────────────────── Gateway link negotiating at 100 Mbps ───────────────
  {
    when: { ethernetLink: '100' },
    solutions: [
      'Swap the Ethernet patch cord between ONT and gateway (should click firmly).',
      'Verify the upstream port or media converter actually supports ≥1 Gbps.',
      'Inspect the cable run for water ingress, kinks, or bent pins.'
    ]
  },

  // ───────────────────── Repeated gateway‑offline events ────────────────────
  {
    when: { event: 'gatewayOffline' },
    solutions: [
      'Power‑cycle the gateway eero and ONT in proper order (ONT first).',
      'Check the power outlet / UPS; brown‑outs can cause random reboots.',
      'Try a different eero power adapter to rule out PSU faults.'
    ]
  },

  // ───────────────────── DFS radar hits forcing channel switch ──────────────
  {
    when: { dfsHits: true },
    solutions: [
      'Disable DFS channels temporarily in Settings ▶ eero Labs ▶ DFS.',
      'Re‑site the eero away from radar sources (weather radar, airports).',
      'Use channels 36–48 to avoid DFS if near military radars.'
    ]
  },

  // ───────────────────── Network name (SSID) recently changed ───────────────
  {
    when: { ssidChanged: true },
    solutions: [
      'Ask customer to "forget" the old SSID on all devices and reconnect.',
      'Update hard‑coded IoT devices (printers, cameras) with the new SSID.',
      'Reboot devices that tend to cache old SSIDs (e.g., Chromecast/FireTV).' 
    ]
  },

  // ───────────────────── New eero node just installed ───────────────────────
  {
    when: { newEero: true },
    solutions: [
      'Wait 5 min for the new node to finish firmware update before testing.',
      'Make sure the new node is >10 ft from the gateway to avoid RF echo.',
      'If wired back‑haul is unavailable, ensure clear line‑of‑sight to another node.'
    ]
  },

  // ───────────────────── Device limited to 2.4 GHz only ─────────────────────
  {
    when: { deviceBandCap: '2.4_only' },
    solutions: [
      'Enable "Legacy Mode" in the eero app to broadcast a 2.4 GHz‑only SSID.',
      'Reduce channel width from 40 MHz to 20 MHz to minimize interference.',
      'Advise customer that max throughput will cap around 50–70 Mbps on 2.4 GHz.'
    ]
  },

  // ───────────────────── Slow speed on 5 GHz band ───────────────────────────
  {
    when: { band: '5', speedBucket: 'sub100' },
    solutions: [
      'Check for DFS hits; force channel 44/80 MHz where possible.',
      'Verify client NIC supports 802.11ac 80 MHz; update drivers/firmware.',
      'Relocate microwave ovens or cordless phones that sit on 5 GHz channels.'
    ]
  },

  // ───────────────────── Under‑performing Wi‑Fi 6E (6 GHz) ───────────────────
  {
    when: { band: '6', speedBucket: 'sub300' },
    solutions: [
      'Confirm client device actually supports Wi‑Fi 6E and WPA3‑SAE.',
      'Update client OS and Wi‑Fi drivers; early 6E stacks had throughput bugs.',
      'Reduce distance; 6 GHz attenuates faster than 5 GHz—stay within one room.'
    ]
  },

  // ───────────────────── Device flapping (disconnect/reconnect) ──────────────
  {
    when: { event: 'deviceFlapping' },
    solutions: [
      'Turn off "Band Steering" for that device to lock it to a single band.',
      'Assign a static IP or DHCP reservation to rule out lease conflicts.',
      'Update device firmware; older IoT sensors often drop when roaming.'
    ]
  },

  // ───────────────────── Speed issues on 2.4 GHz ───────────────────────────
  {
    when: { band: '2.4', speedBucket: 'sub50' },
    solutions: [
      'Switch device to 5 GHz band if supported for better speeds.',
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
  if (step4Data.eero_only_wifi === 'yes') {
    selections.connectionType = 'wifi';
  }
  
  if (step4Data.new_router === 'yes_24h') {
    selections.newEero = true;
  }
  
  if (step4Data.ssid_same_as_old === 'no') {
    selections.ssidChanged = true;
  }

  // Parse Step 5 (Event Stream Analysis) data  
  if (step5Data.selected_events) {
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
  if (step5Data.device_band === '2.4') {
    selections.band = '2.4';
    selections.deviceBandCap = '2.4_only';
  } else if (step5Data.device_band === '5') {
    selections.band = '5';
  } else if (step5Data.device_band === '6') {
    selections.band = '6';
  }

  // Determine speed bucket
  const downloadSpeed = parseInt(step5Data.download_speed || 0);
  if (downloadSpeed < 50) {
    selections.speedBucket = 'sub50';
  } else if (downloadSpeed < 100) {
    selections.speedBucket = 'sub100';
  } else if (downloadSpeed < 300) {
    selections.speedBucket = 'sub300';
  } else {
    selections.speedBucket = 'good';
  }

  // Check Ethernet link speed
  if (step5Data.ethernet_speed === '100') {
    selections.ethernetLink = '100';
  }

  // Signal strength
  if (step5Data.signal_strength === 'poor' || step5Data.signal_strength === 'weak') {
    selections.rssi = 'low';
  } else {
    selections.rssi = 'good';
  }

  return getRecommendations(selections);
}

// Make functions available globally
window.RecommendationEngine = {
  getRecommendations,
  generateRecommendationsFromSteps
};
