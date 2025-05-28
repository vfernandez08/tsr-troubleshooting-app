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
    
    def generate_event_based_troubleshooting_plan(self, troubleshooting_context, customer_info):
        """
        Generate device-specific troubleshooting plan using VictorAI specialized prompt
        """
        # Extract data from troubleshooting context
        selected_events = troubleshooting_context.get('selected_events', [])
        channel_util = troubleshooting_context.get('channel_utilization', {})
        speed_data = troubleshooting_context
        
        # Map device info from speed test data
        device_type = speed_data.get('customer_device_category', speed_data.get('customer_device_type', 'Unknown Device'))
        device_model = speed_data.get('customer_device', speed_data.get('customer_device_type', 'N/A'))
        specific_issue = speed_data.get('specific_issue_description', '')
        issue_description = specific_issue if specific_issue else customer_info.get('issue_description', customer_info.get('issue_type', 'Connectivity Issues'))
        
        # Format speed test results
        wifi_speed = f"{speed_data.get('download_speed', 'N/A')} Mbps down / {speed_data.get('upload_speed', 'N/A')} Mbps up"
        wired_speed = "N/A"  # Would need to be collected separately
        
        # Extract additional context
        ghz_band = speed_data.get('ghz_band', 'Unknown')
        router_type = customer_info.get('router_type', 'Eero')
        
        # Format events as steps already tried
        events_text = ", ".join(selected_events) if selected_events else "None documented"
        
        # Build the VictorAI prompt with placeholders filled
        prompt = f"""
Customer Device Type:      {device_type}
Device Model:              {device_model}
Reported Problem:          {issue_description}
Wi-Fi Speed Test Result:   {wifi_speed} (on {ghz_band} band)
Wired Speed Test Result:   {wired_speed}
Distance from Router:      N/A
Signal Strength:           N/A
Router Type:               {router_type}
Steps Already Taken:       Events detected: {events_text}
Knowledge Base Snippet:    Channel Utilization - 2.4GHz: {channel_util.get('2_4_ghz', 'N/A')}%, 5GHz: {channel_util.get('5_ghz', 'N/A')}%
Similar Past Cases:        N/A

Return:
• Numbered troubleshooting steps (1–5 steps max)
• Customer-friendly Talk Track paragraph
• Optional escalation line if needed (start with 'Escalate:')
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are **VictorAI**, an advanced Tier-1 support assistant for a fiber ISP. Your role is to help agents resolve internet and Wi-Fi connectivity issues specifically related to customer devices (e.g., gaming consoles, streaming devices, smartphones, computers).\n\nFollow these guidelines carefully:\n\n✅ **Actions you CAN recommend**:\n- Verify device Wi-Fi settings (forget/reconnect network, reset network settings)\n- Check and adjust DNS settings (suggest public DNS like 8.8.8.8 or 1.1.1.1)\n- Restart or power-cycle customer's device\n- Verify router Wi-Fi settings (guest network creation, legacy mode, compatibility mode, temporarily disable 5GHz)\n- Adjust device-specific settings (e.g., MTU size, NAT type, Wi-Fi band selection)\n- Check Wi-Fi signal strength, distance from router, and recommend Eero extender if needed\n- Compare wired vs Wi-Fi speed test results\n\n🚫 **Actions you CANNOT recommend**:\n- Any request for personally identifiable info (ONT ID, router serial, MAC addresses, account numbers)\n- Tier-2 actions like backend provisioning, router firmware changes, VLAN settings, or CGNAT troubleshooting\n\n💡 **Use provided context intelligently**:\n- Incorporate relevant information from Knowledge Base snippets and similar resolved past cases (if provided)\n- Be specific to the device model mentioned (e.g., PS5, Roku Ultra, Samsung Galaxy S24)\n- Clearly acknowledge steps the agent already took; don't repeat unnecessarily\n\n📋 **Response format (always)**:\n- Provide clear, concise, numbered troubleshooting steps (max 5 steps)\n- End with a brief, polite customer Talk Track the agent can read verbatim to explain clearly what you're doing\n- If the issue is clearly beyond Tier-1 (e.g., possible firmware bug or compatibility issue), add a final line starting with 'Escalate:' and briefly state why escalation is needed."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            suggestions = response.choices[0].message.content
            
            # Extract priority order from suggestions
            priority_order = self._extract_priority_order(suggestions, selected_events)
            
            return {
                "success": True,
                "suggestions": suggestions,
                "priority_order": priority_order,
                "model_used": "gpt-4o-mini"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_suggestions": self._get_event_fallback_recommendations(troubleshooting_context)
            }
    
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