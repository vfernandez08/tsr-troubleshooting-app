
TROUBLESHOOTING_STEPS = {
    "START": {
        "question": "**STEP 1: VERIFY ONT POWER & LEDS**",
        "description": "**Agent Talk Track:** \"Let's start with your fiber modem. Look at the Nokia ONT and tell me what each light is doing: **Power**, **PON/Alarm** (red or green), and **Data/Internet**. Are they solid, blinking, or off?\"",
        "category": "ont_troubleshooting",
        "input_fields": [
            {
                "name": "ont_power_status",
                "label": "ONT Power Light Status",
                "type": "select",
                "required": True,
                "options": ["Solid Green", "Off", "Blinking", "Solid Red"]
            },
            {
                "name": "ont_pon_status", 
                "label": "ONT PON/Alarm Light Status",
                "type": "select",
                "required": True,
                "options": ["Solid Green", "Solid Red", "Off", "Blinking"]
            },
            {
                "name": "ont_data_status",
                "label": "ONT Data/Internet Light Status", 
                "type": "select",
                "required": True,
                "options": ["Solid Green", "Blinking Green", "Off", "Solid Red"]
            }
        ],
        "options": {
            "Continue to WiFi Check": "WIFI_CHECK"
        },
        "help_text": "**Tip:** Power should be solid green, PON/Alarm should be green (not red), Data/Internet should be solid or blinking green."
    },
    "WIFI_CHECK": {
        "question": "**STEP 2: WIFI ENVIRONMENT CHECK**",
        "description": "Document the customer's WiFi connection details and environment for analysis.",
        "category": "wifi_analysis",
        "input_fields": [
            {
                "name": "connection_type",
                "label": "Connection Type",
                "type": "select",
                "required": True,
                "options": ["wifi", "wired"]
            },
            {
                "name": "wifi_band",
                "label": "WiFi Band",
                "type": "select",
                "required": True,
                "options": ["2.4", "5", "6"]
            },
            {
                "name": "signal_strength",
                "label": "Signal Strength",
                "type": "select",
                "required": True,
                "options": ["excellent", "good", "poor"]
            },
            {
                "name": "device_capability",
                "label": "Device WiFi Capability",
                "type": "select",
                "required": True,
                "options": ["2.4_only", "dual", "6e"]
            },
            {
                "name": "distance_from_router",
                "label": "Distance from Router (feet)",
                "type": "number",
                "required": True,
                "placeholder": "Enter distance in feet"
            }
        ],
        "options": {
            "Continue to Speed Test": "SPEED_TEST_CHECK"
        },
        "help_text": "**Tip:** Collect detailed WiFi environment information for recommendations."
    },
    "SPEED_TEST_CHECK": {
        "question": "**STEP 3: SPEED TEST DOCUMENTATION**", 
        "description": "Document speed test results before troubleshooting begins.",
        "category": "speed_documentation",
        "input_fields": [
            {
                "name": "speed_before",
                "label": "Download Speed Before Troubleshooting (Mbps)",
                "type": "number",
                "required": True,
                "placeholder": "Enter download speed in Mbps"
            },
            {
                "name": "upload_speed_before",
                "label": "Upload Speed Before Troubleshooting (Mbps)",
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
                    "AT&T Speed Test", "Other"
                ]
            },
            {
                "name": "customer_device",
                "label": "Customer Device Used",
                "type": "select",
                "required": True,
                "options": [
                    "iPhone", "Android Phone", "iPad", "Android Tablet",
                    "Windows Laptop", "Mac Laptop", "Desktop PC", "Other"
                ]
            }
        ],
        "options": {
            "Continue to Troubleshooting": "EXECUTE_TROUBLESHOOTING"
        },
        "help_text": "**Tip:** Document baseline speeds before starting troubleshooting steps."
    },
    "EXECUTE_TROUBLESHOOTING": {
        "question": "**STEP 4: EXECUTE TROUBLESHOOTING**",
        "description": "Based on selected events, follow the troubleshooting steps for each event. Complete ALL steps before proceeding.\n\nExecute troubleshooting steps for each selected event and document results.",
        "category": "execution",
        "input_fields": [
            {
                "name": "troubleshooting_steps_completed",
                "label": "Troubleshooting Steps Completed (Document Each Attempt)",
                "type": "textarea",
                "required": True,
                "placeholder": "Document each troubleshooting step attempted and the results..."
            },
            {
                "name": "speed_after_troubleshooting",
                "label": "Speed Test After Troubleshooting",
                "type": "number",
                "required": True,
                "placeholder": "Enter download speed after troubleshooting"
            },
            {
                "name": "issue_status",
                "label": "Issue Status After Troubleshooting",
                "type": "select",
                "required": True,
                "options": [
                    "✅ Resolved completely",
                    "🔄 Improved but still slow", 
                    "❌ No improvement"
                ]
            }
        ],
        "options": {
            "Issue Resolved": "RESOLVED",
            "Issue Improved - Try More Steps": "EXECUTE_TROUBLESHOOTING_NEXT",
            "No Improvement - Escalate": "ESCALATE_TIER2"
        },
        "help_text": "**Tip:** Try all recommended troubleshooting steps and document results before proceeding."
    },
    "EXECUTE_TROUBLESHOOTING_NEXT": {
        "question": "**STEP 4B: ADDITIONAL TROUBLESHOOTING**",
        "description": "Try additional troubleshooting steps since the previous attempts improved but didn't fully resolve the issue.",
        "category": "execution_continued",
        "input_fields": [
            {
                "name": "additional_steps_completed",
                "label": "Additional Troubleshooting Steps Completed",
                "type": "textarea",
                "required": True,
                "placeholder": "Document additional troubleshooting steps attempted..."
            },
            {
                "name": "final_speed_test",
                "label": "Final Speed Test Result",
                "type": "number",
                "required": True,
                "placeholder": "Enter final download speed"
            },
            {
                "name": "final_issue_status",
                "label": "Final Issue Status",
                "type": "select",
                "required": True,
                "options": [
                    "✅ Resolved completely",
                    "🔄 Still having issues"
                ]
            }
        ],
        "options": {
            "Issue Resolved": "RESOLVED",
            "Still Having Issues - Generate Report": "ESCALATE_TIER2"
        },
        "help_text": "**Tip:** Document all additional steps attempted before escalating."
    },
    "ESCALATE_TIER2": {
        "question": "**TIER 2 ESCALATION REQUIRED**",
        "description": "Issue requires escalation to Tier 2. Generating comprehensive report with all troubleshooting data.",
        "category": "escalation",
        "input_fields": [
            {
                "name": "escalation_reason",
                "label": "Reason for Escalation",
                "type": "textarea",
                "required": True,
                "placeholder": "Explain why the issue could not be resolved at Tier 1 and what was attempted..."
            },
            {
                "name": "customer_callback_number",
                "label": "Customer Callback Number",
                "type": "tel",
                "required": True,
                "placeholder": "Enter best callback number for customer"
            },
            {
                "name": "best_time_to_call",
                "label": "Best Time to Call Customer",
                "type": "select",
                "required": True,
                "options": [
                    "Morning (8 AM - 12 PM)",
                    "Afternoon (12 PM - 5 PM)", 
                    "Evening (5 PM - 8 PM)",
                    "Anytime"
                ]
            }
        ],
        "options": {
            "Generate Tier 2 Report": "TIER2_REPORT_GENERATED"
        },
        "help_text": "**Tip:** Provide complete escalation details for Tier 2 follow-up."
    },
    "RESOLVED": {
        "question": "**CASE RESOLVED SUCCESSFULLY**",
        "description": "Customer issue has been resolved through troubleshooting steps.",
        "category": "resolution",
        "options": {},
        "help_text": "**Success:** Issue resolved without escalation needed."
    },
    "TIER2_REPORT_GENERATED": {
        "question": "**TIER 2 ESCALATION COMPLETE**",
        "description": "Comprehensive report generated and case escalated to Tier 2 with all troubleshooting data.",
        "category": "escalation_complete",
        "options": {},
        "help_text": "**Escalated:** Tier 2 team will contact customer using provided information."
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
