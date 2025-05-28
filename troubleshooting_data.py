# Minimal working troubleshooting data to get the app running
TROUBLESHOOTING_STEPS = {
    "START": {
        "question": "**Step 1 · Verify ONT Power & LEDs**",
        "description": "**Agent Talk Track:** \"Let's start with your fiber modem. Look at the Nokia ONT and tell me what each light is doing: **Power**, **PON/Alarm** (red or green), and **Data/Internet**. Are they solid, blinking, or off?\"",
        "category": "ont_troubleshooting",
        "options": {
            "ONT power + PON green + Data green": "SS_START",
            "ONT has issues (power/PON/data problems)": "ONT_LIGHTS_ABNORMAL"
        },
        "help_text": "**Tip:** Power should be solid, PON/Alarm should be green (not red), Data/Internet should be solid green."
    },
    "SS_START": {
        "question": "**Step 2 · Speed Test Documentation**",
        "description": "Document the customer's speed test results and testing environment for AI analysis.",
        "category": "speed_documentation",
        "input_fields": [
            {
                "name": "customer_device",
                "label": "Customer Device Used for Testing",
                "type": "select",
                "required": True,
                "options": [
                    "iPhone", "Android Phone", "iPad", "Android Tablet",
                    "Windows Laptop", "Mac Laptop", "Desktop PC", "Other"
                ]
            },
            {
                "name": "ghz_band",
                "label": "Wi-Fi Band (GHz)",
                "type": "select",
                "required": True,
                "options": ["2.4 GHz", "5 GHz", "6 GHz", "Unknown"]
            },
            {
                "name": "download_speed",
                "label": "Download Speed (Mbps)",
                "type": "number",
                "required": True,
                "placeholder": "Enter download speed in Mbps"
            },
            {
                "name": "upload_speed",
                "label": "Upload Speed (Mbps)",
                "type": "number",
                "required": True,
                "placeholder": "Enter upload speed in Mbps"
            },
            {
                "name": "speed_test_app",
                "label": "Speed Test Application Used",
                "type": "select",
                "required": True,
                "options": [
                    "Speedtest.net (Ookla)", "Fast.com (Netflix)", "Google Speed Test",
                    "AT&T Speed Test", "Verizon Speed Test", "Other"
                ]
            }
        ],
        "options": {
            "Continue to alarm analysis": "ALARM_STREAM_ANALYSIS"
        },
        "help_text": "**Tip:** Collect detailed speed test information for AI analysis of performance issues."
    },
    "ALARM_STREAM_ANALYSIS": {
        "question": "**Step 3 · Stream/Alarm Analysis**",
        "description": "Document any alarms or events from monitoring systems.",
        "category": "alarm_analysis",
        "input_fields": [
            {
                "name": "stream_alarm_details",
                "label": "Stream/Alarm Information",
                "type": "textarea",
                "required": True,
                "placeholder": "Paste alarm details, error messages, or monitoring system information here..."
            }
        ],
        "options": {
            "Get AI recommendations": "AI_RECOMMENDATIONS"
        },
        "help_text": "**Tip:** Include any error messages, alarm codes, or monitoring system alerts."
    },
    "AI_RECOMMENDATIONS": {
        "question": "**AI-Powered Troubleshooting Recommendations**",
        "description": "AI analysis of speed test and alarm data to suggest troubleshooting steps.",
        "category": "ai_analysis",
        "options": {
            "AI recommendations worked - Continue to router check": "EERO_STATUS_CHECK",
            "AI recommendations didn't work - Escalate to Tier 2": "ESCALATE_TIER2_AI"
        },
        "help_text": "**Tip:** Review AI suggestions and try recommended steps before escalating."
    },
    "EERO_STATUS_CHECK": {
        "question": "**Step 4 · Router Status Check**",
        "description": "Check the Eero router status and lights.",
        "category": "router_troubleshooting",
        "options": {
            "Router working normally": "DISPATCH_CHECK",
            "Router has issues": "EERO_REBOOT"
        },
        "help_text": "**Tip:** Eero should show solid white light when working properly."
    },
    "EERO_REBOOT": {
        "question": "**Router Reboot Required**",
        "description": "Guide customer through router reboot process.",
        "category": "router_troubleshooting",
        "options": {
            "Reboot resolved issue": "DISPATCH_CHECK",
            "Reboot didn't help": "DISPATCH_ROUTER_ISSUE"
        },
        "help_text": "**Tip:** Unplug router for 30 seconds, then plug back in and wait 2 minutes."
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
            }
        ],
        "options": {
            "Complete Tier 2 escalation": "ESCALATION_SUMMARY"
        },
        "help_text": "**Tip:** Include all speed test data, alarm information, and AI recommendations attempted in the escalation notes."
    },
    "DISPATCH_CHECK": {
        "question": "**Final Status Check**",
        "description": "Verify if the issue has been resolved or if dispatch is needed.",
        "category": "resolution_check",
        "options": {
            "Issue resolved - Case complete": "RESOLVED",
            "Issue not resolved - Need dispatch": "DISPATCH_SUMMARY"
        },
        "help_text": "**Tip:** Confirm with customer that their internet is working properly."
    },
    "DISPATCH_SUMMARY": {
        "question": "**Generate Dispatch Report**",
        "description": "Create comprehensive dispatch ticket with all troubleshooting information.",
        "category": "dispatch",
        "options": {
            "Generate report": "COMPLETED"
        },
        "help_text": "**Tip:** This will create a detailed report for field technicians."
    },
    "ONT_LIGHTS_ABNORMAL": {
        "question": "**ONT Hardware Issue Detected**",
        "description": "ONT has power, PON, or data light issues requiring technician visit.",
        "category": "hardware_issue",
        "options": {
            "Schedule technician": "DISPATCH_SUMMARY"
        },
        "help_text": "**Tip:** Hardware issues require field technician replacement."
    },
    "DISPATCH_ROUTER_ISSUE": {
        "question": "**Router Issue Detected**",
        "description": "Router problems require replacement or technician visit.",
        "category": "hardware_issue",
        "options": {
            "Schedule technician": "DISPATCH_SUMMARY"
        },
        "help_text": "**Tip:** Router replacement may be needed."
    },
    "RESOLVED": {
        "question": "**Case Resolved Successfully**",
        "description": "Customer issue has been resolved through troubleshooting steps.",
        "category": "resolution",
        "options": {},
        "help_text": "**Success:** Issue resolved without dispatch needed."
    },
    "COMPLETED": {
        "question": "**Case Completed**",
        "description": "Troubleshooting case completed with dispatch scheduled.",
        "category": "completion",
        "options": {},
        "help_text": "**Complete:** Dispatch ticket generated for field technician."
    },
    "ESCALATION_SUMMARY": {
        "question": "**Tier 2 Escalation Complete**",
        "description": "Case escalated to Tier 2 with comprehensive troubleshooting data.",
        "category": "escalation",
        "options": {},
        "help_text": "**Escalated:** Tier 2 team will take over this case."
    }
}

# Equipment information
EQUIPMENT_INFO = {
    "ont_types": {
        "Nokia ONT (Altiplano)": {
            "model": "Nokia ONT",
            "description": "Primary fiber modem with PON connectivity",
            "lights": ["Power", "PON/Alarm", "Data/Internet"]
        }
    },
    "router_types": {
        "Eero": {
            "model": "Eero Router",
            "description": "Mesh Wi-Fi router system",
            "lights": ["Status LED (white/blue/amber)"]
        }
    }
}