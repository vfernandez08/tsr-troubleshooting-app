# Enhanced troubleshooting steps with better structure and additional metadata
TROUBLESHOOTING_STEPS = {
    "START": {
        "question": "Select the customer's ONT (Optical Network Terminal) type from Broadhub:",
        "description": "Check the customer's equipment configuration in Broadhub to identify their ONT model.",
        "options": {
            "Nokia ONT (Altiplano)": "ROUTER_CHECK",
            "Calix ONT (SMX)": "ROUTER_CHECK"
        },
        "help_text": "The ONT type determines which management system to use for diagnostics.",
        "category": "equipment_selection"
    },
    "ROUTER_CHECK": {
        "question": "Select the customer's router/gateway type:",
        "description": "Identify the customer's routing equipment to determine support capabilities.",
        "options": {
            "Eero Router (Insight)": "ISSUE_TYPE",
            "Nokia Router (NWCC)": "ISSUE_TYPE",
            "Customer-Owned Router": "REFER_MFG"
        },
        "help_text": "Company-provided equipment has full support, while customer-owned equipment has limited support.",
        "category": "equipment_selection"
    },
    "REFER_MFG": {
        "question": "Customer is using their own equipment. Advise them to contact their equipment manufacturer's support. Do they agree to proceed?",
        "description": "For customer-owned equipment, we can only provide limited support and must refer to manufacturer.",
        "options": {
            "Yes - Customer will contact manufacturer": "END_MFG",
            "No - Customer wants our support": "END_UNRESOLVED"
        },
        "help_text": "We cannot troubleshoot third-party equipment but can verify our service delivery.",
        "category": "escalation"
    },
    "ISSUE_TYPE": {
        "question": "What type of connectivity issue is the customer experiencing?",
        "description": "Categorize the problem to determine the appropriate troubleshooting path.",
        "options": {
            "Complete outage - No Internet connectivity": "NO_INTERNET",
            "Intermittent issues or slow speeds": "INTERMITTENT"
        },
        "help_text": "Complete outages require immediate diagnosis, while performance issues need detailed analysis.",
        "category": "issue_classification"
    },
    "NO_INTERNET": {
        "question": "Check ONT status in Altiplano/SMX: verify lights, check for alarms, confirm MAC/IP are learned. Is the ONT showing as down or in alarm state?",
        "description": "Perform comprehensive ONT diagnostics to identify network-level issues.",
        "options": {
            "Yes - ONT is down or showing alarms": "HARD_DOWN_INFO",
            "No - ONT appears normal": "ONT_RETEST"
        },
        "help_text": "ONT alarms typically indicate physical layer issues requiring field service.",
        "category": "diagnosis"
    },
    "HARD_DOWN_INFO": {
        "question": "**HARD-DOWN DATA COLLECTION REQUIRED**\n\nFirst, verify and record the head-end hub name.",
        "description": "Critical data collection required before escalating hard-down issues. Each step must be completed.",
        "category": "data_collection",
        "input_fields": [
            {
                "name": "hub_name",
                "label": "Head-end Hub Name",
                "type": "text",
                "required": True,
                "placeholder": "Enter customer's head-end hub name"
            }
        ],
        "options": {
            "Continue to Alarm History": "HARD_DOWN_ALARM"
        },
        "help_text": "Check in Altiplano/SMX system to identify the customer's head-end hub location."
    },
    "HARD_DOWN_ALARM": {
        "question": "Pull and document the alarm history for the exact timeframe of the outage.",
        "description": "Document specific alarm timestamps and details.",
        "category": "data_collection",
        "input_fields": [
            {
                "name": "alarm_start_time",
                "label": "Alarm Start Time",
                "type": "datetime-local",
                "required": True
            },
            {
                "name": "alarm_details",
                "label": "Alarm Details",
                "type": "textarea",
                "required": True,
                "placeholder": "Document ONT loss of PHY layer alarms, timestamps, and details"
            }
        ],
        "options": {
            "Continue to Light Levels": "HARD_DOWN_LIGHT_LEVELS"
        },
        "help_text": "Look for ONT down alarms, loss of signal, or PHY layer disconnections."
    },
    "HARD_DOWN_LIGHT_LEVELS": {
        "question": "Check and record the light levels at both OLT and ONT.",
        "description": "Light levels are critical for diagnosing fiber issues.",
        "category": "data_collection",
        "input_fields": [
            {
                "name": "olt_light_level",
                "label": "OLT Light Level (dBm)",
                "type": "number",
                "step": "0.1",
                "placeholder": "e.g. -15.2"
            },
            {
                "name": "ont_light_level", 
                "label": "ONT Light Level (dBm)",
                "type": "number",
                "step": "0.1",
                "placeholder": "e.g. -22.1"
            }
        ],
        "options": {
            "Continue to PON Status": "HARD_DOWN_PON_CHECK"
        },
        "help_text": "Normal levels are typically -3 to -27 dBm. Record exact values."
    },
    "HARD_DOWN_PON_CHECK": {
        "question": "Check PON status in Altiplano/SMX and document customer impact scope.",
        "description": "Determine if this is an isolated issue or affecting multiple customers.",
        "category": "data_collection",
        "input_fields": [
            {
                "name": "total_onts",
                "label": "Total ONTs on PON",
                "type": "number",
                "required": True,
                "min": "1"
            },
            {
                "name": "alarmed_onts",
                "label": "ONTs Currently in Alarm",
                "type": "number",
                "required": True,
                "min": "0"
            }
        ],
        "options": {
            "Complete Data Collection": "HARD_DOWN_COMPLETE"
        },
        "help_text": "Record total ONT count and alarm count to determine scope of issue."
    },
    "HARD_DOWN_COMPLETE": {
        "instruction": "**HARD-DOWN DATA COLLECTION COMPLETE**\n\nEnsure your ticket includes:\n✓ Head-end hub name\n✓ Alarm history with timestamps\n✓ Light levels (OLT/ONT dBm readings)\n✓ PON status (total ONTs vs. alarmed ONTs)\n✓ Customer report: No-Internet alarm – ONT loss of PHY layer\n✓ Speed-test results: N/A (hard down)\n✓ Equipment rebooted: YES\n✓ All physical connections verified: YES\n✓ Troubleshooting steps: rebooted ONT + router, reseated fiber/ethernet\n\nAll required data has been collected. Proceed to dispatch field technician.",
        "description": "All hard-down data requirements completed.",
        "category": "data_collection",
        "options": {
            "Proceed to Truck Roll": "ROLL_TRUCK"
        }
    },
    "ONT_RETEST": {
        "instruction": "Power cycle the ONT (unplug for 30 seconds, reconnect). Test connectivity after reboot. If service is restored, document the resolution and close the case.",
        "description": "Simple power cycle can resolve temporary software glitches in the ONT.",
        "category": "resolution",
        "estimated_time": "5 minutes"
    },
    "ROLL_TRUCK": {
        "instruction": "Roll a truck: ONT alarm persists and power cycle failed. Include hard-down data in ticket.",
        "description": "Physical issues require field service for resolution.",
        "category": "escalation",
        "next_action": "Create field service ticket"
    },
    "INTERMITTENT": {
        "question": "Is the issue affecting a single device or multiple devices? Is it occurring on WiFi, wired connection, or both?",
        "description": "Isolate whether the issue is device-specific or network-wide.",
        "options": {
            "Single device on WiFi": "DEVICE_WIFI",
            "Single device on wired connection": "DEVICE_WIRED", 
            "Multiple devices affected": "CHECK_CONNECTIONS"
        },
        "help_text": "Single device issues are usually device-specific, while multiple device issues indicate network problems.",
        "category": "diagnosis"
    },
    "DEVICE_WIFI": {
        "instruction": "Have customer: 1) Forget network and reconnect, 2) Ensure device is on 5 GHz or 6 GHz (not 2.4 GHz), 3) Disable Private Wi-Fi Address temporarily if iOS/Android, 4) Update OS / network drivers. If still slow, proceed to speed test.",
        "description": "WiFi profile corruption can cause connectivity issues on individual devices.",
        "category": "resolution",
        "estimated_time": "5 minutes"
    },
    "DEVICE_WIRED": {
        "instruction": "Swap cable/port. Check learned MAC/IP on ONT. If missing, escalate to Tier 2.",
        "description": "Physical connectivity issues are common with wired connections.",
        "category": "resolution",
        "estimated_time": "5 minutes"
    },
    "CHECK_CONNECTIONS": {
        "question": "Verify ONT MAC/IP status and check router health in Eero Insight or NWCC. Are there any issues identified?",
        "description": "Perform comprehensive network diagnostics for multi-device issues.",
        "options": {
            "ONT MAC/IP missing or not learned": "ESCALATE_T2",
            "Router showing errors or offline": "REBOOT_BOTH",
            "No obvious issues found": "SPEED_TEST"
        },
        "help_text": "Missing MAC/IP typically indicates provisioning issues requiring escalation.",
        "category": "diagnosis"
    },
    "ESCALATE_T2": {
        "instruction": "Escalate to Tier 2 Support: ONT not properly learning MAC address or IP configuration, indicating potential provisioning or network configuration issue.",
        "description": "Backend network issues require advanced technical support.",
        "category": "escalation",
        "next_action": "Create Tier 2 escalation ticket"
    },
    "REBOOT_BOTH": {
        "question": "Power-cycle ONT and router. Test speeds next to router. Speeds now within expected range?",
        "description": "Synchronized reboot can resolve communication issues between devices.",
        "options": {
            "Yes - Speeds are now acceptable": "RESOLVED_DOC",
            "No - Still experiencing speed issues": "CHECK_WIFI_ENV"
        },
        "category": "resolution",
        "estimated_time": "10 minutes"
    },
    "SPEED_TEST": {
        "question": "Run speed test (Eero or Ookla) next to router. Are results near plan speed?",
        "description": "Baseline performance testing to identify speed-related issues.",
        "options": {
            "Yes - Speeds are acceptable": "RESOLVED_DOC", 
            "No - Speeds are below expected": "CHECK_WIFI_ENV"
        },
        "category": "diagnosis",
        "estimated_time": "10 minutes"
    },
    "CHECK_WIFI_ENV": {
        "instruction": "**Eero Insight checks:**\n1. Device → Activity → look for frequent disconnects\n2. Network → 2.4/5 GHz → Channel Utilization >80%? Note value\n3. Hardware → Thermal Analysis → any overheating alerts?\n\nIf high utilization or thermal warning, reposition router or move device to less-crowded band, then retest.",
        "description": "Environmental and interference analysis for WiFi performance issues.",
        "category": "diagnosis",
        "options": {
            "After Adjustments Retest Speeds": "REBOOT_BOTH"
        }
    },
    "RESOLVED_DOC": {
        "instruction": "Issue resolved. Document final speeds and steps taken.",
        "description": "Case successfully resolved with documented solution.",
        "category": "resolution"
    },
    "END_MFG": {
        "instruction": "Case closed: Customer agreed to contact equipment manufacturer support for their customer-owned device. Verified our service delivery is functioning properly.",
        "description": "Customer will seek support from equipment vendor.",
        "category": "resolution"
    },
    "END_UNRESOLVED": {
        "instruction": "Case closed as unresolved: Customer declined to use supported equipment configuration. Cannot verify service delivery with unsupported hardware setup.",
        "description": "Customer chose to keep unsupported configuration.",
        "category": "resolution"
    }
}

# Equipment information with visual representations
EQUIPMENT_INFO = {
    "ont_types": {
        "Nokia ONT (Altiplano)": {
            "description": "Nokia Optical Network Terminal managed through Altiplano system",
            "management_system": "Altiplano",
            "icon": "ont-nokia.svg",
            "typical_lights": ["Power", "PON", "LAN", "WiFi"]
        },
        "Calix ONT (SMX)": {
            "description": "Calix Optical Network Terminal managed through SMX system", 
            "management_system": "SMX",
            "icon": "ont-calix.svg",
            "typical_lights": ["Power", "Optical", "Ethernet", "Status"]
        }
    },
    "router_types": {
        "Eero Router (Insight)": {
            "description": "Eero mesh router system managed through Insight platform",
            "management_system": "Eero Insight",
            "icon": "router-eero.svg",
            "support_level": "Full Support"
        },
        "Nokia Router (NWCC)": {
            "description": "Nokia gateway router managed through NWCC system",
            "management_system": "NWCC", 
            "icon": "router-nokia.svg",
            "support_level": "Full Support"
        },
        "Customer-Owned Router": {
            "description": "Third-party router equipment owned by customer",
            "management_system": "Not managed",
            "icon": "router-custom.svg",
            "support_level": "Limited Support"
        }
    }
}

# Quick reference guides
QUICK_REFERENCE = {
    "power_cycle_ont": {
        "title": "ONT Power Cycle Procedure",
        "steps": [
            "Unplug power cable from ONT",
            "Wait 30 seconds", 
            "Reconnect power cable",
            "Wait 2-3 minutes for full boot",
            "Check status lights"
        ]
    },
    "power_cycle_router": {
        "title": "Router Power Cycle Procedure", 
        "steps": [
            "Unplug power cable from router",
            "Wait 30 seconds",
            "Reconnect power cable", 
            "Wait 2-3 minutes for full boot",
            "Test connectivity"
        ]
    },
    "wifi_reconnect": {
        "title": "WiFi Reconnection Process",
        "steps": [
            "Go to device WiFi settings",
            "Find network name and select 'Forget'",
            "Wait 10 seconds",
            "Search for network again",
            "Enter network password",
            "Test connectivity"
        ]
    }
}
