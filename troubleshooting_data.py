# Enhanced troubleshooting steps with better structure and additional metadata
TROUBLESHOOTING_STEPS = {
    "START": {
        "question": "**HARD DOWN · INITIAL CHECKS**\nSelect the ONT light status:",
        "description": "Check the ONT (modem) lights to determine the connectivity issue source.",
        "category": "connectivity_check",
        "options": {
            "ONT shows **normal lights** (power solid, data solid/blinking)": "ONT_NORMAL",
            "ONT shows **alarm light / red light**": "ONT_ALARM", 
            "ONT has **no power / no lights**": "ONT_NO_PWR"
        },
        "help_text": "Ask customer to describe power, data and alarm LEDs."
    },
    "ONT_NORMAL": {
        "question": "**CHECK ROUTER CONNECTION**\nONT looks good. Now let's check the router/gateway:",
        "description": "The ONT is working properly, check router status next.",
        "category": "router_check",
        "options": {
            "Router lights are **normal / online**": "SPEED_TEST",
            "Router lights show **errors** (blinking red/orange)": "ROUTER_REBOOT"
        },
        "help_text": "Ask customer to check router/gateway LED status."
    },
    "ONT_ALARM": {
        "question": "**ONT ALARM DETECTED**\n• Unplug ONT power 30 s, plug back in\n• Wait 2 min and re-check lights",
        "description": "Power cycle the ONT to clear alarm condition.",
        "category": "troubleshooting",
        "options": {
            "Alarm cleared · ONT now normal": "ONT_NORMAL",
            "Alarm persists": "DISPATCH_CHECK"
        },
        "help_text": "ONT power cycle often resolves temporary alarm conditions."
    },
    "ONT_NO_PWR": {
        "question": "**ONT NO POWER**\n• Verify power brick, outlet, and fibre seated\n• Try different outlet if possible",
        "description": "Check all power connections and fiber connections.",
        "category": "power_check",
        "options": {
            "ONT now powers on": "ONT_NORMAL",
            "Still dead / no lights": "DISPATCH_CHECK"
        },
        "help_text": "Verify power adapter, outlet functionality, and fiber connections."
    },
    "ROUTER_REBOOT": {
        "question": "**ROUTER POWER-CYCLE**\nUnplug router 30 s, plug back in. Wait until LEDs settle.",
        "description": "Power cycle router to resolve connectivity issues.",
        "category": "troubleshooting",
        "options": {
            "Router normal after reboot": "SPEED_TEST",
            "Router still erroring": "DISPATCH_CHECK"
        },
        "help_text": "Router reboot resolves most connectivity issues."
    },
    "SPEED_TEST": {
        "question": "**WIRED SPEED TEST**\nRun Ookla or Eero wired test next to router:",
        "description": "Test actual internet connectivity and speed.",
        "category": "final_test",
        "options": {
            "Link is online & speeds meet package": "RESOLVED",
            "No internet or <10 Mbps": "DISPATCH_CHECK"
        },
        "help_text": "Wired speed test provides most accurate connectivity assessment."
    },
    "DISPATCH_CHECK": {
        "question": "**DISPATCH APPROVAL** – fill or confirm the required items",
        "description": "Streamlined dispatch approval form with auto-populated fields.",
        "category": "dispatch",
        "input_fields": [
            {
                "name": "head_end",
                "label": "Head-End Hub",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "HUB-01", "label": "HUB-01"},
                    {"value": "HUB-02", "label": "HUB-02"},
                    {"value": "HUB-03", "label": "HUB-03"}
                ]
            },
            {
                "name": "alarm_code",
                "label": "ONT Alarm Code",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "LOS", "label": "LOS – Loss of Signal"},
                    {"value": "LOA", "label": "LOA – Loss of Acknowledge"},
                    {"value": "LOF", "label": "LOF – Loss of Frame"},
                    {"value": "LOSi", "label": "LOSi – Loss of Sync"}
                ]
            },
            {
                "name": "alarm_window",
                "label": "Alarm Window (auto)",
                "type": "text",
                "placeholder": "e.g. 12:45–12:58",
                "required": True
            },
            {
                "name": "light_levels",
                "label": "Light Levels OLT→ONT (dBm)",
                "type": "text",
                "placeholder": "-19.4 / 1.2",
                "required": True
            },
            {
                "name": "l2_align",
                "label": "L2 User Aligned?",
                "type": "toggle",
                "required": True
            },
            {
                "name": "equip_rebooted",
                "label": "ONT & Router Rebooted?",
                "type": "toggle",
                "required": True
            },
            {
                "name": "conn_verified",
                "label": "All Cables/Fibre Verified?",
                "type": "toggle",
                "required": True
            },
            {
                "name": "others_affected",
                "label": "Other Customers Affected?",
                "type": "toggle",
                "required": True
            },
            {
                "name": "steps_taken",
                "label": "Brief Notes (optional)",
                "type": "textarea",
                "required": False
            }
        ],
        "options": {
            "Submit & Escalate": "ESCALATE"
        },
        "help_text": "Most fields pre-fill; agent confirms or toggles where needed."
    },
    "RESOLVED": {
        "question": "**✅ Issue resolved at Tier 1.**\nDocument summary and close case.",
        "description": "Case successfully resolved without escalation.",
        "category": "resolution",
        "options": {
            "Finish Case": "END_CASE"
        },
        "help_text": "Document resolution details for customer records."
    },
    "ESCALATE": {
        "question": "**⬆ Escalate / Dispatch Truck**\nSend completed form to Tier 2 / Field Ops.",
        "description": "Case requires field service or Tier 2 intervention.",
        "category": "escalation",
        "options": {
            "Finish Case": "END_CASE"
        },
        "help_text": "Ensure all dispatch information is complete before escalation."
    },
    "END_CASE": {
        "question": "*Case closed. View summary or start new case.*",
        "description": "Case completed successfully.",
        "category": "completion",
        "options": {
            "View Summary": "CASE_SUMMARY",
            "Start New Case": "START"
        },
        "help_text": "Case documentation and summary available for review."
    },
    "ROUTER_CHECK": {
        "question": "**ROUTER IDENTIFICATION**\n\nSelect the customer's router/gateway type and enter the Router ID:",
        "description": "Identify the customer's routing equipment and get the 16-digit router identifier.",
        "category": "equipment_selection",
        "input_fields": [
            {
                "name": "router_type",
                "label": "Router Type",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "Eero", "label": "Eero Router (Insight)"},
                    {"value": "Nokia", "label": "Nokia Router (NWCC)"},
                    {"value": "Customer-Owned", "label": "Customer-Owned Router"}
                ]
            },
            {
                "name": "router_id",
                "label": "Router ID (approximately 16 digits)",
                "type": "text",
                "required": True,
                "placeholder": "Enter Router ID (numbers and letters)"
            }
        ],
        "options": {
            "Continue to Issue Type": "ISSUE_TYPE",
            "Customer-Owned Equipment": "REFER_MFG"
        },
        "help_text": "Router ID can be found on the device label or in the management system."
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
        "question": "**ISSUE IDENTIFICATION**\n\nWhat type of connectivity issue is the customer experiencing?",
        "description": "Select the primary issue category to determine the appropriate troubleshooting approach.",
        "category": "issue_identification",
        "input_fields": [
            {
                "name": "issue_type",
                "label": "Issue Type",
                "type": "select",
                "required": True,
                "options": [
                    {
                        "value": "Complete Outage", 
                        "label": "Complete Outage - No internet connection at all",
                        "description": "Customer has zero internet connectivity, no devices can connect to the internet"
                    },
                    {
                        "value": "Intermittent Issue", 
                        "label": "Intermittent Issue - Connection drops or works on/off",
                        "description": "Internet connection comes and goes, works sometimes but not consistently"
                    },
                    {
                        "value": "Slow Speeds", 
                        "label": "Slow Speeds - Internet works but slower than expected",
                        "description": "Internet connection works but speeds are below expected package speeds"
                    }
                ]
            },
            {
                "name": "issue_description",
                "label": "Detailed Issue Description",
                "type": "textarea",
                "required": True,
                "placeholder": "Describe the specific symptoms and when the issue started..."
            }
        ],
        "options": {
            "Complete Outage - Start Hard Down Analysis": "NO_INTERNET",
            "Intermittent/Slow - Start WiFi Environment Analysis": "CHECK_WIFI_ENV"
        },
        "help_text": "Choose the issue type that best matches the customer's reported problem. This determines the troubleshooting path."
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
        "question": "**HARD-DOWN DATA COLLECTION REQUIRED**\n\nFirst, verify and record the head-end hub name and ONT ID.",
        "description": "Critical data collection required before escalating hard-down issues. Each step must be completed.",
        "category": "data_collection",
        "input_fields": [
            {
                "name": "hub_name",
                "label": "Head-end Hub Name",
                "type": "text",
                "required": True,
                "placeholder": "Enter customer's head-end hub name"
            },
            {
                "name": "ont_id",
                "label": "ONT ID (Nokia ONT ID or Calix ONT ID)",
                "type": "text",
                "required": True,
                "placeholder": "Enter Nokia ONT ID or Calix ONT ID from system"
            }
        ],
        "options": {
            "Continue to Router Information": "HARD_DOWN_ROUTERS"
        },
        "help_text": "Check in Altiplano/SMX system to identify the customer's head-end hub location and ONT identification."
    },
    "HARD_DOWN_ROUTERS": {
        "question": "Document all router/extender devices on the customer's network (up to 3 devices).",
        "description": "Some customers may have multiple routers or extenders. Record all device IDs.",
        "category": "data_collection",
        "input_fields": [
            {
                "name": "router_1_id",
                "label": "Primary Router ID",
                "type": "text",
                "required": True,
                "placeholder": "Enter primary router device ID"
            },
            {
                "name": "router_2_id",
                "label": "Secondary Router/Extender ID (if applicable)",
                "type": "text",
                "placeholder": "Enter secondary device ID if present"
            },
            {
                "name": "router_3_id",
                "label": "Third Router/Extender ID (if applicable)",
                "type": "text",
                "placeholder": "Enter third device ID if present"
            }
        ],
        "options": {
            "Continue to Alarm History": "HARD_DOWN_ALARM"
        },
        "help_text": "Record all router and extender device IDs from the management system."
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
        "question": "**HARD DOWN CONFIRMED - CONTACT DISPATCH**\n\nNext step is to contact dispatch and create a SVC ticket for HARD DOWN.",
        "description": "**SCHEDULING INSTRUCTIONS:**\n• If before 2 PM: Consult with dispatch for earliest appointment\n• If after 2 PM: Schedule for next day or create service queue ticket",
        "category": "dispatch",
        "options": {
            "Generate Dispatch Ticket Information": "DISPATCH_TICKET_INFO"
        },
        "help_text": "Contact dispatch immediately for HARD DOWN issues as these affect customer service completely."
    },
    "DISPATCH_TICKET_INFO": {
        "question": "**DISPATCH TICKET INFORMATION**\n\nCopy and paste the following information for your dispatch ticket:",
        "description": "All required information has been collected and is ready for dispatch ticket creation.",
        "category": "dispatch_final",
        "help_text": "Copy this information exactly as shown for your SVC ticket. Include agent name making the request."
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
        "question": "**STEP 1: SPEED TEST DOCUMENTATION**\n\nFirst, document current speed test results from customer device and Eero analytics.",
        "description": "Document baseline speed test results before troubleshooting.",
        "category": "diagnosis",
        "input_fields": [
            {
                "name": "customer_device_type",
                "label": "Customer Device Used for Speed Test",
                "type": "text",
                "required": True,
                "placeholder": "e.g., iPhone 14, Samsung Galaxy S23, MacBook Air, etc."
            },
            {
                "name": "customer_speed_test_time",
                "label": "Time of Customer Speed Test",
                "type": "datetime-local",
                "required": True
            },
            {
                "name": "customer_download_speed",
                "label": "Customer Device Download Speed (Mbps)",
                "type": "number",
                "step": "0.1",
                "required": True,
                "placeholder": "Enter download speed in Mbps"
            },
            {
                "name": "customer_upload_speed",
                "label": "Customer Device Upload Speed (Mbps)",
                "type": "number",
                "step": "0.1",
                "required": True,
                "placeholder": "Enter upload speed in Mbps"
            },
            {
                "name": "eero_analytics_download",
                "label": "Eero Analytics Download Speed (Mbps)",
                "type": "number",
                "step": "0.1",
                "required": True,
                "placeholder": "Speed shown in Eero Insight analytics"
            },
            {
                "name": "eero_analytics_upload",
                "label": "Eero Analytics Upload Speed (Mbps)",
                "type": "number",
                "step": "0.1",
                "required": True,
                "placeholder": "Speed shown in Eero Insight analytics"
            },
            {
                "name": "eero_analytics_time",
                "label": "Time of Eero Analytics Reading",
                "type": "datetime-local",
                "required": True
            }
        ],
        "options": {
            "Continue to Event Stream Analysis": "CHECK_WIFI_EVENTS"
        },
        "help_text": "Document both customer device speed test and Eero analytics speeds with exact timestamps."
    },
    "CHECK_WIFI_EVENTS": {
        "question": "**STEP 2: EVENT STREAM ANALYSIS**\n\nSelect ALL events found in Eero Insight Event Stream from the past 24 hours.",
        "description": "Check Eero Insight → Event Stream and select every relevant event found.",
        "category": "diagnosis",
        "input_fields": [
            {
                "name": "event_stream_check_time",
                "label": "Event Stream Check Time",
                "type": "datetime-local",
                "required": True
            },
            {
                "name": "selected_events",
                "label": "Events Found in Stream (Select All That Apply)",
                "type": "select_multiple",
                "required": True,
                "options": [
                    {
                        "value": "internet_connectivity_failure",
                        "label": "Internet connectivity failure",
                        "description": "The gateway eero has lost its upstream WAN connection (no internet).",
                        "severity": "Critical",
                        "troubleshooting": "1. In Altiplano/SMX, confirm ONT light levels & alarm codes.\n2. Verify head-end hub provisioning.\n3. Power-cycle ONT → wait 2 min → check.\n4. If still down, roll truck."
                    },
                    {
                        "value": "user_device_removed",
                        "label": "User device removed / IP lost",
                        "description": "A client device has disconnected from the network or lost IP assignment.",
                        "severity": "Warning",
                        "troubleshooting": "1. Have customer forget WiFi network and reconnect.\n2. Test device closer to router.\n3. Check for WiFi interference.\n4. Verify device WiFi settings."
                    },
                    {
                        "value": "channel_switch_detected",
                        "label": "Channel switch detected",
                        "description": "The eero has changed Wi-Fi channel (2.4 GHz or 5 GHz) – usually to avoid interference.",
                        "severity": "Info",
                        "troubleshooting": "1. Check Channel Utilization in Insight.\n2. If >80%, manually assign less-crowded channel.\n3. Retest client performance."
                    },
                    {
                        "value": "dfs_strike_detected",
                        "label": "DFS strike detected",
                        "description": "Radar interference forced channel change.",
                        "severity": "Warning",
                        "troubleshooting": "1. Allow 1-2 min for automatic channel re-selection.\n2. If repeats, relocate eero away from radar source.\n3. Consider disabling DFS channels."
                    },
                    {
                        "value": "gateway_to_leaf_link_signal_changed",
                        "label": "Gateway-to-leaf signal issues",
                        "description": "Backhaul signal strength issues between gateway and extender.",
                        "severity": "Warning",
                        "troubleshooting": "1. Check RSSI in Topology view.\n2. Ensure 30-60 ft range with minimal obstructions.\n3. Reposition if signal < -65 dBm."
                    },
                    {
                        "value": "ethernet_port_issues",
                        "label": "Ethernet port carrier/speed issues",
                        "description": "Wired connection problems on eero ports.",
                        "severity": "Warning",
                        "troubleshooting": "1. Check physical cable connections.\n2. Swap to different port/cable.\n3. Test with known-good device."
                    },
                    {
                        "value": "user_device_roaming",
                        "label": "Frequent device roaming",
                        "description": "Device switching between eero nodes frequently.",
                        "severity": "Info",
                        "troubleshooting": "1. Check signal strength at device location.\n2. Optimize eero placement.\n3. Consider band steering settings."
                    },
                    {
                        "value": "no_events_found",
                        "label": "No relevant events found",
                        "description": "Event stream shows no issues in past 24 hours.",
                        "severity": "Info",
                        "troubleshooting": "1. Check channel utilization below.\n2. Test thermal analysis.\n3. Proceed with speed optimization."
                    }
                ]
            },
            {
                "name": "channel_utilization_2_4",
                "label": "2.4 GHz Channel Utilization (%)",
                "type": "number",
                "min": "0",
                "max": "100",
                "required": True,
                "placeholder": "Enter percentage from Insight"
            },
            {
                "name": "channel_utilization_5",
                "label": "5 GHz Channel Utilization (%)",
                "type": "number",
                "min": "0",
                "max": "100",
                "required": True,
                "placeholder": "Enter percentage from Insight"
            }
        ],
        "options": {
            "Continue to Troubleshooting Actions": "EXECUTE_TROUBLESHOOTING"
        },
        "help_text": "Go to Eero Insight → Event Stream. Select ALL events you see. Check Network tab for channel utilization."
    },
    "EXECUTE_TROUBLESHOOTING": {
        "question": "**STEP 3: EXECUTE TROUBLESHOOTING**\n\nBased on selected events, follow the troubleshooting steps for each event. Complete ALL steps before proceeding.",
        "description": "Execute troubleshooting steps for each selected event and document results.",
        "category": "execution",
        "input_fields": [
            {
                "name": "troubleshooting_attempts",
                "label": "Troubleshooting Steps Completed (Document Each Attempt)",
                "type": "textarea",
                "required": True,
                "placeholder": "Document each troubleshooting step attempted:\n\nExample:\n1. User device removed event - Had customer forget network and reconnect - RESULT: Still having issues\n2. Channel utilization 85% on 2.4GHz - Manually set to channel 6 - RESULT: Improved but still slow\n3. Device tested closer to router - RESULT: Speeds improved from 15Mbps to 45Mbps\n\nDocument EVERY step attempted and the outcome."
            },
            {
                "name": "post_troubleshooting_speed_test",
                "label": "Speed Test After Troubleshooting",
                "type": "text",
                "required": True,
                "placeholder": "Download/Upload speeds after troubleshooting (e.g., 45Mbps/12Mbps)"
            },
            {
                "name": "issue_resolved",
                "label": "Issue Status After Troubleshooting",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "resolved", "label": "Issue Resolved - Customer Satisfied"},
                    {"value": "improved", "label": "Improved But Still Below Expected"},
                    {"value": "no_change", "label": "No Improvement - Same Issues"},
                    {"value": "worse", "label": "Issue Got Worse"}
                ]
            }
        ],
        "options": {
            "Issue Resolved": "RESOLVED_DOC",
            "Need Further Troubleshooting": "REBOOT_BOTH"
        },
        "help_text": "Follow each troubleshooting step shown when you selected events. Document EVERY attempt and result."
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
