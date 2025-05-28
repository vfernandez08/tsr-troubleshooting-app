import os
import json
from openai import OpenAI

class TroubleshootingAI:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    def analyze_speed_test_and_alarms(self, speed_test_data, alarm_data, customer_info):
        """
        Analyze speed test results and alarm data to suggest troubleshooting steps
        """
        # Prepare the analysis prompt
        prompt = f"""
You are an expert fiber internet technical support specialist. Based on the following customer data, provide specific troubleshooting recommendations.

CUSTOMER SPEED TEST DATA:
- Device Used: {speed_test_data.get('device_type', 'N/A')}
- GHz Band: {speed_test_data.get('ghz_band', 'N/A')}
- Download Speed: {speed_test_data.get('download_speed', 'N/A')} Mbps
- Upload Speed: {speed_test_data.get('upload_speed', 'N/A')} Mbps
- Speed Test App: {speed_test_data.get('test_app', 'N/A')}
- Expected Package Speed: {customer_info.get('speed_package', 'N/A')}

ALARM/STREAM DATA:
{alarm_data.get('alarm_details', 'No alarms detected')}

ONT EQUIPMENT:
- ONT Type: {customer_info.get('ont_type', 'Nokia')}
- Router Type: {customer_info.get('router_type', 'Eero')}

Please provide 3-5 specific troubleshooting steps in order of priority. Focus on:
1. Speed optimization based on device band and speeds
2. Addressing any alarms found
3. Equipment-specific recommendations for Nokia ONT + Eero setup
4. Connection and configuration checks

Format your response as a numbered list with brief explanations for each step.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using the cost-effective model you mentioned
                messages=[
                    {
                        "role": "system",
                        "content": "You are a fiber internet technical support expert. Provide clear, actionable troubleshooting steps based on speed test and alarm data."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.3  # Lower temperature for more consistent technical advice
            )
            
            return {
                "success": True,
                "recommendations": response.choices[0].message.content,
                "model_used": "gpt-4o-mini"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_recommendations": self._get_fallback_recommendations(speed_test_data, alarm_data)
            }
    
    def generate_comprehensive_troubleshooting_plan(self, troubleshooting_context, customer_info):
        """
        Generate comprehensive troubleshooting plan using all collected data from Steps 1-3
        """
        # Extract all collected data
        device_category = troubleshooting_context.get('customer_device_category', 'Unknown')
        device_model = troubleshooting_context.get('customer_device_type', 'Unknown')
        ghz_band = troubleshooting_context.get('ghz_band', 'Unknown')
        download_speed = troubleshooting_context.get('download_speed', 0)
        upload_speed = troubleshooting_context.get('upload_speed', 0)
        speed_test_app = troubleshooting_context.get('speed_test_app', 'Unknown')
        selected_events = troubleshooting_context.get('selected_events', [])
        channel_util = troubleshooting_context.get('channel_utilization', {})
        event_stream_details = troubleshooting_context.get('event_stream_details', 'No specific details')
        
        # Build comprehensive prompt
        prompt = f"""
I need you to analyze this comprehensive troubleshooting case and provide specific recommendations.

**CUSTOMER DEVICE & PERFORMANCE:**
- Device: {device_model} ({device_category})
- Current Wi-Fi Band: {ghz_band} 
- Speed Test Results: {download_speed} Mbps down / {upload_speed} Mbps up
- Speed Test App Used: {speed_test_app}
- Router: {customer_info.get('router_type', 'Eero')}

**NETWORK ENVIRONMENT:**
- 2.4 GHz Channel Utilization: {channel_util.get('2_4_ghz', 'N/A')}%
- 5 GHz Channel Utilization: {channel_util.get('5_ghz', 'N/A')}%

**EVENTS DETECTED IN EERO INSIGHT:**
{', '.join(selected_events) if selected_events else 'No specific events found'}

**MONITORING DATA:**
{event_stream_details}

**CUSTOMER REPORTED ISSUE:**
{troubleshooting_context.get('specific_issue_description', customer_info.get('issue_type', 'Connectivity Issues'))}

Based on this comprehensive data, I need you to:

1. **Acknowledge the specific situation** - Reference the actual device model and current performance
2. **Provide targeted troubleshooting steps** - Maximum 5 steps, prioritized by likelihood of success
3. **Explain the reasoning** - Why each step addresses the specific issues found
4. **Include a customer talk track** - What the agent should say to explain the situation

Start your response with a brief analysis like: "I can see your {device_model} is currently getting {download_speed} Mbps on the {ghz_band} band. Based on the [specific issues found], here's what we can do..."
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are **VictorAI**, an advanced Tier-1 support assistant for a fiber ISP. Your role is to help agents resolve internet and Wi-Fi connectivity issues specifically related to customer devices (e.g., gaming consoles, streaming devices, smartphones, computers).

Follow these guidelines carefully:

✅ **Actions you CAN recommend**:
- Verify device Wi-Fi settings (forget/reconnect network, reset network settings)
- Check and adjust DNS settings (suggest public DNS like 8.8.8.8 or 1.1.1.1)
- Restart or power-cycle customer's device
- Verify router Wi-Fi settings (guest network creation, legacy mode, compatibility mode, temporarily disable 5GHz)
- Adjust device-specific settings (e.g., MTU size, NAT type, Wi-Fi band selection)
- Check Wi-Fi signal strength, distance from router, and recommend Eero extender if needed
- Compare wired vs Wi-Fi speed test results

🚫 **Actions you CANNOT recommend**:
- Any request for personally identifiable info (ONT ID, router serial, MAC addresses, account numbers)
- Tier-2 actions like backend provisioning, router firmware changes, VLAN settings, or CGNAT troubleshooting

💡 **Use provided context intelligently**:
- Incorporate relevant information from Knowledge Base snippets and similar resolved past cases (if provided)
- Be specific to the device model mentioned (e.g., PS5, Roku Ultra, Samsung Galaxy S24)
- Clearly acknowledge steps the agent already took; don't repeat unnecessarily

📋 **Response format (always)**:
- Start with a brief analysis of the specific situation
- Provide clear, concise, numbered troubleshooting steps (max 5 steps)
- End with a brief, polite customer Talk Track the agent can read verbatim to explain clearly what you're doing
- If the issue is clearly beyond Tier-1 (e.g., possible firmware bug or compatibility issue), add a final line starting with 'Escalate:' and briefly state why escalation is needed."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            suggestions = response.choices[0].message.content
            
            # Extract priority order from suggestions
            priority_order = self._extract_priority_order(suggestions, selected_events)
            
            # Create data summary for verification
            data_summary = f"Analyzed: {device_model} getting {download_speed}/{upload_speed} Mbps on {ghz_band}, {len(selected_events)} events detected"
            
            return {
                "success": True,
                "suggestions": suggestions,
                "priority_order": priority_order,
                "model_used": "gpt-4o-mini",
                "data_summary": data_summary
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_suggestions": self._get_event_fallback_recommendations(troubleshooting_context)
            }

    def generate_event_based_troubleshooting_plan(self, troubleshooting_context, customer_info):
        """
        Generate device-specific troubleshooting plan using VictorAI specialized prompt
        """
        # Redirect to comprehensive method for better data handling
        return self.generate_comprehensive_troubleshooting_plan(troubleshooting_context, customer_info)
    
    def _extract_priority_order(self, suggestions, selected_events):
        """Extract priority order from AI suggestions"""
        priority_events = []
        
        # Look for common event types in the suggestions
        event_keywords = {
            'internet_connectivity_failure': ['connectivity', 'connection', 'internet'],
            'channel_switch_detected': ['channel', 'interference'],
            'user_device_removed': ['device', 'reconnect', 'forget'],
            'dfs_strike_detected': ['radar', 'dfs'],
            'gateway_to_leaf_link_signal_changed': ['backhaul', 'signal', 'placement']
        }
        
        suggestion_lower = suggestions.lower()
        for event, keywords in event_keywords.items():
            if event in selected_events and any(keyword in suggestion_lower for keyword in keywords):
                priority_events.append(event)
        
        return priority_events
    
    def _get_event_fallback_recommendations(self, troubleshooting_context):
        """
        Provide event-based fallback recommendations if AI fails
        """
        recommendations = []
        selected_events = troubleshooting_context.get('selected_events', [])
        channel_util = troubleshooting_context.get('channel_utilization', {})
        
        # Event-specific recommendations
        if 'internet_connectivity_failure' in selected_events:
            recommendations.append("1. Check ONT light status and power cycle if needed")
            recommendations.append("2. Verify Ethernet connection between ONT and Eero")
        
        if 'user_device_removed' in selected_events:
            recommendations.append("3. Have customer forget WiFi network and reconnect")
            recommendations.append("4. Test device closer to router to verify signal strength")
        
        if 'channel_switch_detected' in selected_events or channel_util.get('2_4_ghz', 0) > 80:
            recommendations.append("5. Check channel utilization and manually assign less crowded channel")
        
        if 'dfs_strike_detected' in selected_events:
            recommendations.append("6. Allow time for automatic channel re-selection after radar interference")
        
        # General recommendations if no specific events
        if not recommendations:
            recommendations.append("1. Power cycle Eero router and test speeds")
            recommendations.append("2. Move device closer to router for testing")
            recommendations.append("3. Check for interference and optimize channel selection")
        
        return "\n".join(recommendations)

    def _get_fallback_recommendations(self, speed_test_data, alarm_data):
        """
        Provide basic recommendations if AI fails
        """
        recommendations = []
        
        # Speed-based recommendations
        download_speed = speed_test_data.get('download_speed', 0)
        if isinstance(download_speed, str):
            try:
                download_speed = float(download_speed)
            except:
                download_speed = 0
                
        if download_speed < 100:
            recommendations.append("1. Check device connection - consider switching to 5GHz band for better speeds")
            recommendations.append("2. Reboot ONT and router to refresh connection")
            
        # Band-specific recommendations  
        ghz_band = speed_test_data.get('ghz_band', '').lower()
        if '2.4' in ghz_band:
            recommendations.append("3. Move device to 5GHz network for improved performance")
            
        # Alarm-based recommendations
        if 'alarm' in alarm_data.get('alarm_details', '').lower():
            recommendations.append("4. Address active alarms - check ONT light status and connections")
            
        recommendations.append("5. Verify all cable connections are secure")
        
        return "\n".join(recommendations)