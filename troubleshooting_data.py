# Enhanced troubleshooting steps with better structure and additional metadata
TROUBLESHOOTING_STEPS = {
    "START": {
        "question": "**Step 1 · Verify ONT Power & LEDs**\n\n*Identify whether the issue is power, fiber, or router related.*",
        "description": "**Agent Talk Track:** \"Let's start with your fiber modem. Look at the Nokia ONT and tell me what each light is doing: **Power**, **PON/Alarm** (red or green), and **Data/Internet**. Are they solid, blinking, or off?\"",
        "category": "connectivity_check",
        "input_fields": [
            {
                "name": "ont_light_status",
                "label": "Document ONT Light Status",
                "type": "textarea",
                "required": True,
                "placeholder": "Example:\nPower: Solid green\nPON/Alarm: Blinking red\nData/Internet: Off\n\nDocument exactly what customer reports for each light...",
                "help_text": "Record the exact color and behavior of each LED for troubleshooting documentation"
            }
        ],
        "options": {
            "No lights (completely dark)": "ONT_NO_LIGHTS",
            "Red ALARM light": "ONT_RED_ALARM", 
            "Lights normal (Power solid green, data blinking green)": "ONT_LIGHTS_NORMAL",
            "Lights abnormal (blinking patterns, inconsistent lights)": "ONT_LIGHTS_ABNORMAL"
        },
        "help_text": "**Tip:** Have the customer read the exact color and behavior of every light (e.g., \"Power solid green, Alarm blinking red, Data off\"). Capture these details in the notes box."
    },
    "ONT_NO_LIGHTS": {
        "question": "**Step 2 · ONT Shows No Power**",
        "description": "Ask the customer to try a different outlet or power strip. If the ONT stays dark, the hardware is likely failed.",
        "category": "power_troubleshooting",
        "options": {
            "Tried different outlet/power strip - ONT still dark": "DISPATCH_ONT_DEFECTIVE",
            "Found loose connection or bad outlet - ONT now has lights": "ONT_LIGHTS_NORMAL"
        },
        "help_text": "**Tip:** No LEDs at all almost always means a bad power brick or dead ONT. Prepare a dispatch ticket if swapping outlets fails."
    },
    "ONT_RED_ALARM": {
        "question": "**Step 2 · Red LOS / Alarm Detected**",
        "description": "Run AltiPlano › IBN Provisioning › Troubleshooting. If Rx levels are blank, open Alarm Analyzer and confirm 'Loss of Signal'. Then guide the customer to reboot the ONT.",
        "category": "alarm_troubleshooting",
        "input_fields": [
            {
                "name": "alarm_type",
                "label": "Alarm Type (from Alarm Analyzer)",
                "type": "text",
                "required": True,
                "placeholder": "Enter specific alarm type (e.g., 'ONU Loss of PHY Layer', 'Loss of Signal')"
            },
            {
                "name": "rx_levels",
                "label": "Altiplano Rx Signal Levels",
                "type": "text",
                "required": True,
                "placeholder": "Check Altiplano → IBN Provisioning → Troubleshooting for Rx levels"
            },
            {
                "name": "others_on_pon_down",
                "label": "Are other customers on this PON also down?",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "yes", "label": "Yes - Multiple customers affected"},
                    {"value": "no", "label": "No - Only this customer affected"}
                ]
            },
            {
                "name": "total_on_pon",
                "label": "How many customers total on this PON?",
                "type": "text",
                "required": True,
                "placeholder": "Enter total number of customers on PON (check AltiPlano)"
            }
        ],
        "options": {
            "Rx levels blank (no signal detected) - Fiber break/outage": "DISPATCH_FIBER_ISSUE",
            "Performed ONT reboot - alarm cleared": "ONT_LIGHTS_NORMAL",
            "Performed ONT reboot - alarm returns": "DISPATCH_FIBER_ISSUE"
        },
        "help_text": "**Tip:** If the red light returns after reboot, dispatch a fiber tech (likely damaged or cut fiber)."
    },
    "ONT_LIGHTS_NORMAL": {
        "question": "**Step 3 · ONT OK – Check Eero Router**",
        "description": "Ask: 'Is the light on your Eero solid white, blinking blue, or another color?' Your next step depends on that answer.",
        "category": "router_check",
        "options": {
            "Continue with speed test documentation": "SPEED_TEST_DOCUMENTATION"
        },
        "help_text": "**Tip:** Solid white means the router thinks it's online; blinking blue/amber means it's still starting or disconnected."
    },
    "SPEED_TEST_DOCUMENTATION": {
        "question": "**Step 2A · Detailed Speed Test Documentation**",
        "description": "Let's collect comprehensive speed test data to get AI-powered troubleshooting recommendations tailored to this specific situation.",
        "category": "speed_test_analysis",
        "input_fields": [
            {
                "name": "customer_device",
                "label": "Customer Device Used for Speed Test",
                "type": "text",
                "required": True,
                "placeholder": "Example: iPhone 14, Samsung Galaxy S23, MacBook Pro, etc."
            },
            {
                "name": "ghz_band",
                "label": "What GHz Band is the Device Currently On?",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "2.4ghz", "label": "2.4 GHz"},
                    {"value": "5ghz", "label": "5 GHz"},
                    {"value": "6ghz", "label": "6 GHz (Wi-Fi 6E)"},
                    {"value": "unknown", "label": "Customer doesn't know"},
                    {"value": "wired", "label": "Wired/Ethernet connection"}
                ]
            },
            {
                "name": "download_speed",
                "label": "Download Speed Test Result (Mbps)",
                "type": "number",
                "required": True,
                "placeholder": "Enter download speed in Mbps"
            },
            {
                "name": "upload_speed",
                "label": "Upload Speed Test Result (Mbps)",
                "type": "number",
                "required": True,
                "placeholder": "Enter upload speed in Mbps"
            },
            {
                "name": "speed_test_app",
                "label": "Speed Test App Used",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "speedtest.net", "label": "Speedtest.net (Ookla)"},
                    {"value": "fast.com", "label": "Fast.com (Netflix)"},
                    {"value": "google", "label": "Google Speed Test"},
                    {"value": "att", "label": "AT&T Speed Test"},
                    {"value": "other", "label": "Other"}
                ]
            }
        ],
        "options": {
            "Continue to alarm analysis": "ALARM_STREAM_ANALYSIS"
        },
        "help_text": "**Tip:** This detailed data helps our AI system provide specific troubleshooting steps tailored to the device, connection type, and speed results."
    },
    "ALARM_STREAM_ANALYSIS": {
        "question": "**Step 2B · Document Stream/Alarm Information**",
        "description": "Check your monitoring systems for any alarms or issues. Document what the stream shows so our AI can provide targeted recommendations.",
        "category": "alarm_documentation",
        "input_fields": [
            {
                "name": "stream_alarm_details",
                "label": "What does the stream show for alarms/issues?",
                "type": "textarea",
                "required": True,
                "placeholder": "Document any alarms, error codes, signal levels, or issues found in AltiPlano, monitoring systems, etc."
            }
        ],
        "options": {
            "Get AI troubleshooting recommendations": "AI_RECOMMENDATIONS"
        },
        "help_text": "**Tip:** Be specific about alarm codes, signal levels, and any error messages. This helps the AI provide better recommendations."
    },
    "AI_RECOMMENDATIONS": {
        "question": "**Step 3 · AI-Powered Troubleshooting Recommendations**",
        "description": "Based on the speed test data and alarm information collected, here are intelligent troubleshooting steps generated specifically for this case.",
        "category": "ai_analysis",
        "is_ai_step": True,
        "options": {
            "Try the recommended steps": "ROUTER_STATUS_CHECK",
            "Need to escalate - recommendations didn't help": "ESCALATE_TIER2_AI"
        },
        "help_text": "**Tip:** These AI recommendations are based on the specific device, speed results, and alarm data you documented."
    },
    "ROUTER_STATUS_CHECK": {
        "question": "**Step 4 · Check Eero Router Status**",
        "description": "Now let's check the router. Ask: 'Is the light on your Eero solid white, blinking blue, or another color?'",
        "category": "router_check",
        "options": {
            "Router solid white, no internet": "EERO_NORMAL_CHECK_IP",
            "Router blinking / no Wi-Fi": "EERO_BLINKING_REBOOT",
            "Eero has no lights": "DISPATCH_DEAD_ROUTER"
        },
        "help_text": "**Tip:** Solid white means the router thinks it's online; blinking blue/amber means it's still starting or disconnected."
    },
    "ESCALATE_TIER2_AI": {
        "question": "**Tier 2 Escalation - AI Recommendations Failed**",
        "description": "The AI recommendations were not sufficient to resolve the issue. Escalating to Tier 2 with all collected data.",
        "category": "escalation",
        "input_fields": [
            {
                "name": "escalation_reason",
                "label": "Reason for Escalation",
                "type": "textarea",
                "required": True,
                "placeholder": "Explain why the AI recommendations did not resolve the issue and what was attempted..."
            },
            {
                "name": "contact_number",
                "label": "Customer Contact Number",
                "type": "text",
                "required": True,
                "placeholder": "Best number to reach customer"
            }
        ],
        "options": {
            "Complete Tier 2 escalation": "ESCALATION_SUMMARY"
        },
        "help_text": "**Tip:** Include all speed test data, alarm information, and AI recommendations attempted in the escalation notes."
    },
    "ONT_LIGHTS_ABNORMAL": {
        "question": "**Step 2 · ONT LEDs Abnormal / Cycling**",
        "description": "Have the customer power-cycle the ONT for 30 s. If LEDs still blink randomly or cycle, treat as hardware fault.",
        "category": "ont_troubleshooting",
        "options": {
            "After 30s reboot - ONT lights now normal": "ONT_LIGHTS_NORMAL",
            "After reboot - lights still abnormal": "DISPATCH_ONT_DEFECTIVE"
        },
        "help_text": "**Tip:** Continuous LED cycling after reboot → schedule dispatch to replace ONT."
    },
    "EERO_NORMAL_CHECK_IP": {
        "question": "**Router Solid White – Verify WAN IP**",
        "description": "In AltiPlano › WAN IP note the address. If it begins with 100.64, escalate to Tier 2 (do not mention CGNAT to customer). If a normal IP, run a laptop bypass, then disable/enable the ONT in BroadHub if still offline.",
        "category": "ip_verification",
        "input_fields": [
            {
                "name": "wan_ip",
                "label": "Customer WAN IP (from Altiplano → IBN Provisioning)",
                "type": "text",
                "required": True,
                "placeholder": "Check customer's WAN IP in Altiplano"
            }
        ],
        "options": {
            "CGNAT IP (100.64.x.x) - Escalate to Tier 2": "ESCALATE_TIER2_CGNAT",
            "Normal IP - Run laptop bypass test": "TEST_BYPASS_EERO"
        },
        "help_text": "**Tip:** Record WAN IP, ONT ID, Router MAC, and every step tried—Tier 2 needs those details."
    },
    "TEST_BYPASS_EERO": {
        "question": "**Direct ONT Connection Test**\n\nAsk customer to plug laptop directly into ONT, bypassing router:",
        "description": "Testing directly via ONT helps isolate if router is causing the issue.",
        "category": "isolation_test",
        "options": {
            "Internet works when bypassing Eero": "DISPATCH_FAULTY_EERO",
            "Still no internet directly from ONT": "REFRESH_ONT_IP"
        },
        "help_text": "Always perform this step to isolate router vs ONT issues."
    },
    "REFRESH_ONT_IP": {
        "question": "**Refresh ONT IP Assignment**\n\nGo to BroadHub → Disable/re-enable ONT to refresh IP:",
        "description": "Refresh the ONT's IP assignment to resolve provisioning issues.",
        "category": "ip_refresh",
        "options": {
            "After refresh - internet now works": "RESOLVED_IP_REFRESH",
            "Still no connection after refresh": "ESCALATE_TIER2_PROVISIONING"
        },
        "help_text": "IP refresh often resolves DHCP and provisioning issues."
    },
    "EERO_BLINKING_REBOOT": {
        "question": "**Router Not Broadcasting Wi-Fi**",
        "description": "Guide a full power sequence: unplug ONT & Eero → plug ONT first, wait green LEDs → plug Eero, wait for solid white. If still offline, bypass with laptop and check DHCP lease in AltiPlano.",
        "category": "power_cycle",
        "options": {
            "After power-cycle - Eero now solid white": "RESOLVED_POWER_CYCLE",
            "Still no solid white after 5 mins": "TEST_BYPASS_EERO_AGAIN"
        },
        "help_text": "**Tip:** If DHCP shows a MAC + IP when laptop is connected but not when Eero is, schedule router replacement."
    },
    "TEST_BYPASS_EERO_AGAIN": {
        "question": "**Secondary Bypass Test**\n\nConnect laptop directly to ONT again:",
        "description": "Confirm if the issue is with the Eero router or network provisioning.",
        "category": "isolation_test",
        "options": {
            "Laptop gets IP & internet from ONT": "DISPATCH_BAD_EERO",
            "No IP or internet via ONT": "CHECK_LEARNED_MAC"
        },
        "help_text": "This confirms whether Eero is defective or if there's a provisioning issue."
    },
    "CHECK_LEARNED_MAC": {
        "question": "**Check Learned MAC/IP**\n\nGo to BroadHub → disable/re-enable ONT, then check Altiplano for learned MAC/IP:",
        "description": "Verify if the ONT is properly learning MAC address and IP assignment.",
        "category": "mac_verification",
        "options": {
            "Learned MAC/IP present": "DISPATCH_BAD_EERO",
            "No MAC/IP learned": "ESCALATE_TIER2_DHCP"
        },
        "help_text": "Learned MAC/IP indicates network provisioning is working, confirming Eero is faulty."
    },
    
    # Dispatch and Resolution Steps
    "DISPATCH_ONT_DEFECTIVE": {
        "question": "**DISPATCH: ONT Hardware Replacement**",
        "description": "ONT likely defective - schedule dispatch for hardware replacement.",
        "category": "dispatch",
        "input_fields": [
            {
                "name": "ont_id",
                "label": "ONT ID",
                "type": "text",
                "required": True,
                "placeholder": "Enter ONT serial number or ID from device label"
            },
            {
                "name": "router_id", 
                "label": "Router ID/MAC",
                "type": "text",
                "required": True,
                "placeholder": "Enter Router MAC address or serial number"
            },
            {
                "name": "contact_number",
                "label": "Preferred Contact Number",
                "type": "text",
                "required": True,
                "placeholder": "Customer's preferred contact number for dispatch"
            }
        ],
        "options": {
            "Create dispatch ticket": "DISPATCH_SUMMARY"
        },
        "help_text": "ONT showing no lights or abnormal behavior usually indicates hardware failure."
    },
    "DISPATCH_FIBER_ISSUE": {
        "question": "**DISPATCH: Fiber Issue**",
        "description": "Confirmed fiber issue - dispatch fiber tech immediately.",
        "category": "dispatch",
        "input_fields": [
            {
                "name": "ont_id",
                "label": "ONT ID",
                "type": "text",
                "required": True,
                "placeholder": "Enter ONT serial number or ID from device label"
            },
            {
                "name": "contact_number",
                "label": "Preferred Contact Number",
                "type": "text",
                "required": True,
                "placeholder": "Customer's preferred contact number for dispatch"
            }
        ],
        "options": {
            "Create fiber dispatch ticket": "DISPATCH_SUMMARY"
        },
        "help_text": "Red alarm with no Rx signal or persistent alarm after reboot indicates fiber problem."
    },
    "DISPATCH_DEAD_ROUTER": {
        "question": "**DISPATCH: Dead Router**",
        "description": "Eero router has no power/lights - needs replacement.",
        "category": "dispatch",
        "input_fields": [
            {
                "name": "router_id",
                "label": "Router ID/MAC",
                "type": "text",
                "required": True,
                "placeholder": "Enter Router MAC address or serial number"
            },
            {
                "name": "contact_number",
                "label": "Preferred Contact Number",
                "type": "text",
                "required": True,
                "placeholder": "Customer's preferred contact number for dispatch"
            }
        ],
        "options": {
            "Create router replacement ticket": "DISPATCH_SUMMARY" 
        },
        "help_text": "Router with no lights after verifying power indicates hardware failure."
    },
    "DISPATCH_FAULTY_EERO": {
        "question": "**DISPATCH: Faulty Eero Router**",
        "description": "Internet works bypassing Eero - router is defective.",
        "category": "dispatch",
        "input_fields": [
            {
                "name": "router_id",
                "label": "Router ID/MAC",
                "type": "text",
                "required": True,
                "placeholder": "Enter Router MAC address or serial number"
            },
            {
                "name": "contact_number",
                "label": "Preferred Contact Number",
                "type": "text",
                "required": True,
                "placeholder": "Customer's preferred contact number for dispatch"
            }
        ],
        "options": {
            "Create Eero replacement ticket": "DISPATCH_SUMMARY"
        },
        "help_text": "Bypass test confirms Eero router is causing the connectivity issue."
    },
    "DISPATCH_BAD_EERO": {
        "question": "**DISPATCH: Bad Eero Router**", 
        "description": "Confirmed bad Eero router based on bypass test and MAC learning.",
        "category": "dispatch",
        "input_fields": [
            {
                "name": "router_id",
                "label": "Router ID/MAC",
                "type": "text",
                "required": True,
                "placeholder": "Enter Router MAC address or serial number"
            },
            {
                "name": "contact_number",
                "label": "Preferred Contact Number",
                "type": "text",
                "required": True,
                "placeholder": "Customer's preferred contact number for dispatch"
            }
        ],
        "options": {
            "Create Eero replacement ticket": "DISPATCH_SUMMARY"
        },
        "help_text": "Multiple tests confirm Eero router hardware failure."
    },
    
    # Escalation Steps
    "ESCALATE_TIER2_CGNAT": {
        "question": "**ESCALATE: CGNAT Issue**",
        "description": "CGNAT IP detected - escalate to Tier 2 for resolution.",
        "category": "escalation",
        "input_fields": [
            {
                "name": "ont_id",
                "label": "ONT ID",
                "type": "text",
                "required": True,
                "placeholder": "Enter ONT serial number or ID from device label"
            },
            {
                "name": "router_mac",
                "label": "Router MAC Address",
                "type": "text",
                "required": True,
                "placeholder": "Enter Router MAC address"
            },
            {
                "name": "wan_ip_address",
                "label": "WAN IP Address",
                "type": "text",
                "required": True,
                "placeholder": "Current WAN IP from Altiplano (100.64.x.x)"
            },
            {
                "name": "contact_number",
                "label": "Preferred Contact Number",
                "type": "text",
                "required": True,
                "placeholder": "Customer's preferred contact number"
            }
        ],
        "options": {
            "Create Tier 2 escalation": "ESCALATION_SUMMARY"
        },
        "help_text": "CGNAT issues require Tier 2 network engineering intervention."
    },
    "ESCALATE_TIER2_PROVISIONING": {
        "question": "**ESCALATE: Provisioning/Routing Issue**",
        "description": "No connectivity after IP refresh - escalate to Tier 2.",
        "category": "escalation",
        "input_fields": [
            {
                "name": "ont_id",
                "label": "ONT ID",
                "type": "text",
                "required": True,
                "placeholder": "Enter ONT serial number or ID from device label"
            },
            {
                "name": "router_mac",
                "label": "Router MAC Address",
                "type": "text",
                "required": True,
                "placeholder": "Enter Router MAC address"
            },
            {
                "name": "wan_ip_address",
                "label": "WAN IP Address",
                "type": "text",
                "required": True,
                "placeholder": "Current WAN IP from Altiplano"
            },
            {
                "name": "contact_number",
                "label": "Preferred Contact Number",
                "type": "text",
                "required": True,
                "placeholder": "Customer's preferred contact number"
            }
        ],
        "options": {
            "Create Tier 2 escalation": "ESCALATION_SUMMARY"
        },
        "help_text": "Persistent connectivity issues after troubleshooting require network engineering review."
    },
    "ESCALATE_TIER2_DHCP": {
        "question": "**ESCALATE: DHCP/Provisioning Issue**",
        "description": "No MAC/IP learned - DHCP or provisioning problem.",
        "category": "escalation",
        "input_fields": [
            {
                "name": "ont_id",
                "label": "ONT ID",
                "type": "text",
                "required": True,
                "placeholder": "Enter ONT serial number or ID from device label"
            },
            {
                "name": "router_mac",
                "label": "Router MAC Address",
                "type": "text",
                "required": True,
                "placeholder": "Enter Router MAC address"
            },
            {
                "name": "contact_number",
                "label": "Preferred Contact Number",
                "type": "text",
                "required": True,
                "placeholder": "Customer's preferred contact number"
            }
        ],
        "options": {
            "Create Tier 2 escalation": "ESCALATION_SUMMARY"  
        },
        "help_text": "DHCP and provisioning issues require Tier 2 network engineering expertise."
    },
    
    # Resolution Steps
    "RESOLVED_IP_REFRESH": {
        "question": "**RESOLVED: IP Refresh Fixed Issue**",
        "description": "Internet restored after ONT IP refresh.",
        "category": "resolution",
        "options": {
            "Document resolution": "RESOLVED_DOC"
        },
        "help_text": "IP refresh resolved the connectivity issue - document for future reference."
    },
    "RESOLVED_POWER_CYCLE": {
        "question": "**RESOLVED: Power Cycle Fixed Issue**", 
        "description": "Eero router restored after proper power cycle sequence.",
        "category": "resolution",
        "options": {
            "Document resolution": "RESOLVED_DOC"
        },
        "help_text": "Proper power cycle sequence resolved the router connectivity issue."
    },
    
    # Final Summary Steps
    "DISPATCH_SUMMARY": {
        "question": "**Step 4 · Outcome & Next Action**",
        "description": "Choose Resolved, Dispatch, or Escalate Tier 2. The summary box will auto-include your notes.",
        "category": "summary",
        "options": {
            "Generate Dispatch Report": "CASE_COMPLETED"
        },
        "help_text": "**Tip:** For Tier 2, include: ONT ID, Router MAC, WAN IP, light levels, bypass result, and steps already attempted."
    },
    "ESCALATION_SUMMARY": {
        "question": "**Step 4 · Outcome & Next Action**", 
        "description": "Choose Resolved, Dispatch, or Escalate Tier 2. The summary box will auto-include your notes.",
        "category": "summary",
        "options": {
            "Generate Escalation Report": "CASE_COMPLETED"
        },
        "help_text": "**Tip:** For Tier 2, include: ONT ID, Router MAC, WAN IP, light levels, bypass result, and steps already attempted."
    },
    "CASE_COMPLETED": {
        "question": "**Case Complete**",
        "description": "Case has been completed and report generated.",
        "category": "completion"
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
                    {"value": "ONU LOS PHY LAYER", "label": "ONU LOS PHY LAYER"},
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
                "type": "select",
                "required": True,
                "options": [
                    {"value": "Yes", "label": "Yes"},
                    {"value": "No", "label": "No"}
                ]
            },
            {
                "name": "steps_taken",
                "label": "Brief Notes (optional)",
                "type": "textarea",
                "required": False
            }
        ],
        "options": {
            "Submit & Generate Dispatch Summary": "DISPATCH_SUMMARY"
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
    "DISPATCH_SUMMARY": {
        "question": "**📋 DISPATCH SUMMARY GENERATED**\nCopy the summary below and paste into Teams for field dispatch:",
        "description": "Ready-to-paste dispatch summary with all case details for field service coordination.",
        "category": "dispatch_summary",
        "options": {
            "Finish Case": "END_CASE"
        },
        "help_text": "Summary includes all customer, equipment, and diagnostic information for field technicians."
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
                "label": "Router ID (serial, MAC, or any format)",
                "type": "text",
                "required": True,
                "placeholder": "Paste full router serial, MAC, etc. (min 6 chars)",
                "minlength": "6"
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
            "Slow Speeds - Start Pre-Check": "SS_START",
            "Intermittent - Start WiFi Environment Analysis": "CHECK_WIFI_ENV"
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
    },
    
    # ---- SLOW-SPEED root ---------------------------------------------
    "SS_START": {
        "question": "**FIBER PRE-CHECK**\n\nPull alarms from Altiplano → ONT > Alarms tab → Click \"+ Add Alarm\" for each Active/Cleared entry.",
        "description": "Streamlined fiber diagnostics using authentic Altiplano data with repeatable alarm entry system.",
        "category": "slow_speeds_precheck",
        "input_fields": [
            {
                "name": "alarm_status_1",
                "label": "Alarm Status",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "Active", "label": "🔴 Active"},
                    {"value": "Cleared", "label": "✅ Cleared"},
                    {"value": "No Alarms", "label": "🛡️ No Alarms"}
                ]
            },
            {
                "name": "alarm_type_1",
                "label": "Alarm Type",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "ONU Loss of PHY Layer", "label": "🔗 ONU Loss of PHY Layer"},
                    {"value": "Loss of Signal (LOS)", "label": "📶 Loss of Signal (LOS)"},
                    {"value": "Other/Custom", "label": "❓ Other/Custom"}
                ]
            },
            {
                "name": "light_levels",
                "label": "Light Levels",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "Good (-20 to -10)", "label": "🟢 Good (-20 to -10)"},
                    {"value": "Low (-25 or lower)", "label": "🟡 Low (-25 or lower)"},
                    {"value": "Gap Too Wide (>5 points)", "label": "🔴 Gap Too Wide (>5 points)"},
                    {"value": "Cannot Access", "label": "❓ Cannot Access"}
                ]
            },
            {
                "name": "alarm_notes_1",
                "label": "Notes (Optional)",
                "type": "text",
                "required": False,
                "placeholder": "e.g. Cleared after splice, specific power levels"
            },
            {
                "name": "additional_alarms",
                "label": "Additional Alarms",
                "type": "textarea",
                "required": False,
                "placeholder": "If more alarms exist, list them here with Status, Type, and any notes..."
            }
        ],
        "options": {
            "Begin Troubleshooting": "SS_LIGHT_VALIDATE"
        },
        "help_text": "System validates light levels and compiles all alarm data for trend analysis.",
        "alarm_explanations": {
            "LAN_LOS": {
                "meaning": "ONT detects no active Ethernet connection on LAN port(s)",
                "troubleshooting": "1. Check Ethernet cable connections\n2. Replace cable to rule out faults\n3. Power-cycle ONT/router\n4. Verify connected device is active"
            },
            "Loss_PHY": {
                "meaning": "ONT lost optical connection (no detectable incoming signal)",
                "troubleshooting": "1. Verify fiber connections at ONT and wall jack\n2. Check fiber for visible damage\n3. Clean/reseat fiber connector\n4. Confirm no recent construction near fiber"
            },
            "Upstream_Degradation": {
                "meaning": "ONT's upstream signal quality has degraded, causing errors or speed drops",
                "troubleshooting": "1. Check optical signal levels\n2. Verify gap between OLT Rx and ONT Tx is within 4 dBm\n3. Inspect and clean ONT fiber connector\n4. Check for excessive fiber length"
            },
            "ONT_Reboot": {
                "meaning": "ONT restarted automatically after firmware update or due to firmware issues",
                "troubleshooting": "1. Confirm current firmware version\n2. Check logs for update failures\n3. Power-cycle ONT manually\n4. Escalate persistent reboots to Tier 2"
            },
            "Dying_Gasp": {
                "meaning": "ONT lost power and sent 'last gasp' notification before shutdown",
                "troubleshooting": "1. Confirm recent power outage/surge\n2. Verify power adapter connection\n3. Check outlet functionality\n4. Suggest UPS for frequent outages"
            },
            "High_RX": {
                "meaning": "ONT receiving excessively strong optical signal (> -8 dBm)",
                "troubleshooting": "1. Check splitter configuration\n2. Consider optical attenuator\n3. Dispatch technician if signal remains high"
            },
            "Low_RX": {
                "meaning": "ONT receiving weak optical signal (< -27 dBm), causing intermittent/slow connection",
                "troubleshooting": "1. Inspect fiber for dirt/damage\n2. Verify splitter configuration\n3. Schedule dispatch for fiber integrity check"
            }
        }
    },

    # ---- Validate light-level gap ------------------------------------
    "SS_LIGHT_VALIDATE": {
        "question": "**🚨 BAD OPTICAL LIGHT LEVELS DETECTED**\n\n**What does this mean?**\nThe optical signal strength is outside acceptable range (-10 to -25 dBm) OR the power gap exceeds 5 dB, indicating potential fiber issues.\n\n**Your readings:**\n• ONT Power: {ont_power} dBm\n• OLT Power: {olt_power} dBm\n• Power Gap: {power_gap:.1f} dB\n\n**Acceptable ranges:** Both values should be between -10 to -25 dBm with no more than 5 dB difference between them.\n\n**Common causes:** Dirty/damaged connectors, broken fiber cable, faulty splitters, or recent construction.",
        "description": "Bad light levels detected - requires verification steps before dispatch.",
        "category": "fiber_diagnostics",
        "input_fields": [
            {
                "name": "connections_checked",
                "label": "Connections verified clean, secure, and undamaged",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "Yes", "label": "Yes - Connections verified"},
                    {"value": "No", "label": "No - Issues found with connections"}
                ]
            },
            {
                "name": "environmental_check",
                "label": "No known environmental/construction issues identified",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "Yes", "label": "Yes - No environmental issues"},
                    {"value": "No", "label": "No - Recent construction/damage identified"}
                ]
            },
            {
                "name": "recheck_completed",
                "label": "Optical levels still abnormal after rechecking",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "Yes", "label": "Yes - Still abnormal after recheck"},
                    {"value": "No", "label": "No - Levels improved after basic troubleshooting"}
                ]
            }
        ],
        "options": {
            "All checks completed - Proceed to Dispatch": "DISPATCH_CHECK",
            "Issues resolved - Continue device troubleshooting": "SS_WIFI_OR_WIRED"
        },
        "help_text": "Complete all verification steps before dispatching. This ensures proper troubleshooting and reduces unnecessary truck rolls."
    },

    # ---- Explain fiber results and transition to router testing --------
    "SS_WIFI_OR_WIRED": {
        "question": "**FIBER DIAGNOSTICS COMPLETE ✓**\n\n**Explain to customer:** \"Good news! Our fiber diagnostics show everything is working properly on the modem side. The optical signal levels are within normal range, which means the fiber connection to your home is healthy.\n\nNow we need to test your router to determine what might be causing the slow speeds you're experiencing.\"\n\n**Device Scope:** Are they experiencing slow speeds on specific devices or all devices?",
        "description": "Transition from fiber diagnostics to router testing with clear customer communication.",
        "category": "router_diagnostics_intro",
        "input_fields": [
            {
                "name": "device_scope",
                "label": "Device Scope",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "specific_device", "label": "Specific device(s) only"},
                    {"value": "all_devices", "label": "All devices in the home"},
                    {"value": "some_devices", "label": "Some devices but not others"}
                ],
                "help_text": "Document exactly what the customer reports"
            },
            {
                "name": "device_details",
                "label": "Device Details",
                "type": "textarea",
                "required": True,
                "placeholder": "Document what devices are affected and customer's specific experience...",
                "help_text": "Record customer's exact description of which devices and symptoms"
            },
            {
                "name": "connection_type",
                "label": "Connection Type",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "wifi", "label": "WiFi/Wireless devices"},
                    {"value": "wired", "label": "Wired/Ethernet devices"},
                    {"value": "both", "label": "Both WiFi and wired devices"}
                ],
                "help_text": "Determines troubleshooting path"
            }
        ],
        "options": {
            "WiFi Issues - Test Wireless Setup": "SS_WIFI_SETUP",
            "Wired Issues - Check Ethernet Ports": "SS_WIRED_PORTS"
        },
        "help_text": "Proper customer communication builds confidence while gathering diagnostic information."
    },

    # ---- WiFi Setup and Interference Check ---------------------------
    "SS_WIFI_SETUP": {
        "question": "**WIFI ENVIRONMENT CHECK**\n\nWe're going to check your WiFi setup to identify potential interference or configuration issues.",
        "description": "Comprehensive WiFi environment analysis including device conflicts and SSID issues.",
        "category": "wifi_diagnostics",
        "input_fields": [
            {
                "name": "eero_only_wifi",
                "label": "Is the Eero the ONLY device providing WiFi?",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "yes", "label": "Yes - Only Eero is broadcasting WiFi"},
                    {"value": "no", "label": "No - Other devices also provide WiFi"},
                    {"value": "unsure", "label": "Customer is unsure"}
                ],
                "help_text": "Multiple WiFi sources can cause conflicts and slow speeds"
            },
            {
                "name": "other_wifi_devices",
                "label": "Other WiFi Devices (if any)",
                "type": "textarea",
                "required": False,
                "placeholder": "List any other routers, extenders, or WiFi devices in the home...",
                "help_text": "Document previous provider equipment, extenders, etc."
            },
            {
                "name": "new_router",
                "label": "Did customer recently get this Eero router?",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "yes_new", "label": "Yes - Recently installed/upgraded"},
                    {"value": "no_existing", "label": "No - Has been installed for a while"},
                    {"value": "unsure", "label": "Customer is unsure"}
                ]
            },
            {
                "name": "ssid_same_as_old",
                "label": "Is the WiFi network name (SSID) the same as their previous provider?",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "yes", "label": "Yes - Same network name as before"},
                    {"value": "no", "label": "No - Different network name"},
                    {"value": "unsure", "label": "Customer doesn't know/remember"}
                ],
                "help_text": "Same SSID can cause device confusion and connection issues"
            }
        ],
        "options": {
            "Continue WiFi Analysis": "CHECK_WIFI_ENV"
        },
        "help_text": "WiFi conflicts and SSID issues are common causes of slow speeds in new installations."
    },

    # ---- Eero Model Selection ----------------------------------------
    "SS_WIRED_PORTS": {
        "question": "**ETHERNET PORT ANALYSIS - STEP 1**\n\n**Instructions:** Open Eero Insight → Click on **Summary** → Look for the main Eero (gateway) and select the **down arrow** to the right → Note how many ports are being used and identify which port the ONT is connected to\n\nWhat Eero model does the customer have?",
        "description": "First step: Identify the Eero model to show correct port configuration options.",
        "category": "eero_model_selection",
        "input_fields": [
            {
                "name": "eero_model",
                "label": "Eero Model",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "pro_6e", "label": "Eero Pro 6E"},
                    {"value": "max_7", "label": "Eero Max 7"}
                ],
                "help_text": "Select the customer's Eero model"
            }
        ],
        "options": {
            "Next - Analyze Ports": "SS_PORT_ANALYSIS"
        },
        "help_text": "Identify the Eero model first to show the correct port configuration options."
    },

    # ---- Port Configuration Analysis ------------------------------
    "SS_PORT_ANALYSIS": {
        "question": "**ETHERNET PORT ANALYSIS - STEP 2**\n\n**Port Configuration:** Document what you see in Eero Insight for each port and the customer's setup.",
        "description": "Analyze the specific port configuration and speeds based on the Eero model.",
        "category": "port_configuration_analysis",
        "input_fields": [
            {
                "name": "port_1_device",
                "label": "Port 1 - Connected Device",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "ont", "label": "ONT/Modem"},
                    {"value": "other_device", "label": "Other Device"},
                    {"value": "empty", "label": "Not Connected"}
                ],
                "help_text": "What is connected to Port 1?"
            },
            {
                "name": "port_1_speed",
                "label": "Port 1 - Negotiated Speed",
                "type": "select",
                "required": False,
                "options": [
                    {"value": "100mbps", "label": "100 Mbps"},
                    {"value": "1gbps", "label": "1 Gbps"},
                    {"value": "2_5gbps", "label": "2.5 Gbps"},
                    {"value": "5gbps", "label": "5 Gbps"},
                    {"value": "10gbps", "label": "10 Gbps"}
                ],
                "help_text": "Speed shown in Eero Insight for Port 1"
            },
            {
                "name": "port_2_device",
                "label": "Port 2 - Connected Device",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "ont", "label": "ONT/Modem"},
                    {"value": "other_device", "label": "Other Device"},
                    {"value": "empty", "label": "Not Connected"}
                ],
                "help_text": "What is connected to Port 2?"
            },
            {
                "name": "port_2_speed",
                "label": "Port 2 - Negotiated Speed",
                "type": "select",
                "required": False,
                "options": [
                    {"value": "100mbps", "label": "100 Mbps"},
                    {"value": "1gbps", "label": "1 Gbps"},
                    {"value": "2_5gbps", "label": "2.5 Gbps"},
                    {"value": "5gbps", "label": "5 Gbps"},
                    {"value": "10gbps", "label": "10 Gbps"}
                ],
                "help_text": "Speed shown in Eero Insight for Port 2"
            },
            {
                "name": "port_3_device",
                "label": "Port 3 - Connected Device (Max 7 only)",
                "type": "select",
                "required": False,
                "options": [
                    {"value": "ont", "label": "ONT/Modem"},
                    {"value": "other_device", "label": "Other Device"},
                    {"value": "empty", "label": "Not Connected"}
                ],
                "help_text": "What is connected to Port 3? (Max 7 only)"
            },
            {
                "name": "port_3_speed",
                "label": "Port 3 - Negotiated Speed (Max 7 only)",
                "type": "select",
                "required": False,
                "options": [
                    {"value": "100mbps", "label": "100 Mbps"},
                    {"value": "1gbps", "label": "1 Gbps"},
                    {"value": "2_5gbps", "label": "2.5 Gbps"},
                    {"value": "5gbps", "label": "5 Gbps"},
                    {"value": "10gbps", "label": "10 Gbps"}
                ],
                "help_text": "Speed shown in Eero Insight for Port 3 (Max 7 only)"
            },
            {
                "name": "port_4_device",
                "label": "Port 4 - Connected Device (Max 7 only)",
                "type": "select",
                "required": False,
                "options": [
                    {"value": "ont", "label": "ONT/Modem"},
                    {"value": "other_device", "label": "Other Device"},
                    {"value": "empty", "label": "Not Connected"}
                ],
                "help_text": "What is connected to Port 4? (Max 7 only)"
            },
            {
                "name": "port_4_speed",
                "label": "Port 4 - Negotiated Speed (Max 7 only)",
                "type": "select",
                "required": False,
                "options": [
                    {"value": "100mbps", "label": "100 Mbps"},
                    {"value": "1gbps", "label": "1 Gbps"},
                    {"value": "2_5gbps", "label": "2.5 Gbps"},
                    {"value": "5gbps", "label": "5 Gbps"},
                    {"value": "10gbps", "label": "10 Gbps"}
                ],
                "help_text": "Speed shown in Eero Insight for Port 4 (Max 7 only)"
            },
            {
                "name": "customer_speed_plan",
                "label": "Customer's Speed Plan",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "1gig", "label": "1 Gig"},
                    {"value": "5gig", "label": "5 Gig"},
                    {"value": "8gig", "label": "8 Gig"}
                ],
                "help_text": "What speed plan is the customer paying for?"
            },
            {
                "name": "notes",
                "label": "Additional Notes",
                "type": "textarea",
                "required": False,
                "placeholder": "Any additional observations about the port configuration...",
                "help_text": "Document any other relevant details"
            }
        ],
        "options": {
            "Port configuration is correct": "SS_WIRED_TROUBLESHOOTING",
            "Need to optimize port configuration": "SS_PORT_OPTIMIZATION"
        },
        "help_text": "**Pro 6E:** Port 1=2.5GbE, Port 2=1GbE | **Max 7:** Port 1&2=5GbE, Port 3&4=10GbE. Ensure ONT and speed plan match the correct port for optimal performance."
    },

    # ---- Port Optimization Recommendations ---------------------------
    "SS_PORT_OPTIMIZATION": {
        "question": "**PORT OPTIMIZATION REQUIRED**\n\nBased on the analysis, the customer's ONT is not connected to the optimal port for their speed plan.",
        "description": "Provide specific recommendations for optimal port configuration.",
        "category": "port_optimization",
        "input_fields": [
            {
                "name": "optimization_recommendation",
                "label": "Recommendation",
                "type": "textarea",
                "required": True,
                "placeholder": "Explain what port change is needed and why...",
                "help_text": "Provide clear instructions for optimal port configuration"
            }
        ],
        "options": {
            "Customer will make the change": "SS_WIRED_TROUBLESHOOTING",
            "Schedule technician for optimization": "DISPATCH_CHECK"
        },
        "help_text": "Proper port configuration ensures customers get the speeds they're paying for."
    },

    # ---- Wired Troubleshooting Steps ---------------------------------
    "SS_WIRED_TROUBLESHOOTING": {
        "question": "**WIRED CONNECTION TROUBLESHOOTING**\n\nNow let's perform some basic troubleshooting steps to resolve the wired connection issues.",
        "description": "Systematic troubleshooting steps for wired ethernet connection problems.",
        "category": "wired_troubleshooting",
        "input_fields": [
            {
                "name": "troubleshooting_step",
                "label": "Troubleshooting Step",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "reboot_eero", "label": "Reboot the Eero router"},
                    {"value": "reseat_ethernet", "label": "Reseat ethernet cables"},
                    {"value": "test_different_port", "label": "Test different ethernet port"},
                    {"value": "replace_ethernet_cable", "label": "Replace ethernet cable"}
                ],
                "help_text": "Select the appropriate troubleshooting step"
            },
            {
                "name": "step_instructions",
                "label": "Instructions Given to Customer",
                "type": "textarea",
                "required": True,
                "placeholder": "Document exactly what instructions you provided to the customer...",
                "help_text": "Record the specific steps you asked the customer to perform"
            },
            {
                "name": "step_completed",
                "label": "Did the customer complete this step?",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "yes", "label": "Yes - Customer completed the step"},
                    {"value": "no", "label": "No - Customer could not complete the step"},
                    {"value": "partial", "label": "Partially completed"}
                ]
            },
            {
                "name": "step_result",
                "label": "Did this step resolve the issue?",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "resolved", "label": "Yes - Issue resolved"},
                    {"value": "improved", "label": "Partially improved"},
                    {"value": "no_change", "label": "No change"},
                    {"value": "worse", "label": "Made it worse"}
                ],
                "help_text": "Document the outcome for reporting purposes"
            },
            {
                "name": "additional_notes",
                "label": "Additional Notes",
                "type": "textarea",
                "required": False,
                "placeholder": "Any additional observations or customer feedback...",
                "help_text": "Document any other relevant information"
            }
        ],
        "options": {
            "Issue resolved - Create case summary": "SS_WIRED_RESOLVED", 
            "Try another troubleshooting step": "SS_WIRED_TROUBLESHOOTING_NEXT",
            "Escalate to Tier 2": "SS_WIRED_ESCALATE"
        },
        "help_text": "Always document what step was taken and whether it resolved the issue. This data helps identify the most common causes of wired connection problems."
    },

    # ---- Next Wired Troubleshooting Step -----------------------------
    "SS_WIRED_TROUBLESHOOTING_NEXT": {
        "question": "**ADDITIONAL WIRED TROUBLESHOOTING**\n\nLet's try another troubleshooting step. Select a different method to resolve the wired connection issues.",
        "description": "Continue with additional troubleshooting steps for wired ethernet connection problems.",
        "category": "wired_troubleshooting_continued",
        "input_fields": [
            {
                "name": "troubleshooting_step",
                "label": "Next Troubleshooting Step",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "reboot_eero", "label": "Reboot the Eero router"},
                    {"value": "reseat_ethernet", "label": "Reseat ethernet cables"},
                    {"value": "test_different_port", "label": "Test different ethernet port"},
                    {"value": "replace_ethernet_cable", "label": "Replace ethernet cable"},
                    {"value": "power_cycle_ont", "label": "Power cycle the ONT"},
                    {"value": "check_cable_integrity", "label": "Check ethernet cable for damage"}
                ],
                "help_text": "Select the next troubleshooting step to attempt"
            },
            {
                "name": "step_instructions",
                "label": "Instructions Given to Customer",
                "type": "textarea",
                "required": True,
                "placeholder": "Document exactly what instructions you provided to the customer...",
                "help_text": "Record the specific steps you asked the customer to perform"
            },
            {
                "name": "step_completed",
                "label": "Did the customer complete this step?",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "yes", "label": "Yes - Customer completed the step"},
                    {"value": "no", "label": "No - Customer could not complete the step"},
                    {"value": "partial", "label": "Partially completed"}
                ]
            },
            {
                "name": "step_result",
                "label": "Did this step resolve the issue?",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "resolved", "label": "Yes - Issue resolved"},
                    {"value": "improved", "label": "Partially improved"},
                    {"value": "no_change", "label": "No change"},
                    {"value": "worse", "label": "Made it worse"}
                ],
                "help_text": "Document the outcome for reporting purposes"
            },
            {
                "name": "additional_notes",
                "label": "Additional Notes",
                "type": "textarea",
                "required": False,
                "placeholder": "Any additional observations or customer feedback...",
                "help_text": "Document any other relevant information"
            }
        ],
        "options": {
            "Issue resolved - Create case summary": "SS_WIRED_RESOLVED",
            "Try another troubleshooting step": "SS_WIRED_TROUBLESHOOTING_NEXT",
            "Escalate to Tier 2": "SS_WIRED_ESCALATE"
        },
        "help_text": "Each troubleshooting step will be documented separately to track what methods are most effective for resolving wired connection issues."
    },

    # ---- Wired Case Resolution Summary --------------------------------
    "SS_WIRED_RESOLVED": {
        "question": "**CASE RESOLVED - CREATE BROADHUB SUMMARY**\n\nGenerate a comprehensive summary for BroadHub notes documenting the resolution.",
        "description": "Create detailed case summary for BroadHub documentation when wired issue is resolved.",
        "category": "case_resolution",
        "input_fields": [
            {
                "name": "final_resolution",
                "label": "Final Resolution Method",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "reboot_eero", "label": "Eero router reboot resolved the issue"},
                    {"value": "reseat_cables", "label": "Reseating ethernet cables fixed the problem"},
                    {"value": "different_port", "label": "Using different ethernet port resolved speeds"},
                    {"value": "cable_replacement", "label": "Replacing ethernet cable fixed connection"},
                    {"value": "port_optimization", "label": "Moving to optimal port for speed plan"},
                    {"value": "multiple_steps", "label": "Combination of multiple troubleshooting steps"}
                ],
                "help_text": "Select the primary method that resolved the customer's issue"
            },
            {
                "name": "final_speeds",
                "label": "Final Speed Test Results",
                "type": "text",
                "required": True,
                "placeholder": "Download/Upload speeds after resolution (e.g., 950Mbps/890Mbps)",
                "help_text": "Document the customer's final speed test results"
            },
            {
                "name": "customer_satisfaction",
                "label": "Customer Satisfaction",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "very_satisfied", "label": "Very satisfied - Speeds exceed expectations"},
                    {"value": "satisfied", "label": "Satisfied - Speeds meet expectations"},
                    {"value": "somewhat_satisfied", "label": "Somewhat satisfied - Speeds adequate"}
                ],
                "help_text": "Customer's satisfaction level with the resolution"
            }
        ],
        "options": {
            "Generate BroadHub Summary": "RESOLVED"
        },
        "help_text": "This information will be compiled into a comprehensive summary for BroadHub notes including all customer info, equipment details, steps taken, and resolution."
    },

    # ---- Tier 2 Escalation Summary -----------------------------------
    "SS_WIRED_ESCALATE": {
        "question": "**ESCALATE TO TIER 2**\n\nPrepare comprehensive escalation summary with all collected information for Tier 2 support.",
        "description": "Compile detailed escalation summary including customer contact, equipment, troubleshooting steps, and current status.",
        "category": "tier2_escalation",
        "input_fields": [
            {
                "name": "escalation_reason",
                "label": "Primary Reason for Escalation",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "no_improvement", "label": "No improvement after all troubleshooting steps"},
                    {"value": "intermittent_issues", "label": "Intermittent issues requiring advanced diagnostics"},
                    {"value": "equipment_suspected", "label": "Suspected hardware/equipment failure"},
                    {"value": "complex_configuration", "label": "Complex network configuration beyond Tier 1"},
                    {"value": "customer_request", "label": "Customer specifically requested escalation"}
                ],
                "help_text": "Select the primary reason for escalating to Tier 2"
            },
            {
                "name": "current_speeds",
                "label": "Current Speed Test Results",
                "type": "text",
                "required": True,
                "placeholder": "Download/Upload speeds after troubleshooting (e.g., 45Mbps/12Mbps)",
                "help_text": "Document the customer's current speed test results"
            },
            {
                "name": "customer_availability",
                "label": "Customer Availability for Follow-up",
                "type": "textarea",
                "required": True,
                "placeholder": "Best times to contact customer, preferred contact method, any scheduling constraints...",
                "help_text": "When and how Tier 2 can best reach the customer"
            },
            {
                "name": "priority_level",
                "label": "Escalation Priority",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "high", "label": "High - Service completely unusable"},
                    {"value": "medium", "label": "Medium - Significant performance issues"},
                    {"value": "low", "label": "Low - Minor performance concerns"}
                ],
                "help_text": "Priority level for Tier 2 follow-up"
            }
        ],
        "options": {
            "Generate Tier 2 Escalation": "ESCALATED"
        },
        "help_text": "This will compile all customer information, equipment details, troubleshooting steps taken, and current status into a comprehensive handoff summary for Tier 2."
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
