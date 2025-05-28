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
        Generate prioritized troubleshooting plan based on Eero Insight events and speed test data
        """
        # Prepare the analysis prompt
        selected_events = troubleshooting_context.get('selected_events', [])
        channel_util = troubleshooting_context.get('channel_utilization', {})
        speed_data = troubleshooting_context
        
        events_text = "\n".join([f"- {event}" for event in selected_events]) if selected_events else "No specific events selected"
        
        prompt = f"""
You are an expert Eero WiFi troubleshooting specialist. Based on the following data, create a prioritized step-by-step troubleshooting plan.

SELECTED EERO INSIGHT EVENTS:
{events_text}

CHANNEL UTILIZATION:
- 2.4 GHz: {channel_util.get('2_4_ghz', 'N/A')}%
- 5 GHz: {channel_util.get('5_ghz', 'N/A')}%

SPEED TEST RESULTS:
- Customer Device: {speed_data.get('customer_device', 'N/A')}
- Current Band: {speed_data.get('ghz_band', 'N/A')}
- Customer Speed: {speed_data.get('download_speed', 'N/A')} Mbps down / {speed_data.get('upload_speed', 'N/A')} Mbps up
- Eero Analytics: {speed_data.get('eero_analytics_download', 'N/A')} Mbps down / {speed_data.get('eero_analytics_upload', 'N/A')} Mbps up

EQUIPMENT:
- ONT Type: {customer_info.get('ont_type', 'Nokia')}
- Router Type: {customer_info.get('router_type', 'Eero')}
- Issue Type: {customer_info.get('issue_type', 'Speed Issues')}

Create a prioritized troubleshooting plan with 3-5 specific steps. For each step:
1. State the action clearly
2. Explain why this step addresses the identified events
3. Include expected results/what to look for

Focus on the most impactful fixes first based on the events and speed discrepancy between customer device and Eero analytics.

Format as a numbered list with clear action items.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Eero WiFi troubleshooting specialist. Provide clear, actionable troubleshooting steps prioritized by impact and likelihood of success."
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